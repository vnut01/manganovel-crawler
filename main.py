import asyncio
import time

from config.settings import TruyenYY
from crawlers.async_crawler_TruyenYY import async_crawler_TruyenYY


async def main():
    novel_url = "https://truyenyy.xyz/truyen/yeu-long-co-de"
    novel_url = "https://truyenyy.xyz/truyen/luc-dia-kien-tien"
    novel_url = "https://truyenyy.xyz/truyen/nhan-ngu-tieu-nam"

    async with async_crawler_TruyenYY(TruyenYY) as async_crawler:
        login_success = await async_crawler.login()
        if login_success:
            await async_crawler.update_info(novel_url)
            await asyncio.sleep(1)
            await async_crawler.crawl_chapters(novel_url)
        else:
            print("Login failed!!!!!!!!!!")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
