"""Seed the database with demo data for local development.

Usage:
    python scripts/seed_db.py
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta

from app.database import crud
from app.database.models import Account, Campaign, CampaignAccount, Signal, User
from app.database.session import AsyncSessionLocal

SAMPLE_COMPANIES = [
    {"company_name": "Acme Analytics", "domain": "acmeanalytics.com", "industry": "B2B SaaS"},
    {"company_name": "Globex Inc", "domain": "globex.io", "industry": "DevTools"},
    {"company_name": "Initech", "domain": "initech.com", "industry": "Fintech"},
    {"company_name": "Umbrella Labs", "domain": "umbrellalabs.ai", "industry": "AI/ML"},
    {"company_name": "Stark Robotics", "domain": "starkrobotics.co", "industry": "Hardware"},
]

SIGNAL_TYPES = [
    ("funding", "raised a Series B round"),
    ("job_change", "hired a new VP of Sales"),
    ("news", "announced a major partnership"),
    ("website_intent", "traffic surged 40% week over week"),
    ("product_launch", "launched a new product"),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        user = await crud.get_user_by_email(db, "demo@opensignal.app")
        if not user:
            user = User(email="demo@opensignal.app", full_name="Demo Founder", plan="free")
            user.set_password("password123")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print("Created demo user: demo@opensignal.app / password123")

        campaign = Campaign(
            user_id=user.id,
            name="Seed Demo Campaign",
            description="Personalized outreach to recently-funded B2B companies",
            status="draft",
            channels={"email": True, "linkedin": False, "call": False},
            cadence={"step_interval_days": 2, "max_steps": 3},
        )
        db.add(campaign)

        for company in SAMPLE_COMPANIES:
            account = await crud.find_or_create_account(db, user.id, **company)
            tier = random.choice([1, 2, 3])
            account.score = random.randint(20, 95)
            account.tier = tier
            account.score_rationale = "Seeded demo score"
            db.add(CampaignAccount(campaign_id=campaign.id, account_id=account.id, status="ready", tier=tier))

            for _ in range(random.randint(2, 4)):
                stype, verb = random.choice(SIGNAL_TYPES)
                db.add(
                    Signal(
                        user_id=user.id,
                        account_id=account.id,
                        source=random.choice(["apollo", "sec_edgar", "newsapi", "manual"]),
                        signal_type=stype,
                        title=f"{account.company_name} {verb}",
                        description="Seeded signal for local development.",
                        detected_at=datetime.utcnow() - timedelta(days=random.randint(0, 14)),
                    )
                )

        await db.commit()
        print(
            f"Seeded {len(SAMPLE_COMPANIES)} accounts, a demo campaign, and signals for demo@opensignal.app"
        )


if __name__ == "__main__":
    asyncio.run(main())
