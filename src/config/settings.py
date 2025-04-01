from dotenv import load_dotenv

load_dotenv()


class TruyenYY:
    DATA_PATH: str = "data"
    REQUEST_TIMEOUT: int = 30
    WAITING_TO_RECEIVE_RESPONSE: int = 1
    NUMBER_URL_A_REQUEST_BATCH: int = 200
    BASE_URL: str = "https://truyenyy.xyz"
    NOVEL_URL_FORM: str = "https://truyenyy.xyz/truyen/slug"
    CHAPTER_URL_FORM: str = "https://truyenyy.xyz/truyen/slug/chuong-index.html"
    LOGIN_URL = "https://betatruyen.com/account/login/"
    USERNAME = "playgame.vo@gmail.com"
    PASSWORD = "vuichoi1"
    URL_REDIRECT = "/oauth2/authorize"
    SELECTORS: dict = {
        "title": "body > div.container.novel-detail > div.novel-info > div > h1",
        "other_name": "",
        "cover_image": "body > div.container.novel-detail > div.novel-info > a > img",
        "author": "body > div.container.novel-detail > div.novel-info > div > div.author.mb-3 > a",
        "translator": "",
        "status": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(4) > li:nth-child(1) > a",
        "types": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(3)",
        "description": "#id_novel_summary",
        "last_chapter": "body > div.container.novel-detail > div.novel-info > div > ul:nth-child(6) > li:nth-child(1)",
        "tags": "",
        "chapter_title": "body > main > div.chapter > div.box > h2",
        "chapter_content": "body > main > div.chapter > div.box > div.chap-content",
    }
