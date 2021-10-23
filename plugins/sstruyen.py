from plugins import PluginBase
from utils.html import Html
from queue import Queue

class SSTruyen(PluginBase):
    def get_infor(self):
        html = Html().load(self.url)
        name = html.select('body > div.book-list.story-details > div > div > div.col-md-12.col-lg-9 > div.row.wrap-detail.pc > div.col-md-8 > div.title > h1 > a').get_text().strip()
        author = html.select('body > div.book-list.story-details > div > div > div.col-md-12.col-lg-9 > div.row.wrap-detail.pc > div.col-md-8 > div.content1 > div > p:nth-child(1) > a').get_text().strip()
        return name, author

    def get_urls(self):
        urls = []
        queue = Queue()
        queue.put(self.url)
        while not queue.empty():
            html = Html().load(queue.get())
            for entry in html.select('body > div.book-list.story-details > div > div > div.col-md-12.col-lg-9 > div.row.list-chap').findAll('a'):
                urls.append(entry['href'])
            next_ele = html.find('li', {'class':'next'})
            if next_ele != None:
                next_url = next_ele.find('a')['href']
                if next_url != "#":
                    queue.put(next_url)
        return urls

    def get_content(self, url):
        html = Html().load(url)
        for div in html.find_all("div", {'class':'ads-responsive incontent-ad'}): 
            div.decompose()
        for ele in html.find_all("a", {'href':'https://truyenfull.vn'}):
            ele.decompose()
        content = []
        chapter_title = html.select('#chapter-big-container > div > div > h2 > a').get_text().replace('\n','')
        content.append(chapter_title)
        chapter_content = html.select('#chapter-c')
        for a in html.find_all('a'):
            a.decompose()
        
        chapter_content = str(chapter_content)
        chapter_content = chapter_content.replace("<i>",'')
        chapter_content = chapter_content.replace("</i>",'')
        chapter_content = chapter_content.replace('\n','')
        chapter_content = chapter_content.replace("<br>",'\n')
        chapter_content = chapter_content.replace('<br/>','\n')
        chapter_content = Html(chapter_content).get_text()
        chapter_content = chapter_content.replace('\n ','\n')
        chapter_content = chapter_content.replace(' \n','\n')
        chapter_content = chapter_content.replace('\n\n','\n')
        for line in chapter_content.split('\n'):
            content.append(line)
        return content
