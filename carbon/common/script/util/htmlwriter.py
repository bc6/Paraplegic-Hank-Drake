import random
import blue
import urllib
import urllib2
import util
import copy
import sys
import macho
from urllib import unquote_plus
import re
import json
from datetime import datetime
import types
import functools
import iocp
reserved = {';': '%3B',
 '/': '%2F',
 '?': '%3F',
 ':': '%3A',
 '@': '%40',
 '&': '%26',
 '=': '%3D',
 '+': '%2B',
 '$': '%24',
 ',': '%2C',
 ' ': '%20',
 '#': '%23'}

def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]


    return rx.sub(one_xlat, text)



def multiple_replacer(adict):
    rx = re.compile('|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]



    def replacer(text):
        return rx.sub(one_xlat, text)


    return replacer


Swing = multiple_replacer({'&': '&amp;',
 '<': '&lt;',
 '>': '&gt;'})

def Canonicalize(text):
    text = text.replace('%', '%25')
    for (k, v,) in reserved.iteritems():
        text = text.replace(k, v)

    return text



def HTMLEncode(text):
    t = ''
    for i in range(len(text)):
        tord = ord(text[i])
        if tord == 38:
            testStr = text[(i + 1):(i + text[i:].find(';'))]
            if testStr in ('quot', 'amp', 'lt', 'gt'):
                t = t + text[i]
                continue
        if tord == 34:
            t = t + '&quot;'
        elif tord == 38:
            t = t + '&amp;'
        elif tord == 60:
            t = t + '&lt;'
        elif tord == 62:
            t = t + '&gt;'
        else:
            t = t + text[i]

    return t



def Link(url, title, args = None, props = '', target = None, bolConfirm = 0):
    if title is None:
        return ''
    else:
        if bolConfirm:
            onClick = ' onClick="return confirm(\'Are you sure?\')"'
        else:
            onClick = ''
        if args:
            realArgs = args
            if type(args) == type([]):
                realArgs = {}
                for a in args:
                    realArgs.update(a)

            stuff = url.split('#')
            if len(stuff) > 1:
                url = stuff[0]
            url += '?'
            for (k, v,) in realArgs.iteritems():
                if type(v) == type([]):
                    for i in v:
                        url += unicode(k) + '=' + unicode(i) + '&'

                else:
                    url += unicode(k) + '=' + Canonicalize(unicode(v)) + '&'

            if len(stuff) > 1:
                url += '#' + stuff[1]
        if '&' in url:
            url = url.replace('&', '&amp;')
        if iocp.UsingHTTPS():
            url = ConvertLinkForHTTPS(url)
        if target:
            return '<a href="%s" %s target="%s"%s>%s</a>' % (url,
             props,
             target,
             onClick,
             title)
        return '<a href="%s" %s%s>%s</a>' % (url,
         props,
         onClick,
         title)



def Button(url, title, args = None, color = 'black', bolConfirm = 0):
    props = 'class="button button%s"' % color
    return Link(url, title, args, props, None, bolConfirm)



def ConvertLinkForHTTPS(url):
    if url.startswith('http://'):
        host = url[7:].split('/', 1)[0]
        if ':' in host:
            tcpProxy = sm.services.get('tcpRawProxyService', None)
            if tcpProxy:
                tunnels = tcpProxy.GetTunnelsByType('esp')
                if host in (tunnelHost for (name, port, tunnelHost,) in tunnels):
                    return url.replace('http://', 'https://')
                (ourHostIP, tundict,) = tcpProxy.GetESPTunnelingAddressByNodeID()
                potentialTunnelingAddresses = (ourHostIP + ':' + str(port) for port in tundict.itervalues())
                if host in potentialTunnelingAddresses:
                    return url.replace('http://', 'https://')
            machoNet = sm.GetService('machoNet')
            socket = machoNet.GetTransport('tcp:raw:http')
            espAddress = socket.address
            if host == espAddress:
                return url.replace('http://', 'https://')
    return url



def Image(url, props = 'border=0'):
    return '<img src="%s" %s />' % (url, props)



def Table(headers, lines, props = 'border=0', rowprops = 'valign=top'):
    tbl = ''
    tbl = tbl + '<table %s>\n' % (props,)
    if len(headers):
        tbl = tbl + '<tr>'
        for i in headers:
            tbl = tbl + '<td><b>%s</b></td>' % (i,)

        tbl = tbl + '</tr>\n'
    for row in lines:
        tbl = tbl + '<tr>'
        for col in row:
            tbl = tbl + '<td %s>%s</td>' % (rowprops, col)

        tbl = tbl + '</tr>\n'

    tbl = tbl + '</table>\n'
    return tbl



class UnicodeMemStream(object):
    __slots__ = ['ms']

    def __init__(self):
        self.ms = blue.MemStream()



    def Write(self, s):
        u = unicode(s)
        b = buffer(u)
        self.ms.Write(b)



    def Read(self):
        return self.ms.Read().decode('utf-16')



    def getpos(self):
        return self.ms.pos / 2



    def getsize(self):
        return self.ms.size / 2


    size = property(getsize)
    pos = property(getpos)

    def Seek(self, x):
        self.ms.Seek(2 * x)




def JsonFunction(func):

    @functools.wraps(func)
    def Wrapper(*args, **kwargs):
        args[0].Write(json.dumps(func(*args, **kwargs)))


    return Wrapper



def OutlineDictTable(lines):
    s = UnicodeMemStream()
    s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
    s.Write('<tr>\n')
    s.Write('<td class="tableOutline" valign="top">\n')
    s.Write('<table border="0" cellpadding="7" cellspacing="1" width="100%">\n')
    s.Write('<tr>\n')
    s.Write('<tr>\n')
    headers = []
    if len(lines) == 0:
        headers = lines.iterkeys()
    else:
        headers = lines[0].iterkeys()
    for i in headers:
        s.Write('    <td class="tableHeader"><b>%s</b></td>\n' % header)

    s.Write('</tr>\n')
    for i in lines:
        for row in i.itervalues():
            s.Write('<tr>\n')
            for col in row:
                s.Write('    <td class="tC" valign=top>%s</td>\n' % unicode(col))

            s.Write('</tr>\n')


    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Write('</td>\n')
    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Seek(0)
    return s.Read()



def SortOSST(i, a, b):
    try:
        ai = long(a[i])
        bi = long(b[i])
        return [1, -1][(ai < bi)]
    except:
        sys.exc_clear()
        return [1, -1][(a[i].lower() < b[i].lower())]



def OutlineSortedSegmentedTable(lname, ldict, hd, li, idstr, idx, num, displayNameIDX = None, firstIDX = 0, firstNUM = None):
    li.sort(lambda a, b, d = displayNameIDX: SortOSST(d, a, b))
    return OutlineSegmentedTable(lname, ldict, hd, li, idstr, idx, num, displayNameIDX, firstIDX, firstNUM)



def OutlineSegmentedTable(lname, ldict, hd, li, idstr, idx, num, displayNameIDX = None, firstIDX = 0, firstNUM = None):
    nTotal = len(li)
    if firstNUM is None:
        if nTotal > 10000:
            firstNUM = 1000
        elif nTotal > 1000:
            firstNUM = 250
        elif nTotal > 500:
            firstNUM = 100
        elif nTotal > 250:
            firstNUM = 50
        elif nTotal > 100:
            firstNUM = 25
        else:
            firstNUM = 10
    segmentIDstring = Swing(lname + '/' + ldict['action'] + '/' + str(hd))
    if idx is not None and idstr == segmentIDstring:
        session.SetSessionVariable(segmentIDstring + '.idx', idx)
    else:
        idx = firstIDX
    if num is not None and idstr == segmentIDstring:
        session.SetSessionVariable(segmentIDstring + '.num', num)
    else:
        num = firstNUM
    if displayNameIDX is not None and idstr == segmentIDstring:
        session.SetSessionVariable(segmentIDstring + '.what', displayNameIDX)
    elif displayNameIDX is None:
        displayNameIDX = 0
    (nStart, nCount, nWhat,) = (session.GetSessionVariable(segmentIDstring + '.idx', firstIDX), session.GetSessionVariable(segmentIDstring + '.num', firstNUM), session.GetSessionVariable(segmentIDstring + '.what', displayNameIDX))
    if li and nWhat >= len(li[0]):
        nWhat = len(li[0]) - 1
    elif nWhat < 0:
        nWhat = 0
    l = ''
    ldict = copy.deepcopy(ldict)
    ldict['segmentedTableID'] = segmentIDstring
    ldict['segmentedTableNUM'] = nCount
    ldict['segmentedTableWHAT'] = nWhat
    for i in range(0, nTotal, nCount):
        if nStart < i or nStart >= i + nCount:
            ldict['segmentedTableIDX'] = i
            t = i + nCount - 1
            if t >= len(li):
                t = len(li) - 1
            l += Link(lname, Swing(str(li[i][nWhat])) + '..' + Swing(str(li[t][nWhat])), ldict) + '&nbsp;&nbsp;&nbsp;'

    li = li[nStart:(nStart + nCount)]
    ldict['segmentedTableIDX'] = nStart
    for i in range(len(hd)):
        if i != nWhat:
            ldict['segmentedTableWHAT'] = i
            hd[i] = Link(lname, hd[i], ldict)

    if l:
        if li:
            current = '<br>Now viewing: ' + Swing(str(li[0][nWhat])) + '..' + Swing(str(li[-1][nWhat]))
        else:
            current = ''
        selected = '<br>Select: ' + l + '<br>'
        return GetTable(hd, li) + current + selected
    else:
        return GetTable(hd, li)



def GetA(innerText, href, ctrlID = None, className = None, style = None, onClick = None, title = None, rel = None, rev = None):
    ctrlID = CheckValue('id', ctrlID)
    className = CheckValue('class', className)
    style = CheckValue('style', style)
    onClick = CheckValue('onclick', onClick)
    title = CheckValue('title', title)
    rel = CheckValue('rel', rel)
    rev = CheckValue('rev', rev)
    return '<a href="%s"%s%s%s%s%s%s%s>%s</a>' % (href,
     ctrlID,
     className,
     style,
     onClick,
     title,
     rel,
     rev,
     innerText)



def GetTable(header = None, lines = None, className = 'tablesorter', enableEdit = False, editUrl = None, enableDelete = False, deleteUrl = None, useFilter = False, invertSelection = False, paging = None, customActions = None, serverOrder = False, baseUrl = None, keyFields = None, readOnlyFields = None, showCount = True):
    elementSep = '<span class="toolbar-separator">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
    customActions2 = []
    if customActions is not None:
        for ca in customActions:
            customActions2.append('&nbsp;' * 5)
            customActions2.append(ca)

    if keyFields is None:
        keyFields = []
    if readOnlyFields is None:
        readOnlyFields = []
    className = CheckValue('class', className)
    res = UnicodeMemStream()
    r = random.randint(1, 1000)
    id = 'table_%i' % r
    headerIndexControl = []
    xLoop = 0
    for x in header:
        if '<' in unicode(x):
            headerIndexControl.append(xLoop)
        xLoop += 1

    if enableDelete or enableEdit:
        headerIndexControl.append(len(header))
    res.Write('\n    <script type="text/javascript">\n        $(document).ready(function() {\n            $("#%s").tablesorter(' % id)
    if header is not None and serverOrder is True:
        res.Write('{\n                headers: {')
        t_res = []
        for n in xrange(len(header)):
            t_res.append('%i: {sorter: false}' % n)

        res.Write(', '.join(t_res))
        res.Write('}\n}')
    elif header is not None and len(headerIndexControl) > 0:
        res.Write('{\n                headers: {')
        t_res = []
        for n in headerIndexControl:
            t_res.append('%i: {sorter: false}' % n)

        res.Write(', '.join(t_res))
        res.Write('}\n}')
    res.Write(');\n    });\n    </script>')
    ctrlID = ' id="%s"' % id
    invertText = '<li><a class="csp-invert button buttongray">Invert</a></li>' if invertSelection else ''
    filterBar = '\n        <div class="csp-tool-strip">\n            <a class="button buttongray excel" onclick="exportToExcel(\'%(ctrlID)s\');">Excel</a>\n            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n            <input type="text" size="25" maxlength="30" value="" id="filter_%(ctrlID)s" name="filter_%(ctrlID)s"/>\n        </div>\n    ' % {'ctrlID': id}
    toolbar = '\n        <div class="csp-tool">\n            <div style="float:left;">\n                %(leftbar)s\n            </div>\n            <div style="float:right;">\n                <div class="csp-tool-strip">\n                    <ul>\n                        %(customActions)s\n                        %(sep1)s\n                        %(paging)s\n                        %(sep2)s\n                        %(invert)s\n                    </ul>\n                </div>\n            </div>\n            <div style="clear:both;"></div>\n        </div>\n        '
    res.Write('<div>')
    res.Write('\n        <script type="text/javascript">\n            $(function() {\n                var $%(ctrlID)s = $("#%(ctrlID)s")\n                $("#filter_%(ctrlID)s").keyup(function() {\n                  $.uiTableFilter( $%(ctrlID)s, this.value );\n                });\n                $(".csp-invert").click(function(){\n                    $.each($("#%(ctrlID)s input").not(":disabled"), function(idx,val) {\n                        if ($(val).is(":visible")) {\n                            val.checked = !val.checked;\n                        }\n                    });\n                });\n            });\n        </script>\n    ' % {'ctrlID': id})
    if useFilter or paging is not None or len(customActions2) > 0:
        res.Write(toolbar % {'leftbar': filterBar if useFilter else '',
         'invert': invertText,
         'paging': '' if paging is None else '<li>%s</li>' % paging,
         'customActions': u''.join([ u'<li>%s</li>' % x for x in customActions2 ]),
         'sep1': '' if paging is None else '<li>%s</li>' % elementSep,
         'sep2': '<li>%s</li>' % elementSep if len(invertText) > 0 else ''})
    res.Write('<table %(className)s%(ctrlID)s>' % {'className': className,
     'ctrlID': ctrlID})
    columnRules = []
    if header:
        res.Write('<thead><tr>')
        h_idx = 0
        for h in header:
            th_style = ''
            w = 0
            columnRules.append('')
            if isinstance(h, list):
                if isinstance(h[1], list):
                    w = h[1][0]
                    if len(h[1]) > 1:
                        columnRules[h_idx] = h[1][1]
                elif isinstance(h[1], str):
                    columnRules[h_idx] = h[1]
                elif isinstance(h[1], int):
                    w = h[1]
                th_style = ' style="width: %spx"' % w if w > 0 else ''
                h = h[0]
            if keyFields is not None and h in keyFields:
                k = ' class="csp-table-key"'
            elif readOnlyFields is not None and h in readOnlyFields:
                k = ' class="csp-table-readonly"'
            else:
                k = ''
            if serverOrder is True:
                res.Write('<th%s%s>%s</a></th>' % (k, th_style, GetA(h, '%s&sortcolumn=%i' % (baseUrl, h_idx))))
            else:
                res.Write('<th%s>%s</a></th>' % (th_style, h))
            h_idx += 1

        if enableEdit or enableDelete:
            res.Write('<th></th>')
        res.Write('</tr></thead>')
    if lines:
        for r in lines:
            blue.pyos.BeNice()
            res.Write('<tr>')
            lnr = 0
            for c in r:
                td_style = ''
                if len(columnRules) and len(columnRules) < lnr:
                    td_style = ' class="csp-%s"' % columnRules[lnr]
                res.Write('<td%s>' % td_style)
                if len(columnRules) and len(columnRules) < lnr and columnRules[lnr] in ('number', 'numberleft'):
                    res.Write(AddThousandSeparator(c))
                else:
                    res.Write(c)
                res.Write('</td>')
                lnr += 1

            if enableEdit or enableDelete:
                actions = []
                if enableEdit:
                    actions.append(GetA('Edit', href='#', className='edit-row', rev=editUrl))
                if enableDelete:
                    actions.append(GetA('Delete', href='#', className='delete-row', rev=deleteUrl))
                res.Write('<td>%s</td>' % '&nbsp;|&nbsp;'.join(actions))
            res.Write('</tr>')

    else:
        res.Write('<tr>')
        for h in header:
            res.Write('<td></td>')

        res.Write('</tr>')
    res.Write('</table>')
    if len(lines) > 30:
        if useFilter or paging is not None or len(customActions2) > 0:
            res.Write(toolbar % {'leftbar': '%i rows' % len(lines) if showCount else '',
             'invert': invertText,
             'paging': '' if paging is None else '<li>%s</li>' % paging,
             'customActions': u''.join([ u'<li>%s</li>' % x for x in customActions2 ]),
             'sep1': '' if paging is None else '<li>%s</li>' % elementSep,
             'sep2': '<li>%s</li>' % elementSep if len(invertText) > 0 else ''})
        else:
            res.Write('<div>%i rows</div>' % len(lines))
    elif showCount and len(lines) > 5:
        res.Write('<div>%i rows</div>' % len(lines))
    res.Write('</div>')
    res.Seek(0)
    return res.Read()



def OutlineTable(headers, lines, opLink = '', opAct = '', opWidth = None, opHeadClass = 'tableHeader', nobreak = 0, opColClass = None, opHeaderArgs = None, opTDArgs = None):
    tableStyle = ''
    for headerValue in headers:
        if isinstance(headerValue, list) or isinstance(headerValue, tuple):
            tableStyle = "STYLE='table-layout:fixed'"
            break

    s = UnicodeMemStream()
    if opWidth is not None:
        if opWidth != '':
            opWidth = 'width="%s"' % opWidth
        s.Write('<table border="0" cellpadding="0" cellspacing="0" %s %s>\n' % (opWidth, tableStyle))
    else:
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%%" %s>\n' % tableStyle)
    s.Write('<tr>\n')
    s.Write('<td class="tableOutline" valign="top">\n')
    s.Write('<table border="0" cellpadding="7" cellspacing="0" width="100%%" %s>\n' % tableStyle)
    if len(headers):
        s.Write('<tr>\n')
        for (headerIndex, headerValue,) in enumerate(headers):
            headerTDArgs = ''
            if opHeaderArgs is not None and headerIndex in opHeaderArgs:
                headerTDArgs = ' '.join([ '%s="%s"' % (attribute, value) for (attribute, value,) in opHeaderArgs[headerIndex] ])
            if isinstance(headerValue, list) or isinstance(headerValue, tuple):
                (headerLabel, width,) = headerValue
                s.Write('    <td width=%d class="%s"%s>%s</td>\n' % (width,
                 opHeadClass,
                 headerTDArgs,
                 headerLabel))
            else:
                s.Write('    <td class="%s"%s>%s</td>\n' % (opHeadClass, headerTDArgs, headerValue))

        s.Write('</tr>\n')
    c = 1
    for (rowIndex, rowValue,) in enumerate(lines):
        if len(rowValue) == 1 and unicode(rowValue[0]).lower().find('<tr') == 0:
            s.Write(rowValue[0] + '\n')
            continue
        klass = 'class="tC"'
        if c:
            c = 0
        else:
            klass = 'class="tCO"'
            c = 1
        if opColClass:
            klass = 'class="%s"' % opColClass
        s.Write('<tr>\n')
        for (colIndex, colValue,) in enumerate(rowValue):
            tdArgs = ''
            if opTDArgs is not None and (rowIndex, colIndex) in opTDArgs:
                tdArgs = ' '.join([ '%s="%s"' % (attribute, value) for (attribute, value,) in opTDArgs[(rowIndex, colIndex)] ])
            if colValue == rowValue[0] and opLink != '':
                link = opLink % (colValue, colValue)
                s.Write('<td %s%s>%s</td>\n' % (klass, tdArgs, link))
                continue
            s.Write('<td %s%s>' % (klass, tdArgs))
            if nobreak:
                s.Write('<nobr>')
            s.Write(colValue)
            if nobreak:
                s.Write('</nobr>')
            s.Write('</td>\n')

        s.Write('</tr>\n')

    s.Write('</table>\n')
    s.Write('</td>\n')
    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Seek(0)
    return s.Read()



def OutlinePropertyTable(keyvaldict, header = None):
    s = UnicodeMemStream()
    s.Write('<table border="0" cellpadding="0" cellspacing="0">\n')
    s.Write('<tr>\n')
    s.Write('<td class="tableOutline" valign="top">\n')
    s.Write('<table border="0" cellpadding="7" cellspacing="1">\n')
    s.Write('<tr>\n')
    it = keyvaldict.items()
    if header and len(header):
        s.Write('<tr>')
        for i in header:
            s.Write('<td ')
            if len(header) == 1:
                s.Write('colspan = 2 ')
            s.Write('class="tableHeader"><b>%s</b></td>\n' % (i,))

        s.Write('</tr>\n')
    for i in it:
        s.Write('<tr>\n')
        s.Write('<td class="tC"><b>%s</b></td>\n' % i[0])
        s.Write('<td class="tC">%s</td>\n' % i[1])
        s.Write('</tr>\n')

    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Write('</td>\n')
    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Seek(0)
    return s.Read()



def OutlineKeyValTable(keyval):
    s = UnicodeMemStream()
    s.Write('<table border="0" cellpadding="0" cellspacing="0">\n')
    s.Write('<tr>\n')
    s.Write('<td class="tableOutline" valign="top">\n')
    s.Write('<table border="0" cellpadding="7" cellspacing="1">\n')
    s.Write('<tr>\n')
    for i in keyval:
        s.Write('<tr>\n')
        s.Write('<td class="tC" valign=top><b>%s</b></td>\n' % unicode(i[0]))
        s.Write('<td class="tC" valign=top>%s</td>\n' % unicode(i[1]))
        s.Write('</tr>\n')

    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Write('</td>\n')
    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Seek(0)
    return s.Read()



def BarChart(name = '', data = {}, width = 500, height = 500):
    Tot = 0
    Max = 0
    sortedDataKeys = data.keys()
    sortedDataKeys.sort()
    for k in sortedDataKeys:
        Tot = Tot + data[k]
        if data[k] > Max:
            Max = data[k]

    strHTML = '\n\n<table border=0 cellspacing=2 width="100%%">\n'
    for k in sortedDataKeys:
        strHTML = strHTML + '<tr><td width="50"><b>%s</b><br>%s times</td><td><table height="100%%"  Width="%s%%" border=0 cellpadding=0 bgcolor="#6699cc"><tr><td>&nbsp;</td></tr></table></td></tr>\n' % (k, data[k], int(float(data[k]) / float(Tot) * 100))

    strHTML = strHTML + '</table>'
    return strHTML



def HtmlFormatStack(stack):
    ret = ''
    for each in stack:
        ret += Swing(each) + '<br>'

    return ret



def BrowserCheck(browser):
    valids = ['MSIE 6.0', 'MSIE 5.5']
    ret = 0
    for valid in valids:
        if browser.find(valid) > 0:
            ret = 1

    return ret



def WebPart(title, content, ID = '4', width = '100%', headerClass = '', bodyClass = ''):
    s = UnicodeMemStream()
    s.Write('<table class=WebPartTable cellpadding="0" cellspacing="0" width="' + str(width) + '" border="0" id="' + str(ID) + '">\n')
    s.Write('<tr>\n')
    s.Write('    <td valign="middle" align="left" class="WebPartHeader %s">\n' % headerClass)
    s.Write('    ' + title + '\n')
    s.Write('    </td>\n')
    s.Write('</tr>\n')
    s.Write('<tr>\n')
    s.Write('    <td>\n')
    s.Write('    <table bgcolor="#ffffff" width="100%" cellpadding="0" cellspacing="0" border="0">\n')
    s.Write('    <tr>\n')
    s.Write('        <td valign="top" class="WebPartContent %s">\n' % bodyClass)
    s.Write(content)
    s.Write('        </td>\n')
    s.Write('     </tr>\n')
    s.Write('     </table>\n')
    s.Write('     </td>\n')
    s.Write('</tr>\n')
    s.Write('</table>\n')
    s.Seek(0)
    return s.Read()



def GetFrameOf(what):
    import stackless
    first = stackless.getcurrent()
    if type(what) == type(stackless.getcurrent().frame):
        return what
    current = first
    f = None
    while 1:
        q = current.frame
        while 1:
            if q is not None and not hasattr(q, 'f_locals'):
                q = None
            if q is None:
                break
            if q.f_locals is what:
                return q
            for each in q.f_locals:
                if each is what:
                    return q

            q = q.f_back

        current = current.next
        if current == first:
            break




def FrameIsCallingFrame(f, current = None):
    import stackless
    if current is None:
        current = stackless.getcurrent().frame
    while 1:
        if f is current:
            return 1
        if current.f_back is None or not hasattr(current.f_back, 'f_locals'):
            if f is not None:
                f = f.f_back
            if f is not None and hasattr(f, 'f_locals'):
                return FrameIsCallingFrame(f, current)
            return 0
        current = current.f_back




def Kapling(s):
    s = Swing(s)
    if len(s) > 500:
        s = 'huge mofu (%d)' % len(s) + s[:500]
    return s



def GetXyzzyReferrerInfo(each, inst):
    ok = '<b>' + Kapling(str(type(each))) + '</b>:  ' + Kapling(str(each))
    done = 0
    if type(each) == type({}):
        for yetanother in inst:
            if yetanother.__dict__ is each:
                done = 1
                ok += '<br><b>This ref is owned by this object: ' + Kapling(str(yetanother)) + '</b>'
                break
            for (k, attr,) in yetanother.__dict__.iteritems():
                if attr is each:
                    ok += '<br><b>This ref is ' + Kapling(str(yetanother)) + '.' + k + '</b>'
                    done = 1
                elif type(attr) in (types.TupleType, types.ListType):
                    for i in attr:
                        if i is each:
                            ok += '<br><b>This ref is contained in ' + Kapling(str(yetanother)) + '.' + k + '</b>'
                            done = 1

                elif type(attr) == types.DictType:
                    for i in attr.itervalues():
                        if i is each:
                            ok += '<br><b>This ref is contained in ' + Kapling(str(yetanother)) + '.' + k + '</b>'
                            done = 1



    return (ok, done)



def GetXyzzyReferrers(s, inst = None):
    import stackless
    import traceback
    import gc
    import sys
    ok = ''
    gc.collect()
    referrers = gc.get_referrers(s)
    if inst is None:
        inst = [ o for o in gc.get_objects() if type(o) is types.InstanceType ]
    for each in referrers:
        f = GetFrameOf(each)
        ok += '<br>'
        if FrameIsCallingFrame(f):
            ok += '<br><b>It looks like this ref might belong to this web page:</b>'
        if f is not None:
            ok += '<br><b>Frame: ' + Kapling(str(f)) + '</b>'
            for other in traceback.extract_stack(f, 40):
                ok += '<br>' + Kapling(str(other))

        (ri, done,) = GetXyzzyReferrerInfo(each, inst)
        ok += ri

    gc.collect()
    return ok



def Convert(var):
    try:
        return int(var)
    except:
        sys.exc_clear()
        try:
            return long(var)
        except:
            sys.exc_clear()
            try:
                return float(var)
            except:
                sys.exc_clear()
                if var == 'None':
                    return None
                else:
                    return var



def Pythonize(var):
    if type(var) == type([]):
        ret = []
        for i in var:
            ret.append(Convert(i))

        return ret
    return Convert(var)



def Decanonicalize(text):
    ix = 0
    text = text.replace('+', ' ')
    ret = ''
    while 1:
        newix = text.find('%', ix)
        if newix == -1:
            break
        ret = ret + text[ix:newix]
        ix = newix
        (h2, h1,) = text[(ix + 1):(ix + 3)]
        ch = 0
        if h1 >= '0' and h1 <= '9':
            ch = ord(h1) - ord('0')
        else:
            ch = ord(h1) - ord('A') + 10
        if h2 >= '0' and h2 <= '9':
            ch = ch + (ord(h2) - ord('0')) * 16
        else:
            ch = ch + (ord(h2) - ord('A') + 10) * 16
        ret = ret + chr(ch)
        ix = ix + 3

    return ret + text[ix:]



def SplitArgs(args, dest = None):
    args = str(args)
    if dest is None:
        dest = {}
    arg = args.split('&')
    for i in arg:
        kv = i.split('=', 1)
        if len(kv) == 2:
            s = unquote_plus(kv[1])
            if dest.has_key(kv[0]):
                if type(dest[kv[0]]) != type([]):
                    dest[kv[0]] = [dest[kv[0]]]
                dest[kv[0]].append(s)
            else:
                dest[kv[0]] = s
        else:
            dest[i] = ''

    return dest



def SplitMIMEArgs(fields, dest = None):
    if dest is None:
        dest = {}
    for field in fields.list:
        if dest.has_key(field.name):
            if type(dest[field.name]) != type([]):
                dest[field.name] = [dest[field.name]]
            if field.type != 'text/plain':
                dest[field.name].append(field.value)
            else:
                dest[field.name].append(unquote_plus(field.value))
        elif field.type != 'text/plain':
            dest[field.name] = field.value
        else:
            dest[field.name] = urllib2.unquote(field.value)

    return dest



def PythonizeArgs(args):
    dest = SplitArgs(str(args))
    for (k, v,) in dest.iteritems():
        dest[k] = Pythonize(v)

    return dest



def PackModalDialogueResult(result):
    r = ''
    for (k, v,) in result.iteritems():
        r += str(k) + '=' + str(v) + '&'

    r = r[:-1]
    return r



def UnpackModalDialogueResult(result):
    ret = {}
    if result:
        for each in result.split('&'):
            (k, v,) = each.split('=')
            v = Pythonize(v)
            if k in ret:
                if type(ret[k]) != types.ListType:
                    ret[k] = [ret[k]]
                ret[k].append(v)
            else:
                ret[k] = v

    return ret



def AddThousandSeparator(s):
    res = []
    for (i, c,) in enumerate(reversed(str(s))):
        if i and not i % 3:
            res.insert(0, '.')
        res.insert(0, c)

    return ''.join(res)


CheckValue = lambda id, idValue: (' %s="%s"' % (id, idValue) if idValue is not None and idValue is not '' else '')
exports = {'htmlwriter.UnpackModalDialogueResult': UnpackModalDialogueResult,
 'htmlwriter.PackModalDialogueResult': PackModalDialogueResult,
 'htmlwriter.Pythonize': Pythonize,
 'htmlwriter.Swing': Swing,
 'htmlwriter.MultipleReplacer': multiple_replacer,
 'htmlwriter.Canonicalize': Canonicalize,
 'htmlwriter.Decanonicalize': Decanonicalize,
 'htmlwriter.HTMLEncode': HTMLEncode,
 'htmlwriter.Link': Link,
 'htmlwriter.Button': Button,
 'htmlwriter.Image': Image,
 'htmlwriter.Table': Table,
 'htmlwriter.OutlineDictTable': OutlineDictTable,
 'htmlwriter.GetA': GetA,
 'htmlwriter.GetTable': GetTable,
 'htmlwriter.OutlineTable': OutlineTable,
 'htmlwriter.OutlinePropertyTable': OutlinePropertyTable,
 'htmlwriter.OutlineKeyValTable': OutlineKeyValTable,
 'htmlwriter.BarChart': BarChart,
 'htmlwriter.BrowserCheck': BrowserCheck,
 'htmlwriter.WebPart': WebPart,
 'htmlwriter.HtmlFormatStack': HtmlFormatStack,
 'htmlwriter.GetFrameOf': GetFrameOf,
 'htmlwriter.GetXyzzyReferrers': GetXyzzyReferrers,
 'htmlwriter.SplitArgs': SplitArgs,
 'htmlwriter.SplitMIMEArgs': SplitMIMEArgs,
 'htmlwriter.PythonizeArgs': PythonizeArgs,
 'htmlwriter.UnicodeMemStream': UnicodeMemStream,
 'htmlwriter.JsonFunction': JsonFunction}

class HtmlWriter():
    __guid__ = 'htmlwriter.HtmlWriter'

    def __init__(self, template = 'script:/wwwroot/lib/template/emptybase.html'):
        self.baseTemplate = template
        self.Clear()
        from base import GetServiceSession
        self.session = GetServiceSession('HtmlWriter')
        self.ajaxDefaultURL = None



    def EspIcon(self, filename = 'none.gif', size = 32):
        iconUrl = '/img/' + filename
        return self.Image(iconUrl, 'width=%s height=%s border=0 align=absmiddle' % (size, size))



    def Clear(self):
        self.redirect = 'mainhtml'
        self.inserts = {}
        self.visualization = []
        self.scripts = []
        self.headjsScripts = []
        self.inserts['title'] = 'HTML Writer Title'
        self.inserts['heading'] = 'HTML Writer Heading'
        self.inserts['icon'] = self.EspIcon('none.gif', 32)
        self.inserts['stylesheet'] = '/lib/std.css'
        self.start = blue.os.GetCycles()[0]
        self.inserts['bottom_left'] = util.FmtDate(blue.os.GetTime())
        self.inserts['navigation'] = ''
        self.inserts['jscript'] = ''
        self.inserts['head'] = ''
        self.inserts['scripts'] = ''
        self.inserts['visualscripts'] = ''
        self.inserts['trackpage'] = ''
        self.inserts['treeMenu'] = ''
        self.inserts['headjs'] = ''
        self.inserts['footer'] = ''
        self.visualcallbacks = []
        self.enabledJscript = set()
        self.current_form_rules = None
        self.bsdSupport = False
        self.prettify = False



    def toJavascriptDict(self, d = {}):
        map_fun = lambda x: ('%s' % x if x.startswith('function') or x.startswith('[') else "'%s'" % x)
        map_outer = lambda x: ('%s: %s' % (x, self.toJavascriptDict(d[x])) if isinstance(d[x], types.DictType) else '%s: %s' % (x, str(d[x]).lower()))
        map_key = lambda x: ('%s: %s' % (x, map_fun(d[x])) if isinstance(d[x], types.StringType) else map_outer(x))
        return ''.join(['{', ', '.join(map(map_key, d.keys())), '}'])



    def Swing(self, text):
        return Swing(text)



    def AddScript(self, src):
        self.scripts.append('<script type="text/javascript" src="%s"></script>' % src)



    def AddHeadScript(self, src):
        self.headjsScripts.append('<script>head.js("%s")</script>' % src)



    def AddCss(self, src):
        self.scripts.append('<link rel="stylesheet" href="%s" type="text/css"/>' % src)



    def AddSyntaxHighlighting(self, element, language = 'python'):
        if not self.prettify:
            self.AddScript('/js/prettify.js')
            self.AddCss('/css/prettify.css')
            self.WriteDirect('jscript', '$(document).ready(function(){ prettyPrint(); });')
            self.prettify = True
        return '<code class="prettyprint lang-%(language)s">%(element)s</code>' % locals()



    def AddVisualJScript(self, package, source):
        self.EnableVisualTool(package=package)
        self.WriteDirect('visualscripts', source)



    def AddVisualQueryJScript(self, package, visualTool, ajax, ctrlID, options = None, query = None, reloadData = None):
        self.EnableVisualTool(package=package)
        temp_reloadData = '\nsetTimeout(doVisual,%i);\n' % reloadData if reloadData is not None else None
        temp_script = []
        temp_script.append("var query_%(ctrlID)s = new google.visualization.Query('%(ajax)s');" % {'ctrlID': ctrlID,
         'ajax': ajax})
        if query is not None:
            temp_script.append("query_%(ctrlID)s.setQuery('%(query)s');" % {'ctrlID': ctrlID,
             'query': query})
        temp_script.append('query_%(ctrlID)s.send(handle%(ctrlID)sResponse);' % {'ctrlID': ctrlID})
        if temp_reloadData:
            temp_script.append(temp_reloadData)
        self.WriteDirect('visualscripts', '\n'.join(temp_script))
        handleResponse = "\n        var visual%(ctrlID)s;\n        function handle%(ctrlID)sResponse(response) {\n            if (response.isError()) {\n                alert('Error in query: '+ response.getMessage() + ' ' + response.getDetailedMessage());\n            }\n            var data = response.getDataTable();\n            if (!visual%(ctrlID)s) {\n                visual%(ctrlID)s = new google.visualization.%(visualTool)s(document.getElementById('%(ctrlID)s'));\n            }\n            visual%(ctrlID)s.draw(data, %(opt)s);\n            try {\n                if (graphLoaded) {\n                    graphLoaded();\n                }\n            }\n            catch(e) {}\n        }\n        " % {'ctrlID': ctrlID,
         'visualTool': visualTool,
         'opt': 'null' if options is None else self.toJavascriptDict(d=options)}
        self.visualcallbacks.append(handleResponse)



    def FormatDate(self, dateString):
        if dateString is not None:
            date_part = [ int(x) for x in dateString.split('.') ]
            return blue.os.GetTimeFromParts(date_part[0], date_part[1], date_part[2], 0, 0, 0, 0)



    def GetExcelWebQuery(self, q, label):
        url = 'http://%s:%s%s' % (self.request.Host()[0], self.request.Host()[1], q)
        return self.GetA(innerText=label, href='/info/iqy.py?q=%s' % url)



    def EnableVisualTool(self, package):
        allowedTools = ['annotatedtimeline',
         'areachart',
         'barchart',
         'columnchart',
         'corechart',
         'gauge',
         'geomap',
         'imageareachart',
         'imagebarchart',
         'imagechart',
         'imagelinechart',
         'imagepiechart',
         'imagesparkline',
         'intensitymap',
         'linechart',
         'map',
         'motionchart',
         'orgchart',
         'piechart',
         'scatterchart',
         'table',
         'treemap']
        if package not in allowedTools:
            raise Exception("The tool '%s' isn't allowed. Allowed tools are %s" % (package, allowedTools))
        if package not in self.visualization:
            self.visualization.append(package)



    def EnableResizable(self, ctrlID):
        jscript = '\n    <SCRIPT type=text/javascript>\n        $(function() {\n            $("#%(ctrlID)s").resizable({\n                handles: "se" });\n        });\n        </SCRIPT>' % {'ctrlID': ctrlID}
        self.WriteDirect('jscript', jscript)



    def EnableFormValidation(self, formID):
        jscript = '\n    $(document).ready(function() {\n        $("#%(formID)s").validate(%(formrules)s);\n    });\n        ' % {'formID': formID,
         'formrules': '' if self.current_form_rules is None else '{rules: %s}' % self.current_form_rules}
        self.WriteDirect('jscript', jscript)



    def EnableFormRules(self, rules = {}):
        self.current_form_rules = self.toJavascriptDict(rules)



    def EnableTextEditor(self, ctrlID):
        jscript = '\n        <script type="text/javascript">\n        $(function() {\n            $("#%(ctrlID)s").htmlarea();\n        })            \n        </script>\n        ' % {'ctrlID': ctrlID}
        self.Write(jscript)



    def EnableAccordion(self, ctrlID):
        jscript = '\n    $(function() {\n        $("#%(ctrlID)s").accordion();\n    });\n        ' % {'ctrlID': ctrlID}
        self.WriteDirect('jscript', jscript)



    def EnableChar(self):
        jscript = 'var api = new jGCharts.Api();\n'
        self.WriteDirect('jscript', jscript)



    def __EnableTabs(self, tabsID):
        jscript = '\n    <script type="text/javascript">\n    $(function() {\n        $("#%(tabsID)s").tabs({\n            select: function(event, ui) {\n                window.location = "#"+ui.index\n            },\n            spinner: \'Retrieving data\'\n        });\n    });\n    $(function() {\n        var loc = window.location.toString().split("#");\n        if (loc.length == 2) {\n            $("#%(tabsID)s").tabs("option", "selected", parseInt(loc[1]));\n        }\n    });\n    </script>\n        ' % {'tabsID': tabsID}
        self.Write(jscript)



    def __GetElementBegin(self, elementName, attributes):
        return '<%s%s>' % (elementName, attributes)



    def __GetElementEnd(self, elementName):
        return '</%s>' % elementName



    def __GetElement(self, ctrlName, ctrlValue, ctrlID = None, className = None, style = None):
        controlID = CheckValue('id', ctrlID)
        controlName = CheckValue('id', ctrlID)
        className = CheckValue('class', className)
        style = CheckValue('style', style)
        return '\n'.join([self._HtmlWriter__GetElementBegin(ctrlName, '%s%s%s%s' % (controlID,
          controlName,
          className,
          style)), ctrlValue, self._HtmlWriter__GetElementEnd(ctrlName)])



    def __GetElements(self, elements = None, ctrlName = 'div', ctrlID = None, className = None, style = None, title = None, dataBind = None):
        ctrlID = CheckValue('id', ctrlID)
        className = CheckValue('class', className)
        style = CheckValue('style', style)
        title = CheckValue('title', title)
        dataBind = CheckValue('data-bind', dataBind)
        res = UnicodeMemStream()
        res.Write(self._HtmlWriter__GetElementBegin(ctrlName, '%s%s%s%s%s' % (ctrlID,
         className,
         style,
         title,
         dataBind)))
        if isinstance(elements, list):
            if elements and len(elements) > 0:
                for n in elements:
                    res.Write(unicode(n))

        elif elements is not None:
            res.Write(unicode(elements))
        res.Write(self._HtmlWriter__GetElementEnd(ctrlName))
        res.Seek(0)
        return res.Read()



    def GetStyleButton(self, href, innerText, cssClass = 'buttonblack'):
        res = UnicodeMemStream()
        if cssClass is not None:
            cssClass = ' %s' % cssClass
        res.Write('<a href="%s" class="button %s">' % (href, cssClass))
        res.Write(innerText)
        res.Write('</a>')
        res.Seek(0)
        return res.Read()



    def GetImage(self, src, ctrlID = None, className = None, style = None, title = None):
        ctrlID = CheckValue('id', ctrlID)
        className = CheckValue('class', className)
        style = CheckValue('style', style)
        title = CheckValue('title', title)
        return '<img src="%s" %s%s%s%s/>' % (src,
         ctrlID,
         className,
         style,
         title)



    def GetMessage(self, heading, label, cssClass):
        return '<div class="message %s"><p><strong>%s</strong>&nbsp;%s</p></div>' % (cssClass, heading, label)



    def GetSuccess(self, label):
        return self.GetMessage('Success!', label, 'success')



    def GetError(self, label):
        return self.GetMessage('Error!', label, 'error')



    def GetWarning(self, label):
        return self.GetMessage('Warning!', label, 'warning')



    def GetTip(self, label):
        return self.GetMessage('Tip!', label, 'tip')



    def GetInlineHeader(self, ctrlID, innerText, rev):
        return '<h3 id="%(ctrlID)s" class="editable" rev="%(rev)s">%(innerText)s</h3>' % {'ctrlID': ctrlID,
         'rev': rev,
         'innerText': innerText}



    def GetInlineArea(self, ctrlID, innerText, rev):
        return '<p id="%(ctrlID)s" class="editable-area" rev="%(rev)s">%(innerText)s</p>' % {'ctrlID': ctrlID,
         'rev': rev,
         'innerText': innerText}



    def GetInlineHelp(self, label, header, body):
        return '<span title="%(header)s|%(body)s">%(label)s</span>' % {'label': label,
         'header': header,
         'body': body}



    def GetInline(self, ctrlID, innerText, rev):
        return '<span id="%(ctrlID)s" class="editable" rev="%(rev)s">%(innerText)s</span>' % {'ctrlID': ctrlID,
         'rev': rev,
         'innerText': innerText}



    def GetForm(self, ctrlID, formMethod, fileName, formAction, elements, multiPart = False):
        self.EnableFormValidation(ctrlID)
        encType = ' enctype="multipart/form-data"' if multiPart else ''
        formAction = '%(fileName)s?action=%(formAction)s' % {'fileName': fileName,
         'formAction': formAction}
        res = []
        res.append(self._HtmlWriter__GetElementBegin('form', ' id="%s" action="%s" method="%s"' % (ctrlID, formAction, formMethod)))
        for n in elements:
            res.append(n)

        res.append(self._HtmlWriter__GetElementEnd('form'))
        return ''.join(res)



    def GetLayoutTable(self, ctrlID = None, rows = []):
        res = UnicodeMemStream()
        ctrlID = CheckValue('id', ctrlID)
        res.Write('<div%s class="csp-table">' % ctrlID)
        for r in rows:
            res.Write('<div class="csp-row">')
            if isinstance(r, list):
                for c in r:
                    res.Write('<div class="csp-cell">%s</div>' % c)

            else:
                res.Write('<div class="csp-cell">%s</div>' % r)
            res.Write('</div>')

        res.Write('</div>')
        res.Seek(0)
        return res.Read()



    def MaxPageNumber(self, current_page, page_size, num_of_records):
        num_of_pages = num_of_records / page_size + (1 if num_of_records % page_size > 0 else 0)
        if current_page > num_of_pages:
            current_page = 1
        return (current_page, num_of_pages)



    def GetPagingNext(self, nextOptions = {}, pageCount = 0, nextEnabled = True):
        if nextEnabled:
            url = urllib.urlencode(nextOptions)
            return self.GetA(innerText='Next %s' % str(pageCount) if pageCount > 0 else '', href='?%s' % url, className='button buttonblue')
        else:
            return self.GetSpan(['Next %s' % str(pageCount) if pageCount > 0 else ''], className='dark-gray')



    def GetPagingFirstNext(self, firstOptions = {}, nextOptions = {}, pageCount = 0, firstEnabled = True, nextEnabled = True):
        action = []
        if firstEnabled:
            url = urllib.urlencode(firstOptions)
            action.append(self.GetA(innerText='First', href='?%s' % url, className='button buttonblue'))
        else:
            action.append(self.GetSpan(['First'], className='dark-gray'))
        if nextEnabled:
            url = urllib.urlencode(nextOptions)
            action.append(self.GetA(innerText='Next %s' % str(pageCount) if pageCount > 0 else '', href='?%s' % url, className='button buttonblue'))
        else:
            action.append(self.GetSpan(['Next %s' % str(pageCount) if pageCount > 0 else ''], className='dark-gray'))
        return ' | '.join(action)



    def GetPaging(self, current_page, page_size, num_of_records, page_sizes):
        res = UnicodeMemStream()
        num_of_pages = num_of_records / page_size + (1 if num_of_records % page_size > 0 else 0)
        if page_size not in [0] + page_sizes:
            page_sizes.append(page_size)
        options = []
        for p in page_sizes:
            options.append('<option value="%(num)i"%(sel)s>%(num)i</option>' % {'num': p,
             'sel': ' selected="selected"' if page_size == p else ''})

        options.append('<option value="0"%(sel)s>All</option>' % ' selected' if page_size is 0 else '')
        res.Write('\n\n        <div class="%(tableid)s">\n            <span class="csp-paging"><img src="/img/ds_first.png" alt="First"/></span>\n            <span class="csp-paging"><img src="/img/ds_previous.png" alt="Previous"/></span>\n            <span class="csp-paging">&nbsp<input id="%(tableid)s_row" type="text" value="%(current_page)i" style="width:15px;"/> <span title="Count: %(pages)i">of %(numofpages)i</span></span>\n            <span class="csp-paging"><img src="/img/ds_next.png" alt="Next"/></span>\n            <span class="csp-paging"><img src="/img/ds_last.png" alt="Last"/></span>\n            <span class="csp-paging">\n                &nbsp;<select id="%(tableid)s_numofpages">\n                    %(opt)s\n                </select>\n            </span>\n            <span class="csp-paging">&nbsp;<a class="csp-paging-submit button buttongray">Go</a></span>\n\n           <script type="text/javascript">\n                $(".csp-paging-submit").click(function(e) {\n                    p = parseInt($("#%(tableid)s_row").val());\n                    s = parseInt($("#%(tableid)s_numofpages").val());\n                    $.paginglocation(location.href, {"page": p, "pagesize": s});\n                });\n                $(".%(tableid)s").find("img").click(function(e) {\n                    var src = $(this).attr("src");\n                    p = parseInt($("#%(tableid)s_row").val());\n                    if (src.indexOf("ds_first") > 0 && p > 1) {\n                        $.paginglocation(location.href, {"page": 1, "pagesize": %(pagesize)i});\n                    }\n                    else if (src.indexOf("ds_previous") > 0 && p > 1) {\n                        $.paginglocation(location.href, {"page": p-1, "pagesize": %(pagesize)i});\n                    }\n                    else if (src.indexOf("ds_next") > 0 && p < %(numofpages)i) {\n                        $.paginglocation(location.href, {"page": p+1, "pagesize": %(pagesize)i});\n                    }\n                    else if (src.indexOf("ds_last") > 0) {\n                        $.paginglocation(location.href, {"page": %(numofpages)i, "pagesize": %(pagesize)i});\n                    }\n                });\n           </script>\n        </div>\n        ' % {'current_page': current_page,
         'pages': num_of_records,
         'pagesize': page_size,
         'opt': '\n'.join(options),
         'numofpages': num_of_pages,
         'tableid': 'csp-table-paging'})
        res.Seek(0)
        return res.Read()



    def GetTreeTable(self, header = [], lines = [], index = 0, index_parent = 1):
        id = 'table_%s' % str(random.randint(1, 1000))
        res = UnicodeMemStream()
        res.Write('\n            <script type="text/javascript">\n            $(document).ready(function()  {\n              $("#%(tableId)s").treeTable();\n            });\n            </script>\n        ' % {'tableId': id})
        res.Write('<table id="%s" class="treeTable"><thead><tr>' % id)
        res.Write(''.join([ '<th>%s</th>' % x for x in header ]))
        res.Write('</tr></thead><tbody>')
        for row in lines:
            res.Write('<tr id="node-%i"%s>' % (row[index], '' if row[index_parent] is None else ' class="child-of-node-%i"' % row[index_parent]))
            for i in range(0, len(row)):
                if index_parent != i:
                    res.Write('<td%s>%s</td>' % (' class="first"' if i == 0 else '', row[i]))

            res.Write('</tr>')

        res.Write('</tbody></table>')
        res.Seek(0)
        return res.Read()



    def GetPropertyTable(self, header = None, lines = None, style = 'width: 250px'):
        lines = [ ['<strong>%s</strong>' % x, y] for (x, y,) in lines.items() ]
        return self.GetDiv([self.GetTable(header, lines)], style=style)



    def GetTable(self, header = None, lines = None, className = 'tablesorter', enableEdit = False, editUrl = None, enableDelete = False, deleteUrl = None, useFilter = False, invertSelection = False, paging = None, customActions = None, serverOrder = False, baseUrl = None, keyFields = None, readOnlyFields = None, showCount = True):
        return GetTable(header, lines, className, enableEdit, editUrl, enableDelete, deleteUrl, useFilter, invertSelection, paging, customActions, serverOrder, baseUrl, keyFields, readOnlyFields, showCount)



    def GetDashboard(self, layout, area1, area2 = None, area3 = None, area4 = None, area5 = None, area6 = None, area7 = None, area8 = None, skin = True):
        if layout not in ('dashboard0', 'dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'):
            raise Exception('GetDashboard(layout... only accepts one of those elements [dashboard0, dashboard1, dashboard2, dashboard3, dashboard4, dashboard5, dashboard6]')
        layouts = {'dashboard0': '<div class="csp-row"><div class="csp-cell-dash">%(area1)s</div></div><div class="csp-row"><div class="csp-cell-dash">%(area2)s</div></div>',
         'dashboard1': '<div class="csp-row"><div class="csp-cell-dash">%(area1)s</div><div class="csp-cell-dash">%(area2)s</div></div>',
         'dashboard2': '<div class="csp-row"><div class="csp-cell-dash">%(area1)s</div><div class="csp-cell-dash">%(area2)s</div></div>\n                <div class="csp-row"><div class="csp-cell-dash">%(area3)s</div><div class="csp-cell-dash">%(area4)s</div></div>',
         'dashboard3': '<div class="csp-row"><div class="csp-cell-dash">%(area1)s</div><div class="csp-cell-dash">%(area2)s</div></div>\n                <div class="csp-row"><div class="csp-cell-dash">%(area3)s</div><div class="csp-cell-dash"><div class="csp-table">\n                <div class="csp-row"><div class="csp-cell-dash">%(area4)s</div><div class="csp-cell-dash">%(area5)s</div></div></div></div></div>',
         'dashboard4': '\n            <div class="csp-row">\n                <div class="csp-cell-dash">%(area1)s</div>\n                <div class="csp-cell-dash">%(area2)s</div>\n                <div class="csp-cell-dash">%(area3)s</div>\n            </div>\n            <div class="csp-row">\n                <div class="csp-cell-dash">%(area4)s</div>\n                <div class="csp-cell-dash">%(area5)s</div>\n                <div class="csp-cell-dash">%(area6)s</div>\n            </div>',
         'dashboard5': '<div class="csp-row"><div class="csp-cell-dash">%(area1)s</div><div class="csp-cell-dash">%(area2)s</div>\n                <div class="csp-cell-dash">%(area3)s</div><div class="csp-cell-dash">%(area4)s</div></div>\n                <div class="csp-row"><div class="csp-cell-dash">%(area5)s</div><div class="csp-cell-dash">%(area6)s</div>\n                <div class="csp-cell-dash">%(area7)s</div><div class="csp-cell-dash">%(area8)s</div></div>',
         'dashboard6': '\n                <div class="csp-row">\n                    <div class="csp-cell-dash">%(area1)s</div>\n                </div>\n            </div>\n            <div class="csp-table-dash">\n                <div class="csp-row">\n                    <div class="csp-cell-dash">%(area2)s</div>\n                    <div class="csp-cell-dash">%(area3)s</div>\n                </div>'}
        cssHPart = CheckValue('class', 'csp-part-header' if skin is True else 'csp-part-header-noskin')
        cssPart = CheckValue('class', 'csp-part' if skin is True else 'csp-part-noskin')
        checkTuple = lambda x, y: '<div%(cssheader)s>%(h)s</div><div%(cssbody)s>%(b)s</div>' % {'h': x,
         'b': y,
         'cssheader': cssHPart,
         'cssbody': cssPart}
        checkIndex = lambda area: (''.join([ checkTuple(x, y) for (x, y,) in area ]) if area is not None else '')
        res = UnicodeMemStream()
        res.Write('<div class="csp-table-dash">')
        res.Write(layouts[layout] % {'area1': checkIndex(area1),
         'area2': checkIndex(area2),
         'area3': checkIndex(area3),
         'area4': checkIndex(area4),
         'area5': checkIndex(area5),
         'area6': checkIndex(area6),
         'area7': checkIndex(area7),
         'area8': checkIndex(area8)})
        res.Write('</div>')
        res.Seek(0)
        return res.Read()



    def GetProcessCssClass(self, percent, process_scale):
        className = 'bar-high'
        if process_scale == 3:
            if percent < 34:
                className = 'bar-low'
            elif percent < 67:
                className = 'bar-mid'
            elif percent < 100:
                className = 'bar-high-mid'
            elif percent > 99:
                className = 'bar-high'
        elif process_scale == 5:
            if percent < 26:
                className = 'bar-low'
            elif percent < 51:
                className = 'bar-mid-low'
            elif percent < 76:
                className = 'bar-mid'
            elif percent < 100:
                className = 'bar-high-mid'
        return className



    def GetCellBullet(self, percent, process_scale = 3):
        className = self.GetProcessCssClass(percent, process_scale)
        className = CheckValue('class', className)
        return '<div class="csp-bullet"><div %(className)sstyle="width: 100%%"></div></div>' % {'className': className}



    def GetCellProcess(self, percent, process_scale = 3):
        className = self.GetProcessCssClass(percent, process_scale)
        className = CheckValue('class', className)
        return '<div class="csp-progress"><div title="%(percenttext)s%%" %(className)sstyle="width: %(percent)s%%"></div></div>' % {'percent': min(int(percent), 100),
         'percenttext': int(percent),
         'className': className}



    def GetFieldset(self, ctrlID = None, elements = [], label = None):
        res = []
        res.append(self._HtmlWriter__GetElementBegin('fieldset', ''))
        if label:
            res.append('<legend>%s</legend>' % label)
        for n in elements:
            res.append(n)

        res.append(self._HtmlWriter__GetElementEnd('fieldset'))
        return '\n'.join(res)



    def GetSimpleForm(self, formMethod = 'post', fileName = '', formAction = '', elements = None):
        ctrlID = 'form_%s' % str(random.randint(1, 1000))
        self.EnableFormValidation(ctrlID)
        formAction = '%(fileName)s?action=%(formAction)s' % {'fileName': fileName,
         'formAction': formAction}
        res = []
        res.append(self._HtmlWriter__GetElementBegin('form', ' id="%s" action="%s" method="%s"' % (ctrlID, formAction, formMethod)))
        res.append(self._HtmlWriter__GetElementBegin('div', ''))
        for n in elements:
            res.append(self.GetP([n]))

        res.append(self._HtmlWriter__GetElementEnd('form'))
        return '\n'.join(res)



    def GetSimpleDialogForm(self, formMethod = 'post', fileName = '', formAction = '', elements = None, height = 140, width = 300, title = '', autoOpen = True, ctrlID = None, submitButton = 'Submit'):
        if ctrlID is None:
            ctrlID = 'form_%i' % random.randint(1, 1000)
        m_ctrlID = 'dialog-modal_%s' % ctrlID
        self.Write('<script type="text/javascript">\n    $(function() {\n        $( "#%(ctrlID)s" ).dialog({\n            autoOpen: %(autoOpen)s,\n            height: %(height)s,\n            width: %(width)s,\n            modal: true,\n            buttons: {\n                "%(submitButton)s" : function() {\n                    $("#%(formID)s").submit();\n                },\n                Cancel: function() {\n                    $(this).dialog("close");\n                }\n            }\n        });\n    });\n    </script>' % {'ctrlID': m_ctrlID,
         'height': height,
         'width': width,
         'autoOpen': str(autoOpen).lower(),
         'submitButton': submitButton,
         'formID': ctrlID})
        form = self.GetForm(ctrlID=ctrlID, formMethod=formMethod, fileName=fileName, formAction=formAction, elements=elements)
        return self.GetDiv([form], ctrlID=m_ctrlID, title=title)



    def GetHidden(self, name, value = ''):
        return '<input type="hidden" name="%(name)s" id="%(name)s" value="%(value)s"/>' % {'name': name,
         'value': value}



    def GetDiv(self, elements, ctrlID = None, className = None, style = None, title = None, dataBind = None):
        return self._HtmlWriter__GetElements(elements, 'div', ctrlID, className, style, title, dataBind)



    def GetSpan(self, elements, ctrlID = None, className = None, style = None, title = None, dataBind = None):
        return self._HtmlWriter__GetElements(elements, 'span', ctrlID, className, style, title, dataBind)



    def GetP(self, elements, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElements(elements, 'p', ctrlID, className, style)



    def GetUl(self, elements, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElements(elements, 'ul', ctrlID, className, style)



    def GetLi(self, elements, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElements(elements, 'li', ctrlID, className, style)



    def GetA(self, innerText, href, ctrlID = None, className = None, style = None, onClick = None, title = None, rel = None, rev = None):
        return GetA(innerText, href, ctrlID, className, style, onClick, title, rel, rev)



    def GetH1(self, innerText, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElement(ctrlName='h1', ctrlValue=innerText, ctrlID=ctrlID, className=className, style=style)



    def GetH2(self, innerText, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElement(ctrlName='h2', ctrlValue=innerText, ctrlID=ctrlID, className=className, style=style)



    def GetH3(self, innerText, ctrlID = None, className = None, style = None):
        return self._HtmlWriter__GetElement(ctrlName='h3', ctrlValue=innerText, ctrlID=ctrlID, className=className, style=style)



    def GetFileInput(self, ctrlID, labelCaption, className = None, width = None, title = ''):
        if width:
            width = ' style="width:%spx"' % width
        else:
            width = ''
        className = CheckValue('class', className)
        title = CheckValue('title', title)
        res = []
        if labelCaption is not None:
            res.append('<label class="form-label" for="%s">%s</label>' % (ctrlID, labelCaption))
        res.append('<input id="%(ctrlID)s" name="%(ctrlID)s" type="file" %(className)s%(width)s%(title)s/>' % {'ctrlID': ctrlID,
         'className': className,
         'width': width,
         'title': title})
        return '\n'.join(res)



    def GetInput(self, ctrlID, labelCaption, className = None, minLength = None, width = None, value = None, title = ''):
        minLength = CheckValue('minlength', minLength)
        if width:
            width = ' style="width:%spx"' % width
        else:
            width = ''
        className = CheckValue('class', className)
        value = CheckValue('value', value)
        title = CheckValue('title', title)
        res = []
        if labelCaption is not None:
            res.append('<label class="form-label" for="%s">%s</label>' % (ctrlID, labelCaption))
        res.append('<input id="%s" name="%s"%s%s%s%s%s/>' % (ctrlID,
         ctrlID,
         className,
         minLength,
         width,
         value,
         title))
        return '\n'.join(res)



    def GetSelect(self, elements, controlID, labelCaption = None, elementClass = None, selectedValue = None):
        elementClass = CheckValue('class', elementClass)
        if controlID:
            controlID = ' id="%s" name="%s"' % (controlID, controlID)
        opt0 = lambda row: (' selected="selected"' if row[0] == selectedValue else '')
        opt1 = lambda row: '<option value="%s"%s>%s</option>\n' % (row[0], CheckValue('selected', row[2]) if len(row) > 2 else opt0(row), row[1])
        res = []
        if labelCaption is not None:
            res.append('<label class="form-label" for="%s">%s</label>' % (controlID, labelCaption))
        res.append(self._HtmlWriter__GetElementBegin('select', '%s%s' % (controlID, elementClass)))
        res.append(''.join(map(opt1, elements.items() if isinstance(elements, dict) else elements)))
        res.append(self._HtmlWriter__GetElementEnd('select'))
        return ''.join(res)



    def GetToggle(self):
        return self.GetCheck(ctrlID='', labelCaption='', className='toggle-table', checked=False)



    def GetCheck(self, ctrlID, labelCaption, className, checked, disabled = False):
        className = CheckValue('class', className)
        ctrlNa = CheckValue('name', ctrlID)
        ctrlID = CheckValue('id', ctrlID)
        if checked:
            checked = ' checked ="true"'
        else:
            checked = ''
        res = []
        if labelCaption:
            res.append('<label class="form-label" for="%s">%s</label>' % (ctrlID, labelCaption))
        dis = ' disabled' if disabled else ''
        res.append('<input type="checkbox"%s%s%s%s%s/>' % (ctrlID,
         ctrlNa,
         className,
         checked,
         dis))
        return '\n'.join(res)



    def GetTextArea(self, ctrlID, labelCaption, className, cols, rows, innerHtml = None):
        className = CheckValue('class', className)
        cols = CheckValue('cols', cols)
        rows = CheckValue('rows', rows)
        ctrlFor = CheckValue('for', ctrlID)
        ctrlID2 = CheckValue('id', ctrlID)
        ctrlName = CheckValue('name', ctrlID)
        if innerHtml is None:
            innerHtml = ''
        lines = []
        if labelCaption:
            lines.append('<label class="form-label"%(ctrlID)s>%(labelCaption)s</label>' % {'ctrlID': ctrlFor,
             'labelCaption': labelCaption})
        lines += [self._HtmlWriter__GetElementBegin('textarea', '%(ctrlID)s%(className)s%(cols)s%(rows)s%(ctrlName)s' % {'ctrlID': ctrlID2,
          'className': className,
          'cols': cols,
          'rows': rows,
          'ctrlName': ctrlName}), innerHtml, self._HtmlWriter__GetElementEnd('textarea')]
        return ''.join(lines)



    def GetButton(self, className, elementValue):
        return '<input class="%(className)s" type="submit" value="%(elementValue)s" />' % {'className': className,
         'elementValue': elementValue}



    def GetTabs(self, tabs, content, ctrlID):
        self._HtmlWriter__EnableTabs(ctrlID)
        tabs = ['<ul>'] + tabs + ['</ul>'] + content
        return self.GetDiv(tabs, ctrlID)



    def GetTabsAjax(self, links):
        ctrlID = 'tabs_%s' % str(random.randint(1, 1000))
        self._HtmlWriter__EnableTabs(ctrlID)
        elements = []
        elements.append('<ul>')
        for l in links:
            if len(l[0]):
                elements.append('<li><a href="%s"><span>%s</span></a></li>' % (l[0], l[1]))
            else:
                elements.append('<li><span>%s</span></li>' % (l[1],))

        elements.append('</ul>')
        return self.GetDiv(elements, ctrlID=ctrlID, className=None, style=None)



    def GetTab(self, ctrlID, label):
        return self.GetLi([self.GetA(label, '#%s' % ctrlID)], None)



    def GetFloatMessage(self, messageText):
        return '\n        <div class="messagebox information">\n            Information<br />\n            <strong>%s</strong>\n        </div>\n        <script type="text/javascript">\n            var options = {};\n            $(".messagebox").show("blind", options, 1500, showCallback);\n\n            function showCallback() {\n                $(".messagebox").hide("blind", options, 1500);\n            }\n        </script>\n        ' % messageText



    def GetTooltip(self, href, ajax, title, caption, ctrlID = None):
        return self.GetA(innerText=caption, href=href, ctrlID=ctrlID, className='a-tip', style=None, onClick=None, title=title, rel=ajax)



    def GetTooltipActions(self, href, ajax, title, caption, actions = [], ctrlID = None):
        html = '<div class="csp-dropmenu"><span>%(tooltip)s<em class="csp-opener"><img alt="dropdown" src="/img/down.png"></em>\n                    <ul class="csp-sublist">%(links)s</ul></span></div>' % {'tooltip': self.GetTooltip(href, ajax, title, caption + ' &nbsp;'),
         'links': ''.join([ '<li>%s</li>' % x for x in actions ])}
        return html



    def Write(self, html):
        if not self.inserts.has_key(self.redirect):
            self.inserts[self.redirect] = html
        else:
            self.inserts[self.redirect] = self.inserts[self.redirect] + html



    def WriteFloatMessage(self, messageText):
        self.Write(self.GetFloatMessage(messageText))



    def WriteBeginForm(self, formName, formMethod, formAction):
        self.Write('<form id="%s" method="%s" action="%s">' % (formName, formMethod, formAction))



    def WriteEndForm(self):
        self.Write('</form>')



    def GetDatePicker(self, ctrlID, ctrlCaption, ctrlFormat = 'yy-mm-dd', ctrlValue = None, ctrlTitle = None):
        now = datetime.now()
        res = []
        res.append('<SCRIPT type=text/javascript>\n            $(function() {\n                $("#%(ctrlID)s").datepicker({\n                    dateFormat: \'%(ctrlFormat)s\',\n                    changeMonth: true,\n                    changeYear: true,\n                    showWeek: true,\n                    showOn: \'button\',\n                    yearRange: \'%(fromYear)i:%(toYear)s\'\n                    });\n            });\n            </SCRIPT>\n' % {'ctrlID': ctrlID,
         'ctrlFormat': ctrlFormat,
         'fromYear': now.year - 85,
         'toYear': now.year + 35})
        ctrlValue = CheckValue('value', ctrlValue)
        ctrlTitle = CheckValue('title', ctrlTitle)
        if ctrlCaption:
            res.append('<label class="form-label" for="%(ctrlID)s">%(ctrlCaption)s</label>' % {'ctrlID': ctrlID,
             'ctrlCaption': ctrlCaption})
        res.append('<input id="%(ctrlID)s" name="%(ctrlID)s" type="text" style="width: 80px;"%(ctrlValue)s%(ctrlTitle)s/>' % {'ctrlID': ctrlID,
         'ctrlValue': ctrlValue,
         'ctrlTitle': ctrlTitle})
        return ''.join(res)



    def GetDateTimePicker(self, ctrlDateID, ctrlTimeID, ctrlCaption, ctrlFormat = 'yy-mm-dd', ctrlValue = None, ctrlTitle = None):
        v = ctrlValue.split(' ') if isinstance(ctrlValue, basestring) else ('', '')
        if len(v) == 1:
            v = (v, '00:00')
        res = []
        res.append(self.GetDatePicker(ctrlID=ctrlDateID, ctrlCaption=ctrlCaption, ctrlFormat=ctrlFormat, ctrlValue=v[0], ctrlTitle=ctrlTitle))
        res.append(self.GetInput(ctrlID=ctrlTimeID, labelCaption=None, className=None, minLength=None, width='60', value=v[1]))
        return ''.join(res)



    def GetAjaxTree(self, ctrlID, url, child_function, search_function = None, create_function = None, remove_function = None, rename_function = None, move_function = None, contextMenu = None):
        mem = UnicodeMemStream()
        contextMenu = ' "contextmenu": { "items": %s },  ' % contextMenu if contextMenu is not None else ''
        mem.Write('\n<script type="text/javascript">\n$(function () {\n        if (!$.jstree) {\n            alert("Tree is disabled, please contact help desk!")\n        } else {\n        $("#%(ctrlID)s")\n        .jstree({\n            "plugins" : [ "themes", "json_data", "ui", "crrm", "dnd", "search", "types", "hotkeys", "contextmenu" ],\n            %(contextMenu)s\n            "json_data" : {\n                "ajax" : {\n                    "url" : "%(url)s",\n                    "data" : function (n) {\n                        return { "action" : "%(child_function)s", "id" : n.attr ? n.attr("id") : -1 };\n                    }}},' % {'ctrlID': ctrlID,
         'url': url,
         'child_function': child_function,
         'contextMenu': contextMenu})
        if search_function is not None:
            mem.Write('\n                "search" : {\n                    "ajax" : {\n                        "url" : "%(url)s",\n                        "data" : function (str) {\n                            return { "action" : "%(search_function)s", "search" : str };\n                        }}},' % {'url': url,
             'search_function': search_function})
        mem.Write('\n            "types" : {\n                "max_depth" : -2, "max_children" : -2, "valid_children" : [ "root" ],\n                "types" : {\n                    "default" : { "valid_children" : "none", "icon" : { "image" : "/img/folder.png" } },\n                    "file" : { "valid_children" : [ ],\n                        "icon" : { "image" : "/img/file.png" }\n                    },\n                    "folder" : { "valid_children" : [ "default", "folder", "file" ],\n                        "icon" : { "image" : "/img/folder.png" }\n                    },\n                    "root" : {\n                        "valid_children" : [ "default", "folder", "file" ],\n                        "icon" : { "image" : "/img/root.png" },\n                        "start_drag" : false, "move_node" : false, "delete_node" : false, "remove" : false\n                    }\n                }\n            }\n        })')
        if create_function is not None:
            mem.Write('\n            .bind("create.jstree", function (e, data) {\n                $.post(\n                    "%(url)s?action=%(create_function)s",\n                    {\n                        "id" : data.rslt.parent.attr("id"),\n                        "position" : data.rslt.position,\n                        "title" : data.rslt.name,\n                        "type" : data.rslt.obj.attr("rel")\n                    },\n                    function (r) {\n                        if(r.status) {\n                            $(data.rslt.obj).attr("id", r.id);\n                            $(data.rslt.obj).attr("rel", r.type);\n                        } else { $.jstree.rollback(data.rlbk); }\n                    }\n                );\n            })' % {'url': url,
             'create_function': create_function})
        if remove_function is not None:
            mem.Write('\n            .bind("remove.jstree", function (e, data) {\n                data.rslt.obj.each(function () {\n                    $.ajax({\n                        async : false,\n                        type: \'POST\',\n                        url: "%(url)s?action=%(remove_function)s",\n                        data : {\n                            "id" : this.id\n                        },\n                        success : function (r) {\n                            if(!r.status) { data.inst.refresh(); }\n                        }\n                    });\n                });\n            })' % {'url': url,
             'remove_function': remove_function})
        if rename_function is not None:
            mem.Write('\n            .bind("rename.jstree", function (e, data) {\n                $.post(\n                    "%(url)s?action=%(rename_function)s",\n                    {\n                        "id" : data.rslt.obj.attr("id"),\n                        "title" : data.rslt.new_name\n                    },\n                    function (r) {\n                        if(!r.status) { $.jstree.rollback(data.rlbk); }\n                    }\n                );\n            })' % {'url': url,
             'rename_function': rename_function})
        if move_function is not None:
            mem.Write('\n            .bind("move_node.jstree", function (e, data) {\n                data.rslt.o.each(function (i) {\n                    $.ajax({\n                        async : false,\n                        type: \'POST\',\n                        url: "%(url)s?action=%(move_function)s",\n                        data : {\n                            "id" : $(this).attr("id"),\n                            "ref" : data.rslt.np.attr("id"),\n                            "position" : data.rslt.cp + i,\n                            "title" : data.rslt.name,\n                            "copy" : data.rslt.cy ? 1 : 0\n                        },\n                        success : function (r) {\n                            if(!r.status) { $.jstree.rollback(data.rlbk); }\n                            else {\n                                $(data.rslt.oc).attr("id", r.id);\n                                if(data.rslt.cy && $(data.rslt.oc).children("UL").length) {\n                                    data.inst.refresh(data.inst._get_parent(data.rslt.oc));\n                                }\n                            }\n                        }\n                    });\n                });\n            });' % {'url': url,
             'move_function': move_function})
        mem.Write('\n}});\n</script>')
        mem.Seek(0)
        self.WriteDirect('jscript', mem.Read())
        return '<div id="%s"><a href="base:%s" style="display:hidden;"></a></div>' % (ctrlID, url)



    def GetTree(self, ctrlID, data, expand = []):
        caseCon = []
        treeCon = []
        treeCon.append('<input type="hidden" id="%s" value="" />' % ctrlID)
        treeCon.append('<div id="%s_container">' % ctrlID)
        if_then = lambda a, b: (b if a is None else '%s:%s' % (a, b))
        recFunc = lambda idel, label, url: '<li id="li_%s"><a href="%s">%s</a>' % (idel, if_then(url, idel), label)
        level = {}
        last = -1
        for (idel, par, lab, url,) in data:
            if not level.has_key(idel):
                if not level.has_key(par):
                    level[par] = 0
                    level[idel] = 0
                else:
                    level[idel] = level[par] + 1
            if last < level[idel]:
                treeCon.append('<ul>')
            elif last == level[idel]:
                treeCon.append('</li>')
            if url is not None and url.startswith('js:'):
                caseCon.append('case "%s": %s(%s); break;' % (idel, url.split(':')[1], idel))
            if level[idel] < last:
                for x in range(0, last - level[idel]):
                    treeCon.append('</ul></li>')

            treeCon.append(recFunc(idel, lab, url))
            last = level[idel]

        treeCon.append('</div>')
        js = '\n        <script type="text/javascript">\n        $("#%(ctrlID)s_container").bind("select_node.jstree", function (event, data) {\n                         var mar = data.args[0];\n                         try {\n                         if (mar.href != undefined) {\n                             var myargs = mar.href.split(\':\');\n                             if (myargs[0] == "url") {\n                                window.location.href = mar.href.split(\':\')[1]+":"+mar.href.split(\':\')[2];\n                                return;\n                             } else if (myargs[0] == "js") {\n                                switch(myargs[myargs.length-1])\n                                {\n                                    %(caselines)s\n                                }\n                             }\n                             var myargs = marhref.split(\'/\');\n                             a = myargs[myargs.length-1]\n                             $("#%(ctrlID)s").val(a);\n                         }\n                         } catch(err) {}\n                    })\n        $("#%(ctrlID)s_container")\n            .jstree({\n                "core" : { "initially_open"  : %(expand)s },\n                "plugins" : ["themes","html_data","ui","crrm","hotkeys"]\n        });\n        </script>\n        ' % {'ctrlID': ctrlID,
         'expand': [ 'li_%s' % x for x in expand ],
         'caselines': '\n'.join(caseCon)}
        return ''.join([''.join(treeCon), js])



    def GetAutoComplete(self, ctrlID, ctrlLabel, callbackPy, minLength = 4, labelClass = 'form-label'):
        jscript = '\n    <script type="text/javascript">\n    $(function() {\n        var cache_%(ctrlID)s = {};\n        $("#%(ctrlID)s_ac").autocomplete({\n            select: function(event,ui) {\n                $("#%(ctrlID)s").val(ui.item.id);\n                $("#%(ctrlID)s_sr").html(" <span title=\'"+ui.item.label+"\'> Selected: "+ui.item.id+"</span>");\n            },\n            source: function(request, response) {\n                var no = parseInt(request.term);\n                if (!isNaN(no)) {\n                    response($.parseJSON(\'[{"id":"\'+no+\'","label":"\'+no+\'"}]\'));\n                    $("#%(ctrlID)s").val(no);\n                    $("#%(ctrlID)s_sr").html(" <span title=\'"+no+"\'> Selected: "+no+"</span>");\n                    return;\n                }\n                if (cache_%(ctrlID)s.term == request.term && cache_%(ctrlID)s.content) {\n                    response(cache_%(ctrlID)s.content);\n                    return;\n                }\n                if (new RegExp(cache_%(ctrlID)s.term).test(request.term) && cache_%(ctrlID)s.content && cache_%(ctrlID)s.content.length < 13) {\n                    response($.ui.autocomplete.filter(cache_%(ctrlID)s.content, request.term));\n                    return;\n                }\n                $.ajax({\n                    url: "%(callbackPy)s",\n                    dataType: "json",\n                    data: request,\n                    success: function(data) {\n                        cache_%(ctrlID)s.term = request.term;\n                        cache_%(ctrlID)s.content = data;\n                        $("#%(ctrlID)s_sr").html(" Found: "+data.length);\n                        response(data);\n                    }\n                });\n            },\n            minLength: %(minLength)s\n        });\n    });\n    </script>' % {'ctrlID': ctrlID,
         'callbackPy': callbackPy,
         'minLength': str(minLength)}
        labelClass = CheckValue('class', labelClass)
        return ''.join([jscript,
         '<input type="hidden" id="%(ctrlID)s" name="%(ctrlID)s" value="" />' % {'ctrlID': ctrlID},
         '<label %(labelClass)s for="%(ctrlID)s_ac">%(ctrlLabel)s</label>' % {'labelClass': labelClass,
          'ctrlID': ctrlID,
          'ctrlLabel': ctrlLabel} if ctrlLabel else '',
         '<input id="%(ctrlID)s_ac"/>' % {'ctrlID': ctrlID},
         '<span id="%(ctrlID)s_sr" class=""></span>' % {'ctrlID': ctrlID}])



    def GetGrowl(self, innerText, header, body):
        return self.GetA(innerText=innerText, href='#', onClick="javascript:addNotice('<strong>%s</strong><p>%s<p>')" % (header, body))



    def RecordToDateTime(self, r):
        (year, month, wd, day, hour, mi, sec, ms,) = blue.os.GetTimeParts(r)
        return datetime(year, month, day, hour, mi, sec, ms)



    def WriteTable(self, header = None, lines = None, className = 'tablesorter', enableEdit = False, editUrl = None, enableDelete = False, deleteUrl = None, useFilter = False, invertSelection = False, paging = None, customActions = None, serverOrder = False, baseUrl = None, keyFields = None, readOnlyFields = None, showCount = True, maxRows = None, title = None, ctrlID = None):
        if maxRows:
            if len(lines) == maxRows:
                if customActions is None:
                    customActions = []
                customActions.append(self.FontRed('ONLY TOP %s RECORDS ARE LISTED' % maxRows))
        t = self.GetTable(header, lines, showCount=showCount, customActions=customActions, useFilter=useFilter, invertSelection=invertSelection, paging=paging, enableEdit=enableEdit, editUrl=editUrl, enableDelete=enableDelete, deleteUrl=deleteUrl, serverOrder=serverOrder, baseUrl=baseUrl, keyFields=keyFields, readOnlyFields=readOnlyFields)
        if title is None:
            self.Write(t)
        elif ctrlID is None:
            if title is None or title == '':
                ctrlID = 'wp_1'
            else:
                ctrlID = 'wp_' + title.lower().replace(' ', '')
        self.Write(self.WebPart(title, t, ctrlID))



    def WriteForm(self, ctrlID, formMethod, fileName, formAction, elements):
        self.Write(self.GetForm(ctrlID, formMethod, fileName, formAction, elements))



    def WriteSimpleForm(self, formMethod = 'post', fileName = '', formAction = '', elements = []):
        self.Write(self.GetSimpleForm(formMethod, fileName, formAction, elements))



    def WriteDatePicker(self, ctrlID, ctrlCaption, ctrlFormat = 'dd-mm-yy', ctrlValue = None, ctrlTitle = None):
        self.Write(self.GetDatePicker(ctrlID, ctrlCaption, ctrlFormat, ctrlValue, ctrlTitle))



    def WriteDateTimePicker(self, ctrlDateID, ctrlTimeID, ctrlCaption, ctrlFormat = 'yy-mm-dd', ctrlValue = None, ctrlTitle = None):
        self.Write(self.GetDateTimePicker(ctrlDateID=ctrlDateID, ctrlTimeID=ctrlTimeID, ctrlCaption=ctrlCaption, ctrlFormat=ctrlFormat, ctrlValue=ctrlValue, ctrlTitle=ctrlTitle))



    def WriteAutoComplete(self, ctrlID, ctrlLabel, callbackPy):
        self.Write(self.GetAutoComplete(ctrlID, ctrlLabel, callbackPy))



    def WriteAccordion(self, controlId, headers, bodies):
        self.EnableAccordion(controlId)
        self.Write('<div id="%s">' % controlId)
        for i in range(0, len(headers)):
            self.Write('<h3><a href="#">%s</a></h3>' % headers[i])
            self.Write('<div><p>%s</p></div>' % bodies[i])

        self.Write('</div>')



    def WriteLi(self, html):
        self.Write('   <li>%s\n' % html)



    def WriteH1(self, html):
        self.Write('<h1>%s</h1>\n' % html)



    def WriteH2(self, html):
        self.Write(self.GetH2(innerText=html, ctrlID=None, className=None, style=None))



    def WriteH3(self, html):
        self.Write('<h3>%s</h3>\n' % html)



    def WriteH4(self, html):
        self.Write('<h4>%s</h4>\n' % html)



    def WriteNotice(self, title, text):
        self.Write('<table width=420 class=NoticeTable cellpadding=5 cellspacing=0><tr><td valign=top width=24><img src="/img/msg_infoicon.gif"></td><td><b>%s</b><br>%s</td></tr></table>' % (title, text))



    def WriteDirect(self, redirect, html):
        oldRedirect = self.redirect
        self.Redirect(redirect)
        self.Write(html)
        self.Redirect(oldRedirect)



    def WriteBreak(self, num):
        br = ''
        for i in range(num):
            br = br + '<br />\n'

        self.Write(br)



    def WriteAnchor(self, anchor):
        self.Write('<a name="%s"></a>\n' % anchor)



    def Paragraph(self, p, style = ''):
        self.Write('<p')
        if style != '':
            self.Write(' style="%s"' % style)
        self.Write('>%s</p>' % p)



    def WriteAligned(self, align, paragraph):
        self.Write('<div align="%s">%s</div>' % (align, paragraph))



    def AddNavbar(self, html):
        self.inserts['navigation'] = self.inserts['navigation'] + ' ' + html + '<br>\n'



    def Redirect(self, whereto):
        self.redirect = whereto



    def UnorderedList(self, lines):
        s = UnicodeMemStream()
        s.Write('<ul>\n')
        for line in lines:
            s.Write('<li>')
            s.Write(line)
            s.Write('\n')

        s.Write('</ul>\n')
        s.Seek(0)
        return s.Read()



    def OrderedList(self, lines):
        s = UnicodeMemStream()
        s.Write('<ol>\n')
        for line in lines:
            s.Write('<li>')
            s.Write(line)
            s.Write('\n')

        s.Write('</ol>\n')
        s.Seek(0)
        return s.Read()



    def CheckAll(self, element):
        return '<input type="checkbox" name="checkall" onclick="ch=false;if(this.checked){ch=true;};o=document.getElementsByName(\'%s\');for(i=0;i<o.length;i++){o[i].checked=ch;};">' % element



    def AppBottomLeft(self):
        return ''



    def AppBottomRight(self):
        return ''



    def Generate(self):
        if not self.inserts.has_key('mainhtml'):
            return ''
        if len(self.visualization) > 0:
            temp_script = '\n    <script type="text/javascript" src="http://www.google.com/jsapi"></script>\n    <script type="text/javascript">\n      google.load(\'visualization\', \'1\', {packages: [\'%s\']});\n    </script>\n' % "','".join(self.visualization)
            self.WriteDirect('scripts', temp_script)
        if len(self.scripts) > 0:
            self.WriteDirect('scripts', '\n    '.join(self.scripts))
        if len(self.headjsScripts) > 0:
            self.WriteDirect('headjs', '\n    '.join(self.headjsScripts))
        if len(self.inserts['visualscripts']) > 0:
            visualScripts = ['function doVisual() {\n', self.inserts['visualscripts'], '\n}\n'] + self.visualcallbacks
            self.inserts['visualscripts'] = ''.join(['<script type="text/javascript">\n'] + visualScripts + ['\ngoogle.setOnLoadCallback(doVisual);</script>'])
        import util
        import nasty
        file = nasty.ResFile()
        ok = False
        for filename in util.wwwRoot.Map(self.baseTemplate):
            try:
                file.OpenAlways(filename, 1)
                ok = True
                break
            except IOError:
                file.Close()
                sys.exc_clear()

        if not ok:
            raise IOError, '%s not found under %s' % (self.baseTemplate, util.wwwRoot)
        base = str(file.Read())
        file.Close()
        pos = 0
        begin = 0
        (stop, hz,) = blue.os.GetCycles()
        dt = (stop - self.start) / float(hz) * 1000.0
        self.inserts['bottom_left'] = '%s (%.1f ms) %s' % (self.inserts['bottom_left'], dt, self.AppBottomLeft())
        trackID = 1 if prefs.clusterMode == 'LOCAL' else prefs.GetValue('webTrackID', -1)
        trackUrl = prefs.GetValue('trackUrl', 'http://10.1.5.131/piwik/')
        if not trackUrl.endswith('/'):
            trackUrl += '/'
        if trackID > -1:
            self.inserts['trackpage'] = '\n    <!-- Piwik -->\n    <script type="text/javascript">\n    var pkBaseURL = (("https:" == document.location.protocol) ? "%(trackHttps)s" : "%(trackHttp)s");\n    document.write(unescape("%%3Cscript src=\'" + pkBaseURL + "piwik.js\' type=\'text/javascript\'%%3E%%3C/script%%3E"));\n    </script><script type="text/javascript">\n    try {\n    var user = { \'userID\' : %(userid)s };\n    var piwikTracker = Piwik.getTracker(pkBaseURL + "piwik.php", %(trackID)d);\n    piwikTracker.setCustomData(user);\n    piwikTracker.setDocumentTitle(\'%(documentTitle)s\');\n    piwikTracker.trackPageView();\n    piwikTracker.enableLinkTracking();\n    } catch( err ) {}\n    </script><noscript><p><img src="%(trackHttp)spiwik.php?idsite=%(trackID)d" style="border:0" alt="" /></p></noscript>\n    <!-- End Piwik Tracking Tag -->\n            ' % {'userid': session.userid,
             'documentTitle': self.inserts['title'],
             'trackID': trackID,
             'trackHttp': trackUrl,
             'trackHttps': trackUrl.replace('http:', 'https:')}
        nodeInfo = ''
        if macho.mode == 'server':
            nodeID = sm.services['machoNet'].GetNodeID()
            nodeInfo = '&nbsp;&middot;&nbsp; Node: %s' % self.Link('/admin/network.py', '<font color=silver>%s</font>' % nodeID, {'action': 'Node',
             'nodeID': nodeID})
        self.inserts['bottom_right'] = '<font color=SILVER>%s%s</font> %s' % (prefs.clusterName, nodeInfo, self.AppBottomRight())
        output = ''
        output = base % self.inserts
        return output



    def Canonicalize(self, *args, **kw):
        return Canonicalize(*args, **kw)



    def HTMLEncode(self, *args, **kw):
        return HTMLEncode(*args, **kw)



    def Link(self, *args, **kw):
        return Link(*args, **kw)



    def Button(self, *args, **kw):
        return Button(*args, **kw)



    def Image(self, *args, **kw):
        return Image(*args, **kw)



    def Table(self, *args, **kw):
        return Table(*args, **kw)



    def OutlineDictTable(self, *args, **kw):
        return OutlineDictTable(*args, **kw)



    def OutlineSortedSegmentedTable(self, *args, **kw):
        return OutlineSortedSegmentedTable(*args, **kw)



    def OutlineSegmentedTable(self, *args, **kw):
        return OutlineSegmentedTable(*args, **kw)



    def OutlineTable(self, *args, **kw):
        return OutlineTable(*args, **kw)



    def OutlinePropertyTable(self, *args, **kw):
        return OutlinePropertyTable(*args, **kw)



    def OutlineKeyValTable(self, *args, **kw):
        return OutlineKeyValTable(*args, **kw)



    def BarChart(self, *args, **kw):
        return BarChart(*args, **kw)



    def BrowserCheck(self, *args, **kw):
        return BrowserCheck(*args, **kw)



    def WriteEOFModalDialogue(self, buttonName = 'Done'):
        element = self.request.QueryString('modalDialogueElement')
        if buttonName is not None:
            self.Write('\n                <input type="button" value="%s" onClick="all2Element(\'%s\')">\n            ' % (buttonName, element))
        self.Write('\n                <script language="javascript">\n                    function all2Element(element){\n                        var pairs = new Array();\n                        var disp  = new Array();\n\n                        var allInput = document.getElementsByTagName(\'input\');\n                        for(i=0;i<allInput.length;i++){\n                            if((allInput[i].type==\'radio\')||(allInput[i].type==\'checkbox\')){\n                                if(allInput[i].checked){\n                                    pairs[pairs.length]=allInput[i].name+\'=\'+allInput[i].value;\n                                    disp[disp.length]=allInput[i].name;\n                                }\n                            }else if ((allInput[i].type!=\'button\') && (allInput[i].value.length>0)) {\n                                pairs[pairs.length]=allInput[i].name+\'=\'+allInput[i].value;\n                                disp[disp.length]=allInput[i].name+\'=\'+allInput[i].value;\n                            }\n                        }\n                        var allSelect = document.getElementsByTagName(\'select\')\n                        for(i=0;i<allSelect.length;i++){\n                            for (n=0;n<allSelect[i].options.length;n++){\n                                if (allSelect[i].options[n].selected && allSelect[i].options[n].value!=\'None\') {\n                                    pairs[pairs.length]= allSelect[i].name+\'=\'+allSelect[i].options[n].value;\n                                    disp[disp.length]  = allSelect[i].name+\'=\'+allSelect[i].options[n].text;\n                                }\n                            }\n                        }\n\n                        window.opener.document.all[element].value=pairs.join("&");\n                        window.opener.document.all[element+\'Disp\'].value=disp.join(", ");\n\n                        self.close();\n                    }\n\n                    function fetchFromElement(element){\n                        if(window.opener.document.all[element].value!=\'\'){\n                            var currentValues = window.opener.document.all[element].value.split("&");\n                            for(i=0;i<currentValues.length;i++){\n                                var pair = currentValues[i].split(\'=\');\n                                var modularElement = document.all[pair[0]]\n                                if(modularElement){\n                                    if(modularElement.tagName==\'SELECT\'){\n                                        for(si=0;si<modularElement.options.length;si++){\n                                            if(modularElement.options[si].value == pair[1]){\n                                                modularElement.options[si].selected = true;\n                                            }\n                                        }\n                                    }\n                                    if(modularElement.tagName==\'INPUT\'){\n                                        if(modularElement.type==\'text\'){\n                                            document.all[pair[0]].value = pair[1];\n                                        }\n                                        if(modularElement.type==\'checkbox\'){\n                                            if(pair[1]==\'on\'){document.all[pair[0]].checked=true;}\n                                        }\n                                    }\n                                }\n                            }\n                        }\n                    }\n\n                    document.onload = fetchFromElement(\'%s\');\n                </script>\n            ' % element)



    def UnpackModalDialogueResult(self, *args):
        return UnpackModalDialogueResult(*args)



    def PackModalDialogueResult(self, *args):
        return PackModalDialogueResult(*args)



    def FormatHtmlKWArgs(self, htmlKwargs = {}, prohibitedKeys = []):
        result = ''
        htmlOpt = lambda each: " %s='%s'" % each
        for each in htmlKwargs.iteritems():
            if each[0].lower() not in prohibitedKeys:
                result += htmlOpt(each)

        return result



    def FormatFunctionArguments(self, functionArgs, trailingComma = False):
        argStr = ''
        if functionArgs is not None:
            for each in functionArgs:
                if each is None:
                    argStr += 'null,'
                elif type(each) == types.BooleanType:
                    argStr += '%s,' % str(each).lower()
                elif type(each) in types.StringTypes:
                    if each.startswith('this'):
                        argStr += '%s,' % each
                    else:
                        argStr += "'%s'," % each
                else:
                    argStr += '%s,' % each

            if not trailingComma:
                argStr = argStr[:-1]
        return argStr



    def FormatSelectOptions(self, elements):
        selectOpt = lambda row: '<option value="%s" %s >%s</option>\n' % (row[0], 'selected' if row[2] else '', row[1])
        return '  '.join(map(selectOpt, elements))



    def FormatAjaxArgs(self, action, arguments, extras):
        extraArgs = {}
        ajaxArgsStr = 'action=%s' % action
        if arguments is not None:
            for each in arguments.iteritems():
                if each[1] is None:
                    ajaxArgsStr += '&%s=None' % each[0]
                elif each[0] in extras:
                    extraArgs[each[0]] = each[1]
                elif type(each[1]) in types.StringTypes:
                    ajaxArgsStr += '&%s=%s' % each
                else:
                    ajaxArgsStr += '&%s=%s' % each

        return (ajaxArgsStr, extraArgs)



    def EnableBSDSupport(self):
        if not self.bsdSupport:
            self.bsdSupport = True
            self.AddCss(src='/gd/bsd.css')
            self.AddScript(src='/gd/bsd.js')



    def MakeBSDIdentity(self, schemaName, tableName, columnName, keyID, keyID2 = 0, keyID3 = 0, callbackFunc = ''):
        res = util.KeyVal(schemaName=schemaName, tableName=tableName, columnName=columnName, keyID=keyID, keyID2=keyID2, keyID3=keyID3, callbackFunc=callbackFunc)
        res.tableID = self.BSD.TableID(schemaName, tableName)
        if res.tableID is None:
            raise RuntimeError('Unknown Schema Name or Table Name!')
        if res.columnName not in self.BSD.GetColumnData(res.schemaName, res.tableName).Index('columnName'):
            raise RuntimeError('Unknown Column Name')
        return res



    def _MakeBSDIdentityStr(self, bsdKV):
        self.EnableBSDSupport()
        key = self.BSD.RevisionKey(bsdKV.keyID, bsdKV.keyID2, bsdKV.keyID3, split='|')
        return '%d:%s:%s:%s' % (bsdKV.tableID,
         bsdKV.columnName,
         key,
         bsdKV.callbackFunc)



    def GetBSDInput(self, bsdKV, labelCaption = None, className = '', title = '', showStatusIcon = True, width = None):
        self.EnableBSDSupport()
        bsdID = self._MakeBSDIdentityStr(bsdKV)
        className += ' bsd-input'
        inputTitle = ''
        if not showStatusIcon:
            inputTitle = title
        res = self.GetInput(bsdID, labelCaption, className, width=width, title=inputTitle)
        if showStatusIcon:
            res += self.GetBSDStatusIcon(bsdID=bsdID, title=title)
        return res



    def GetBSDSelector(self, bsdKV, elements, labelCaption = None, title = '', elementClass = '', showStatusIcon = True):
        self.EnableBSDSupport()
        bsdID = self._MakeBSDIdentityStr(bsdKV)
        elementClass += ' bsd-input'
        res = self.GetSelect(elements, bsdID, labelCaption, elementClass)
        if showStatusIcon:
            res += self.GetBSDStatusIcon(bsdID=bsdID, title=title)
        return res



    def GetBSDCheck(self, bsdKV, labelCaption = None, className = '', title = '', showStatusIcon = True):
        self.EnableBSDSupport()
        bsdID = self._MakeBSDIdentityStr(bsdKV)
        className += ' bsd-check'
        res = self.GetCheck(bsdID, labelCaption, className, False)
        if showStatusIcon:
            res += self.GetBSDStatusIcon(bsdID=bsdID, title=title)
        return res



    def GetBSDTextArea(self, bsdKV, cols, rows, title = '', labelCaption = '', className = '', innerHtml = None, showStatusIcon = True):
        self.EnableBSDSupport()
        bsdID = self._MakeBSDIdentityStr(bsdKV)
        className += ' bsd-input'
        res = ''
        if showStatusIcon:
            res += self.GetBSDStatusIcon(bsdID=bsdID, title=title)
        res += '<label class="form-label"%(ctrlID)s:label>%(labelCaption)s</label><br>' % {'ctrlID': bsdID,
         'labelCaption': labelCaption}
        res += self.GetTextArea(bsdID, None, className, cols, rows, innerHtml)
        return res



    def GetBSDStatusIcon(self, bsdKV = None, bsdID = None, title = '', className = '', ctrlID = None):
        if not bsdID:
            if not bsdKV:
                raise RuntimeError('GetStatusIcon must be passed a bsdKV val or bsdID!')
            bsdID = self._MakeBSDIdentityStr(bsdKV)
        className = 'a-tip ' + className
        return self.GetA(innerText=self.Image('/img/bsd.png', 'id="%s:img" style="border: medium none;" ' % bsdID), href='/gd/bsd.py', ctrlID=ctrlID, className=className, style=None, onClick=None, title=title, rel='/gd/bsd.py?action=GetBSDStatusInfo&identData=%s' % bsdID)



    def GetBSDIconBtn(self, bsdKV, func, imgSrc, title = '', confirmStr = ''):
        self.EnableBSDSupport()
        bsdID = self._MakeBSDIdentityStr(bsdKV)
        p = {'bsdID': bsdID,
         'func': func,
         'imgSrc': imgSrc,
         'title': title,
         'confirmStr': confirmStr}
        return '<img onclick="%(func)s(\'%(bsdID)s\', \'%(confirmStr)s\')" src="%(imgSrc)s" title="%(title)s" />' % p



    def SetAjaxDefaultUrl(self, url):
        self.ajaxDefaultURL = url



    def EnableAjaxInput(self):
        if 'EnableAjaxInput' in self.enabledJscript:
            return 
        self.enabledJscript.add('EnableAjaxInput')
        jscript = '\n                    function OnChangeAjax(dataID, attr, value, url, action, successFunc) {\n                        if (null == successFunc) successFunc = function(data){};\n                        $.ajax({\n                            url: url,\n                            cache: false,\n                            dataType: \'json\',\n                            data: "action="+ action + "&dataID=" + dataID + "&attr=" + attr + "&value=" +  value,\n                            success: successFunc\n                            }); //end Ajax\n                        };// end Function \n                    '
        self.WriteDirect('jscript', jscript)



    def GetAjaxInput(self, labelCaption, dataID, attr, url, funcName, title = '', ctrlID = '', className = '', minLength = None, width = None, value = None):
        self.EnableAjaxInput()
        minLength = CheckValue('minlength', str(minLength))
        if width:
            width = ' style="width:%spx"' % width
        className = CheckValue('class', className)
        value = CheckValue('value', value)
        res = []
        if labelCaption is not None:
            res.append('<label class="form-label" id="lbl_%s">%s</label>' % (ctrlID, labelCaption))
        attrs = {'ctrlID': ctrlID,
         'className': className,
         'minLength': minLength,
         'width': width,
         'value': value,
         'dataID': dataID,
         'attr': attr,
         'url': url,
         'funcName': funcName,
         'title': title,
         'successFunc': "function(data){$('#%s').val(data)}" % ctrlID}
        res.append('<input id="%(ctrlID)s" \n                       name="%(ctrlID)s"%(className)s%(minLength)s%(width)s%(value)s \n                       onchange="OnChangeAjax(%(dataID)s, \'%(attr)s\', this.value, \'%(url)s\', \'%(funcName)s\', %(successFunc)s )" \n                       title="%(title)s" />\n                   ' % attrs)
        return '\n'.join(res)



    def EnableAjaxA(self):
        if 'EnableAjaxA' not in self.enabledJscript:
            self.enabledJscript.add('EnableAjaxA')
            jscript = '\n                        function OnClickAjaxAnchor(url, action, successFunc) {\n                            if (null == successFunc) successFunc = function(data){}\n                            $.ajax({\n                                url: url,\n                                cache: false,\n                                dataType: \'json\',\n                                data: "action="+ action,\n                                success: successFunc\n                                }); //end Ajax\n                            };// end Function \n                        '
            self.WriteDirect('jscript', jscript)



    def EnableAjaxExpandableTitle(self):
        if 'EnableAjaxExpandableTitle' in self.enabledJscript:
            return 
        self.enabledJscript.add('EnableAjaxExpandableTitle')
        jscript = '\n                    function OnClickExpandableTitle(url, action, dataID, ctrlID) {\n                        var divKey="#div_" + ctrlID;\n                        var icnKey="#icn_" + ctrlID;\n                        if ($("div").find(divKey).css("display") == \'none\'){\n                            $.ajax({\n                                url: url,\n                                cache: false,\n                                data: "action="+ action + "&dataID=" + dataID,\n                                success: function(html){\n                                    if (html.length > 2){\n                                        $("div").find(divKey).empty();\n                                        $("div").find(divKey).append(html);\n                                        $(icnKey).attr("src", "/img/toggle-collapse-dark.png");\n                                        $("div").find(divKey).toggle( );\n                                        }\n                                    }\n                               }); //end Ajax\n                            } // end if\n                            else {\n                                $(icnKey).attr("src", "/img/toggle-expand-dark.png");\n                                $("div").find(divKey).toggle( );\n                            }\n                        };// end Function \n                    '
        self.WriteDirect('jscript', jscript)



    def GetAjaxExpandableTitle(self, innerText, dataID, url, action, ctrlID, title = ''):
        self.EnableAjaxExpandableTitle()
        args = {'ctrlID': ctrlID,
         'url': url,
         'action': action,
         'dataID': dataID,
         'innerText': innerText,
         'title': title}
        args['icon'] = self.Image('/img/toggle-expand-dark.png', 'border=0 id="icn_%(ctrlID)s" onClick="OnClickExpandableTitle(\'%(url)s\', \'%(action)s\', %(dataID)s, %(ctrlID)s)" title="%(title)s" ' % args)
        expand = 'toggle-collapse-dark.png'
        return '%(icon)s %(innerText)s<div id="div_%(ctrlID)s"  style="display:none;" >Hi there this is the div</div>' % args



    def GetAjaxSelect(self, elements, dataID, url, action, attr, ctrlID, title = '', labelCaption = '', elementClass = ''):
        self.EnableAjaxInput()
        args = {'ctrlID': ctrlID,
         'url': url or self.ajaxDefaultURL,
         'action': action,
         'attr': attr,
         'dataID': dataID,
         'title': title,
         'elementClass': elementClass}
        if ctrlID:
            ctrlID = ' id="%s" name="%s"' % (ctrlID, ctrlID)
        opt1 = lambda row: '<option value="%s" %s >%s</option>\n' % (row[0], ['', 'selected'][row[2]], row[1])
        attrTxt = 'class="%(elementClass)s" onchange="OnChangeAjax(%(dataID)s, \'%(attr)s\', this.value, \'%(url)s\', \'%(action)s\', null)" title="%(title)s" ' % args
        return ''.join(['<label class="form-label" for="%s">%s</label>' % (ctrlID, labelCaption),
         self._HtmlWriter__GetElementBegin('select', '%s %s' % (ctrlID, attrTxt)),
         ''.join(map(opt1, elements)),
         self._HtmlWriter__GetElementEnd('select')])



    def GetAjaxCheckbox(self, ctrlID, labelCaption, className, checked, dataID, url, action, attr, title = '', disabled = False, successFunc = 'null'):
        self.EnableAjaxInput()
        className = CheckValue('class', className)
        if checked:
            checked = ' checked ="true"'
        else:
            checked = ''
        res = []
        if labelCaption:
            res.append('<label class="form-label" for="%s">%s</label>' % (ctrlID, labelCaption))
        args = {'ctrlID': ctrlID,
         'className': className,
         'checked': checked,
         'dataID': dataID,
         'attr': attr,
         'url': url,
         'action': action,
         'title': title,
         'disabled': ['', 'disabled'][(disabled or False)],
         'successFunc': successFunc}
        res.append('<input type="checkbox" id="%(ctrlID)s" name="%(ctrlID)s" %(className)s %(checked)s %(disabled)s onchange="OnChangeAjax(%(dataID)s, \'%(attr)s\', this.checked, \'%(url)s\', \'%(action)s\', %(successFunc)s )" title="%(title)s" />' % args)
        return '\n'.join(res)



    def EnableAjaxBtn(self):
        if 'EnableAjaxIconBtn' not in self.enabledJscript:
            self.enabledJscript.add('EnableAjaxIconBtn')
            jscript = '\n                        function OnClickAjaxBtn(url, ajaxArgs, successFunc, confirmTxt, dataType) {\n                            if (null == successFunc) successFunc = function(data){};\n                            if (confirmTxt.length == 0 || confirm(confirmTxt) ) { \n                                $.ajax({\n                                    url: url,\n                                    cache: false,\n                                    dataType: dataType,\n                                    data: ajaxArgs,\n                                    success: successFunc \n                                    }); //end Ajax\n                                };\n                            };// end Function \n                        '
            self.WriteDirect('jscript', jscript)



    def GetAjaxBtn(self, btnText, action, actionKwargs = {}, htmlKWargs = {}, url = None):
        htmlArgStr = self.FormatHtmlKWArgs(htmlKWargs, ['onclick', 'type'])
        (ajaxArgsStr, extraArgs,) = self.FormatAjaxArgs(action, actionKwargs, ['successFunc', 'confirm', 'dataType'])
        args = {'btnText': btnText,
         'url': url or self.ajaxDefaultURL,
         'dataType': 'json',
         'htmlArgs': htmlArgStr,
         'ajaxArgs': ajaxArgsStr,
         'confirm': ''}
        args.update(extraArgs)
        return '<button type="button" onclick="OnClickAjaxBtn(\'%(url)s\', \'%(ajaxArgs)s\', %(successFunc)s, \'%(confirm)s\', \'%(dataType)s\')" \'%(htmlArgs)s\' >%(btnText)s</button>' % args



    def GetAjaxIconBtn(self, imageURL, action, actionKwargs = {}, htmlKwargs = {}, url = None):
        self.EnableAjaxBtn()
        if (url or self.ajaxDefaultURL) is None:
            raise RuntimeError('There is no URL for this call, please pass a URL or set the default RLL')
        (ajaxArgsStr, extraArgs,) = self.FormatAjaxArgs(action, actionKwargs, ['confirm', 'dataType', 'successFunc'])
        htmlArgsStr = self.FormatHtmlKWArgs(htmlKwargs)
        args = {'imageUrl': imageURL,
         'htmlArgs': htmlArgsStr,
         'url': url or self.ajaxDefaultURL,
         'action': action,
         'ajaxArgs': ajaxArgsStr,
         'dataType': 'json',
         'successFunc': 'null',
         'confirm': ''}
        args.update(extraArgs)
        return '<img src="%(imageUrl)s" %(htmlArgs)s onclick="OnClickAjaxBtn(\'%(url)s\', \'%(ajaxArgs)s\', %(successFunc)s, \'%(confirm)s\', \'%(dataType)s\')" />' % args



    def GetAjaxA(self, innerText, action, actionKwargs = {}, htmlKwargs = {}, url = None):
        self.EnableAjaxBtn()
        if (url or self.ajaxDefaultURL) is None:
            raise RuntimeError('There is no URL for this call, please pass a URL or set the default RLL')
        (ajaxArgsStr, extraArgs,) = self.FormatAjaxArgs(action, actionKwargs, ['confirm', 'dataType', 'successFunc'])
        htmlArgsStr = self.FormatHtmlKWArgs(htmlKwargs)
        args = {'innerText': innerText,
         'htmlArgs': htmlArgsStr,
         'url': url or self.ajaxDefaultURL,
         'action': action,
         'ajaxArgs': ajaxArgsStr,
         'dataType': 'json',
         'successFunc': 'null',
         'confirm': ''}
        args.update(extraArgs)
        return '<a %(htmlArgs)s onclick="OnClickAjaxBtn(\'%(url)s\', \'%(ajaxArgs)s\', %(successFunc)s, \'\', \'%(dataType)s\')">%(innerText)s</a>' % args



    def GetJscriptIconBtn(self, func, imgSrc, funcArgs = None, htmlKwargs = {}):
        argStr = self.FormatFunctionArguments(funcArgs)
        htmlArgsStr = self.FormatHtmlKWArgs(htmlKwargs, ['onclick']) + ' onclick="%s(%s)" ' % (func, argStr)
        return '<img src="%(imgSrc)s" %(htmlArgs)s />' % {'imgSrc': imgSrc,
         'htmlArgs': htmlArgsStr}



    def GetJscriptSelect(self, elements, func, funcArgs = None, htmlKwargs = {}):
        argStr = self.FormatFunctionArguments(funcArgs, True)
        htmlArgsStr = self.FormatHtmlKWArgs(htmlKwargs, ['onchange']) + ' onchange="%s(%s this.value)" ' % (func, argStr)
        selectStr = '<select %s >\n' % htmlArgsStr
        selectStr += self.FormatSelectOptions(elements)
        selectStr += '</select>\n'
        return selectStr



    def GetJscriptA(self, innerText, func, funcArgs = None, htmlKwargs = {}):
        argStr = self.FormatFunctionArguments(funcArgs)
        htmlArgsStr = self.FormatHtmlKWArgs(htmlKwargs, ['onclick']) + ' onclick="%s(%s)" ' % (func, argStr)
        return '<a %s ">%s</a>' % (htmlArgsStr, innerText)



    def GetExportedForAction(self, action):
        exported = self.__exportedactions__.get(action)
        if exported is None:
            return 
        if callable(exported):
            exported = exported()
        return exported



    def GetActionArgs(self, request, action):
        exported = self.GetExportedForAction(action)
        if exported is None:
            return 
        if len(exported) and type(exported[0]) in (types.IntType, types.LongType):
            if exported[0] & session.role == 0:
                roles = self.session.ConnectToAnyService('cache').Rowset(const.cacheUserRoles)
                requiredRoles = ''
                for role in roles:
                    if exported[0] & role.roleID == role.roleID:
                        requiredRoles = requiredRoles + role.roleName + ', '

                session.LogSessionError("Called %s::%s, which requires of the following roles: %s, which the user doesn't have" % (request.path, action, requiredRoles))
                raise RoleNotAssignedError(exported[0])
            preargs = exported[1:]
        else:
            preargs = exported
        params = {}
        for each in preargs:
            if request.QueryString(each) is not None:
                params[each] = request.QueryString(each)
            elif request.Form(each) is not None:
                params[each] = request.Form(each)

        return ((), params)




class HtmlWriterEx(HtmlWriter):
    __guid__ = 'htmlwriter.HtmlWriterEx'
    useAutomagicTitles = 1
    useItemProps = 0
    useOwnerProps = 0
    useSessionProps = 0
    usePannelUpdate = 1

    def __init__(self, template = 'script:/wwwroot/lib/template/base.html', populateGlobals = 1):
        HtmlWriter.__init__(self, template)
        self.inserts['stylesheet'] = '/lib/ex.css'
        self.inserts['topMenu'] = ''
        self.inserts['topMenuSub'] = ''
        self.inserts['l1Menu'] = ''
        self.inserts['l1MenuSub'] = ''
        self.inserts['lMenu'] = ''
        self.inserts['lSelected'] = ''
        self.inserts['rMenu'] = ''
        self.inserts['props'] = ''
        self.inserts['floaters'] = ''
        self.inserts['watchlist'] = ''
        self.inserts['body'] = ' onload="SetFocusToFirst();"'
        self.inserts['onload'] = ''
        self.inserts['rMenuWidth'] = 200



    def HandleAction(self, action, request, response):
        self.request = request
        self.response = response
        if action is None:
            action = self.__defaultaction__
        argstuple = self.GetActionArgs(request, action)
        if argstuple:
            (args, kwargs,) = argstuple
            try:
                getattr(self, action)(*args, **kwargs)
            except TypeError as e:
                sm.services['http'].LogError('Bad params (', kwargs, ') sent to ', action, ', resulting in exception: ', e)
                raise 
        else:
            self.Write('Action not listed ' + str(action) + '<br>')
        if self.useAutomagicTitles == 1:
            self.inserts['title'] = self.inserts['title'] + ' - ' + str(action)
            self.inserts['heading'] = self.inserts['title']
        elif self.useAutomagicTitles == 2:
            self.inserts['heading'] = self.inserts['title']



    def AddTopMenu(self, id, disp, help, url, args = None):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        if id:
            self.inserts['topMenu'] = self.inserts['topMenu'] + '        addMSMenu("%s", "%s", "%s", "%s");\n' % (id,
             disp,
             help,
             url)
        else:
            self.inserts['topMenu'] = self.inserts['topMenu'] + '        addMSMenuDivider();\n'



    def AddTopMenuSub(self, parentid, disp, url, args = None, disabled = False):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        d = '%s' % disp
        color = 'gray' if disabled else ''
        self.inserts['topMenuSub'] = self.inserts['topMenuSub'] + '        addMSSubMenu("%s", "%s", "%s", "%s");\n' % (parentid,
         d,
         url,
         color)



    def AddTopMenuSubLine(self, parentid):
        self.inserts['topMenuSub'] = self.inserts['topMenuSub'] + '        addMSSubMenuLine("%s");\n' % parentid



    def AddMenu(self, id, disp, help, url, args = None):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        self.inserts['l1Menu'] = self.inserts['l1Menu'] + '        addICPMenu("%s", "%s", "%s", "%s");\n' % (id,
         disp,
         help,
         url)



    def SelectMenu(self, id, color = '#FFB043'):
        self.inserts['l1Menu'] = self.inserts['l1Menu'] + '        setICPSeleted("%s", "%s");\n' % (id, color)



    def AddMenuSub(self, parentid, disp, url, args = None):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        self.inserts['l1MenuSub'] = self.inserts['l1MenuSub'] + '  addICPSubMenu("%s", "%s", "%s");\n' % (parentid, disp, url)



    def AddHorMenu(self, id, disp, url, args = None):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        self.inserts['l1Menu'] = self.inserts['l1Menu'] + '        AddHorMenuItem("%s", "%s", "%s");\n' % (id, disp, url)



    def SelectHorMenu(self, id):
        self.inserts['l1Menu'] = self.inserts['l1Menu'] + '        setHorSeleted("%s");\n' % id



    def AddLeftHeading(self, id, disp):
        self.inserts['lMenu'] = self.inserts['lMenu'] + '        AddLeftMenu("%s", "%s");\n' % (id, disp)



    def AddLeftMenu(self, parentid, id, disp, url, args = None, cssClass = None):
        if args:
            url = url + '?'
            for (k, v,) in args.iteritems():
                url = url + str(k) + '=' + str(v) + '&'

        if cssClass is None:
            cssClass = ''
        self.inserts['lMenu'] = self.inserts['lMenu'] + '        AddLeftMenuItem("%s","%s","%s","%s","%s");\n' % (parentid,
         id,
         disp,
         url,
         cssClass)



    def ContainerDetails(self, heading, header, lines, opLink = ''):
        s = UnicodeMemStream()
        if heading and len(heading):
            s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
            s.Write('<tr>\n')
            s.Write('<td class="tableOutline" valign="top">\n')
            s.Write('<table border="0" cellpadding="7" cellspacing="1" width="100%">\n')
            s.Write('<tr>\n')
            s.Write('    <td class="tableHeader"><small><b>%s</b></small></td>\n' % (heading,))
            s.Write('</tr>\n')
            s.Write('</table>\n')
            s.Write('</td>\n')
            s.Write('</tr>\n')
            s.Write('</table>\n')
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td class="tableOutline" valign="top">\n')
        s.Write('<table border="0" cellpadding="7" cellspacing="1" width="100%">\n')
        if header and len(header):
            s.Write('<tr>\n')
            for i in header:
                s.Write('    <td class="tableHeader"><b>%s</b></td>\n' % i)

            s.Write('</tr>\n')
        c = 1
        if len(lines):
            for row in lines:
                klass = 'class="tC"'
                if c:
                    c = 0
                else:
                    klass = 'class="tCO"'
                    c = 1
                s.Write('<tr>\n')
                for col in row:
                    if col == row[0] and opLink != '':
                        link = opLink % (col, col)
                        s.Write('    <td %s valign=top><small>%s</small></td>\n' % (klass, link))
                    else:
                        s.Write('    <td %s valign=top><small>%s</small></td>\n' % (klass, unicode(col)))

                s.Write('</tr>\n')

        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return s.Read()



    def WebPart(self, *args, **kw):
        return WebPart(*args, **kw)



    def Floater(self, title, content, ID = 'NotUnique', width = '50%'):
        s = UnicodeMemStream()
        s.Write('<div id="' + str(ID) + '" class="clsFloaterContainer" style="position:absolute;top:0;left:0;width:' + str(width) + ';visibility:hidden;">')
        s.Write('<table id="goup" cellpadding="0" cellspacing="0" class="clsFloater" width="100%" border="0">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="clsFloaterHead" valign="top" align="left" style="width:15" >')
        s.Write('    <img class="clsFloaterHead" src="/lib/webparts/gripgray.gif" height="19" width="15">')
        s.Write('    </td>\n')
        s.Write('    <td class="clsFloaterHead" valign="middle" align="left" width="' + str(width - 45) + '" STYLE="BORDER-TOP:1px solid #999999;">\n')
        s.Write('    <b class="clsFloaterHead">' + title + '</b>\n')
        s.Write('    </td>\n')
        s.Write('    <td class="clsFloaterRight" valign="top" align="right" height="19" width="25" >\n')
        s.Write('    <img class="clsMinimize" src="/lib/webparts/downlevel.gif" height="19" width="25">\n')
        s.Write('    </td>\n')
        s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td colspan="3">\n')
        s.Write('    <table bgcolor="#ffffff" width="100%" cellpadding="0" cellspacing="0" border="0">\n')
        s.Write('    <tr>\n')
        s.Write('        <td bgcolor="#aaaaaa" colspan="1" width="1px" valign="top"><div style="margin:1px;padding:0px;"></div></td>\n')
        s.Write('        <td  colspan="2" bgcolor="#f1f1f1" valign="top" style="padding:10px">\n')
        s.Write(content)
        s.Write('        </td>\n')
        s.Write('        <td bgcolor="#aaaaaa" colspan="1" width="1px" valign="top"><div style="margin:1px;padding:0px;"></div>\n')
        s.Write('        </td>\n')
        s.Write('     </tr>\n')
        s.Write('     <tr>\n')
        s.Write('        <td bgcolor="#aaaaaa" colspan="3" height="1" valign="top"><div style="margin:1px;padding:0px;"></div>\n')
        s.Write('        </td>\n')
        s.Write('     </tr>\n')
        s.Write('     </table>\n')
        s.Write('     </td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</div>\n\n<SCRIPT>prepCentralize("' + str(ID) + '")</SCRIPT>')
        s.Seek(0)
        return s.Read()



    def MessageboardStyles(self, Config):
        s = UnicodeMemStream()
        s.Write('<style type="text/css"> \n')
        s.Write('<!--  \n')
        s.Write('  a:link    {color:%s;text-decoration:%s} \n' % (Config['LinkColor'], Config['LinkTextDecoration']))
        s.Write('  a:visited {color:%s;text-decoration:%s} \n' % (Config['VisitedLinkColor'], Config['VisitedTextDecoration']))
        s.Write('  a:hover   {color:%s;text-decoration:%s} \n' % (Config['HoverLinkColor'], Config['HoverTextDecoration']))
        s.Write('  a:active  {color:%s;text-decoration:%s} \n' % (Config['ActiveLinkColor'], Config['ActiveTextDecoration']))
        s.Write('.mbHead{ \n')
        s.Write('   BACKGROUND-COLOR:%s;\n' % Config['HeadCellColor'])
        s.Write('   COLOR:%s;\n' % Config['HeadFontColor'])
        s.Write('   FONT-FAMILY:%s;\n' % Config['DefaultFontFace'])
        s.Write('   FONT-SIZE:%s;\n' % Config['HeaderFontSize'])
        s.Write(' } \n')
        s.Write('.mbForum{ \n')
        s.Write('   BACKGROUND-COLOR:%s;\n' % Config['ForumCellColor'])
        s.Write('   COLOR:%s;\n' % Config['DefaultFontColor'])
        s.Write('   FONT-FAMILY:%s;\n' % Config['DefaultFontFace'])
        s.Write('   FONT-SIZE:%s;\n' % Config['DefaultFontSize'])
        s.Write(' } \n')
        s.Write('.mbForumFirst{ \n')
        s.Write('   BACKGROUND-COLOR:%s;\n' % Config['ForumFirstCellColor'])
        s.Write('   COLOR:%s;\n' % Config['DefaultFontColor'])
        s.Write('   FONT-FAMILY:%s;\n' % Config['DefaultFontFace'])
        s.Write('   FONT-SIZE:%s;\n' % Config['DefaultFontSize'])
        s.Write(' } \n')
        s.Write('.mbForumAlt{ \n')
        s.Write('   BACKGROUND-COLOR:%s;\n' % Config['ForumAltCellColor'])
        s.Write('   COLOR:%s;\n' % Config['DefaultFontColor'])
        s.Write('   FONT-FAMILY:%s;\n' % Config['DefaultFontFace'])
        s.Write('   FONT-SIZE:%s;\n' % Config['DefaultFontSize'])
        s.Write(' } \n')
        s.Write('--> \n')
        s.Write('</style> \n')
        s.Seek(0)
        return s.Read()



    def MessageboardChannels(self, Data, Config):
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        if len(Data):
            s.Write('<tr>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="10">&nbsp</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>Forums</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="10%%"><b>Posts</font></b></td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="10%%"><b>Last Post</b></td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="10">&nbsp</td>\n')
            s.Write('</tr>\n')
            for d in Data:
                s.Write('<tr>\n')
                s.Write('    <td class="mbForum" align=left valign=middle width="10">&nbsp</td>\n')
                s.Write('    <td class="mbForum" align=left valign=middle><A href="?action=WebTopics&channelID=%s">%s</A><br>%s</td>\n' % (d['channelID'], d['channelName'], d['description']))
                s.Write('    <td class="mbForum" align=center valign=middle Width="10%%">%s</td>\n' % d['numPosts'])
                s.Write('    <td class="mbForum" align=center valign=middle Width="10%%"><nobr>%s</nobr><br>by: <A href="javascript:pop(\'mb_pop.py?action=character&characterID=%s\',\'mb_popChar\',300,400);">%s</A></td>\n' % (util.FmtDate(d['lastPost'], 'ss'), d['lastAuthor'], d['lastAuthorName']))
                s.Write('    <td class="mbForum" align=left valign=middle width="10">&nbsp</td>\n')
                s.Write('</tr>\n')

        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageboardThreads(self, Data, Config, Threads, Page):
        if not Page:
            Page = 1
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        if len(Data):
            s.Write('<tr>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="10">&nbsp</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>Topic</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>Author</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>Replies</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>Read</td>\n')
            s.Write('    <td class="mbHead" align=center valign=middle><b>LastPost</td>\n')
            s.Write('</tr>\n')
            for d in Data:
                replies = d['sc_replies'] - 1
                if replies == -1:
                    replies = 0
                s.Write('<tr>\n')
                s.Write('    <td class="mbForum" align=left valign=middle width="10">&nbsp</td>\n')
                s.Write('    <td class="mbForum" align=left valign=middle><A href="?action=WebTopic&threadID=%s">%s</A>' % (d['threadID'], d['sc_title']))
                if d['sc_replies'] > int(Config['PageSize']):
                    s.Write('<br>&nbsp;&nbsp;&nbsp;' + self.MessageBoardPages(d['sc_replies'], Config['PageSize'], 0, '?action=WebTopic&threadID=' + str(d['threadID']), Config['ActiveLinkColor']))
                s.Write('    </td>\n')
                s.Write('    <td class="mbForum" align=center valign=middle><A href="charpop.py?characterID=%s">%s</A></td>\n' % (d['sc_authorID'], d['authorName']))
                s.Write('    <td class="mbForum" align=center valign=middle>%s</td>\n' % replies)
                s.Write('    <td class="mbForum" align=center valign=middle>%s</td>\n' % d['sc_reads'])
                s.Write('    <td class="mbForum" align=center valign=middle Width="10%%"><nobr>%s</nobr><br>by: <A href="javascript:pop(\'mb_pop.py?action=character&characterID=%s\',\'mb_popChar\',300,400);">%s</A></td>\n' % (util.FmtDate(d['sc_modified'], 'ss'), d['sc_lastauthorID'], d['lastAuthorName']))
                s.Write('</tr>\n')

        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        if Threads > int(Config['PageSize']):
            s.Write('<br>Pages: %s\n' % self.MessageBoardPages(Threads, Config['PageSize'], Page, '?action=WebTopics&channelID=' + str(d['channelID']), Config['ActiveLinkColor']))
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageboardResponses(self, Data, Config, Replies, Page, User):
        if not Page:
            Page = 1
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        if len(Data):
            s.Write('<tr>\n')
            s.Write('    <td class="mbHead" align=center valign=middle width="%s"><b>Author</td>\n' % Config['TopicWidthLeft'])
            s.Write('    <td class="mbHead" align=center valign=middle ><b>Topic</td>\n')
            s.Write('</tr>\n')
            i = 0
            for d in Data:
                if i == 0 and d['line'] == 1:
                    mbClass = 'mbForumFirst'
                elif i % 2 == 0:
                    mbClass = 'mbForumAlt'
                else:
                    mbClass = 'mbForum'
                Edit = ''
                if d['userID'] == User:
                    Edit = ' - <a href="?action=WebEdit&threadID=%s&line=%s">Edit</A>' % (d['threadID'], d['line'])
                s.Write('<tr>\n')
                s.Write('    <td class="%s" align=left valign=top width="%s"><A href="javascript:pop(\'mb_pop.py?action=character&characterID=%s\',\'mb_popChar\',300,400);">%s</A></td>\n' % (mbClass,
                 Config['TopicWidthLeft'],
                 d['authorID'],
                 d['authorName']))
                s.Write('    <td class="%s" align=left valign=top >Posted - %s %s<hr noshade size="1">%s</td>\n' % (mbClass,
                 util.FmtDate(d['created'], 'ss'),
                 Edit,
                 self.MessageBoardFormat(d['text'])))
                s.Write('</tr>\n')
                i = i + 1

        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        if len(Data):
            if Replies > int(Config['PageSize']):
                s.Write('<br>Pages: %s\n' % self.MessageBoardPages(Replies, Config['PageSize'], Page, '?action=WebTopic&threadID=' + str(d['threadID']), Config['ActiveLinkColor']))
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageboardPost(self, postType, channelID, threadID, Data, Config, ActiveCharacter, Characters):
        Header = ''
        text = ''
        line = ''
        if postType == 'Post':
            Header = 'Post New Topic'
            Button = 'Post New Topic'
        if postType == 'Reply':
            Header = 'Reply to Topic'
            Button = 'Post Reply'
        if postType == 'Edit':
            Header = 'Edit'
            Button = '   Update   '
            line = threadID[1]
            threadID = threadID[0]
            text = Data.text
        s = UnicodeMemStream()
        s.Write('<form name="WebPost" method="post" action="?action=%s">\n' % postType)
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbHead" align=center valign=middle colspan=2><b>%s</td>\n' % Header)
        s.Write('</tr>\n')
        if Config['AllowForumCode'] == '1':
            s.Write('<tr>\n')
            s.Write('    <td class="mbForum" align=right valign=center >Format:</td>\n')
            s.Write('    <td class="mbForum" align=left valign=top >Formating of Forum Code</td>\n')
            s.Write('</tr>\n')
        if postType == 'Post':
            s.Write('<tr>\n')
            s.Write('    <td class="mbForum" align=right valign=center >Subject:</td>\n')
            s.Write('    <td class="mbForum" align=left valign=top ><input type="text" name="subject" size=63 /></td>\n')
            s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=right valign=center >Message:</td>\n')
        s.Write('    <td class="mbForum" align=left valign=top ><textarea name=text cols=48 rows=10>%s</textarea></td>\n' % text)
        s.Write('</tr>\n')
        if postType == 'Post' or postType == 'Reply':
            s.Write('<tr>\n')
            s.Write('    <td class="mbForum" align=right valign=center >Character:</td>\n')
            s.Write('    <td class="mbForum" align=left valign=top>')
            s.Write('    <select name=characterID>')
            for char in Characters:
                s.Write('    <option ')
                if session.charid == char.characterID:
                    s.Write('  SELECTED  ')
                s.Write('    value="%s">%s</option>' % (char.characterID, char.characterName))

            s.Write('    </select><input type=checkbox name=signature value=1>Check here to include your profile signature')
            s.Write('    </td>\n')
            s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=right valign=center >&nbsp;</td>\n')
        s.Write('    <td class="mbForum" align=left valign=top >')
        s.Write('    <input type=submit value="%s">\n' % Button)
        s.Write('    <input type=button value="Cancel" onClick="JavaScript:history.go(-1);">\n')
        s.Write('    <input type=button value="Preview">\n')
        s.Write('    <input type=reset value="Reset Fields">\n')
        s.Write('    <input type=hidden name="channelID" value="%s">\n' % channelID)
        s.Write('    <input type=hidden name="threadID"  value="%s">\n' % threadID)
        s.Write('    <input type=hidden name="line"      value="%s">\n' % line)
        s.Write('    </td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</form>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageBoardPages(self, replies, pagesize, current, url, color):
        pages = ''
        if int(replies) > int(pagesize):
            for i in range(1, int(replies / int(pagesize) + 2)):
                style = ''
                if i == current:
                    style = 'STYLE="FONT-WEIGHT:bolder;Color:%s;"' % color
                pages = pages + '<A href="%s&page=%s" %s>%s</A>&nbsp;' % (url,
                 str(i),
                 style,
                 str(i))

        return pages



    def MessageBoardFormat(self, text):
        text = text.replace(chr(13) + chr(10), '<br>')
        return text



    def MessageboardNoCharacter(self, Config):
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbHead" align=center valign=middle><b>No Character</b></td>\n')
        s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=center valign=middle>&nbsp;<br>You must create at least one character before you can participate in the forums.<br>&nbsp;<br>\n')
        s.Write('    <A href="JavaScript:history.go(-1);">Continue</A></td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageboardNotYourCharacter(self, Config):
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbHead" align=center valign=middle><b>Not Your Character</b></td>\n')
        s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=center valign=middle>&nbsp;<br>The character you used to post does for some reason not belong to you!<br>CONCORD has been notified<br>&nbsp;<br>\n')
        s.Write('    <A href="JavaScript:history.go(-1);">Continue</A></td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageBoardNotYourPost(self, Config):
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbHead" align=center valign=middle><b>Not Your Post</b></td>\n')
        s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=center valign=middle>&nbsp;<br>The Post/Reply you trying to edit does for some reason not belong to you!<br>CONCORD has been notified<br>&nbsp;<br>\n')
        s.Write('    <A href="JavaScript:history.go(-1);">Continue</A></td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()



    def MessageBoardEOF(self, Config):
        s = UnicodeMemStream()
        s.Write('<table border="0" cellpadding="0" cellspacing="0" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('<td valign="top" bgcolor="%s">\n' % Config['TableBorderColor'])
        s.Write('<table border="0" cellpadding="4" cellspacing="1" width="100%">\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbHead" align=center valign=middle><b>Data could not be retrieved</b></td>\n')
        s.Write('</tr>\n')
        s.Write('<tr>\n')
        s.Write('    <td class="mbForum" align=center valign=middle>&nbsp;<br>For some reason the data you requested could not be retrieved. [EOF]<br>&nbsp;<br>\n')
        s.Write('    <A href="JavaScript:history.go(-1);">Continue</A></td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Write('</td>\n')
        s.Write('</tr>\n')
        s.Write('</table>\n')
        s.Seek(0)
        return self.MessageboardStyles(Config) + s.Read()




class Form():
    __guid__ = 'htmlwriter.Form'

    def __init__(self, url = '', action = '', method = 'GET', target = '', formName = 'NeedAName', encType = ''):
        self.url = url
        self.formName = formName
        self.action = action
        self.method = method
        self.target = target
        self.elements = []
        self.encType = encType



    def AddDateTimePicker(self, label, dateName, timeName, value):
        v = value.split(' ')
        if len(v) == 1:
            v = (value, '00:00')
        writer = HtmlWriter()
        self.elements.append([label, writer.GetDatePicker(ctrlID=dateName, ctrlCaption=None, ctrlFormat='yy-mm-dd', ctrlValue=v[0], ctrlTitle=''), writer.GetInput(ctrlID=timeName, labelCaption=None, className=None, minLength=None, width='60', value=v[1])])



    def AddDatePicker(self, label, name, value):
        writer = HtmlWriter()
        self.elements.append([label, writer.GetDatePicker(ctrlID=name, ctrlCaption=None, ctrlFormat='yy-mm-dd', ctrlValue=value, ctrlTitle=''), ''])



    def AddText(self, text):
        self.elements.append(['', text, ''])



    def AddHTML(self, html):
        self.elements.append(['', html, ''])



    def AddHTMLWithLabel(self, label, html):
        self.elements.append([label, html, ''])



    def AddReadOnly(self, name, value = '', prettyName = None):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, value, ''])



    def AddHidden(self, name, value = '', prettyName = None):
        self.elements.append(['', '<input type="hidden" name="%s" id="%s" value="%s">' % (name, name, value), ''])



    def AddInput(self, name, value = '', size = 20, text = '', prettyName = None, params = ''):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, self.Input(name, value, size, text, prettyName, params), text])



    def Input(self, name, value = '', size = 20, text = '', prettyName = None, params = ''):
        if prettyName is None:
            prettyName = name
        return '<input type="text" id="%s" name="%s" size="%d" value="%s" %s>' % (name,
         name,
         size,
         value,
         params)



    def AddCheckedInput(self, chkName, edtName, edtValue = '', label = None, chkLabel = '', edtLabel = '', edtSize = 20, chkChecked = 0, chkDisabled = 0, edtParams = '', lblParams = ''):
        if label is None:
            label = chkName + edtName
        self.elements.append([self.Checkbox(chkName, checked=chkChecked, disabled=chkDisabled, prettyName=chkLabel), '<label class="form-label" for="%s" %s>%s</label></td><td>' % (chkName, lblParams, label), self.Input(edtName, value=edtValue, size=edtSize, prettyName=edtLabel, params=edtParams)])



    def AddPassword(self, name, value = '', size = 20, prettyName = None, text = ''):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, '<input type="password" name="%s" size="%d" value="%s">' % (name, size, value), text])



    def AddCheckbox(self, name, text = '', checked = 0, prettyName = None, disabled = 0):
        if prettyName is None:
            prettyName = name
        self.elements.append(['<label class="form-label" for="%s">%s</label>' % (name, prettyName), self.Checkbox(name, text, checked, prettyName, disabled), '<label class="form-label" for="%s">%s</label>' % (name, text)])



    def Checkbox(self, name, text = '', checked = 0, prettyName = None, disabled = 0):
        if prettyName is None:
            prettyName = name
        code = '    <input type="checkbox" id="%s" name="%s"%s%s>' % (name,
         name,
         ['', ' checked'][(not not checked)],
         ['', ' disabled'][(not not disabled)])
        return code



    def AddRadioGroup(self, name, valname, selected = None, prettyName = None):
        if prettyName is None:
            prettyName = name
        bms = UnicodeMemStream()
        if selected is not None:
            checked = ' '
        else:
            checked = 'checked'
        if type(valname) == types.DictType:
            valname = valname.items()
        for (k, v,) in valname:
            if selected is not None and selected == k:
                bms.Write('<input type=radio name="%s" value="%s" checked>%s\n' % (name, k, v))
            else:
                bms.Write('<input type=radio name="%s" value="%s" %s>%s\n' % (name,
                 k,
                 checked,
                 v))
                checked = ' '

        bms.Seek(0)
        self.elements.append([prettyName, bms.Read(), ''])



    def AddSelect(self, name, valname, prettyName = None, selected = None, multiple = 0, evenhandler = '', Text = '', style = None, sort = True):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, self.Select(name, valname, prettyName=prettyName, selected=selected, multiple=multiple, evenhandler=evenhandler, Text=Text, style=style, sort=sort), ''])



    def Select(self, name, valname, prettyName = None, selected = None, multiple = 0, evenhandler = '', Text = '', style = None, sort = True):
        if prettyName is None:
            prettyName = name
        style = CheckValue('style', style)
        bms = UnicodeMemStream()
        if multiple:
            if multiple < 2 or type(multiple) != type(1):
                multiple = 4
            bms.Write('    <select id="%s" name="%s" %s size=%s%s multiple>\n' % (name,
             name,
             evenhandler,
             multiple,
             style))
        else:
            bms.Write('    <select id="%s" name="%s" %s%s>\n' % (name,
             name,
             evenhandler,
             style))
        if type(valname) == type([]):
            for i in valname:
                if selected is not None and (i[0] == selected or multiple and i[0] in selected):
                    bms.Write('        <option value="%s" Selected>%s</option>\n' % (i[0], i[1]))
                else:
                    bms.Write('        <option value="%s">%s</option>\n' % (i[0], i[1]))

        else:
            sortedList = valname.items()
            if sort:
                sortedList.sort(key=lambda (key, value,): value)
            for (key, value,) in sortedList:
                if selected is not None and selected == key:
                    bms.Write('        <option value="%s" selected>%s</option>\n' % (key, value))
                else:
                    bms.Write('        <option value="%s">%s</option>\n' % (key, value))

        bms.Write('    </select> %s\n' % Text)
        bms.Seek(0)
        return bms.Read()



    def AddSoundSelect(self, name, valname, prettyName = None, selected = None, eventHandler = ''):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, self.SoundSelect(name, valname, prettyName, selected, eventHandler), ''])



    def SoundSelect(self, name, valname, prettyName = None, selected = None, eventHandler = ''):
        if prettyName is None:
            prettyName = name
        bms = UnicodeMemStream()
        bms.Write('    <select id="%s" name="%s" onchange="play_%s(this);">\n' % (name, name, name))
        if type(valname) == type([]):
            for i in valname:
                if selected is not None and (i[0] == selected or multiple and i[0] in selected):
                    bms.Write('        <option value="%s" SELECTED>  %s  </option>\n' % (i[0], i[1]))
                else:
                    bms.Write('        <option value="%s">  %s  </option>\n' % (i[0], i[1]))

        else:
            l = valname.items()
            l.sort(lambda x, y: cmp(x[1], y[1]))
            for i in l:
                if selected is not None and selected == i[0]:
                    bms.Write('        <option value="%s" SELECTED>  %s  </option>\n' % (i[0], i[1]))
                else:
                    bms.Write('        <option value="%s">  %s  </option>\n' % (i[0], i[1]))

        bms.Write('    </select> \n')
        bms.Seek(0)
        return bms.Read()



    def AddTextArea(self, name, value = '', cols = 68, rows = 26, prettyName = None, props = ''):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, '    <textarea name="%s" cols=%d rows=%d %s>%s</textarea>' % (name,
          cols,
          rows,
          props,
          value), ''])



    def AddHtmlArea(self, name, value = '', cols = 68, rows = 26, prettyName = None, props = ''):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, '    <textarea name="%s" cols=%d rows=%d %s>%s</textarea>\n<script language=\'javascript1.2\'>editor_generate(\'%s\');</script>' % (name,
          cols,
          rows,
          props,
          value,
          name), ''])



    def AddPicker(self, name, Action, Strokes = 3, prettyName = None, SubmitOnSelect = 0, default = None):
        if prefs.languageID == 'ZH':
            Strokes = 100
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, self.Picker(name, Action, Strokes, prettyName, SubmitOnSelect, default), ''])



    def Picker(self, name, Action, Strokes = 3, prettyName = None, SubmitOnSelect = 0, default = None):
        if prettyName is None:
            prettyName = name
        self.s = UnicodeMemStream()
        if self.formName == 'NeedAName':
            if default is not None:
                OnSelect = ''
                if SubmitOnSelect:
                    OnSelect = 'onChange="this.form.submit();"'
                self.s.Write('<!--BegMark--><SELECT Name="%s" ID="%s" onClick ="%sgoBack(this, event);"  onContextMenu="%sgoBack(this, event);" %s>\n' % (name,
                 name,
                 name,
                 name,
                 OnSelect))
                self.s.Write('<OPTION VALUE="%s" Selected>%s</OPTION>\\n\'\n' % (default[0], default[1]))
                self.s.Write('</SELECT>\n')
                self.s.Write('<!--EndMark-->\n')
            else:
                self.s.Write('<!--BegMark--><input type="text" name="%s" ID="%s" onKeyUp="%sGetSelect(event)"><!--EndMark-->\n' % (name, name, name))
            self.s.Write('<iframe id="ifrGetSelect%s" style="display: none; width:1;height:1;border:0px;"></iframe>\n' % name)
            self.s.Write('<script type="text/javascript">\n')
            self.s.Write('     function %sGetSelect(e){\n' % name)
            self.s.Write('         var el = $("#%s"); \n' % name)
            self.s.Write('         window.status = el.val(); \n')
            self.s.Write('         PressEnter = false; \n')
            self.s.Write('         if((e.keyCode == 13)&&(el.val().length > 0)){PressEnter = true;}; \n')
            self.s.Write('         if(isNaN(el.val())){\n')
            self.s.Write('             if((el.val().length >= %s)||(PressEnter == true)){\n' % Strokes)
            self.s.Write("               document.getElementById('ifrGetSelect%s').src='/lib/pickpopulate.py?action=%s&ReplaceElement=%s&Search='+UESconvertText(el.val())+'&SubmitOnSelect=%s';\n" % (name,
             Action,
             name,
             SubmitOnSelect))
            self.s.Write("               document.getElementById('%s').disabled=true;\n" % name)
            self.s.Write('             }\n')
            self.s.Write('         }\n')
            self.s.Write('     }\n')
            self.s.Write('     function %sgoBack(oElement, e){\n' % name)
            self.s.Write("         if((e.ctrlLeft)||(e.type == 'contextmenu')){\n")
            self.s.Write('             repCode = \'<input type="text" name="%s" id="%s" onKeyUp="%sGetSelect(event)">\';\n' % (name, name, name))
            self.s.Write("             inJect = oElement.parentNode.innerHTML.replace(/^.*(.|\\n)*?<\\!--EndMark-->/gi,'<\\!--BegMark-->'+repCode+'<\\!--EndMark-->');\n")
            self.s.Write('             oElement.parentNode.innerHTML = inJect;\n')
            self.s.Write('             e.cancelBubble = true;\n')
            self.s.Write('         }\n')
            self.s.Write('     }\n')
            self.s.Write('</script>\n')
        elif default is not None:
            OnSelect = ''
            if SubmitOnSelect:
                OnSelect = 'onChange="this.form.submit();"'
            self.s.Write('<!--BegMark--><select Name="%s" ID="%s" onClick ="%s%sgoBack(this, event);"  onContextMenu="%s%sgoBack(this, event);" %s>\n' % (name,
             name,
             self.formName,
             name,
             self.formName,
             name,
             OnSelect))
            self.s.Write('<option value="%s" Selected>%s</option>\\n\'\n' % (default[0], default[1]))
            self.s.Write('</select>\n')
            self.s.Write('<!--EndMark-->\n')
        else:
            self.s.Write('<!--BegMark--><input type="text" name="%s" id="%s" onKeyUp="%s%sGetSelect(event)"><!--EndMark-->\n' % (name,
             name,
             self.formName,
             name))
        self.s.Write('<iframe id="ifrGetSelect%s" style="display: none; width:1;height:1;border:0px;"></iframe>\n\n' % name)
        self.s.Write('<script type="text/javascript">\n')
        self.s.Write('     function %s%sGetSelect(e){\n' % (self.formName, name))
        self.s.Write('         var el = document.%s.%s;\n' % (self.formName, name))
        self.s.Write('         window.status = el.value; \n')
        self.s.Write('         PressEnter = false \n')
        self.s.Write('         if((e.keyCode == 13)&&(el.value.length > 0)){PressEnter = true;} \n')
        self.s.Write('         if(isNaN(el.value)){\n')
        self.s.Write('             if((el.value.length >= %s)||(PressEnter == true)){\n' % Strokes)
        self.s.Write('               document.getElementById("ifrGetSelect%s").src=\'/lib/pickpopulate.py?action=%s&ReplaceElement=%s&Search=\'+UESconvertText(el.value)+\'&SubmitOnSelect=%s&FormName=%s\';\n' % (name,
         Action,
         name,
         SubmitOnSelect,
         self.formName))
        self.s.Write('               el.disabled=true;\n')
        self.s.Write('             }\n')
        self.s.Write('         }\n')
        self.s.Write('     }\n')
        self.s.Write('     function %s%sgoBack(oElement, e){\n' % (self.formName, name))
        self.s.Write("         if((e.ctrlLeft)||(e.type == 'contextmenu')){\n")
        self.s.Write('             repCode = \'<input type="text" name="%s" ID="%s" onKeyUp="%s%sGetSelect(event)">\';\n' % (name,
         name,
         self.formName,
         name))
        self.s.Write("             inJect = oElement.parentNode.innerHTML.replace(/^.*(.|\\n)*?<\\!--EndMark-->/gi,'<\\!--BegMark-->'+repCode+'<\\!--EndMark-->');\n")
        self.s.Write('             oElement.parentNode.innerHTML = inJect;\n')
        self.s.Write('             e.cancelBubble = true;\n')
        self.s.Write('         }\n')
        self.s.Write('     }\n')
        self.s.Write('</script>\n')
        self.s.Seek(0)
        return self.s.Read()



    def AddModal(self, name, url, parameters = {}, initValues = '', size = 20, prettyName = None, width = 350, height = 350, scroll = 0):
        if prettyName is None:
            prettyName = name
        p = '&modalDialoguePopUp=1'
        for (k, v,) in parameters.iteritems():
            p += '&%s=%s' % (k, v)

        self.elements.append(['<a href="javascript:Wopen%s();">%s</a>\n\n<script>\nfunction Wopen%s(){\nmodal=window.open(\'%s?modalDialogueElement=%s%s\',\'modalForm\',\'toolbar=0,location=0,directories=no,status=no,menubar=no,scrollbars=%s,resizable=no,width=%s,height=%s\');\n}\n</script>\n' % (name,
          prettyName,
          name,
          url,
          name,
          p,
          scroll,
          width,
          height), '<input type="text" name="%sDisp" size="%s" id="%sDisp"><input type="hidden" value="%s" name="%s" id="%s">' % (name,
          size,
          name,
          initValues,
          name,
          name), ''])



    def AddButton(self, onClick = '', nm = 'Create', error = '', bolConfirm = 0):
        if bolConfirm:
            onClick = 'onClick="if(confirm(\'Are you sure?\')){%s}"' % onClick
        else:
            onClick = 'onClick="%s"' % onClick
        self.elements.append(['', '<input type="button" name="%s" value="%s"  %s>' % (nm, nm, onClick), error])



    def AddFile(self, name = 'file1', prettyName = None):
        if prettyName is None:
            prettyName = name
        self.elements.append([prettyName, '<input type="file" name="%s">' % name, ''])



    def AddSubmit(self, action = '', nm = 'Create', error = '', bolConfirm = 0, onClick = 0, style = 1, name = 'Post'):
        inLineJavaScript = ''
        if bolConfirm:
            inLineJavaScript = 'onClick="return confirm(\'Are you sure?\')"'
        if onClick != 0:
            inLineJavaScript = 'onClick="%s"' % onClick
        self.elements.append(['', '<input type="submit" id="%s" name="%s" value="%s"  %s>\n<input type="hidden" name="action" value="%s">' % (name,
          name,
          nm,
          inLineJavaScript,
          action), error])
        return self.Generate(style)



    def SetColumnCount(self, columnCount = 0):
        self.elements.append(['/*SETCOLUMNS*/', columnCount])



    def SetColumnWidth(self, n, w = None):
        self.elements.append(['/*SETCOLUMNWIDTH*/', n, w])



    def Generate(self, style = 1):
        self.s = UnicodeMemStream()
        target = ''
        if self.target != '':
            target = 'target="%s"' % self.target
        encType = ''
        if self.encType != '':
            encType = 'enctype="%s"' % self.encType
        if self.url is None and self.action is None:
            self.s.Write('<form name="%s" method="%s" %s>\n' % (self.formName, self.method, target))
        else:
            stuff = self.url.split('#')
            if len(stuff) > 1:
                self.s.Write('<form name="%s" id="%s" action="%s?action=%s" method="%s" %s %s>\n' % (self.formName,
                 self.formName,
                 stuff[0],
                 self.action + '#' + stuff[1],
                 self.method,
                 target,
                 encType))
            else:
                self.s.Write('<form name="%s" id="%s" action="%s?action=%s" method="%s" %s %s>\n' % (self.formName,
                 self.formName,
                 self.url,
                 self.action,
                 self.method,
                 target,
                 encType))
        if style != 2:
            self.s.Write('<table Border=0>\n')
        if style == 1:
            columns = 1
            prevcolumns = []
            width = {}
            i = 0
            while i < len(self.elements):
                self.s.Write('<tr>\n')
                istart = i
                for n in range(columns):
                    try:
                        if istart + n < len(self.elements):
                            element = self.elements[(istart + n)]
                            if element[0] == '/*SETCOLUMNS*/':
                                if element[1]:
                                    prevcolumns.append(columns)
                                    columns = element[1]
                                else:
                                    columns = prevcolumns.pop(-1)
                                self.s.Write('</tr>\n')
                                self.s.Write('</table>\n')
                                self.s.Write('<table Border=0>\n')
                                self.s.Write('<tr>\n')
                                break
                            if element[0] == '/*SETCOLUMNWIDTH*/':
                                width[element[1]] = element[2]
                            else:
                                w = width.get(0, None)
                                if w:
                                    w = 'width=%s' % w
                                else:
                                    w = ''
                                self.s.Write('    <td valign=top %s><font face="Arial,Verdana,Sans-Seriff" size="1">%s</font></td>\n' % (w, element[0]))
                                w = width.get(n + 1, None)
                                if w:
                                    w = 'width=%s' % w
                                else:
                                    w = ''
                                self.s.Write('    <td %s>\n' % w)
                                self.s.Write('    %s %s\n' % (element[1], element[2]))
                                self.s.Write('    </td>\n')

                    finally:
                        i += 1


                self.s.Write('</tr>\n')

        elif style == 0:
            self.s.Write('<tr>')
            for element in self.elements:
                self.s.Write('    <td valign=top>%s</td>\n' % element[0])

            self.s.Write('</tr>')
            self.s.Write('<tr>')
            for element in self.elements:
                self.s.Write('    <td valign=top>%s</font></td>\n' % element[1])

            self.s.Write('</tr>')
        elif style == 2:
            for element in self.elements:
                if not element[0].startswith('/*'):
                    self.s.Write(element[0])
                    self.s.Write(element[1])
                    self.s.Write(element[2])

        if style != 2:
            self.s.Write('</table>')
        self.s.Write('</form>')
        self.s.Seek(0)
        return self.s.Read()



try:
    sm.services['http'].codeCache.clear()
except:
    sys.exc_clear()

