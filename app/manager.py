import asyncio
import platform
from contextlib import asynccontextmanager
from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
)
from toolbox.utils import get_env


MAX_TABS = get_env("MAX_TABS", 10, verbose=1)
HEADLESS = get_env("HEADLESS", False, verbose=1)
IDLE_TIMEOUT = get_env("IDLE_TIMEOUT", 900, verbose=1)  # seconds (15 min)


class BrowserManager:
    def __init__(self) -> None:
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright: Playwright | None = None
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(MAX_TABS)
        self._idle_task: asyncio.Task | None = None

    async def _ensure_browser(self) -> BrowserContext:
        async with self._lock:
            if self._browser is None:
                self._playwright = await async_playwright().start()
                env = (
                    {"DISPLAY": ":99"}
                    if not HEADLESS and platform.system() != "Windows"
                    else None
                )
                self._browser = await self._playwright.firefox.launch(
                    headless=HEADLESS, env=env
                )
                self._context = await self._browser.new_context()
                if not HEADLESS:
                    background = await self._context.new_page()
                    await background.goto("about:blank")
        return self._context

    def _reset_idle_timer(self) -> None:
        if self._idle_task and not self._idle_task.done():
            self._idle_task.cancel()
        self._idle_task = asyncio.create_task(self._idle_shutdown())

    async def _idle_shutdown(self) -> None:
        await asyncio.sleep(IDLE_TIMEOUT)
        await self._shutdown()

    async def _shutdown(self) -> None:
        async with self._lock:
            if self._context is not None:
                await self._context.close()
                self._context = None
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None

    async def close(self) -> None:
        """Cancel idle timer and shut down the browser cleanly."""
        if self._idle_task and not self._idle_task.done():
            self._idle_task.cancel()
        await self._shutdown()

    @asynccontextmanager
    async def get_page(self):
        await self._semaphore.acquire()
        try:
            context = await self._ensure_browser()
            page: Page = await context.new_page()
            try:
                yield page
            finally:
                await page.close()
                self._reset_idle_timer()
        finally:
            self._semaphore.release()


browser_manager = BrowserManager()
