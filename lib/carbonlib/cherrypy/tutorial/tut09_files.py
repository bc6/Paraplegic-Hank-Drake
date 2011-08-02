import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
import cherrypy
from cherrypy.lib import static

class FileDemo(object):

    def index(self):
        return '\n        <html><body>\n            <form action="upload" method="post" enctype="multipart/form-data">\n            filename: <input type="file" name="myFile" /><br />\n            <input type="submit" />\n            </form>\n        </body></html>\n        '


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

cherrypy.tree.mount(FileDemo())
if __name__ == '__main__':
    import os.path
    thisdir = os.path.dirname(__file__)
    cherrypy.quickstart(config=os.path.join(thisdir, 'tutorial.conf'))

