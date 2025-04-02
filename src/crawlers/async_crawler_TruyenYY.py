import os
import re, asyncio
from typing import Any, Dict

from bs4 import BeautifulSoup

from src.storage.local_storage import LocalStorage

from .async_base_crawler import AsyncBaseCrawler


class async_crawler_TruyenYY(AsyncBaseCrawler):
    async def update_info(self, url: str) -> bool:
        result = await self.fetch(url)
        if result["status"] != 200:
            return False
        soup = BeautifulSoup(result["content"], "html.parser")
        # Save the HTML content of the page for debugging purposes
        # with open("soup.html", "w", encoding="utf-8") as file:
        #     file.write(soup.prettify())
        info = {
            "url": url,
            "title": "",
            "other_name": "",
            "cover_image": "",
            "author": "",
            "translator": "",
            "status": "Còn Tiếp",
            "types": [],
            "description": "",
            "last_chapter": 0,
            "tags": [],
        }

        if self.DEFINE.SELECTORS["title"] != "":
            info["title"] = soup.select_one(self.DEFINE.SELECTORS["title"]).text.strip()
        if self.DEFINE.SELECTORS["other_name"] != "":
            info["other_name"] = soup.select_one(
                self.DEFINE.SELECTORS["other_name"]
            ).text.strip()
        if self.DEFINE.SELECTORS["cover_image"] != "":
            info["cover_image"] = soup.select_one(self.DEFINE.SELECTORS["cover_image"])[
                "data-src"
            ]
        if self.DEFINE.SELECTORS["author"] != "":
            info["author"] = soup.select_one(
                self.DEFINE.SELECTORS["author"]
            ).text.strip()
        if self.DEFINE.SELECTORS["translator"] != "":
            info["translator"] = soup.select_one(
                self.DEFINE.SELECTORS["translator"]
            ).text.strip()
        if self.DEFINE.SELECTORS["status"] != "":
            if soup.select_one(self.DEFINE.SELECTORS["status"]) is not None:
                if (
                    "Hoàn Thành"
                    in soup.select_one(self.DEFINE.SELECTORS["status"]).text.strip()
                ):
                    info["status"] = "Hoàn Thành"
        if self.DEFINE.SELECTORS["types"] != "":
            info["types"] = [
                a.text.strip()
                for a in soup.select(self.DEFINE.SELECTORS["types"] + " a")
            ]
        if self.DEFINE.SELECTORS["description"] != "":
            info["description"] = (
                soup.select_one(self.DEFINE.SELECTORS["description"])
                .contents[0]
                .strip()
            )
        if self.DEFINE.SELECTORS["last_chapter"] != "":
            info["last_chapter"] = int(
                re.search(
                    r"\d+",
                    soup.select_one(self.DEFINE.SELECTORS["last_chapter"]).text.strip(),
                ).group()
            )
        if self.DEFINE.SELECTORS["tags"] != "":
            info["tags"] = soup.select_one(self.DEFINE.SELECTORS["tags"]).text.strip()

        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)
        data = local_storage.load_novel_info()
        if data is None:
            data = {}
            data["info"] = info
            data["chapters"] = {}
        else:
            if data["info"]["last_chapter"] < info["last_chapter"]:
                print(f"Dont has new chapter - > {url}")
                return False
            data["info"]["title"] = info["title"]
            data["info"]["other_name"] = info["other_name"]
            data["info"]["cover_image"] = info["cover_image"]
            data["info"]["author"] = info["author"]
            data["info"]["translator"] = info["translator"]
            data["info"]["status"] = info["status"]
            data["info"]["types"] = info["types"]
            data["info"]["description"] = info["description"]
            data["info"]["last_chapter"] = info["last_chapter"]
            data["info"]["tags"] = info["tags"]

        for i in range(1, data["info"]["last_chapter"] + 1):
            if str(i) not in data["chapters"]:
                data["chapters"][i] = {
                    "index": i,
                    "title": "",
                    "status": "to_download",
                    "re_download": 0,
                }

        local_storage.save_novel_info(data)
        return True

    async def crawl_chapters(self, url: str, is_retry=False):
        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)
        data = local_storage.load_novel_info()
        if data is None:
            return [-1, -1]
        
        urls = [
            f"{self.DEFINE.BASE_URL}/truyen/{slug}/chuong-{index}.html"
            for index, chapter in data["chapters"].items()
            if chapter["status"] == "to_download"
        ]
        self.logger.info(f"Number chapter need download: {len(urls)}")
        print("Crawling . . . ")
        print(f"Number chapter need download: {len(urls)}")
        fetch_successful = 0
        fetch_failed = 0
        results = await self.fetch_multiple(urls)
        for result in results:
            if result["status"] == 200:
                soup = BeautifulSoup(result["content"], "html.parser")
                url_pattern = r"/truyen/(?P<slug>[^/]+)/chuong-(?P<index>\d+)\.html"
                match = re.search(url_pattern, result["url"])
                slug = match.group("slug")
                index = str(match.group("index"))
                
                title = soup.select_one(self.DEFINE.SELECTORS["chapter_title"])
                title = title.text.strip() if title else ""

                content = soup.select_one(self.DEFINE.SELECTORS["chapter_content"])
                content = content.text.strip() if content else ""

                if content != "":
                    data["chapters"][index]["title"] = title
                    data["chapters"][index]["status"] = "downloaded"
                    local_storage.save_chapter(content, index)
                    fetch_successful += 1
                else:
                    fetch_failed += 1
                    data["chapters"][index]["re_download"] = (
                        data["chapters"][index]["re_download"] + 1
                    )

        local_storage.save_novel_info(data)
        self.logger.info(f"Number chapter downloaded successful: {fetch_successful}")
        self.logger.info(f"Number chapter download failed: {fetch_failed}")
        print("Finish fetch data for -> {url}")
        print(f"Number chapter download successful: {fetch_successful}")
        print(f"Number chapter download failed: {fetch_failed}")

        return [fetch_successful, fetch_failed]
