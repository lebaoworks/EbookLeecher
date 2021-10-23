from plugins import PluginBase
from utils.html import Html
from queue import Queue

class Plugin(PluginBase):
    def get_infor(self):
        html = Html().load(self.url)
        name = html.select('#truyen-title').get_text().strip()
        author = html.select('#tacgia > a').get_text().strip()
        return name, author

    def get_urls(self):
        urls = []
        queue = Queue()
        html = Html().load(self.url + "/muc-luc?page=all")
        for entry in html.select('#mucluc-list > div').findAll('a'):
            urls.append("https://bachngocsach.com" + entry['href'])
        return urls

    def get_content(self, url):
        html = Html().load(url)
        content = []
        chapter_title = html.select('#chuong-title').get_text().replace('\n','')
        content.append(chapter_title)
        chapter_content = html.select('#noi-dung').findAll('p')
        for element in chapter_content:
            content.append(element.get_text())
        return content
