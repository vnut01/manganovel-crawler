from dotenv import load_dotenv

load_dotenv()


class MeTruyenCV:
    DATA_PATH: str = "data"
    REQUEST_TIMEOUT: int = 30
    WAITING_TO_RECEIVE_RESPONSE: int = 1
    NUMBER_URL_A_REQUEST_BATCH: int = 200
    BASE_URL: str = "https://metruyencv.com"
    NOVEL_URL_FORM: str = "https://metruyencv.com/truyen/slug"
    CHAPTER_URL_FORM: str = "https://metruyencv.com/truyen/slug/chuong-index.html"

    LOGIN_URL = "https://backend.metruyencv.com/api/auth/login"
    REDIRECT_URL = "https://metruyencv.com"
    USERNAME = "playgame.vo@gmail.com"
    PASSWORD = "vuichoi1"

    SELECTORS: dict = {
        "title": "#app > div:nth-child(3) > div > main > div.space-y-5 > div.block > div.mb-4.mx-auto.text-center > h1 > a",
        "other_name": "",
        "cover_image": "#app > div:nth-child(3) > div > main > div.space-y-5 > div.block > div.mb-4 > div > a > img",
        "author": "#app > div:nth-child(3) > div > main > div.space-y-5 > div.block > div.mb-4.mx-auto.text-center > div:nth-child(2) > a",
        "translator": "",
        "status": "#app > div:nth-child(3) > div > main > div.space-y-5 > div.block > div.mb-4.mx-auto.text-center > div.leading-10",
        "types": "",
        "description": "#synopsis > div:nth-child(2)",
        "last_chapter": "",
        "tags": "",
        "chapter_title": "#app > div:nth-child(3) > div > main > div.flex.justify-center.space-x-2.items-center.px-2 > div > h2",
        "chapter_content": "#chapter-detail > div:nth-child(1)",
    }


class TruyenYY:
    DATA_PATH: str = "data"
    REQUEST_TIMEOUT: int = 30
    WAITING_TO_RECEIVE_RESPONSE: int = 1
    NUMBER_URL_A_REQUEST_BATCH: int = 200
    BASE_URL: str = "https://truyenyy.xyz"
    NOVEL_URL_FORM: str = "https://truyenyy.xyz/truyen/slug"
    CHAPTER_URL_FORM: str = "https://truyenyy.xyz/truyen/slug/chuong-index.html"
    LOGIN_URL = "https://betatruyen.com/account/login/"
    REDIRECT_URL = "/oauth2/authorize"
    USERNAME = "playgame.vo@gmail.com"
    PASSWORD = "vuichoi1"

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
