from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_optional_current_user
from app.database.user_model import UserModel

router = APIRouter()


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: float
    price_yearly: float
    description: str
    popular: bool = False
    badge: Optional[str] = None
    features: List[str]


class SubscriptionPlansResponse(BaseModel):
    plans: List[SubscriptionPlan]
    currency: str = "USD"


class CheckoutRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"  # "monthly" or "yearly"


class CheckoutResponse(BaseModel):
    success: bool
    message: str
    plan_id: str
    billing_cycle: str
    transaction_id: str
    status: str = "active"


PLANS: List[SubscriptionPlan] = [
    SubscriptionPlan(
        id="free",
        name="Free Starter",
        price_monthly=0.0,
        price_yearly=0.0,
        description="Essential tools to search and explore modern remote & tech jobs.",
        popular=False,
        badge=None,
        features=[
            "Full-text Job Search (FTS5)",
            "Basic Job Filters & Sorting",
            "Up to 5 Saved Jobs",
            "1 Active Job Alert",
            "Community Support",
        ],
    ),
    SubscriptionPlan(
        id="pro",
        name="Pro Candidate",
        price_monthly=19.0,
        price_yearly=180.0,  # $15/mo billed annually
        description="Supercharge your job hunt with AI matching, unlimited alerts & instant sync.",
        popular=True,
        badge="Most Popular",
        features=[
            "Everything in Free Starter",
            "AI Candidate Match Engine (Unlimited)",
            "Unlimited Saved Jobs & Personal Notes",
            "Up to 20 Real-Time Job Alerts",
            "Instant Automated Job Ingestion",
            "Priority Application Tracking",
            "Direct Employer Link Verification",
        ],
    ),
    SubscriptionPlan(
        id="enterprise",
        name="Career Accelerator",
        price_monthly=49.0,
        price_yearly=468.0,  # $39/mo billed annually
        description="For ambitious professionals seeking 1-on-1 AI match tuning & analytics.",
        popular=False,
        badge="Ultimate",
        features=[
            "Everything in Pro Candidate",
            "Custom AI Resume Parsing & Scoring",
            "Salary Proximity Analytics & Trends",
            "Automated Application Follow-Up Reminders",
            "Export Job Data (CSV / JSON)",
            "Dedicated 24/7 VIP Support",
        ],
    ),
]


@router.get(
    "/plans",
    response_model=SubscriptionPlansResponse,
)
def get_subscription_plans():
    """Retrieve available subscription pricing tiers and features."""
    return SubscriptionPlansResponse(plans=PLANS, currency="USD")


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
)
def checkout_subscription(
    req: CheckoutRequest,
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
):
    """Simulate a subscription checkout / upgrade."""
    valid_plan_ids = [p.id for p in PLANS]
    if req.plan_id not in valid_plan_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan ID. Must be one of: {', '.join(valid_plan_ids)}",
        )

    import uuid

    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    user_email = current_user.email if current_user else "Guest User"

    return CheckoutResponse(
        success=True,
        message=f"Successfully upgraded {user_email} to {req.plan_id.upper()} plan!",
        plan_id=req.plan_id,
        billing_cycle=req.billing_cycle,
        transaction_id=tx_id,
        status="active",
    )
