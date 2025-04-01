import aiohttp
import asyncio
from typing import Optional, Dict, Any
from config.settings import TruyenYY, Config

class AsyncBaseCrawler:
    def __init__(self, domain: str):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.is_logged_in = False  # Track login status
        if "truyenyy" in domain:
            self.request_timeout = TruyenYY.REQUEST_TIMEOUT
            self.waiting_to_receive_response = TruyenYY.WAITING_TO_RECEIVE_RESPONSE
            self.base_url = TruyenYY.BASE_URL
            self.selectors = TruyenYY.SELECTORS
            self.login_url = TruyenYY.LOGIN_URL

    async def __aenter__(self):
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close_session()

    async def create_session(self):
        """Init aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                # timeout=aiohttp.ClientTimeout(total=self.request_timeout)
            )
    async def close_session(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def login(self, login_url: str, username: str, password: str) -> bool:
        """Login with username and password"""
        if not self.session:
            await self.create_session()
        
        payload = {
            'username': username,
            'password': password,
            'next': '/oauth2/authorize'
        }

        try:
            async with self.session.post(login_url, data=payload) as response:
                if response.status == 200:
                    self.is_logged_in = True
                    print("Login successfull")
                    return True
                else:
                    print(f'Login failed with status {response.status}')
        except aiohttp.ClientError as e:
            print(f'Login request failed: {str(e)}')
            return False

    async def fetch(self, url: str, **kwargs) -> Dict[str, Any]:
        if not self.session:
            await self.create_session()
        try:
            async with self.session.get(url, **kwargs) as response:
                await asyncio.sleep(self.waiting_to_receive_response)
                content = await response.text()
                return {
                    'url': url,
                    'content': content,
                    'status': response.status,
                    'headers': dict(response.headers)
                }
        except aiohttp.ClientError as e:
            print(f"Request to {url} failed: {str(e)}")
            return {
                'url': url,
                'content': None,
                'status': 500,
                'error': str(e)
            }
    
    async def fetch_multiple(self, urls: list) -> list:
        tasks = [self.fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
