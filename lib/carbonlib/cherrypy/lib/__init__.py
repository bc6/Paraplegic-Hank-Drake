from cherrypy.lib.reprconf import _Builder, unrepr, modules, attributes

class file_generator(object):

    def __init__(self, input, chunkSize = 65536):
        self.input = input
        self.chunkSize = chunkSize



    def __iter__(self):
        return self



    def __next__(self):
        chunk = self.input.read(self.chunkSize)
        if chunk:
            return chunk
        self.input.close()
        raise StopIteration()


    next = __next__


def file_generator_limited(fileobj, count, chunk_size = 65536):
    remaining = count
    while remaining > 0:
        chunk = fileobj.read(min(chunk_size, remaining))
        chunklen = len(chunk)
        if chunklen == 0:
            return 
        remaining -= chunklen
        yield chunk




def set_vary_header(response, header_name):
    varies = response.headers.get('Vary', '')
    varies = [ x.strip() for x in varies.split(',') if x.strip() ]
    if header_name not in varies:
        varies.append(header_name)
    response.headers['Vary'] = ', '.join(varies)



