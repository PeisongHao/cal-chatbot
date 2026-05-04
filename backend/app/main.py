from fastapi import FastAPI

from app.modules.chat.router import router as chat_router
# from app.modules.cal.router import router as cal_router

app = FastAPI(
    title="Cal.com AI Chatbot",
    description="AI chatbot backend for booking, listing, and canceling Cal.com events.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


app.include_router(chat_router)
# for test cal.com use
# app.include_router(cal_router)