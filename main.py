from fastapi import FastAPI, HTTPException, Query

from datetime import datetime, timedelta

app = FastAPI()


class RateLimiter:
    def __init__(self, request_limit=5, window_seconds=60):
        self.request_log = {}
        self.request_limit = request_limit
        self.window_seconds = window_seconds

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        timestamps = self.request_log.get(user_id, [])

        timestamps = [t for t in timestamps if now - t < timedelta(seconds=self.window_seconds)]

        if len(timestamps) >= self.request_limit:
            return False

        timestamps.append(now)
        self.request_log[user_id] = timestamps
        return True

    def current_requests(self, user_id: str) -> int:
        now = datetime.now()
        timestamps = self.request_log.get(user_id, [])

        timestamps = [t for t in timestamps if now - t < timedelta(seconds=self.window_seconds)]

        return len(timestamps)

    def reset(self) -> bool:
        self.request_log.clear()


limiter = RateLimiter()


@app.post("/ping")
def retrieve_user_activity(user_id: str = Query(...)):
    if not limiter.is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    return {"message": "pong!"}


@app.get("/status")
def retrieve_user_current_activity(user_id: str = Query(...)):
    return limiter.current_requests(user_id)


@app.get("/reset")
def reset_users_activity():
    limiter.reset_requests()
    return {"message": "All user activity logs have been cleared."}
