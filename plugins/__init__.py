import sys,time,os,random,string
from utils.html import Html
from threading import Thread
from queue import Queue
class PluginBase:
    url = None
    name = None
    author = None
    
    def __init__(self, url):
        self.url = url
        self.name, self.author = self.get_infor()

    def __progress(self, count, total):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '+' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('\r[%s] %d/%d  [%d%s] ' % (bar, count, total, percents,'%'))
        sys.stdout.flush()

    def _download(self):
        while not self.__download_queue.empty():
            try:
                index, url = self.__download_queue.get()
                content = [' '.join(line.split()) for line in self.get_content(url)]
                open(os.path.join(self.path,str(index).zfill(4)+'.txt'),'wb').write('\n'.join(content).encode('utf-8'))
                self.__progress(self.__total-self.__download_queue.qsize(), self.__total)
            except Exception as e:
                print(e)
                pass
                
    def download(self, path="", threads = 10):
        self.path = os.path.join(path,self.name)
        try:
            os.mkdir(self.path)
        except:
            if not os.path.isdir(self.path):
                raise Exception("[!] Cannot create folder!")

        #Task 1: Get urls
        self.__download_queue = Queue()
        for i, url in enumerate(self.get_urls()):
            self.__download_queue.put((i,url))

        #Task 2: Download contents
        self.__total = self.__download_queue.qsize()
        workers = []
        for _ in range(0, threads):
            worker = Thread(target=self._download)
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()
    
    #Get book informations from main url
    #return -> (name, author)
    def get_infor(self):
        if self.get_infor == PluginBase.get_infor:
            raise Exception("get_info() is not defined in %s!"%self.__class__.__name__)
        return None, None

    #Get urls list
    #return -> [chap1_url, chap2_url,...]
    def get_urls(self):
        if self.get_urls == PluginBase.get_urls:
            raise Exception("get_urls() is not defined in %s!"%self.__class__.__name__)
        return []

    #Get chapter content
    #return -> [title, line1,...]
    def get_content(self, url):
        if self.get_urls == PluginBase.get_urls:
            raise Exception("get_content() is not defined in %s!"%self.__class__.__name__)
        return []
