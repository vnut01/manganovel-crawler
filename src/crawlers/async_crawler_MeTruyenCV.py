import os
import re, asyncio
from typing import Any, Dict

from bs4 import BeautifulSoup

from src.storage.local_storage import LocalStorage

from .async_base_crawler import AsyncBaseCrawler
import json


class async_crawler_MeTruyenCV(AsyncBaseCrawler):
    async def update_info(self, url: str) -> bool:
        slug = url.split("/")[-1]
        novel_folder = os.path.join(self.DEFINE.DATA_PATH, slug)
        local_storage = LocalStorage(novel_folder)
        data = local_storage.load_novel_info()
        if data:
            book_id = data["info"]["id"]
            # Update Chapters List
            chapters_list = await self.fetch_list_chapters(book_id)
            for i in range(len(data["chapters"]), len(chapters_list)):
                data["chapters"].append(chapters_list[i])
            data["info"]["last_chapter_url_index"] = chapters_list[-1]["url_index"]
            print("Update chapters list")
            local_storage.save_novel_info(data)
            return True

        result = await self.fetch(url)
        if result["status"] != 200:
            return False
        soup = BeautifulSoup(result["content"], "html.parser")
        # Save the HTML content of the page for debugging purposes
        with open("soup.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        # Extract the <script> tag containing `window.bookData`
        script_tag = soup.find("script", text=lambda t: t and "window.bookData" in t)
        if script_tag:
            # Extract the content of the script tag
            match = re.search(r'"id":(\d+)', script_tag.string)
            book_id = int(match.group(1)) if match else None
            chapters_list = await self.fetch_list_chapters(book_id)

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

        if data is None:
            data = {}
            data["info"] = info
            data["chapters"] = chapters_list
        else:
            data["info"]["title"] = info["title"]
            data["info"]["other_name"] = info["other_name"]
            data["info"]["cover_image"] = info["cover_image"]
            data["info"]["author"] = info["author"]
            data["info"]["translator"] = info["translator"]
            data["info"]["status"] = info["status"]
            data["info"]["types"] = info["types"]
            data["info"]["description"] = info["description"]
            data["info"]["last_chapter_url_index"] = info["last_chapter_url_index"]
            data["info"]["tags"] = info["tags"]
            # append new chapters to the existing list
            for i in range(len(data["chapters"]), len(chapters_list)):
                data["chapters"].append(chapters_list[i])

        local_storage.save_novel_info(data)
        return True

    async def crawl_chapters(self, url: str, is_retry=False):
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

        # urls = [
        #     f"{self.DEFINE.BASE_URL}/truyen/{slug}/chuong-{index}.html"
        #     for index, chapter in data["chapters"]
        #     if chapter and chapter["status"] == "to_download"
        # ]
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
                # slug = match.group("slug")
                url_index = int(match.group("index"))

                # title = soup.select_one(self.DEFINE.SELECTORS["chapter_title"])
                # title = title.text.strip() if title else ""

                content = soup.select_one(self.DEFINE.SELECTORS["chapter_content"])
                content = content.decode_contents() if content else ""

                if content != "":
                    # data["chapters"][index]["title"] = title
                    data["chapters"][url_index - 1]["status"] = "downloaded"
                    local_storage.save_chapter(content, url_index)
                    fetch_successful += 1
                else:
                    fetch_failed += 1
                    data["chapters"][url_index - 1]["re_download"] = (
                        data["chapters"][url_index - 1]["re_download"] + 1
                    )

        local_storage.save_novel_info(data)
        self.logger.info(f"Number chapter downloaded successful: {fetch_successful}")
        self.logger.info(f"Number chapter download failed: {fetch_failed}")
        print("Finish fetch data for -> {url}")
        print(f"Number chapter download successful: {fetch_successful}")
        print(f"Number chapter download failed: {fetch_failed}")

        return [fetch_successful, fetch_failed]
