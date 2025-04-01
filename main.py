from crawlers.async_crawler_TruyenYY import async_crawler_TruyenYY
import asyncio
import time

async def main():
    novel_url = "https://truyenyy.xyz/truyen/yeu-long-co-de"
    username = "playgame.vo@gmail.com"
    password = "vuichoi1"
    login_url = "https://betatruyen.com/account/login"

    async with async_crawler_TruyenYY('https://truyenyy.xyz') as async_crawler:
        login_success = await async_crawler.login(login_url, username, password)
        if login_success:
            await async_crawler.update_novel_info(novel_url)
            await asyncio.sleep(1)
            await async_crawler.crawl_chapters(novel_url)
        else:
            print("Login failed!!!!!!!!!!")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")