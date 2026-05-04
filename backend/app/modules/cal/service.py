from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings
from app.modules.cal.schemas import (
    BookingAttendeeSummary,
    BookingSummary,
    CreateBookingRequest,
)


class CalService:
    BASE_URL = "https://api.cal.com/v2"

    def _headers(self) -> Dict[str, str]:
        if not settings.CAL_API_KEY:
            raise ValueError("CAL_API_KEY is missing. Please set it in your .env file.")

        return {
            "Authorization": f"Bearer {settings.CAL_API_KEY}",
            "Content-Type": "application/json",
            "cal-api-version": settings.CAL_API_VERSION,
        }

    def _build_create_booking_payload(
        self,
        request: CreateBookingRequest,
    ) -> Dict[str, Any]:
        event_type_slug = settings.CAL_EVENT_TYPE_SLUG
        username = settings.CAL_USERNAME

        if not event_type_slug:
            raise ValueError(
                "eventTypeSlug is missing. Provide it in the request or set CAL_EVENT_TYPE_SLUG in .env."
            )

        if not username:
            raise ValueError(
                "username is missing. Provide it in the request or set CAL_USERNAME in .env."
            )

        payload: Dict[str, Any] = {
            "start": request.start,
            "attendee": request.attendee.dict(exclude_none=True),
            "eventTypeSlug": event_type_slug,
            "username": username,
        }

        optional_fields = {
            "organizationSlug": request.organizationSlug,
            "guests": request.guests,
            "metadata": request.metadata,
            "lengthInMinutes": request.lengthInMinutes,
            "bookingFieldsResponses": request.bookingFieldsResponses,
            "location": request.location,
            "allowConflicts": request.allowConflicts,
            "allowBookingOutOfBounds": request.allowBookingOutOfBounds,
        }

        for key, value in optional_fields.items():
            if value is not None:
                payload[key] = value

        return payload

    def create_booking(self, request: CreateBookingRequest) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bookings"
        payload = self._build_create_booking_payload(request)

        try:
            response = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=30,
            )
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Cal.com request timed out while creating booking.",
                "data": {
                    "sent_payload": payload,
                },
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": "Failed to connect to Cal.com while creating booking.",
                "data": {
                    "error": str(e),
                    "sent_payload": payload,
                },
            }

        if response.status_code != 201:
            return {
                "success": False,
                "message": "Failed to create booking.",
                "data": {
                    "status_code": response.status_code,
                    "error": response.text,
                    "sent_payload": payload,
                },
            }

        return {
            "success": True,
            "message": "Booking created successfully.",
            "data": response.json(),
        }

    def list_bookings(self, email: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bookings"

        params: Dict[str, str] = {}

        if email:
            params["attendeeEmail"] = email

        try:
            response = requests.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=30,
            )
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Cal.com request timed out while fetching bookings.",
                "bookings": [],
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": "Failed to connect to Cal.com while fetching bookings.",
                "data": {
                    "error": str(e),
                },
                "bookings": [],
            }

        if response.status_code != 200:
            return {
                "success": False,
                "message": "Failed to fetch bookings.",
                "data": {
                    "status_code": response.status_code,
                    "error": response.text,
                },
                "bookings": [],
            }

        data = response.json()
        raw_bookings = data.get("data", [])

        bookings: List[BookingSummary] = []

        for booking in raw_bookings:
            raw_attendees = booking.get("attendees") or []

            attendees = [
                BookingAttendeeSummary(
                    name=attendee.get("name"),
                    email=attendee.get("email"),
                    timeZone=attendee.get("timeZone"),
                    phoneNumber=attendee.get("phoneNumber"),
                    language=attendee.get("language"),
                    absent=attendee.get("absent"),
                )
                for attendee in raw_attendees
            ]

            event_type = booking.get("eventType") or {}

            bookings.append(
                BookingSummary(
                    id=booking.get("id"),
                    uid=booking.get("uid"),
                    title=booking.get("title"),
                    description=booking.get("description"),
                    status=booking.get("status"),
                    start=booking.get("start"),
                    end=booking.get("end"),
                    duration=booking.get("duration"),
                    location=booking.get("location"),
                    meetingUrl=booking.get("meetingUrl"),
                    eventTypeId=booking.get("eventTypeId"),
                    eventTypeSlug=event_type.get("slug"),
                    attendees=attendees,
                    createdAt=booking.get("createdAt"),
                    updatedAt=booking.get("updatedAt"),
                    metadata=booking.get("metadata"),
                    bookingFieldsResponses=booking.get("bookingFieldsResponses"),
                )
            )

        return {
            "success": True,
            "message": "Bookings fetched successfully.",
            "bookings": bookings,
        }


cal_service = CalService()