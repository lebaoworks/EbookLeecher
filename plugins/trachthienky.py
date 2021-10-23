from plugins.base import PluginBase
from utils.html import Html
from queue import Queue

class TrachThienKy(PluginBase):
    def get_infor(self):
        html = Html().load(self.url)
        name = html.select('body > div.container > div.content > div.row > div.col-md-9.book-info > div:nth-child(1) > div.col-sm-8 > h4').get_text().strip()
        author = html.select('body > div.container > div.main.row > div > h2 > span.author').get_text().strip()
        return name, author

    def get_urls(self):
        urls = []
        queue = Queue()
        main = Html().load(self.url)
        urls = [f"http://www.trachthienky.com{ele.find('a')['href']}" for ele in main.find_all("div",{"class":"col-md-6 chapter-title hidden-xs hidden-sm"})]
        return urls

    def get_content(self, url):
        html = Html().load(url)
        content = [html.select('body > div.container > div.content > div.chapter-container > h1').get_text().replace('\n','')]
        content_element = html.find("div",{"class":"chapter-content-s"})
        for p in content_element.find_all("p"): 
            p.decompose()
        for line in content_element.get_text().split('\n'):
            line = ' '.join(line.split()).replace(' .','.')
            if line:
                content.append(line)
        return content
