import asyncio
from typing import Any, Dict, Optional
from fake_useragent import UserAgent
from src.config.logger import logger
import aiohttp
import json


class AsyncBaseCrawler:
    def __init__(self, config):
        self.logger = logger(self.__class__.__name__)
        self.ua = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": self.ua.random,
            "Content-Type": "application/json",
        }
        self.is_logged_in = False
        self.token: Optional[str] = None
        self.DEFINE = config
        self.logger.info("AsyncBaseCrawler initialized.")

    async def __aenter__(self):
        await self.create_session()
        self.logger.info("Session created.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close_session()
        self.logger.info("Session closed.")

    async def create_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            self.logger.info("HTTP session created with headers: %s", self.headers)

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("HTTP session closed.")

    async def login(self) -> bool:
        """Login to the website and retrieve the token."""
        if not self.session:
            await self.create_session()

        payload = {
            "email": self.DEFINE.USERNAME,
            "password": self.DEFINE.PASSWORD,
            "remember": 1,
            "device_name": self.headers["User-Agent"],
        }

        try:
            async with self.session.post(
                self.DEFINE.LOGIN_URL, json=payload
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    self.token = response_json["data"]["token"]
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    self.is_logged_in = True
                    self.logger.info("Login successful. Token added to headers.")
                    return True
                else:
                    response_text = await response.text()
                    self.logger.info(
                        f"Login failed with status {response.status}. Response: {response_text}"
                    )
                    return False
        except aiohttp.ClientError as e:
            self.logger.error(f"Login request failed: {str(e)}")
            return False

    async def fetch(self, url: str, **kwargs) -> Dict[str, Any]:
        if not self.session:
            await self.create_session()
        try:
            async with self.session.get(url, **kwargs) as response:
                await asyncio.sleep(self.DEFINE.WAITING_TO_RECEIVE_RESPONSE)
                content = await response.text()
                return {
                    "url": url,
                    "content": content,
                    "status": response.status,
                    "headers": dict(response.headers),
                }
        except aiohttp.ClientError as e:
            self.logger.info(f"Failed -> {url}")
            return {"url": url, "content": None, "status": 500, "error": str(e)}

    async def fetch_multiple(self, urls: list) -> list:
        semaphore = asyncio.Semaphore(self.DEFINE.NUMBER_URL_A_REQUEST_BATCH)

        async def limited_fetch(url):
            async with semaphore:
                return await self.fetch(url)

        tasks = [limited_fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
