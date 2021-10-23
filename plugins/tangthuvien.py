from plugins import PluginBase
from utils.html import Html
from queue import Queue
import time

class Plugin(PluginBase):
    story_id = None
    def get_infor(self):
        html = Html().load(self.url)
        name = html.select('body > div.book-detail-wrap.center990 > div.book-information.cf > div.book-info > h1').get_text().strip()
        author = html.select('#authorId > p > a').get_text().strip()
        self.story_id = html.find("input", {"id":"story_id_hidden"})['value']
        return name, author

    def get_urls(self):
        toc = Html().load("https://truyen.tangthuvien.vn/story/chapters?story_id="+self.story_id)
        urls = [entry['href'] for entry in toc.find_all('a')]
        return urls

    def get_content(self, url):
        html = Html().load(url)
        while 'Site Maintenance' in str(html):
            time.sleep(0.5)
            html = Html().load(url)

        content = []
        chapter_title = html.select('body > div.container.body-container > div > div.col-xs-12.chapter > h2').get_text().replace('\n','').replace('\xa0',' ')
        content.append(chapter_title)
        chapter_content = html.find('div', {'class':'box-chap'}).get_text()
        for line in chapter_content.split('\n'):
            if line.strip() != '':
                content.append(line.strip())
        return content
