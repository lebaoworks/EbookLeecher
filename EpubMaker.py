import os
import io
import zipfile
import pathlib

class ZipFile:
    def __init__(self):
        self.data = io.BytesIO()
        self.zip = zipfile.ZipFile(self.data,"a",compression=zipfile.ZIP_DEFLATED)
    def add(self, file_name, file_data):
        with self.zip.open(file_name,"w") as file:
            file.write(file_data)
    def writetofile(self,path):
        self.zip.close()
        self.data.seek(0)
        f = open(path,"wb")
        f.write(self.data.read())
        f.close()
        self.zip = zipfile.ZipFile(self.data,"a")
    def close(self):
        self.zip.close()
        self.data.close()

class EpubMaker:
    
    media_types =  {
        ".png" : "image/png",
        ".jpg" : "image/jpeg",
        ".jpeg" : "image/jpeg"}

    def __init__(self):
        self.__book_name = "unknown"
        self.__book_author = "unknown"
        self.__book_uid = "unknown"
        self.__book_language = "unknown"

        self.__txt_files = []
        self.__html_files = []
        self.__media_files = [] #(name,binary_data)

    def set_name(self, new_name):
        self.__book_name = new_name
    def set_uid(self, new_uid):
        self.__book_uid = new_uid
    def set_author(self, new_author):
        self.__book_author = new_author
    def set_language(self, new_language):
        self.__book_language = new_language

    def make_mimetype(self):
        return "application/epub+zip"
    def make_container_xml(self):
        return (
            '<?xml version="1.0" ?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '    <rootfiles>\n'
            '        <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/>\n'
            '    </rootfiles>\n'
            '</container>\n')
    def make_style_css(self):
        return (
            '.center { text-align: center;  text-indent: 0em; }\n'
            '.right { text-align: right; }\n'
            '.caption { font-weight: bold; }\n'
            '.noindent { text-indent: 0em; }\n'
            '.smallcaps { font-variant: small-caps; }\n'
            '.small { font-size: small; }\n'
            '.large { font-size: large; }\n'
            '.note { font-size: small; text-indent: 0em; }\n'
            '.chapter_heading { text-align: center; text-indent: 0em; margin-top: 20pt; margin-bottom: 20pt; }\n'
            '.toc_heading { text-align: center; margin-top: 20pt; margin-bottom: 20pt; }\n'
            '.p_normal { text-indent: 10mm; margin-top: 5pt; margin-bottom: 5pt;}\n'
            '.p_first { text-indent: 0mm; margin-top: 5pt; margin-bottom: 5pt;}\n'
            '.p_toc { text-indent: 10mm; margin-top: 10pt; margin-bottom: 10pt;}\n')
    def make_toc_ncx(self):
        data = (
            '<?xml version="1.0" encoding="utf-8" ?>\n'
            '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n'
            '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="en" version="2005-1">\n'
            '    <head>\n'
            '        <meta name="dtb:uid" content="'+ self.__book_uid + '" />\n'
            '        <meta name="dtb:depth" content="1" />\n'
            '        <meta name="dtb:totalPageCount" content="0" />\n'
            '        <meta name="dtb:maxPageNumber" content="0" />\n'
            '    </head>\n'
            '\n'
            '    <docTitle>\n'
            '        <text>'+self.__book_name+'</text>\n'
            '    </docTitle>\n'
            '\n'
            '    <navMap>')
        for index,chapter in enumerate(self.__txt_files):
            data += (
                '        <navPoint id="navPoint-1" playOrder="1">\n'
                '            <navLabel>\n'
                '                <text>'+chapter[0]+'</text>\n'
                '            </navLabel>\n'
                '            <content src="'+'{:04d}'.format(index)+'.html" />\n'
                '        </navPoint>\n')
        data += (
            '    </navMap>\n'
            '</ncx>\n')
        return data
    def make_content_opf(self):
        data = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">\n'
            '    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf">\n'
            '        <dc:title>'+self.__book_name+'</dc:title>\n'
            '        <dc:creator>'+self.__book_author+'</dc:creator>\n'
            '        <dc:language>'+self.__book_language+'</dc:language>\n'
            '        <dc:identifier id="BookId">'+self.__book_uid+'</dc:identifier>\n'
            '        <dc:subject>General Fiction</dc:subject>\n'
            '        <dc:date>2019-09-02</dc:date>\n'
            '    </metadata>\n'
            '\n'
            '    <manifest>\n'
            '        <item id="toc_ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />\n'
            '        <item id="style_css" href="style.css" media-type="text/css" />\n')
        for index in range(len(self.__txt_files)):
            data += (
                '        <item id="'+'{:04d}'.format(index)+'_html" href="'+'{:04d}'.format(index)+'.html" media-type="application/xhtml+xml" />\n')   
        for name, _ in self.__media_files:
            data += (
                '        <item id="'+name.replace('.','_')+'" href="'+name+'" media-type="'+EpubMaker.media_types[pathlib.Path(name).suffix]+'" />\n')
        data += (
            '    </manifest>\n'
            '    <spine toc="toc_ncx">\n')
        for index in range(len(self.__txt_files)):
            data += (
                '        <itemref idref="'+'{:04d}'.format(index)+'_html"/>\n')
        data += (
            '    </spine>\n'
            '    <guide>\n'
            '    </guide>\n'
            '</package>\n')
        return data

    def make_html_files(self):
        self.__html_files.clear()
        for chapter in self.__txt_files:
            data = (
                '<?xml version="1.0" encoding="utf-8" ?>\n'
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
                '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                '    <head>\n'
                '        <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />\n'
                '        <link rel="stylesheet" type="text/css" href="style.css" />\n'
                '        <title>'+chapter[0]+'</title>\n'
                '    </head>\n'
                '\n'
                '    <body>\n'
                '        <h3 class="chapter_heading">'+chapter[0]+'</h3>\n'
                '\n')
            if (len(chapter)>1):
                data += '        <p class="p_first">'+chapter[1]+'</p>\n'
            for i in range(2,len(chapter)):
                data += '        <p class="p_normal">'+chapter[i]+'</p>\n'
            data += (
                '    </body>\n'
                '</html>\n')
            self.__html_files.append(data)
    def read_data(self, path = ""):
        files = [os.path.join(path,f) for f in os.listdir(path)]
        txts = [f for f in files if os.path.isfile(f) and pathlib.Path(f).suffix == '.txt']
        medias = [f for f in files if os.path.isfile(f) and pathlib.Path(f).suffix in EpubMaker.media_types]
        
        print("Reading txt file(s)...")
        for name in txts:
            #print('\t'+name)
            file = open(name,'r',encoding='utf-8')
            self.__txt_files.append([line.replace('\n','').replace('\r','') for line in file])
            file.close()

        print("Reading media file(s)...")
        for name in medias:
            #print('\t'+name)
            file = open(name,'rb')
            self.__media_files.append((os.path.basename(name),file.read()))
            file.close()

    def make(self,input_path = "", output_path = ""):
        if output_path == "":
            output_path = self.__book_name
        self.read_data(input_path)
        self.make_html_files()

        print("Making EPUB file...")
        epub = ZipFile()
        epub.add("mimetype",self.make_mimetype().encode("utf-8"))
        epub.add("META-INF/container.xml",self.make_container_xml().encode("utf-8"))
        epub.add("OPS/content.opf",self.make_content_opf().encode("utf-8"))
        epub.add("OPS/toc.ncx",self.make_toc_ncx().encode("utf-8"))
        epub.add("OPS/style.css",self.make_style_css().encode("utf-8"))
        for index,html in enumerate(self.__html_files):
            epub.add("OPS/"+'{:04d}'.format(index)+".html",html.encode("utf-8"))
        for name,binary in self.__media_files:
            epub.add("OPS/"+name,binary)
        epub.writetofile(output_path)
        epub.close()
        print("Done!")

if __name__ == "__main__":
    import argparse, configparser
    parser = argparse.ArgumentParser(description='EpubMaker')
    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_known_args()[0]
    config_file = '__info__.ini'
    try:
        info_path = os.path.join(args.path, config_file)
        print(open(info_path,"rb").read())
        info = configparser.ConfigParser()
        info.read(info_path)
        info = info[info.sections()[0]]
    except Exception as e:
        print(f"Config file {config_file} is missing or corrupted! -> {e}")
        exit(1)
    
    try:
        maker = EpubMaker()
        maker.set_name(info['name'])
        maker.set_author(info['author'])
        maker.set_language(info['language'])
        maker.set_uid(info['UID'])
    except:
        print(f"Config file {config_file} is corrupted!")
        exit(1)

    maker.make(args.path, f"{os.path.join(args.path, info['UID'])}.epub")
