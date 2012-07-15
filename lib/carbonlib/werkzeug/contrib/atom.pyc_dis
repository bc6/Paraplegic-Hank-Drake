#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\atom.py
from datetime import datetime
from werkzeug.utils import escape
from werkzeug.wrappers import BaseResponse
XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

def _make_text_block(name, content, content_type = None):
    if content_type == 'xhtml':
        return u'<%s type="xhtml"><div xmlns="%s">%s</div></%s>\n' % (name,
         XHTML_NAMESPACE,
         content,
         name)
    if not content_type:
        return u'<%s>%s</%s>\n' % (name, escape(content), name)
    return u'<%s type="%s">%s</%s>\n' % (name,
     content_type,
     escape(content),
     name)


def format_iso8601(obj):
    return obj.strftime('%Y-%m-%dT%H:%M:%SZ')


class AtomFeed(object):
    default_generator = ('Werkzeug', None, None)

    def __init__(self, title = None, entries = None, **kwargs):
        self.title = title
        self.title_type = kwargs.get('title_type', 'text')
        self.url = kwargs.get('url')
        self.feed_url = kwargs.get('feed_url', self.url)
        self.id = kwargs.get('id', self.feed_url)
        self.updated = kwargs.get('updated')
        self.author = kwargs.get('author', ())
        self.icon = kwargs.get('icon')
        self.logo = kwargs.get('logo')
        self.rights = kwargs.get('rights')
        self.rights_type = kwargs.get('rights_type')
        self.subtitle = kwargs.get('subtitle')
        self.subtitle_type = kwargs.get('subtitle_type', 'text')
        self.generator = kwargs.get('generator')
        if self.generator is None:
            self.generator = self.default_generator
        self.links = kwargs.get('links', [])
        self.entries = entries and list(entries) or []
        if not hasattr(self.author, '__iter__') or isinstance(self.author, (basestring, dict)):
            self.author = [self.author]
        for i, author in enumerate(self.author):
            if not isinstance(author, dict):
                self.author[i] = {'name': author}

        if not self.title:
            raise ValueError('title is required')
        if not self.id:
            raise ValueError('id is required')
        for author in self.author:
            if 'name' not in author:
                raise TypeError('author must contain at least a name')

    def add(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0], FeedEntry):
            self.entries.append(args[0])
        else:
            kwargs['feed_url'] = self.feed_url
            self.entries.append(FeedEntry(*args, **kwargs))

    def __repr__(self):
        return '<%s %r (%d entries)>' % (self.__class__.__name__, self.title, len(self.entries))

    def generate(self):
        if not self.author:
            if False in map(lambda e: bool(e.author), self.entries):
                self.author = ({'name': u'unbekannter Autor'},)
        if not self.updated:
            dates = sorted([ entry.updated for entry in self.entries ])
            self.updated = dates and dates[-1] or datetime.utcnow()
        yield u'<?xml version="1.0" encoding="utf-8"?>\n'
        yield u'<feed xmlns="http://www.w3.org/2005/Atom">\n'
        yield '  ' + _make_text_block('title', self.title, self.title_type)
        yield u'  <id>%s</id>\n' % escape(self.id)
        yield u'  <updated>%s</updated>\n' % format_iso8601(self.updated)
        if self.url:
            yield u'  <link href="%s" />\n' % escape(self.url, True)
        if self.feed_url:
            yield u'  <link href="%s" rel="self" />\n' % escape(self.feed_url, True)
        for link in self.links:
            yield u'  <link %s/>\n' % ''.join(('%s="%s" ' % (k, escape(link[k], True)) for k in link))

        for author in self.author:
            yield u'  <author>\n'
            yield u'    <name>%s</name>\n' % escape(author['name'])
            if 'uri' in author:
                yield u'    <uri>%s</uri>\n' % escape(author['uri'])
            if 'email' in author:
                yield '    <email>%s</email>\n' % escape(author['email'])
            yield '  </author>\n'

        if self.subtitle:
            yield '  ' + _make_text_block('subtitle', self.subtitle, self.subtitle_type)
        if self.icon:
            yield u'  <icon>%s</icon>\n' % escape(self.icon)
        if self.logo:
            yield u'  <logo>%s</logo>\n' % escape(self.logo)
        if self.rights:
            yield '  ' + _make_text_block('rights', self.rights, self.rights_type)
        generator_name, generator_url, generator_version = self.generator
        if generator_name or generator_url or generator_version:
            tmp = [u'  <generator']
            if generator_url:
                tmp.append(u' uri="%s"' % escape(generator_url, True))
            if generator_version:
                tmp.append(u' version="%s"' % escape(generator_version, True))
            tmp.append(u'>%s</generator>\n' % escape(generator_name))
            yield u''.join(tmp)
        for entry in self.entries:
            for line in entry.generate():
                yield u'  ' + line

        yield u'</feed>\n'

    def to_string(self):
        return u''.join(self.generate())

    def get_response(self):
        return BaseResponse(self.to_string(), mimetype='application/atom+xml')

    def __call__(self, environ, start_response):
        return self.get_response()(environ, start_response)

    def __unicode__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string().encode('utf-8')


class FeedEntry(object):

    def __init__(self, title = None, content = None, feed_url = None, **kwargs):
        self.title = title
        self.title_type = kwargs.get('title_type', 'text')
        self.content = content
        self.content_type = kwargs.get('content_type', 'html')
        self.url = kwargs.get('url')
        self.id = kwargs.get('id', self.url)
        self.updated = kwargs.get('updated')
        self.summary = kwargs.get('summary')
        self.summary_type = kwargs.get('summary_type', 'html')
        self.author = kwargs.get('author')
        self.published = kwargs.get('published')
        self.rights = kwargs.get('rights')
        self.links = kwargs.get('links', [])
        self.xml_base = kwargs.get('xml_base', feed_url)
        if not hasattr(self.author, '__iter__') or isinstance(self.author, (basestring, dict)):
            self.author = [self.author]
        for i, author in enumerate(self.author):
            if not isinstance(author, dict):
                self.author[i] = {'name': author}

        if not self.title:
            raise ValueError('title is required')
        if not self.id:
            raise ValueError('id is required')
        if not self.updated:
            raise ValueError('updated is required')

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.title)

    def generate(self):
        base = ''
        if self.xml_base:
            base = ' xml:base="%s"' % escape(self.xml_base, True)
        yield u'<entry%s>\n' % base
        yield u'  ' + _make_text_block('title', self.title, self.title_type)
        yield u'  <id>%s</id>\n' % escape(self.id)
        yield u'  <updated>%s</updated>\n' % format_iso8601(self.updated)
        if self.published:
            yield u'  <published>%s</published>\n' % format_iso8601(self.published)
        if self.url:
            yield u'  <link href="%s" />\n' % escape(self.url)
        for author in self.author:
            yield u'  <author>\n'
            yield u'    <name>%s</name>\n' % escape(author['name'])
            if 'uri' in author:
                yield u'    <uri>%s</uri>\n' % escape(author['uri'])
            if 'email' in author:
                yield u'    <email>%s</email>\n' % escape(author['email'])
            yield u'  </author>\n'

        for link in self.links:
            yield u'  <link %s/>\n' % ''.join(('%s="%s" ' % (k, escape(link[k], True)) for k in link))

        if self.summary:
            yield u'  ' + _make_text_block('summary', self.summary, self.summary_type)
        if self.content:
            yield u'  ' + _make_text_block('content', self.content, self.content_type)
        yield u'</entry>\n'

    def to_string(self):
        return u''.join(self.generate())

    def __unicode__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string().encode('utf-8')