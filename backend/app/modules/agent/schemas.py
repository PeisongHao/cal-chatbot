from typing import Optional, Literal

from pydantic import BaseModel, Field


class UserIntentExtraction(BaseModel):
    action: Literal[
        "create_booking",
        "list_bookings",
        "cancel_pending",
        "general",
    ] = Field(
        ...,
        description=(
            "create_booking: user wants to book/schedule/create a meeting. "
            "list_bookings: user wants to show/list/view/check scheduled meetings. "
            "cancel_pending: user wants to cancel the current unfinished flow. "
            "general: unrelated message."
        ),
    )

    name: Optional[str] = Field(
        default=None,
        description="Attendee name if mentioned.",
    )

    email: Optional[str] = Field(
        default=None,
        description="Attendee email if mentioned.",
    )

    date: Optional[str] = Field(
        default=None,
        description="Meeting date in YYYY-MM-DD format if mentioned.",
    )

    time: Optional[str] = Field(
        default=None,
        description="Meeting time in HH:MM 24-hour format if mentioned.",
    )

    timezone: Optional[str] = Field(
        default=None,
        description="Timezone if mentioned.",
    )

    reason: Optional[str] = Field(
        default=None,
        description="Meeting reason if mentioned.",
    )