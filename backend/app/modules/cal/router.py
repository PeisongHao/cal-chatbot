from typing import Optional

from fastapi import APIRouter, Query

from app.modules.cal.schemas import (
    CreateBookingRequest,
    CreateBookingResponse,
    ListBookingsResponse,
)
from app.modules.cal.service import cal_service


router = APIRouter(
    prefix="/cal",
    tags=["Cal.com"],
)


@router.post("/bookings", response_model=CreateBookingResponse)
def create_booking(request: CreateBookingRequest):
    """
    Create a new booking on the host's Cal.com account.

    The user is the attendee.
    The host's username and event type slug are loaded from .env by default.
    """
    result = cal_service.create_booking(request)

    return CreateBookingResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        data=result.get("data"),
    )


@router.get("/bookings", response_model=ListBookingsResponse)
def list_bookings(
    email: Optional[str] = Query(
        default=None,
        description="Optional attendee email used to filter bookings.",
        example="testuser@example.com",
    )
):
    """
    List bookings from the host's Cal.com account.

    If email is provided, return bookings related to that attendee email.
    """
    result = cal_service.list_bookings(email=email)

    return ListBookingsResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        bookings=result.get("bookings", []),
    )