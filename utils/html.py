from bs4 import BeautifulSoup
import requests

class Html(BeautifulSoup):
    def __init__(self, text=""):
        super().__init__(text,"html.parser")
    
    def load(self, url):
        resp = requests.get(url)
        self.__init__(resp.text)
        return self

    def get_text(self):
        return super().get_text('\n')

    def select(self, *args, **kwargs):
        return Html(str(super().select(*args, **kwargs)[0]))


