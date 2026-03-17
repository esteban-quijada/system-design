from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import secrets

app = FastAPI()

# In-memory storage: short_code -> original URL
url_store: dict[str, str] = {}


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest):
    short_code = secrets.token_urlsafe(6)
    url_store[short_code] = str(request.url)
    return ShortenResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}",
    )


@app.get("/{short_code}")
def redirect_url(short_code: str):
    original_url = url_store.get(short_code)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=original_url)
