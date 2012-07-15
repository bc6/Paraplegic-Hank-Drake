#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/datatable.py
import datetime

class DataTableException(Exception):
    pass


class DataTableQuery(object):

    def __init__(self):
        self.__query_list = {}

    def filter(self, tq):
        utq = tq.upper()
        pos_list = []
        i = utq.find('SELECT')
        if i > -1:
            pos_list.append((i, 'SELECT'))
        i = utq.find('WHERE')
        if i > -1:
            pos_list.append((i, 'WHERE'))
        i = utq.find('ORDER BY')
        if i > -1:
            pos_list.append((i, 'ORDER BY'))
        i = utq.find('LIMIT')
        if i > -1:
            pos_list.append((i, 'LIMIT'))
        i = utq.find('OFFSET')
        if i > -1:
            pos_list.append((i, 'OFFSET'))
        pos_list.sort(lambda x, y: cmp(x[0], y[0]))
        for x in range(0, len(pos_list)):
            if x < len(pos_list) - 1:
                t1, t2 = pos_list[x], pos_list[x + 1]
                self.__query_list[t1[1]] = tq[t1[0]:t2[0]].replace(t1[1], '').strip()
            else:
                t1 = pos_list[x]
                self.__query_list[t1[1]] = tq[int(t1[0]):].replace(t1[1], '').strip()

        return self

    def query(self, table_def, table_rows):
        if len(self.__query_list) == 0:
            return (table_def, table_rows)
        if self.__query_list.has_key('SELECT'):
            sel = self.__query_list['SELECT'].replace(' ', '').split(',')
            skip_idx = []
            columns = {}
            for x in range(0, len(table_def)):
                columns[table_def[x][0]] = x
                if table_def[x][0] not in sel:
                    skip_idx.append(x)

            table_def = filter(lambda x: x[0] in sel, table_def)
            if self.__query_list.has_key('ORDER BY'):
                idx = columns[self.__query_list['ORDER BY']]
                table_rows.sort(lambda x, y: cmp(x[idx], y[idx]))
            if len(skip_idx) > 0:
                t_rows = []
                for tr in table_rows:
                    t_row = []
                    idx = 0
                    for t in tr:
                        if idx not in skip_idx:
                            t_row.append(t)
                        idx += 1

                    t_rows.append(t_row)

                table_rows = t_rows
        limit = int(self.__query_list['LIMIT']) if self.__query_list.has_key('LIMIT') else len(table_rows)
        offset = 0 if not self.__query_list.has_key('OFFSET') else int(self.__query_list['OFFSET'])
        return (table_def, table_rows[offset:offset + limit])


class DataTable(object):

    def __init__(self, table_def = None, table_rows = [], version = '0.6', tqx = None, tq = None):
        self.__allowedColumn = ['boolean',
         'number',
         'string',
         'date',
         'datetime',
         'timeofday']
        if tq is not None and table_def is not None:
            tableQuery = DataTableQuery()
            self.__table_def, self.__rows = tableQuery.filter(tq).query(table_def, table_rows)
        else:
            self.__table_def = table_def
            self.__rows = table_rows
        self.__version = version
        self.__tqxdict = {}
        if tqx is not None:
            for x in tqx.split(';'):
                args = x.split(':')
                self.__tqxdict[args[0]] = args[1]

        self.__errors = []
        self.__output = []

    def Render(self, response, output = 'datatable'):
        output = output.lower()
        if output == 'xml':
            response.contentType = 'application/xml; charset=utf-8'
            return self.toXml()
        elif output == 'csv':
            return self.toCsv()
        elif output == 'datatable':
            response.contentType = 'text/HTML; charset=utf-8'
            return self.toDataTable()
        elif output == 'htmltable':
            response.contentType = 'text/HTML; charset=utf-8'
            return self.toHtmlTable()
        elif output == 'rss':
            response.contentType = 'application/xml; charset=utf-8'
            return self.toRss()
        else:
            return 'unknown output(%s)' % output

    def toRss(self, title, description, link):
        reply = []
        reply.append('<?xml version="1.0" encoding="UTF-8" ?>')
        reply.append('<rss version="2.0">')
        reply.append('<channel>')
        reply.append('\t<title>%s</title>' % title)
        reply.append('\t<description>%s</description>' % description)
        reply.append('  <link>%s</link>' % link)
        for r in self.__rows:
            if len(r) is not 5:
                raise DataTableException('RSS feed must contain [title,link,description,uniqueId,pubDate]')
            reply.append('\t<item>')
            if r[0] is not None:
                reply.append('      <title>%s</title>' % r[0])
            if r[1] is not None:
                reply.append('      <link>%s</link>' % r[1])
            if r[2] is not None:
                reply.append('      <description><![CDATA[\n%s\n]]></description>' % r[2])
            if r[3] is not None:
                reply.append('      <guid>%s</guid>' % r[3])
            if r[4] is not None:
                reply.append('      <pubDate>%s</pubDate>' % r[4])
            reply.append('\t</item>')

        reply.append('</channel>')
        reply.append('</rss>')
        return '\n'.join(reply)

    def toDataTable(self):
        reply = []
        reply.append(self.__Column(self.__table_def))
        reply.append(',')
        reply.append(self.__Rows(self.__rows))
        return self.__Wrapper(reply)

    def toCsv(self):
        reply = []
        reply.append(', '.join(map(lambda x: x[0], self.__table_def)))
        reply.append('\n'.join([ ', '.join([ unicode(y) for y in x ]) for x in self.__rows ]))
        return '\n'.join(reply)

    def toHtmlTable(self):
        reply = []
        reply.append('<table>')
        reply.append('<tr><td>' + '</td><td>'.join(map(lambda x: x[0], self.__table_def)) + '</td></tr>\n')
        reply.append('\n'.join([ '<tr><td>%s</td></tr>' % '</td><td>'.join(x) for x in self.__rows ]))
        reply.append('</table>')
        return '\n'.join(reply)

    def toXml(self):
        reply = []
        reply.append('<?xml version="1.0" encoding="UTF-8" ?>')
        reply.append('<root>\n<rows>')
        for r in self.__rows:
            reply.append('<row>')
            row_idx = 0
            for x in self.__table_def:
                reply.append('<%(name)s>%(row)s</%(name)s>' % {'name': x[0],
                 'row': r[row_idx]})
                row_idx += 1

            reply.append('</row>')

        reply.append('</rows>\n</root>')
        return '\n'.join(reply)

    def __Column(self, columns):
        temp = []
        if not columns or not isinstance(columns, (list, tuple)):
            raise DataTableException('Table definition is wrong!')
        for h in self.__table_def:
            if len(h) != 4 or h[2] not in self.__allowedColumn:
                raise DataTableException('Table column %s definition is wrong!' % h)
            temp.append("{id:'%s',label:'%s',type:'%s',pattern:'%s'}" % (h[0],
             h[1],
             h[2],
             h[3]))

        return ''.join(['cols:[', ','.join(temp), ']'])

    def __Row(self, row, rownum):
        temp = []
        if not row or not isinstance(row, (list, tuple)) or len(row) != len(self.__table_def):
            raise DataTableException('Table row has problems! %s' % row)
        cidx = 0
        td = self.__table_def
        for r in row:
            typeName = td[cidx][2]
            if typeName == 'boolean':
                if not isinstance(r, bool):
                    raise DataTableException("Row doesn't contain bool '%s'. Line(column): %i(%i)" % (row, cidx, rownum))
                temp.append('{v:%s}' % str(r).lower())
            elif typeName == 'number':
                if isinstance(r, int):
                    temp.append('{v:%i}' % r)
                elif isinstance(r, float):
                    temp.append('{v:%f}' % r)
                else:
                    raise DataTableException("Row doesn't contain int '%s'. Line(column): %i(%i). Value: %s" % (row,
                     cidx,
                     rownum,
                     r))
            elif typeName == 'string':
                temp.append("{v:'%s'}" % str(r))
            elif typeName == 'date':
                if not isinstance(r, datetime.date):
                    raise DataTableException("Row doesn't contain date '%s'. Line(column): %i(%i)" % (row, cidx, rownum))
                temp.append('{v:new Date(%(year)s,%(month)s,%(day)s)}' % {'year': r.year,
                 'month': r.month - 1,
                 'day': r.day})
            elif typeName == 'datetime':
                if not isinstance(r, datetime.datetime):
                    raise DataTableException("Row doesn't contain date '%s'. Line(column): %i(%i)" % (row, cidx, rownum))
                temp.append('{v:new Date(%(year)s,%(month)s,%(day)s,%(hour)s,%(minute)s,%(second)s)}' % {'year': r.year,
                 'month': r.month - 1,
                 'day': r.day,
                 'hour': r.hour,
                 'minute': r.minute,
                 'second': r.second})
            elif typeName == 'timeofday':
                if not isinstance(r, datetime.datetime):
                    raise DataTableException("Row doesn't contain date '%s'. Line(column): %i(%i)" % (row, cidx, rownum))
                temp.append('{v:[%(hour)s,%(minute)s,%(second)s]}' % {'year': r.year,
                 'month': r.month - 1,
                 'day': r.day,
                 'hour': r.hour,
                 'minute': r.minute,
                 'second': r.second})
            cidx += 1

        return ''.join(['{c:[', ','.join(temp), ']}'])

    def __Rows(self, rows):
        temp = []
        ridx = 0
        for row in rows:
            temp.append(self.__Row(row, ridx))
            ridx += 1

        return ''.join(['rows:[', ','.join(temp), ']'])

    def __Wrapper(self, data):
        version = "version:'%s'" % self.__version
        reqId = "reqId:'%s'" % self.__tqxdict['reqId'] if self.__tqxdict.has_key('reqId') else ''
        status = "status:'ok'" if len(self.__errors) == 0 else "status:'error'"
        errors = ''.join(['errors:[{', ','.join(self.__errors), '}]']) if len(self.__errors) > 0 else ''
        table = 'table:{%s}' % ''.join(data) if len(self.__errors) == 0 else ''
        return ''.join(['google.visualization.Query.setResponse({', ','.join([version,
          reqId,
          status,
          table if errors == '' else errors]), '});'])

    def __Error(self, error_number, error_message):
        self.__errors.append("{reason:'internal_error',message:'Error in line:%(line)s. Error: %(message)s'}" % {'line': error_number,
         'message': error_message})


exports = {'util.DataTableException': DataTableException,
 'util.DataTableQuery': DataTableQuery,
 'util.DataTable': DataTable}