"""Tests for the background Celery task wrappers (campaigns.run, signals.*).

These tasks use asyncio.run() with real DB sessions, so we exercise them against
the SQLite test DB and monkeypatch the heavy async internals (run_campaign,
detector, scorer) so the tests are fast and don't need Redis/external APIs.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.auth.jwt import decode_access_token
from app.database import crud
from app.database.models import Campaign
from app.database.session import AsyncSessionLocal
from app.tasks import campaign_tasks, signal_tasks

from tests.conftest import auth_headers


def _run_in_thread(fn, *args):
    """Run a sync Celery task (which calls asyncio.run) in its own thread + event loop."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(fn, *args).result()


async def _owner_id(token: str) -> uuid.UUID:
    return uuid.UUID(decode_access_token(token)["sub"])


async def _create_campaign(db, user_id: uuid.UUID, name: str = "TaskCampaign") -> Campaign:
    campaign = Campaign(name=name, user_id=user_id)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


# ---------------------------------------------------------------- campaigns.run
async def test_campaign_run_task_success(client, user_token, monkeypatch):
    owner_id = await _owner_id(user_token)
    async with AsyncSessionLocal() as db:
        campaign = await _create_campaign(db, owner_id)

    async def fake_run_campaign(db, user, campaign):
        return {"processed": 1, "signals": 2, "scored": 1, "generated": 1, "errors": 0}

    monkeypatch.setattr(campaign_tasks, "run_campaign", fake_run_campaign)

    result = _run_in_thread(campaign_tasks.run_campaign_task, str(owner_id), str(campaign.id))
    assert result["ok"] is True
    assert result["processed"] == 1


async def test_campaign_run_task_missing_campaign(client, user_token, monkeypatch):
    owner_id = await _owner_id(user_token)

    async def fake_run_campaign(db, user, campaign):
        raise AssertionError("should not be called")

    monkeypatch.setattr(campaign_tasks, "run_campaign", fake_run_campaign)

    result = _run_in_thread(campaign_tasks.run_campaign_task, str(owner_id), str(uuid.uuid4()))
    assert result["ok"] is False
    assert "not found" in result["error"]


async def test_campaign_run_task_missing_user(client, user_token, monkeypatch):
    missing_user = uuid.uuid4()

    async def fake_run_campaign(db, user, campaign):
        raise AssertionError("should not be called")

    monkeypatch.setattr(campaign_tasks, "run_campaign", fake_run_campaign)

    result = _run_in_thread(campaign_tasks.run_campaign_task, str(missing_user), str(uuid.uuid4()))
    assert result["ok"] is False
    assert "not found" in result["error"]


# ---------------------------------------------------------------- signals.detect_account
async def test_detect_account_task_success(client, user_token, monkeypatch):
    owner_id = await _owner_id(user_token)

    async def fake_detect(db, user, account):
        return ["signal1", "signal2"]

    monkeypatch.setattr(signal_tasks.detector, "detect_for_account", fake_detect)

    async with AsyncSessionLocal() as db:
        account = await crud.find_or_create_account(db, owner_id, "DetectCo", domain="detectco.com")

    result = _run_in_thread(signal_tasks.detect_account_task, str(owner_id), str(account.id))
    assert result["ok"] is True
    assert result["detected"] == 2


async def test_detect_account_task_missing_account(client, user_token, monkeypatch):
    owner_id = await _owner_id(user_token)

    async def fake_detect(db, user, account):
        raise AssertionError("should not be called")

    monkeypatch.setattr(signal_tasks.detector, "detect_for_account", fake_detect)

    result = _run_in_thread(signal_tasks.detect_account_task, str(owner_id), str(uuid.uuid4()))
    assert result["ok"] is False
    assert "not found" in result["error"]


# ---------------------------------------------------------------- signals.score_account
async def test_score_account_task_success(client, user_token, monkeypatch):
    owner_id = await _owner_id(user_token)

    async def fake_score(db, user, account):
        return {"score": 82, "tier": 1, "rationale": "strong signals"}

    monkeypatch.setattr(signal_tasks.scorer, "score_account", fake_score)

    async with AsyncSessionLocal() as db:
        account = await crud.find_or_create_account(db, owner_id, "ScoreCo", domain="scoreco.com")

    result = _run_in_thread(signal_tasks.score_account_task, str(owner_id), str(account.id))
    assert result["ok"] is True
    assert result["score"] == 82
    assert result["tier"] == 1


async def test_score_account_task_missing_user(client, user_token, monkeypatch):
    missing_user = uuid.uuid4()

    async def fake_score(db, user, account):
        raise AssertionError("should not be called")

    monkeypatch.setattr(signal_tasks.scorer, "score_account", fake_score)

    result = _run_in_thread(signal_tasks.score_account_task, str(missing_user), str(uuid.uuid4()))
    assert result["ok"] is False
    assert "not found" in result["error"]


# ---------------------------------------------------------------- celery_app wiring
def test_celery_app_imports_tasks():
    """celery_app imports the task modules (no import errors)."""
    from app.tasks.celery_app import celery_app

    assert celery_app.main == "opensignal"
    # The task modules register names via @shared_task at import time.
    assert "campaigns.run" in celery_app.tasks
    assert "signals.detect_account" in celery_app.tasks
    assert "signals.score_account" in celery_app.tasks
