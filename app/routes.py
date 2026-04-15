from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from bs4 import BeautifulSoup
from app.manager import browser_manager
from app.schemas import FetchRequest, FetchResponse
from toolbox.utils import get_env


API_KEY = get_env("API_KEY", "", verbose=1)

api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="ApiKeyAuth")
router = APIRouter()


async def verify_api_key(api_key: str = Security(api_key_header)) -> None:
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
        )


@router.post("/fetch", dependencies=[Security(verify_api_key)])
async def fetch(request: FetchRequest) -> FetchResponse:
    async with browser_manager.get_page() as page:
        try:
            response = await page.goto(request.url, wait_until="domcontentloaded")
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

        html = await page.content()
        title = await page.title()
        soup = BeautifulSoup(html, "lxml")

        return FetchResponse(
            url=page.url,
            status_code=response.status if response else 0,
            title=title,
            html=str(soup),
        )
