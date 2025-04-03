import asyncio
import time

from src.config.settings import TruyenYY, MeTruyenCV
from src.crawlers.async_crawler_TruyenYY import async_crawler_TruyenYY
from src.crawlers.async_crawler_MeTruyenCV import async_crawler_MeTruyenCV


async def main():

    novel_url = "https://metruyencv.com/truyen/cac-nguoi-tu-tien-ta-lam-ruong"
    async with async_crawler_MeTruyenCV(MeTruyenCV) as async_crawler:
        login_success = await async_crawler.login()
        if login_success:
            await async_crawler.update_info(novel_url)
            await asyncio.sleep(1)
            await async_crawler.crawl_chapters(novel_url)
        else:
            print("Login failed!!!!!!!!!!")

    # novel_url = "https://truyenyy.xyz/truyen/thon-thien-chua-te"
    # async with async_crawler_TruyenYY(TruyenYY) as async_crawler:
    #     # login_success = await async_crawler.login()
    #     if True:
    #         await async_crawler.update_info(novel_url)
    #         await asyncio.sleep(1)
    #         await async_crawler.crawl_chapters(novel_url)
    #     else:
    #         print("Login failed!!!!!!!!!!")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
