from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from riaes.agents.scraper_agent import RetailScraper

router = APIRouter()
scraper = RetailScraper()

class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_product(request: ScrapeRequest):
    result = scraper.scrape(request.url)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
