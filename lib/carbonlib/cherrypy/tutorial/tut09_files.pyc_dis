#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\tutorial\tut09_files.py
import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
import cherrypy
from cherrypy.lib import static

class FileDemo(object):

    def index(self):
        return '\n        <html><body>\n            <h2>Upload a file</h2>\n            <form action="upload" method="post" enctype="multipart/form-data">\n            filename: <input type="file" name="myFile" /><br />\n            <input type="submit" />\n            </form>\n            <h2>Download a file</h2>\n            <a href=\'download\'>This one</a>\n        </body></html>\n        '

    index.exposed = True

    def upload(self, myFile):
        out = '<html>\n        <body>\n            myFile length: %s<br />\n            myFile filename: %s<br />\n            myFile mime-type: %s\n        </body>\n        </html>'
        size = 0
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)

        return out % (size, myFile.filename, myFile.content_type)

    upload.exposed = True

    def download(self):
        path = os.path.join(absDir, 'pdf_file.pdf')
        return static.serve_file(path, 'application/x-download', 'attachment', os.path.basename(path))

    download.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(FileDemo(), config=tutconf)
else:
    cherrypy.tree.mount(FileDemo(), config=tutconf)