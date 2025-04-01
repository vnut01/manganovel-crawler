import requests
import time
from config.settings import TruyenYY

class BaseCrawler:
    def __init__(self, domain):
        if "truyenyy" in domain:
            self.request_timeout = TruyenYY.REQUEST_TIMEOUT
            self.waiting_to_receive_response = TruyenYY.WAITING_TO_RECEIVE_RESPONSE
            self.base_url = TruyenYY.BASE_URL
            self.novel_url_form = TruyenYY.NOVEL_URL_FORM
            self.chapter_url_form = TruyenYY.CHAPTER_URL_FORM
            self.selectors = TruyenYY.SELECTORS
        
        self.section = requests.Session()
    
    def fetch(self, url):
        try:
            response = self.section.get(
                url,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            time.sleep(self.waiting_to_receive_response)
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None