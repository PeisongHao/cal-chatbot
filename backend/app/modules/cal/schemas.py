from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field


class AttendeeInput(BaseModel):
    name: str = Field(
        ...,
        example="Test User",
        description="The name of the attendee.",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        example="testuser@example.com",
        description="The email of the attendee.",
    )
    timeZone: str = Field(
        ...,
        example="America/Los_Angeles",
        description="The time zone of the attendee.",
    )
    phoneNumber: Optional[str] = Field(
        default=None,
        example="+19876543210",
        description="The phone number of the attendee in international format.",
    )
    language: Optional[str] = Field(
        default="en",
        example="en",
        description="The preferred language of the attendee.",
    )


class CreateBookingRequest(BaseModel):
    start: str = Field(
        ...,
        example="2026-05-08T22:00:00Z",
        description="Booking start time in UTC ISO 8601 format.",
    )

    attendee: AttendeeInput = Field(
        ...,
        description="The attendee's details.",
    )

    eventTypeSlug: Optional[str] = Field(
        default=None,
        example="30min",
        description=(
            "Optional override. If not provided, backend will use "
            "CAL_EVENT_TYPE_SLUG from .env."
        ),
    )

    username: Optional[str] = Field(
        default=None,
        example="peisong",
        description=(
            "Optional override. If not provided, backend will use "
            "CAL_USERNAME from .env."
        ),
    )

    organizationSlug: Optional[str] = Field(
        default=None,
        example="acme-corp",
        description="Optional organization slug.",
    )

    guests: Optional[List[EmailStr]] = Field(
        default=None,
        example=["guest1@example.com", "guest2@example.com"],
        description="Optional list of guest emails attending the event.",
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"reason": "Discuss Cal.com chatbot project"},
        description="Additional custom data to store with the booking.",
    )

    lengthInMinutes: Optional[int] = Field(
        default=None,
        example=30,
        description=(
            "Optional booking length. If not provided, event type default length is used."
        ),
    )

    bookingFieldsResponses: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"customField": "customValue"},
        description=(
            "Custom booking field responses. Keys should match booking field slugs."
        ),
    )

    location: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"type": "integration", "integration": "cal-video"},
        description="Optional location object. Use only if your event type requires it.",
    )

    allowConflicts: Optional[bool] = Field(
        default=False,
        example=False,
        description=(
            "When true and the authenticated user is host, availability conflict checks "
            "can be bypassed."
        ),
    )

    allowBookingOutOfBounds: Optional[bool] = Field(
        default=None,
        example=False,
        description=(
            "When true and the authenticated user is host, booking time out-of-bounds "
            "checks can be bypassed."
        ),
    )


class BookingAttendeeSummary(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    timeZone: Optional[str] = None
    phoneNumber: Optional[str] = None
    language: Optional[str] = None
    absent: Optional[bool] = None


class BookingSummary(BaseModel):
    id: Optional[int] = None
    uid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    start: Optional[str] = None
    end: Optional[str] = None
    duration: Optional[int] = None

    location: Optional[str] = None
    meetingUrl: Optional[str] = None

    eventTypeId: Optional[int] = None
    eventTypeSlug: Optional[str] = None

    attendees: List[BookingAttendeeSummary] = []

    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None
    bookingFieldsResponses: Optional[Dict[str, Any]] = None


class CreateBookingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ListBookingsResponse(BaseModel):
    success: bool
    message: str
    bookings: List[BookingSummary] = []