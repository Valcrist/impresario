import httpx
from bs4 import BeautifulSoup


SERVICE_URL = "http://localhost:8077"


async def fetch(url: str) -> BeautifulSoup:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SERVICE_URL}/fetch", json={"url": url})
        r.raise_for_status()
        return BeautifulSoup(r.json()["html"], "lxml")
