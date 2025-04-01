from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATA_PATH: str = "data"

class TruyenYY:
    REQUEST_TIMEOUT: int = 30
    WAITING_TO_RECEIVE_RESPONSE: int = 1
    BASE_URL: str = "https://truyenyy.xyz"
    NOVEL_URL_FORM: str = "https://truyenyy.xyz/truyen/slug"
    CHAPTER_URL_FORM: str = "https://truyenyy.xyz/truyen/slug/chuong-index.html"
    LOGIN_URL = "https://betatruyen.com/account/login/"
    SELECTORS: dict = {
        "title": "body > div.container.novel-detail > div.novel-info > div > h1",
        # "title": "body > main > div > div.info-zone > div.info > h1",
        "other_name": "",
        "cover_image": "body > div.container.novel-detail > div.novel-info > a > img",
        # "cover_image": "body > main > div > div.info-zone > div.novel-cover > img",
        "author": "body > div.container.novel-detail > div.novel-info > div > div.author.mb-3 > a",
        # "author": "body > main > div > div.info-zone > div.info > div.alt-name.mb-1 > a",
        "translator": "",
        # "status": "body > main > div > div.novel-meta > table > tr:nth-child(2) > td:nth-child(2)",
        "status": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(4) > li:nth-child(1) > a",
        "types": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(3)",
        # "types": "body > main > div > div.novel-meta > table > tr:nth-child(1) > td.a-list",
        "description": "#id_novel_summary",
        # "description": "body > main > div > article.well > div.well-content > div.novel-summary-more > div",
        # "last_chapter": "",
        "last_chapter": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(6) > li:nth-child(1)",
        # "last_chapter": "body > main > div > div.novel-meta > table > tr:nth-child(3) > td:nth-child(2)",
        "tags": "",
        "chapter_title": "body > main > div.chapter > div.box > h2",
        "chapter_content": "body > main > div.chapter > div.box > div.chap-content"
    }


