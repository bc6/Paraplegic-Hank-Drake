from paste.request import construct_url
PONY = '\neJyFkkFuxCAMRfdzCisbJxK2D5D2JpbMrlI3XXQZDt9PCG0ySgcWIMT79rcN0XClUJlZRB9jVmci\nFmV19khjgRFl0RzrKmqzvY8lRUWFlXvCrD7UbAQR/17NUvGhypAF9og16vWtkC8DzUayS6pN3/dR\nki0OnpzKjUBFpmlC7zVFRNL1rwoq6PWXXQSnIm9WoTzlM2//ke21o5g/l1ckRhiPbkDZXsKIR7l1\n36hF9uMhnRiVjI8UgYjlsIKCrXXpcA9iX5y7zMmtG0fUpW61Ssttipf6cp3WARfkMVoYFryi2a+w\no/2dhW0OXfcMTnmh53oR9egzPs+qkpY9IKxdUVRP5wHO7UDAuI6moA2N+/z4vtc2k8B+AIBimVU=\n'
UNICORN = '\neJyVVD1vhDAM3e9XeAtIxB5P6qlDx0OMXVBzSpZOHdsxP762E0JAnMgZ8Zn37OePAPC60eV1Dl5b\nSS7fB6DmQNGhtegpNlPIQS8HmkYGdSqNqDF9wcMYus4TuBYGsZwIPqXfEoNir5K+R3mbzhlR4JMW\neGpikPpn9wHl2sDgEH1270guZwzKDRf3nTztMvfI5r3fJqEmNxdCyISBcWjNgjPG8Egg2hgT3mJi\nKBwNvmPB1hbWJ3TwBfMlqdTzxNyDE2H8zOD5HA4KkqJGPVY/TwnxmPA82kdSJNj7zs+R0d1pB+JO\nxn2DKgsdxAfFS2pfTSD0Fb6Uzv7dCQSvE5JmZQEQ90vNjBU1GPuGQpCPS8cGo+dQgjIKqxnJTXbw\nucFzPFVIJXtzk6BXKGPnYsKzvFmGx7A0j6Zqvlvk5rETXbMWTGWj0RFc8QNPYVfhJfMMniCPazWJ\nlGtPZecIGJWW6oL2hpbWRZEkChe8eg5Wb7xx/MBZBFjxeZPEss+mRQ3Uhc8WQv684seSRO7i3nb4\n7HlKUg8sraz47LmXyh8S0somADvoUpoHjGWl+rUkF0H+EIf/gbyyMg58BBk6L634/fkHUCodMw==\n'

class PonyMiddleware(object):

    def __init__(self, application):
        self.application = application



    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info == '/pony':
            url = construct_url(environ, with_query_string=False)
            if 'horn' in environ.get('QUERY_STRING', ''):
                data = UNICORN
                link = 'remove horn!'
            else:
                data = PONY
                url += '?horn'
                link = 'add horn!'
            msg = data.decode('base64').decode('zlib')
            msg = '<pre>%s\n<a href="%s">%s</a></pre>' % (msg, url, link)
            start_response('200 OK', [('content-type', 'text/html')])
            return [msg]
        else:
            return self.application(environ, start_response)




def make_pony(app, global_conf):
    return PonyMiddleware(app)



