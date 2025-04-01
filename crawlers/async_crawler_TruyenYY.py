from bs4 import BeautifulSoup
from typing import Dict, Any
from .async_base_crawler import AsyncBaseCrawler
from storage.local_storage import LocalStorage
from config.settings import Config
import re, os


class async_crawler_TruyenYY(AsyncBaseCrawler):
    async def update_novel_info(self, url: str):
        result = await self.fetch(url)
        if result['status'] != 200:
            return
        soup = BeautifulSoup(result['content'], 'html.parser')
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
            "last_chapter_downloaded": 0,
            "error_chapters": [],
            "tags": []
        }

        if self.selectors["title"] != "":
            info["title"] = soup.select_one(self.selectors["title"]).text.strip()
        if self.selectors["other_name"] != "":
            info["other_name"] = soup.select_one(self.selectors["other_name"]).text.strip()
        if self.selectors["cover_image"] != "":
            info["cover_image"] = soup.select_one(self.selectors["cover_image"])["data-src"]
        if self.selectors["author"] != "":
            info["author"] = soup.select_one(self.selectors["author"]).text.strip()
        if self.selectors["translator"] != "":
            info["translator"] = soup.select_one(self.selectors["translator"]).text.strip()
        if self.selectors["status"] != "":
            if soup.select_one(self.selectors["status"]) is not None:
                    if "Hoàn Thành" in soup.select_one(self.selectors["status"]).text.strip():
                        info["status"] = "Hoàn Thành"
        if self.selectors["types"] != "":
            info["types"] = [a.text.strip() for a in soup.select(self.selectors["types"] + " a")]
        if self.selectors["description"] != "":
            info["description"] = soup.select_one(self.selectors["description"]).contents[0].strip()
        if self.selectors["last_chapter"] != "":
            info["last_chapter"] = int(re.search(r'\d+', soup.select_one(self.selectors["last_chapter"]).text.strip()).group())
        if self.selectors["tags"] != "":
            info["tags"] = soup.select_one(self.selectors["tags"]).text.strip()

        slug = url.split('/')[-1]
        novel_path = os.path.join(Config.DATA_PATH, slug)
        local_storage = LocalStorage(novel_path)
        data = local_storage.load_novel_info()
        if data is None:
            data = {}
            data['info'] = info
            data['chapters'] = {}
        else:
            data['info']["title"] = info["title"]
            data['info']["other_name"] = info["other_name"]
            data['info']["cover_image"] = info["cover_image"]
            data['info']["author"] = info["author"]
            data['info']["translator"] = info["translator"]
            data['info']["status"] = info["status"]
            data['info']["types"] = info["types"]
            data['info']["description"] = info["description"]
            data['info']["last_chapter"] = info["last_chapter"]
            data['info']["tags"] = info["tags"]
        
        for i in range(1, data['info']["last_chapter"]+1):
            if str(i) not in data['chapters']:
                data['chapters'][i] = {
                    'index': i,
                    'title': '',
                    'status': 'to_download',
                    're_download': 0
                }

        local_storage.save_novel_info(data)
    
    async def crawl_chapters(self, url: str, is_retry = False):
        slug = url.split('/')[-1]
        novel_path = os.path.join(Config.DATA_PATH, slug)
        local_storage = LocalStorage(novel_path)
        data = local_storage.load_novel_info()
        if data is None:
            return
        if is_retry:
            urls = [f"{self.base_url}/truyen/{slug}/chuong-{index}.html" for index, chapter in data['chapters'].items() if chapter['status'] == 'to_download' and chapter['re_download'] < 3]
            print(f"Number chapter need re-download: {len(urls)}")
        else:
            urls = [f"{self.base_url}/truyen/{slug}/chuong-{index}.html" for index, chapter in data['chapters'].items() if chapter['status'] == 'to_download']
            print(f"Number chapter need download: {len(urls)}")

        while urls:
            batch = urls[:200]
            urls = urls[200:]
            results = await self.fetch_multiple(batch)
            for result in results:
                if result['status'] == 200:
                    soup = BeautifulSoup(result['content'], 'html.parser')
                    url_pattern = r'/truyen/(?P<slug>[^/]+)/chuong-(?P<index>\d+)\.html'
                    match = re.search(url_pattern, result['url'])
                    slug = match.group('slug')
                    index = str(match.group('index'))
                    title = ""
                    content = ""
                    try:
                        title = soup.select_one(self.selectors['chapter_title'])
                        title = title.text.strip() if title else ""
                        content = soup.select_one(self.selectors['chapter_content']).text.strip()
                    except:
                        print(f"fetch chapter error -> {result['url']}")

                    if content !=  "":
                        data['chapters'][index]['title'] = title
                        data['chapters'][index]['status'] = 'downloaded'
                        local_storage.save_chapter(content, index)
                    else:
                        # data['chapters'][index]['status'] = 'error'
                        data['chapters'][index]['re_download'] = data['chapters'][index]['re_download'] + 1


        local_storage.save_novel_info(data)