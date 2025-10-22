import httpx
import asyncio
from wphunter.utils.logger import Logger

class HTTPClient:
    def __init__(self, timeout=10, follow_redirects=True, max_retries=1, logger: Logger = None):
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.max_retries = max_retries
        self.logger = logger
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout),
                                        follow_redirects=self.follow_redirects)

    async def get(self, url: str, headers=None, params=None):
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response
            except httpx.TimeoutException:
                pass
            except httpx.NetworkError as e:
                pass
            except httpx.HTTPStatusError as e:
                return e.response
            except Exception as e:
                pass
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        return None

    async def post(self, url: str, headers=None, data=None, json=None):
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(url, headers=headers, data=data, json=json)
                response.raise_for_status()
                return response
            except httpx.TimeoutException:
                pass
            except httpx.NetworkError as e:
                pass
            except httpx.HTTPStatusError as e:
                return e.response
            except Exception as e:
                pass
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        return None

    async def close(self):
        await self.client.aclose()
