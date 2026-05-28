from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from riaes.api import agents_router, portal_router, scraper_router
import uvicorn
import os

app = FastAPI(title="RIAES: Autonomous Retail Intelligence")

os.makedirs("riaes/portal/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="riaes/portal/static"), name="static")
templates = Jinja2Templates(directory="riaes/portal/templates")

@app.get("/")
async def root(request: Request):
    return {"message": "RIAES Retail Intelligence API is running"}

app.include_router(agents_router.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(scraper_router.router, prefix="/api/v1/scraper", tags=["Scraper"])
app.include_router(portal_router.router, prefix="/portal", tags=["Portal"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
