import os
import re
import asyncio
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from src.storage.local_storage import LocalStorage
from .async_base_crawler import AsyncBaseCrawler
import json


class async_crawler_MeTruyenCV(AsyncBaseCrawler):
    async def update_info(self, url: str) -> bool:
        """Fetch and update novel metadata."""
        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)

        result = await self.fetch(url)
        if result["status"] != 200:
            return False

        soup = BeautifulSoup(result["content"], "html.parser")

        # Save the HTML content of the page for debugging purposes
        with open("soup.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        # Extract the <script> tag containing `window.bookData`
        script_tag = soup.find("script", text=lambda t: t and "window.bookData" in t)
        if not script_tag:
            self.logger.error("Failed to find the script tag containing book data.")
            return False

        # Extract the content of the script tag
        match = re.search(r'"id":(\d+)', script_tag.string)
        book_id = int(match.group(1)) if match else None

        info = {
            "url": url,
            "id": book_id,
            "title": "",
            "other_name": "",
            "cover_image": "",
            "author": "",
            "translator": "",
            "status": "Còn Tiếp",
            "types": [],
            "description": "",
            "last_chapter_url_index": 0,
            "tags": [],
        }

        # Extract metadata using selectors
        if self.DEFINE.SELECTORS["title"]:
            info["title"] = soup.select_one(self.DEFINE.SELECTORS["title"]).text.strip()
        if self.DEFINE.SELECTORS["other_name"]:
            info["other_name"] = soup.select_one(
                self.DEFINE.SELECTORS["other_name"]
            ).text.strip()
        if self.DEFINE.SELECTORS["cover_image"]:
            info["cover_image"] = soup.select_one(self.DEFINE.SELECTORS["cover_image"])[
                "src"
            ]
        if self.DEFINE.SELECTORS["author"]:
            info["author"] = soup.select_one(
                self.DEFINE.SELECTORS["author"]
            ).text.strip()
        if self.DEFINE.SELECTORS["translator"]:
            info["translator"] = soup.select_one(
                self.DEFINE.SELECTORS["translator"]
            ).text.strip()
        if self.DEFINE.SELECTORS["status"]:
            if soup.select_one(self.DEFINE.SELECTORS["status"]) is not None:
                list = soup.select_one(self.DEFINE.SELECTORS["status"]).find_all("a")
                if len(list) > 0:
                    info["status"] = list[0].text.strip()
                    info["types"] = [list[i].text.strip() for i in range(1, len(list))]
        if self.DEFINE.SELECTORS["description"]:
            info["description"] = soup.select_one(
                self.DEFINE.SELECTORS["description"]
            ).decode_contents()
        if self.DEFINE.SELECTORS["tags"] != "":
            info["tags"] = soup.select_one(self.DEFINE.SELECTORS["tags"]).text.strip()

        # Save novel info
        data = local_storage.load_novel_info()
        if data is None:
            data = {"info": info, "chapters": []}
        else:
            data["info"].update(info)

        local_storage.save_novel_info(data)
        return True

    async def update_chapter_list(self, url: str) -> bool:
        """Fetch and update the list of chapters."""
        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)
        data = local_storage.load_novel_info()

        if not data or "info" not in data or "id" not in data["info"]:
            self.logger.error("Novel info is missing. Please run update_info first.")
            return False

        book_id = data["info"]["id"]

        # Fetch the list of chapters
        chapters_list = await self.fetch_list_chapters(book_id)
        if not chapters_list:
            self.logger.error("Failed to fetch chapters list.")
            return False

        # Update chapters list
        for i in range(len(data["chapters"]), len(chapters_list)):
            data["chapters"].append(chapters_list[i])
        data["info"]["last_chapter_url_index"] = chapters_list[-1]["url_index"]

        print("Update chapters list")
        local_storage.save_novel_info(data)
        return True

    async def fetch_list_chapters(self, book_id) -> list:
        """Fetch the list of chapters for a given book ID."""
        if not self.session:
            await self.create_session()
        url = f"https://backend.metruyencv.com/api/chapters?filter[book_id]={book_id}&filter[type]=published"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    data = [
                        {
                            "url_index": int(chapter["index"]),
                            "name": chapter["name"],
                            "status": "to_download",
                            "re_download": 0,
                        }
                        for chapter in data["data"]
                    ]
                    chapters_list = [{} for i in range(0, data[-1]["url_index"])]
                    for chapter in data:
                        chapters_list[chapter["url_index"] - 1] = chapter

                    return chapters_list
                else:
                    self.logger.info(
                        f"Failed to fetch chapters with status {response.status}."
                    )
                    return []
        except :
            self.logger.error("Failed to fetch chapters")
            return []

    async def crawl_chapters(self, url: str, is_retry=False) -> List[int]:
        """Crawl and download chapters."""
        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)
        data = local_storage.load_novel_info()
        if data is None:
            return [-1, -1]

        urls = []
        for chapter in data["chapters"]:
            if chapter and chapter["status"] == "to_download":
                urls.append(
                    f"{self.DEFINE.BASE_URL}/truyen/{slug}/chuong-{chapter['url_index']}.html"
                )

        self.logger.info(f"Number of chapters to download: {len(urls)}")
        print("Crawling . . . ")
        print(f"Number of chapters to download: {len(urls)}")

        fetch_successful = 0
        fetch_failed = 0
        results = await self.fetch_multiple(urls)
        for result in results:
            if result["status"] == 200:
                soup = BeautifulSoup(result["content"], "html.parser")
                url_pattern = r"/truyen/(?P<slug>[^/]+)/chuong-(?P<index>\d+)\.html"
                match = re.search(url_pattern, result["url"])
                url_index = int(match.group("index"))

                content = soup.select_one(self.DEFINE.SELECTORS["chapter_content"])
                content = content.decode_contents() if content else ""

                if content != "":
                    data["chapters"][url_index - 1]["status"] = "downloaded"
                    local_storage.save_chapter(content, url_index)
                    fetch_successful += 1
                else:
                    fetch_failed += 1
                    data["chapters"][url_index - 1]["re_download"] += 1

        local_storage.save_novel_info(data)
        self.logger.info(f"Number of chapters downloaded successfully: {fetch_successful}")
        self.logger.info(f"Number of chapters failed to download: {fetch_failed}")
        print(f"Number of chapters downloaded successfully: {fetch_successful}")
        print(f"Number of chapters failed to download: {fetch_failed}")

        return [fetch_successful, fetch_failed]