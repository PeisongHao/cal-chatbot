# Cal.com AI Scheduling Chatbot

This project is an AI scheduling chatbot built with **FastAPI**, **React**, **LangChain**, **OpenAI tool calling**, and the **Cal.com API**.

The chatbot allows users to book meetings on the host's Cal.com account and list scheduled meetings through a ChatGPT-style chat interface.

## Demo

[![Watch the demo](https://img.youtube.com/vi/JbBnvnc8nMI/maxresdefault.jpg)](https://youtu.be/JbBnvnc8nMI)

[Watch the demo on YouTube](https://youtu.be/JbBnvnc8nMI)

## Features

### 1. Book a Meeting Through Chat

Users can book a meeting using natural language.

Example:

```text
Book a meeting for Test User, email testuser@example.com, on 2026-05-08 at 3pm. Reason: discuss chatbot project.
```

The chatbot extracts the attendee name, email, meeting date, meeting time, meeting reason, and timezone. Then it creates a booking on the host's Cal.com account.

### 2. Multi-turn Booking Flow

Users do not need to provide all booking details at once.

Example:

```text
User: I want to book a meeting.
Bot: I still need name, email, date, time, and reason.

User: My name is Test User and my email is testuser@example.com.
Bot: I have your name and email. I still need date, time, and reason.

User: May 8 2026 at 3pm.
Bot: I still need the reason.

User: Reason is discuss chatbot project.
Bot: Booking created successfully.
```

### 3. Update Pending Booking Details

Before the booking is created, users can update details during the conversation.

Example:

```text
User: Book it on 2026-05-08 at 3pm.
User: Actually make it 4pm.
```

The chatbot updates the pending meeting time from `15:00` to `16:00`.

### 4. List Scheduled Meetings by Email

Users can list scheduled meetings by attendee email.

Example:

```text
Show meetings for testuser@example.com.
```

### 5. Multi-turn Meeting Lookup

If the user does not provide an email, the chatbot asks for it.

Example:

```text
User: Show my scheduled meetings.
Bot: What email should I use to look up the scheduled meetings?

User: testuser@example.com
Bot: Here are the scheduled meetings for testuser@example.com.
```

### 6. Session-based Conversation Memory

The backend uses `session_id` to keep temporary conversation state.

If the frontend does not provide a `session_id`, the backend can generate one and return it. The frontend stores the `session_id` in `localStorage` and sends it with future chat messages.

This allows the chatbot to remember unfinished booking or listing flows.

### 7. ChatGPT-style React Frontend

The frontend includes:

- Sidebar
- New chat button
- Message list
- User and assistant message bubbles
- Loading state
- Persistent `session_id`
- Bottom input box
- Enter-to-send behavior

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- OpenAI API
- Cal.com API v2
- Pydantic
- Requests
- python-dotenv
- Uvicorn

### Frontend

- React
- TypeScript
- Vite
- CSS
- Axios

## Project Structure

```text
cal-chatbot/
  backend/
    app/
      core/
        config.py

      modules/
        agent/
          service.py
          tools.py
          prompts.py
          schemas.py

        cal/
          router.py
          service.py
          schemas.py

        chat/
          router.py
          service.py
          schemas.py

      main.py

    requirements.txt
    .env.example

  frontend/
    src/
      api/
        chatApi.ts

      components/
        Sidebar.tsx
        ChatHeader.tsx
        MessageList.tsx
        ChatInput.tsx

      types/
        chat.ts

      App.tsx
      App.css

    package.json
    .env.example
```

## Backend Setup

### 1. Create a Python Virtual Environment

From the project root:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

If you are inside the `backend` folder and the `venv` folder is in the project root, use:

```bash
source ../venv/bin/activate
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, install dependencies manually:

```bash
pip install fastapi uvicorn python-dotenv requests langchain langchain-openai pydantic email-validator
```

Then generate `requirements.txt`:

```bash
pip freeze > requirements.txt
```

### 3. Create Backend Environment File

Create a `.env` file inside the `backend` folder:

```bash
touch .env
```

Add the following:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

CAL_API_KEY=your_cal_api_key
CAL_API_VERSION=2026-02-25
CAL_USERNAME=your_cal_username
CAL_EVENT_TYPE_SLUG=your_event_type_slug
CAL_TIMEZONE=America/Los_Angeles
```

Example:

```env
CAL_USERNAME=nather-hao-7bopsq
CAL_EVENT_TYPE_SLUG=30min
CAL_TIMEZONE=America/Los_Angeles
```

If your Cal.com booking link is:

```text
https://cal.com/nather-hao-7bopsq/30min
```

Then:

```env
CAL_USERNAME=nather-hao-7bopsq
CAL_EVENT_TYPE_SLUG=30min
```

### 4. Create Backend `.env.example`

Create:

```bash
touch .env.example
```

Add:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

CAL_API_KEY=
CAL_API_VERSION=2026-02-25
CAL_USERNAME=
CAL_EVENT_TYPE_SLUG=
CAL_TIMEZONE=America/Los_Angeles
```

Do not commit the real `.env` file.

### 5. Start Backend Server

From the `backend` folder:

```bash
uvicorn app.main:app --reload
```

Or, if using a root-level virtual environment:

```bash
../venv/bin/python -m uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Backend API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Chat Endpoint

```http
POST /chat
```

Request:

```json
{
  "message": "I want to book a meeting.",
  "session_id": "test_session_1"
}
```

Response:

```json
{
  "reply": "I still need the following information to book the meeting: name, email, date, time, reason.",
  "session_id": "test_session_1"
}
```

### Create Booking Directly

```http
POST /cal/bookings
```

Request:

```json
{
  "start": "2026-05-08T22:00:00Z",
  "attendee": {
    "name": "Test User",
    "email": "testuser@example.com",
    "timeZone": "America/Los_Angeles",
    "language": "en"
  },
  "metadata": {
    "reason": "Discuss Cal.com chatbot project"
  }
}
```

Important:

```text
start must be in UTC ISO 8601 format.
```

For example:

```text
2026-05-08 3:00 PM Los Angeles time
```

is:

```text
2026-05-08T22:00:00Z
```

### List Bookings Directly

```http
GET /cal/bookings
```

Optional email filter:

```http
GET /cal/bookings?email=testuser@example.com
```

## Frontend Setup

### 1. Install Frontend Dependencies

From the project root:

```bash
cd frontend
npm install
```

If Axios is missing:

```bash
npm install axios
```

### 2. Create Frontend Environment File

Create a `.env` file inside the `frontend` folder:

```bash
touch .env
```

Add:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Create Frontend `.env.example`

Create:

```bash
touch .env.example
```

Add:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. Start Frontend Server

```bash
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Running the Full App

Open two terminal windows.

### Terminal 1: Start Backend

```bash
cd backend
../venv/bin/python -m uvicorn app.main:app --reload
```

If your virtual environment is already activated:

```bash
cd backend
uvicorn app.main:app --reload
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

## Example Chat Prompts

### Book a Meeting with All Details

```text
Book a meeting for Test User, email testuser@example.com, on 2026-05-08 at 3pm. Reason: discuss chatbot project.
```

### Book a Meeting Step by Step

```text
I want to book a meeting.
```

Then:

```text
My name is Test User and my email is testuser@example.com.
```

Then:

```text
May 8 2026 at 3pm.
```

Then:

```text
Reason is discuss chatbot project.
```

### Update Meeting Details Before Booking

```text
Actually make it 4pm.
```

### List Scheduled Meetings

```text
Show meetings for testuser@example.com.
```

### List Meetings Without Email First

```text
Show my scheduled meetings.
```

Then:

```text
testuser@example.com
```

## Environment Variables

### Backend

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | OpenAI model name, for example `gpt-4o-mini` |
| `CAL_API_KEY` | Cal.com API key |
| `CAL_API_VERSION` | Cal.com API version, currently `2026-02-25` |
| `CAL_USERNAME` | Cal.com username of the host |
| `CAL_EVENT_TYPE_SLUG` | Cal.com event type slug, for example `30min` |
| `CAL_TIMEZONE` | Default timezone, for example `America/Los_Angeles` |

### Frontend

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Backend API base URL |

## Important Notes

### Do Not Commit API Keys

Never commit:

```text
.env
```

Only commit:

```text
.env.example
```

### Do Not Commit Virtual Environment

Do not commit:

```text
venv/
```

Each developer should create their own virtual environment locally.

### Do Not Commit Node Modules

Do not commit:

```text
node_modules/
```

Run this to recreate dependencies:

```bash
npm install
```

## Recommended `.gitignore`

```gitignore
# Python
venv/
__pycache__/
*.pyc
.pytest_cache/

# Environment
.env
.env.local

# Node
node_modules/
dist/

# OS
.DS_Store

# IDE
.vscode/
.idea/
```

## Current Limitations

- Pending conversation state is stored in backend memory.
- If the backend restarts, unfinished booking or listing flows are lost.
- In production, this should be replaced with Redis, PostgreSQL, or another persistent store.
- Cancel booking is not implemented.
- Reschedule booking is not implemented.
- Slot availability checking is not implemented before booking. Cal.com validates the booking request when creating the booking.

## Future Improvements

- Add cancel booking flow.
- Add reschedule booking flow.
- Add slot availability lookup before booking.
- Store session state in Redis.
- Add user authentication.
- Improve frontend UI.
- Add markdown rendering for assistant messages.
- Add deployment configuration.
