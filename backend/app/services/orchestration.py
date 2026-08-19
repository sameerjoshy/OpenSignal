"""Omnichannel orchestration - route accounts to channels by buying intent tier.

Email is the only channel implemented today; the tier rules are designed so
SMS / Slack / LinkedIn can be slotted in without changing campaign logic.
"""

EMAIL = "email"
SMS = "sms"
SLACK = "slack"
LINKEDIN = "linkedin"

ALL_CHANNELS = (EMAIL, SMS, SLACK, LINKEDIN)

TIER_CHANNELS: dict[int, tuple[str, ...]] = {
    1: (EMAIL, SMS, LINKEDIN),
    2: (EMAIL, SLACK),
    3: (EMAIL,),
}


def route_campaign(account: object | None, tier: int | None = None) -> list[str]:
    """Return the ordered channel list for an account given its intent tier.

    Accepts either a tier int or an account-like object with a `.tier` attribute.
    Unscored accounts are treated as Tier 3 (nurture).
    """
    resolved = tier if tier is not None else getattr(account, "tier", None)
    tier_value = resolved if isinstance(resolved, int) and resolved in TIER_CHANNELS else 3
    return list(TIER_CHANNELS[tier_value])


def tier_for_channels(channels: list[str] | None) -> int:
    """Map a desired channel set back to the minimum tier that unlocks it."""
    channels = channels or [EMAIL]
    if SMS in channels or LINKEDIN in channels:
        return 1
    if SLACK in channels:
        return 2
    return 3