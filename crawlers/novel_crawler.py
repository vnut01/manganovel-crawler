from bs4 import BeautifulSoup
from crawlers.base_crawler import BaseCrawler
from storage.local_storage import LocalStorage

class NovelCrawler(BaseCrawler):
    def get_novel_info(self, url):
        print(f"get_novel_info -> {url}")
        html = self.fetch(url)
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        info = {
            "url": url,
            "title": "",
            "other_name": "",
            "cover_image": "",
            "author": "",
            "translator": "",
            "status": "",
            "types": [],
            "description": "",
            "last_chapter_index": "",
            "last_chapter_index_downloaded": 0,
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
            info["status"] = soup.select_one(self.selectors["status"]).text.strip()
        if self.selectors["types"] != "":
            info["types"] = [a.text.strip() for a in soup.select(self.selectors["types"] + " a")]
        if self.selectors["description"] != "":
            info["description"] = soup.select_one(self.selectors["description"]).contents[0].strip()
        if self.selectors["last_chapter_index"] != "":
            info["last_chapter_index"] = int(soup.select_one(self.selectors["last_chapter_index"]).text.strip())
        if self.selectors["tags"] != "":
            info["tags"] = soup.select_one(self.selectors["tags"]).text.strip()
        
        return info

    def fetch_chapter_content(self, url, index):
        url = f"{url}/chuong-{index}.html"
        print(f"fetch_chapter_content -> {url}")
        html = self.fetch(url)
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        chapter_title = ""
        chapter_content = ""
        if self.selectors['chapter_title'] != "":
            chapter_title = soup.select_one(self.selectors['chapter_title']).text.strip()
        if self.selectors['chapter_content'] != "":
            chapter_content = soup.select_one(self.selectors['chapter_content']).text.strip()

        return {"chapter_title": chapter_title, "chapter_content": chapter_content}


    def crawl_novel(self, url):
        local_storage = LocalStorage('data')
        slug = url.split('/')[-1]
        novel = local_storage.load_json(slug)
        new_info = self.get_novel_info(url)
        if novel is None:
            novel = {}
            novel['info'] = new_info
            novel['chapters'] = {}
        else:
            novel['info']["title"] = new_info["title"]
            novel['info']["other_name"] = new_info["other_name"]
            novel['info']["cover_image"] = new_info["cover_image"]
            novel['info']["author"] = new_info["author"]
            novel['info']["translator"] = new_info["translator"]
            novel['info']["status"] = new_info["status"]
            novel['info']["types"] = new_info["types"]
            novel['info']["description"] = new_info["description"]
            novel['info']["last_chapter_index"] = new_info["last_chapter_index"]
            novel['info']["tags"] = new_info["tags"]
        
        chapters_need_download_index = list(range(novel['info']['last_chapter_index_downloaded'] + 1, novel['info']['last_chapter_index'] + 1))
        chap = self.fetch_chapter_content(url, chapters_need_download_index[0])
        if chap is not None:
            novel['chapters'][chapters_need_download_index[0]] = chap
            novel['info']["last_chapter_index_downloaded"] = chapters_need_download_index[0]

        local_storage.save_json(novel, slug)
    
    