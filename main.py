import asyncio
import time

from src.config.settings import TruyenYY, MeTruyenCV
from src.crawlers.async_crawler_TruyenYY import async_crawler_TruyenYY
from src.crawlers.async_crawler_MeTruyenCV import async_crawler_MeTruyenCV


async def main():

    url = "https://metruyencv.com/truyen/bay-nat-lien-vo-dich-xuat-sinh-giay-tien-de"
    async with async_crawler_MeTruyenCV(MeTruyenCV) as async_crawler:
        login_success = await async_crawler.login()
        if login_success:
            # Update novel info
            if await async_crawler.update_info(url):
                print("Novel info updated successfully!")

            # Update chapter list
            if await async_crawler.update_chapter_list(url):
                print("Chapter list updated successfully!")

            # Crawl and download chapters
            results = await async_crawler.crawl_chapters(url)
            print(f"Chapters downloaded: {results[0]}, Failed: {results[1]}")
        else:
            print("Login failed!!!!!!!!!!")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
