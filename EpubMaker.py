import os
import zipfile
import pathlib
import configparser

from natsort import natsorted as numeric_sorted

class Epub:
    MIME = "application/epub+zip"
    CONTAINER_XML = (
        '<?xml version="1.0" ?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '    <rootfiles>\n'
        '        <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        '    </rootfiles>\n'
        '</container>\n'
    )
    CSS = (
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
        '.p_toc { text-indent: 10mm; margin-top: 10pt; margin-bottom: 10pt;}\n'
    )
    MEDIA_TYPES = {
        ".png" : "image/png",
        ".jpg" : "image/jpeg",
        ".jpeg" : "image/jpeg"
    }

    def __init__(self, meta_path=None):
        self.name = None
        self.author = None
        self.uid = None
        self.language = None

        if meta_path is not None:
            meta = configparser.ConfigParser()
            meta.read(meta_path)
            self.name = meta.get('info', 'name')
            self.author = meta.get('info', 'author')
            self.uid = meta.get('info', 'UID')
            self.language = meta.get('info', 'language')

    def __scan(path):
        text_paths = []
        media_paths = []
        for root, dir_names, file_names in os.walk(path):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                file_ext = pathlib.Path(file_name).suffix
                if file_ext == '.txt':
                    text_paths.append(file_path)
                elif file_ext in Epub.MEDIA_TYPES:
                    media_paths.append(file_path)

        texts = []
        for text_path in numeric_sorted(text_paths):
            print(f"-> TEXT: {text_path}")
            with open(text_path,'r',encoding='utf-8') as file:
                texts.append([line.replace('\n','').replace('\r','') for line in file])

        medias = []
        for media_path in numeric_sorted(media_paths):
            print(f"-> MEDIA: {media_path}")
            with open(media_path,'rb') as file:
                medias.append((os.path.basename(media_path), file.read()))
        
        return texts, medias
    
    def __build_html(self, text: list[str]) -> str:
        data = (
            '<?xml version="1.0" encoding="utf-8" ?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '    <head>\n'
            '        <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />\n'
            '        <link rel="stylesheet" type="text/css" href="style.css" />\n'
            '        <title>'+text[0]+'</title>\n'
            '    </head>\n'
            '\n'
            '    <body>\n'
            '        <h3 class="chapter_heading">'+text[0]+'</h3>\n'
            '\n')
        if (len(text)>1):
            data += '        <p class="p_first">'+text[1]+'</p>\n'
        for i in range(2,len(text)):
            data += '        <p class="p_normal">'+text[i]+'</p>\n'
        data += (
            '    </body>\n'
            '</html>\n')
        return data

    def __build_toc(self, texts: list[list[str]]) -> str:
        data = (
            '<?xml version="1.0" encoding="utf-8" ?>\n'
            '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n'
            '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="en" version="2005-1">\n'
            '    <head>\n'
            '        <meta name="dtb:uid" content="'+self.uid+'" />\n'
            '        <meta name="dtb:depth" content="1" />\n'
            '        <meta name="dtb:totalPageCount" content="0" />\n'
            '        <meta name="dtb:maxPageNumber" content="0" />\n'
            '    </head>\n'
            '\n'
            '    <docTitle>\n'
            '        <text>'+self.name+'</text>\n'
            '    </docTitle>\n'
            '\n'
            '    <navMap>')
        for index, chapter in enumerate(texts):
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
    
    def __build_content(self, htmls: list[str], medias: list[tuple[str, bytes]]) -> str:
        data = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">\n'
            '    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf">\n'
            '        <dc:title>'+self.name+'</dc:title>\n'
            '        <dc:creator>'+self.author+'</dc:creator>\n'
            '        <dc:language>'+self.language+'</dc:language>\n'
            '        <dc:identifier id="BookId">'+self.uid+'</dc:identifier>\n'
            '        <dc:subject>General Fiction</dc:subject>\n'
            '        <dc:date>2019-09-02</dc:date>\n'
            '    </metadata>\n'
            '\n'
            '    <manifest>\n'
            '        <item id="toc_ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />\n'
            '        <item id="style_css" href="style.css" media-type="text/css" />\n')
        for index in range(len(htmls)):
            data += (
                '        <item id="'+'{:04d}'.format(index)+'_html" href="'+'{:04d}'.format(index)+'.html" media-type="application/xhtml+xml" />\n')   
        for name, _ in medias:
            data += (
                '        <item id="'+name.replace('.','_')+'" href="'+name+'" media-type="'+Epub.MEDIA_TYPES[pathlib.Path(name).suffix]+'" />\n')
        data += (
            '    </manifest>\n'
            '    <spine toc="toc_ncx">\n')
        for index in range(len(htmls)):
            data += (
                '        <itemref idref="'+'{:04d}'.format(index)+'_html"/>\n')
        data += (
            '    </spine>\n'
            '    <guide>\n'
            '    </guide>\n'
            '</package>\n')
        return data

    def make(self, dir_path, dest_path):
        print("Scan for files...")      
        texts, medias = Epub.__scan(dir_path)

        print("Build...")
        htmls = [self.__build_html(text) for text in texts]
        toc = self.__build_toc(texts)
        content = self.__build_content(htmls, medias)

        print("Making EPUB file...")
        with zipfile.ZipFile(dest_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zip:
            def add(file_name, file_data):
                with zip.open(file_name,"w") as file:
                    file.write(file_data)
            add("mimetype", Epub.MIME.encode("utf-8"))
            add("META-INF/container.xml", Epub.CONTAINER_XML.encode("utf-8"))
            add("OPS/content.opf", content.encode("utf-8"))
            add("OPS/toc.ncx", toc.encode("utf-8"))
            add("OPS/style.css", Epub.CSS.encode("utf-8"))
            for index, html in enumerate(htmls):
                add("OPS/{:04d}.html".format(index), html.encode("utf-8"))
            for name, binary in medias:
                add(f"OPS/{name}", binary)

        print("Done!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='EpubMaker')
    parser.add_argument('--meta_path', type=str, required=True)
    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_known_args()[0]
    
    book = Epub(meta_path=args.meta_path)
    book.make(args.path, f"{book.uid}.epub")
