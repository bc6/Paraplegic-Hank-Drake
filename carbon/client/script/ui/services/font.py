import blue
import bluepy
import types
import os
import log
import uicls
import uiutil
import uiconst
import fontConst
import const
import types
import trinity
import _PyFreeTypeP as ft
from _PyFreeTypeP import FTC_Manager, FTC_Scaler, FTC_CMapCache, FTC_SBitCache, FTC_ImageType, FTC_SBit, IBBox
from _PyFreeTypeP import Clear_Buffer
globals().update(ft.constants)
FTException = ft.Exception
tmp = 1
exports = {}
for state in ['b', 'i', 'u']:
    exports['fontflags.' + state] = tmp
    tmp *= 2


class FreeType(object):
    __guid__ = 'util.FreeType'

    def __init__(self):
        self.lib = ft.FT_Init_FreeType()
        self.cache = None



    def __del__(self):
        self.Close()



    def Raw(self):
        return self.lib



    def Version(self):
        return ft.FT_Library_Version(self.lib)



    def SetCache(self, cache):
        self.cache = cache



    def Close(self):
        if self.cache:
            del self.cache
            self.cache = None
        if self.lib:
            ft.FT_Done_FreeType(self.lib)
            self.lib = None



    def New_Face(self, filepathname, face_index = 0):
        f = file(filepathname, 'rb')
        return Face(ft.FT_New_File_Face(self.lib, f, face_index), filepathname, self)



    def New_Memory_Face(self, data, face_index = 0):
        return Face(ft.FT_New_Memory_Face(self.lib, data, face_index), '', self)



    def New_File_Face(self, file, face_index = 0):
        return Face(ft.FT_New_File_Face(self.lib, file, face_index), '', self)



    def New_Res_Face(self, path, face_index = 0):
        f = bluepy.PyResFile(path, 'rb')
        return self.New_File_Face(f, face_index)




class CacheManager(ft.FTC_Manager):
    __slots__ = ['cmc', 'sbc']

    def __new__(cls, lib, max_faces = 15, max_sizes = 40, max_bytes = 41943040):
        r = ft.FTC_Manager.__new__(cls, lib.Raw(), max_faces, max_sizes, max_bytes, cls.FaceRequester(lib))
        return r



    def LookupFace(self, face_id):
        return StructWrap.New(ft.FTC_Manager.LookupFace(self, face_id))



    class FaceRequester(object):

        def __init__(self, lib):
            self.lib = lib



        def __call__(self, font_id):
            if callable(font_id):
                return font_id(self.lib)
            index = 0
            coords = None
            if type(font_id) is types.TupleType:
                if len(font_id) == 2:
                    (filename, index,) = font_id
                elif len(font_id) == 3:
                    (filename, index, coords,) = font_id
            else:
                filename = font_id
            face = self.lib.New_Res_Face(filename, index)
            if coords:
                l = []
                for axis in face.Get_MM_Var()[3]:
                    l.append(coords.get(axis[0], 0.0))

                face.Set_Var_Blend_Coordinates(l)
            return face.Detach()




    def CMapCache(self):
        try:
            return self.cmc
        except AttributeError:
            self.cmc = ft.FTC_Manager.CMapCache(self)
            return self.cmc



    def SBitCache(self):
        try:
            return self.sbc
        except AttributeError:
            self.sbc = ft.FTC_Manager.SBitCache(self)
            return self.sbc



    def AddCMapIdx(self, face_ids, encoding = FT_ENCODING_UNICODE):
        r = []
        for id in face_ids:
            idx = self.LookupFace(id).Get_Charmap_Index(encoding)
            if idx >= 0:
                r.append((id, idx))

        return r




class StructWrap(object):
    wraps = {}

    def New(cobj):
        cls = StructWrap.wraps.get(ft.Wrap_GetName(cobj), StructWrap)
        return cls(cobj)


    New = staticmethod(New)

    def __init__(self, cobj):
        self._c = cobj



    def __getattr__(self, attr):
        v = ft.Wrap_GetAttr(self._c, attr)
        if type(v) == type(self._c):
            v = StructWrap.New(v)
        else:
            setattr(self, attr, v)
        return v



    def Dir(self):
        return ft.Wrap_GetDir(self._c)



    def Dict(self):
        r = {}
        for a in self.Dir():
            r[a] = getattr(self, a)

        return r



    def __str__(self):
        return '<Wrapped %s at %s>' % (ft.Wrap_GetName(self._c), id(self))



    def __repr__(self):
        r = '<Wrapped %s: ' % ft.Wrap_GetName(self._c)
        d = self.Dir()
        for a in d[:-1]:
            r += '%s:%s, ' % (repr(a), str(getattr(self, a)))

        a = d[-1]
        r += '%s:%s>' % (repr(a), str(getattr(self, a)))
        return r




class FaceWrap(StructWrap):

    def Get_Postscript_Name(self):
        return ft.FT_Get_Postscript_Name(self._c)



    def Get_Glyph_Name(self, glyph_index):
        return ft.FT_Get_Glyph_Name(self._c, glyph_index)



    def Get_Name_Index(self, glyph_name):
        return ft.FT_Get_Name_Index(self._c, glyph_name)



    def Get_Charmap_Index(self, encoding):
        maps = self.charmaps
        for i in range(len(maps)):
            if maps[i]['encoding'] == encoding:
                return i

        return -1



    def Get_MM_Var(self):
        return ft.FT_Get_MM_Var(self._c)



    def Set_Var_Design_Coordinates(self, coords):
        return ft.FT_Set_Var_Design_Coordinates(self._c, coords)



    def Set_Var_Blend_Coordinates(self, coords):
        return ft.FT_Set_Var_Blend_Coordinates(self._c, coords)


    for a in ft.constants.keys():
        if not a.startswith('FT_FACE_FLAG_'):
            continue
        name = a[13:]
        code = 'def %s(self): return (self.face_flags & %s) != 0' % (name, a)
        exec code


StructWrap.wraps['FT_FaceRec'] = FaceWrap

class Face(FaceWrap):
    __slots__ = ['lib', 'filename', 'data']

    def __init__(self, _face, filename, lib):
        r = FaceWrap.__init__(self, _face)
        self.lib = lib
        self.filename = filename
        self.Select_Charmap(FT_ENCODING_UNICODE)
        return r



    def __del__(self):
        self.Close()



    def Detach(self):
        r = self._c
        self._c = None
        return r



    def Close(self):
        if self._c:
            ft.FT_Done_Face(self._c)
        self._c = None



    def Select_Charmap(self, encoding):
        return ft.FT_Select_Charmap(self._c, encoding)




class CMMeasurer(object):

    def __init__(self, cm, limit = None):
        self.cm = cm
        self.sbc = cm.SBitCache()
        self.cmc = cm.CMapCache()
        self.imageType = FTC_ImageType()
        self.scaler = FTC_Scaler()
        self.scaler.pixel = 1
        self.flags = FT_LOAD_TARGET_LIGHT
        self.Reset(limit)



    def Reset(self, limit = None, *args):
        self.asc = 0
        self.des = 0
        self.height = 0
        self.cursor = 0
        self.last = (None, 0)
        self.limit = limit
        self.bBox = IBBox()



    def AddTextGetRenderData(self, unit, params):
        valid = u''
        validsBits = []
        validStart = self.cursor
        renderData = []
        (n, last, bbox,) = (0, None, None)
        lastURange = -1
        for char in unit:
            unicodeRange = uicore.font.GetUnicodeRange(ord(char))
            if unicodeRange != lastURange:
                if valid:
                    renderData.append((valid,
                     validStart,
                     self.cursor,
                     params,
                     validsBits[:]))
                    validsBits = []
                    validStart = self.cursor
                    valid = u''
                params = uicore.font.AlterParams(params, unicodeRange)
            (cursor, last, bbox, sBit,) = self.AddChar(char, params)
            if self.limit and cursor > self.limit:
                break
            self.cursor = cursor
            self.last = last
            self.bBox.Add(bbox)
            valid += char
            validsBits.append(sBit)
            lastURange = unicodeRange
            n += 1

        if valid:
            renderData.append((valid,
             validStart,
             self.cursor,
             params,
             validsBits[:]))
            validsBits = []
            validStart = self.cursor
            valid = u''
        return (n,
         last,
         bbox,
         renderData)



    def AddText(self, unit, params):
        (n, last, bbox, renderData,) = self.AddTextGetRenderData(unit, params)
        if n and params.underline:
            self.Underline(params)
        return (n, last, bbox)



    def AddSpace(self, size):
        cursor = self.cursor + size
        if cursor > self.limit:
            return False
        self.cursor = cursor
        self.last = (None, 0)
        return True



    def Lookup(self, fgi):
        return self.cm.LookupKerningXP(self.scaler, self.last[1], fgi)



    def AddChar(self, char, params):
        fgi = self.cmc.LookupFB(params.face, ord(char), uicore.font.GetFallbackFonts())
        self.imageType.width = self.scaler.width = self.imageType.height = self.scaler.height = params.fontsize
        kern = 0
        if self.last[0] != fgi[0]:
            self.imageType.flags = params.flags
            self.GetMetrics(fgi[0], params)
        startX = self.cursor + kern
        self.imageType.face_id = fgi[0]
        sBit = self.sbc.Lookup(self.imageType, fgi[1])
        bbox = sBit.BBox().Shift(startX)
        return (startX + sBit.xadvance + (params.letterspace or 0),
         fgi,
         bbox,
         sBit)



    def GetMetrics(self, face_id, params = None):
        self.scaler.face_id = face_id
        m = self.cm.LookupMetrics(self.scaler)
        self.asc = max(self.asc, m.ascender >> 6)
        self.des = min(self.des, m.descender >> 6)
        self.height = self.asc - self.des
        if self.des == 0:
            self.des = min(self.des, self.asc - self.height)



    def Underline(self, params):
        fgi = self.cmc.LookupFB(params.face, ord('_'), uicore.font.GetFallbackFonts())
        self.imageType.face_id = fgi[0]
        sbit = self.sbc.Lookup(self.imageType, fgi[1])
        self.bBox.Add(sbit.BBox())




class CMRenderer(object):

    def __init__(self, cm, target, shift, strong = 0, shadow = [(1, -1, -1090519040)]):
        self.cm = cm
        self.sbc = cm.SBitCache()
        self.cmc = cm.CMapCache()
        self.imageType = FTC_ImageType()
        self.scaler = FTC_Scaler()
        self.scaler.pixel = 1
        self.Reset(target, shift, strong, shadow)



    def Reset(self, bufferData, shift, strong = 0, shadow = [(1, -1, -1090519040)]):
        self.cursor = 0
        self.bufferData = bufferData
        self.shift = shift
        self.strong = strong
        self.shadow = shadow



    def AddTextFast(self, unit, params, sBits):
        (xShift, yShift,) = self.shift
        (data, width, height, pitch,) = self.bufferData
        if self.shadow:
            x = 0
            for sBit in sBits:
                for (sx, sy, scol,) in self.shadow:
                    sBit.ToBuffer(data, width, height, pitch, x + xShift + sx, yShift + sy, scol)

                x += sBit.xadvance + (params.letterspace or 0)

        x = 0
        for sBit in sBits:
            color = params.color or -1
            if type(color) != types.IntType:
                tricol = trinity.TriColor(*color)
                color = tricol.AsInt()
            sBit.ToBuffer(data, width, height, pitch, x + xShift, yShift, color)
            if self.strong:
                sBit.ToBuffer(data, width, height, pitch, x + xShift, yShift, color)
            x += sBit.xadvance + (params.letterspace or 0)

        x -= params.letterspace or 0
        if params.underline and x:
            self.Underline(params, xShift, yShift, x)



    def Underline(self, params, xShift, yShift, underlinewidth):
        fgi = self.cmc.LookupFB(params.face, ord('_'), uicore.font.GetFallbackFonts())
        self.imageType.width = self.imageType.height = self.scaler.width = self.scaler.height = params.fontsize
        self.imageType.flags = params.flags
        self.imageType.face_id = fgi[0]
        (data, width, height, pitch,) = self.bufferData
        sbit = self.sbc.Lookup(self.imageType, fgi[1])
        widthScale = float(underlinewidth) / sbit.width
        if self.shadow:
            for (sx, sy, scol,) in self.shadow:
                sbit.ToBuffer(data, width, height, pitch, xShift + sx, yShift + sy, scol, widthScale, tweak=True)

        color = params.color or -1
        if type(color) != types.IntType:
            tricol = trinity.TriColor(*color)
            color = tricol.AsInt()
        sbit.ToBuffer(data, width, height, pitch, xShift, yShift, color, widthScale, tweak=True)
        if self.strong:
            sbit.ToBuffer(data, width, height, pitch, xShift, yShift, color, widthScale, tweak=True)




class CMGlyphString(list):
    __slots__ = ['cm',
     'cmc',
     'sbc',
     'baseLine',
     'baseHeight',
     'imageType',
     'scaler',
     'last',
     'asc',
     'des',
     'width',
     'shadow',
     'strong',
     'overlays']

    def __init__(self, cm, other = None):
        if other:
            list.__init__(self, other)
        self.cm = cm
        self.cmc = self.cm.CMapCache()
        self.sbc = self.cm.SBitCache()
        self.imageType = FTC_ImageType()
        self.scaler = FTC_Scaler()
        self.scaler.pixel = 1
        self.Reset()



    def __repr__(self):
        return 'CMGlyphString id: %s (%d entries)' % (id(self), len(self))



    def __iadd__(self, other):
        list.extend(self, other)
        return self



    def Reset(self):
        self.baseLine = 0
        self.baseHeight = 0
        self.last = (None, 0)
        self.asc = 0
        self.des = 0
        self.width = 0
        self.strong = 0
        self.shadow = None
        while self:
            list.pop(self)




    def Remove(self, startIdx, endIdx):
        for i in xrange(startIdx, endIdx):
            self.pop(startIdx)




    def FlushFromIndex(self, idx):
        while len(self) > idx:
            list.pop(self, -1)




    def FlushToIndex(self, idx):
        for i in xrange(idx):
            if len(self):
                list.pop(self, 0)




    def Insert(self, params, text, idx, align = 0):
        letterspace = params.letterspace or 0
        color = params.color or -1
        if type(color) != types.IntType:
            tricol = trinity.TriColor(*color)
            color = tricol.AsInt()
        wordspace = params.wordspace
        last = (None, 0)
        lastURange = -1
        for char in text:
            unicodeRange = uicore.font.GetUnicodeRange(ord(char))
            if unicodeRange != lastURange:
                newParams = uicore.font.AlterParams(params, unicodeRange)
            lastURange = unicodeRange
            if char == u'\xa0':
                rchar = u' '
            else:
                rchar = char
            fgi = self.cmc.LookupFB(newParams.face, ord(rchar), uicore.font.GetFallbackFonts())
            if fgi[0] != last[0] or self.scaler.height != newParams.fontsize:
                self.imageType.width = self.imageType.height = self.scaler.width = self.scaler.height = newParams.fontsize
                self.imageType.flags = newParams.flags
                self.imageType.face_id = fgi[0]
                self.GetMetrics(fgi[0])
                self.baseLine = max(self.baseLine, self.asc)
                self.baseHeight = max(self.baseHeight, self.asc - self.des)
                kern = 0
            else:
                kern = self.cm.LookupKerningXP(self.scaler, last[1], fgi[1])
            last = fgi
            sbit = self.sbc.Lookup(self.imageType, fgi[1])
            advance = sbit.xadvance + (letterspace or 0) + kern
            if rchar == u' ':
                advance += wordspace
            self.insert(idx, (advance,
             align,
             color,
             sbit,
             char,
             self.asc,
             self.des,
             newParams.Copy()))
            idx += 1




    def Reload(self):
        data = [ (params, char) for (advance, align, color, sbit, char, asc, des, params,) in self ]
        del self[:]
        for (params, char,) in data:
            self.Append(params, char)




    def Append(self, params, text, align = 0):
        letterspace = params.letterspace or 0
        color = params.color or -1
        if type(color) != types.IntType:
            tricol = trinity.TriColor(*color)
            color = tricol.AsInt()
        wordspace = params.wordspace
        width = self.width
        last = self.last
        lastURange = -1
        for char in text:
            unicodeRange = uicore.font.GetUnicodeRange(ord(char))
            if unicodeRange != lastURange:
                newParams = uicore.font.AlterParams(params, unicodeRange)
            lastURange = unicodeRange
            if char == u'\xa0':
                rchar = u' '
            else:
                rchar = char
            fgi = self.cmc.LookupFB(newParams.face, ord(rchar), uicore.font.GetFallbackFonts())
            if fgi[0] != last[0] or self.scaler.height != newParams.fontsize:
                self.imageType.width = self.imageType.height = self.scaler.width = self.scaler.height = newParams.fontsize
                self.imageType.flags = newParams.flags
                self.imageType.face_id = fgi[0]
                self.GetMetrics(fgi[0])
                self.baseLine = max(self.baseLine, self.asc)
                self.baseHeight = max(self.baseHeight, self.asc - self.des)
                kern = 0
            else:
                kern = self.cm.LookupKerningXP(self.scaler, last[1], fgi[1])
            last = fgi
            sbit = self.sbc.Lookup(self.imageType, fgi[1])
            advance = sbit.xadvance + (letterspace or 0) + kern
            if rchar == u' ':
                advance += wordspace
            self.append((advance,
             align,
             color,
             sbit,
             char,
             self.asc,
             self.des,
             newParams))
            width += advance

        self.last = last
        self.width = width
        return params



    def GetMetrics(self, face_id):
        self.scaler.face_id = self.imageType.face_id = face_id
        m = self.cm.LookupMetrics(self.scaler)
        self.asc = m.ascender >> 6
        self.des = m.descender >> 6
        if self.des == 0:
            self.des = self.asc - (m.height >> 6)



    def AddSpace(self, params, width = 0.0):
        newParams = uicore.font.AlterParams(params)
        fgi = self.cmc.LookupFB(newParams.face, ord(' '), uicore.font.GetFallbackFonts())
        self.imageType.face_id = fgi[0]
        sbit = self.sbc.Lookup(self.imageType, fgi[1])
        self.append((width,
         0,
         -1,
         sbit,
         None,
         0,
         0,
         newParams))
        self.width = max(self.width, self.width + width)



    def GetBBox(self):
        baseLine = baseHeight = 0
        bbox = IBBox()
        x = 0
        for t in self:
            bbox.Add(t[3].BBox().Shift(x))
            baseLine = max(baseLine, t[5])
            baseHeight = max(baseHeight, t[5] - t[6])
            x += t[0]

        self.baseLine = baseLine
        self.baseHeight = baseHeight
        self.width = x
        return bbox



    def GetWidth(self):
        return self.width



    def DrawToBuf(self, buf, bx0, by0, checkUnderline = 1):
        x = 0
        activeUnderline = None
        for t in self:
            (asc, des,) = (t[5], t[6])
            g = t[3]
            (shadowshiftX, shadowshiftY,) = (0, 0)
            if self.shadow:
                shadowshiftY = self.shadow[-1][1]
                for (sx, sy, scol,) in self.shadow:
                    g.ToBuffer(buf.data, buf.width, buf.height, buf.pitch, x + bx0 + sx, by0 + sy - shadowshiftY, scol)

            params = t[7]
            color = params.color or -1
            if type(color) != types.IntType:
                tricol = trinity.TriColor(*color)
                color = tricol.AsInt()
            g.ToBuffer(buf.data, buf.width, buf.height, buf.pitch, x + bx0, by0 - shadowshiftY, color)
            if self.strong:
                g.ToBuffer(buf.data, buf.width, buf.height, buf.pitch, x + bx0, by0 - shadowshiftY, color)
            hasUnderline = bool(params.underline)
            if hasUnderline:
                if activeUnderline and activeUnderline[-1] != (params.face,
                 params.fontsize,
                 color,
                 params.flags):
                    self.DrawUnderline(buf, activeUnderline)
                    activeUnderline = None
                if activeUnderline:
                    activeUnderline[1] = x + bx0 + t[0]
                else:
                    activeUnderline = [x + bx0,
                     x + bx0 + t[0],
                     by0 - shadowshiftY,
                     buf.pitch,
                     asc,
                     des,
                     (params.face,
                      params.fontsize,
                      color,
                      params.flags)]
            elif activeUnderline:
                self.DrawUnderline(buf, activeUnderline)
                activeUnderline = None
            x += t[0]

        if activeUnderline:
            self.DrawUnderline(buf, activeUnderline)



    def DrawUnderline(self, buf, ulData):
        (xStart, xEnd, y, pitch, asc, des, (face, fontsize, color, flags,),) = ulData
        xStart = max(0, xStart)
        ulfgi = self.cmc.LookupFB(face, ord('_'), uicore.font.GetFallbackFonts())
        self.imageType.width = self.imageType.height = self.scaler.width = self.scaler.height = fontsize
        self.imageType.flags = flags
        self.GetMetrics(ulfgi[0])
        sbit = self.sbc.Lookup(self.imageType, ulfgi[1])
        widthScale = float(xEnd - xStart) / sbit.width
        sbit.ToBuffer(buf.data, buf.width, buf.height, pitch, xStart - sbit.left * widthScale, y, color, widthScale, tweak=True)



import re
tag = re.compile('<color=0x.*?>|<right>|<center>|<left>')
import service

class Font(service.Service):
    default_unicodeRange = 0
    __guid__ = 'svc.font'
    __update_on_reload__ = 1
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.Release()
        self.freetype = FreeType()
        self.fontcache = CacheManager(self.freetype)
        self.freetype.SetCache(self.fontcache)



    def Stop(self, stream):
        pass



    def Release(self):
        self.fontcache = None
        self.cmapIdx = {}
        self.fallbackFonts = None
        self.measureCache = {}
        self.textmeasurer = None
        self.textMeasureCache = {}
        self.GetFallbackFonts()
        self.defaultFaces = {}



    def DeTag(self, s):
        return tag.sub('', s)



    def GetTextHeight(self, strng, width = 0, font = None, fontsize = None, linespace = None, letterspace = 0, autowidth = 0, singleline = 0, shadow = [(1, -1, -1090519040)], uppercase = 0, specialIndent = 0, getTextObj = 0, tabs = []):
        if strng is None or strng == '':
            return 0
        font = font or fontConst.DEFAULT_FONT
        fontsize = fontsize or fontConst.DEFAULT_FONTSIZE
        letterspace = letterspace or fontConst.DEFAULT_LETTERSPACE
        uppercase = uppercase or fontConst.DEFAULT_UPPERCASE
        if singleline:
            width = 0
            strng = u'\xd3gd'
        cacheKey = (strng,
         width,
         font,
         fontsize,
         linespace,
         letterspace,
         singleline,
         uppercase,
         specialIndent,
         getTextObj)
        cache = self.GetCache(cacheKey)
        if cache:
            return cache
        t = uicls.Label(text=strng, parent=None, align=uiconst.TOPLEFT, width=width, autowidth=autowidth, autoheight=1, tabs=tabs, fontsize=fontsize, linespace=linespace, letterspace=letterspace, singleline=singleline, uppercase=uppercase, specialIndent=specialIndent, font=font, shadow=shadow, measuringText=not getTextObj)
        if getTextObj:
            retval = t
        else:
            retval = t.textheight
        self.SetCache(cacheKey, retval)
        return retval



    def GetTextWidth(self, strng, fontsize = 12, letterspace = 0, uppercase = 0, font = None):
        if not strng:
            return 0
        font = font or fontConst.DEFAULT_FONT
        fontsize = fontsize or fontConst.DEFAULT_FONTSIZE
        letterspace = letterspace or fontConst.DEFAULT_LETTERSPACE
        uppercase = uppercase or fontConst.DEFAULT_UPPERCASE
        cacheKey = (strng,
         fontsize,
         letterspace,
         uppercase,
         font)
        if cacheKey in self.textMeasureCache:
            return self.textMeasureCache[cacheKey]
        if '<br>' in strng:
            val = max([ self.GetTextWidth(line, fontsize, letterspace, uppercase, font) for line in strng.split('<br>') ])
        else:
            textmeasurer = uicls.Label(text=uiutil.StripTags(strng, ignoredTags=['b']), parent=None, align=uiconst.TOPLEFT, autowidth=1, autoheight=1, fontsize=fontsize, letterspace=letterspace, uppercase=uppercase, font=font, measuringText=True)
            val = textmeasurer.textwidth
        self.textMeasureCache[cacheKey] = val
        return val



    def MeasureTabstops(self, stringsData, margin = None, minwidth = 32):
        if margin is None:
            margin = 6
        tabstops = []
        tabCount = 0
        for stringData in stringsData:
            if len(stringData) == 5:
                (tabSeperatedColumns, fontsize, letterSpace, shift, uppercase,) = stringData
            else:
                (tabSeperatedColumns, fontsize, letterSpace, shift,) = stringData
                uppercase = 0
            columnTexts = tabSeperatedColumns.split('<t>')
            columnTextsCount = len(columnTexts)
            if columnTextsCount > tabCount:
                tabstops.extend([minwidth] * (columnTextsCount - tabCount))
                tabCount = columnTextsCount
            i = 0
            for columnText in columnTexts:
                width = max(0, shift - margin) + margin + self.GetTextWidth(columnText, fontsize, letterSpace, uppercase) + margin + 2
                if width > tabstops[i]:
                    tabstops[i] = width
                i += 1
                shift = 0


        i = 1
        while i < tabCount:
            tabstops[i] += tabstops[(i - 1)]
            i += 1

        return tabstops



    def MergeTabstops(self, tabs1, tabs2):
        (t1, t2,) = (self.GetTabstopsAsWidth(tabs1), self.GetTabstopsAsWidth(tabs2))
        if not len(t2) and len(t1):
            return tabs1
        if not len(t1) and len(t2):
            return tabs2
        if not len(t1) and not len(t2):
            return []
        newtabs = [max(t1[0], t2[0])]
        for i in xrange(len(t1) - 1):
            if len(t1) > i + 1:
                _t1 = t1[(i + 1)]
            else:
                _t1 = 0
            if len(t2) > i + 1:
                _t2 = t2[(i + 1)]
            else:
                _t2 = 0
            newtabs.append(newtabs[i] + max(_t1, _t2))

        return newtabs



    def GetTabstopsAsWidth(self, tabs1):
        tabs = tabs1[:1]
        for i in xrange(len(tabs1) - 1):
            tabs.append(tabs1[(i + 1)] - tabs1[i])

        return tabs



    def GetNodeCopyData(self, node, fromIdx, toIdx):
        glyphString = self.GetLineGlyphString(node)
        if glyphString:
            if toIdx == -1:
                return ''.join([ glyph[4] or ' ' for glyph in glyphString[fromIdx:] ])
            else:
                return ''.join([ glyph[4] or ' ' for glyph in glyphString[fromIdx:toIdx] ])
        return ''



    def GetLineGlyphString(self, node):
        return node.get('glyphString', None)



    def GetLetterIdx(self, node, cursorXpos):
        i = 0
        glyphString = self.GetLineGlyphString(node)
        if glyphString:
            w = 0
            for glyph in glyphString:
                if w <= cursorXpos <= w + glyph[0]:
                    glyphCenter = glyph[0] / 2.0
                    if cursorXpos > w + glyphCenter:
                        return (i + 1, int(w + glyph[0]))
                    return (i, int(w))
                i += 1
                w += glyph[0]

            if cursorXpos > w:
                return (i, int(w))
        return (0, 0)



    def GetWidthToIdx(self, node, idx, getWidth = 0):
        glyphString = self.GetLineGlyphString(node)
        if glyphString:
            if idx < len(glyphString):
                w = sum([ t[0] for t in glyphString[:idx] ])
                if getWidth:
                    return (int(w), int(glyphString[idx][0]))
                else:
                    return int(w)
            else:
                w = sum([ t[0] for t in glyphString ])
                if getWidth:
                    return (int(w), 0)
                else:
                    return int(w)
        if getWidth:
            return (0, 0)
        else:
            return 0



    def AlterParams(self, params, unicodeRange = None, formatLinks = False):
        if unicodeRange is None:
            unicodeRange = self.default_unicodeRange
        if not params.face:
            params.face = self.GetFace(params.font)
        if not params.face:
            params.face = self.GetFace(fontConst.DEFAULT_FONT)
        params.flags = params.flags or FT_LOAD_TARGET_LIGHT
        return params



    def GetUnicodeRange(self, charIdx):
        if charIdx < 256:
            return 1
        if self.IsAsian(charIdx):
            return 2
        return 0



    def GetFace(self, fontpath, *args):
        if fontpath is None:
            return 
        if fontpath in self.defaultFaces:
            return self.defaultFaces[fontpath]
        seekfontpath = fontpath
        if fontpath.startswith('res:'):
            seekfontpath = fontpath.replace('res:', blue.os.respath)
        elif fontpath.find(':') == -1:
            fontDir = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS)
            seekfontpath = fontDir + '/' + fontpath
        try:
            f = self.freetype.New_Res_Face(seekfontpath)
            charmapIndex = f.Get_Charmap_Index(FT_ENCODING_UNICODE)
            self.defaultFaces[fontpath] = (seekfontpath, charmapIndex)
            return (seekfontpath, charmapIndex)
        except:
            self.defaultFaces[fontpath] = None



    def IsAsian(self, char):
        return bool(12288 <= char <= 12591 or 12688 <= char <= 19893 or 19904 <= char <= 40891 or 40960 <= char <= 42191 or 63744 <= char <= 64255 or 65072 <= char <= 65103 or 131072 <= char <= 173782)



    def GetCache(self, key):
        cache = self.measureCache.get(key, None)
        if cache:
            return cache[1]



    def SetCache(self, key, value):
        ts = blue.os.GetTime()
        self.measureCache[key] = (ts, value)



    def InvalidateTextMeasureCache(self):
        t = blue.os.GetTime()
        ks = self.measureCache.keys()
        for k in ks:
            cacheTime = self.measureCache[k][0]
            if t - cacheTime > const.SEC * 30:
                del self.measureCache[k]




    def GetParams(self):
        fontParams = uiutil.Bunch()
        fontParams.__doc__ = 'Font Parameters'
        fontParams.font = fontConst.DEFAULT_FONT
        fontParams.fontsize = fontConst.DEFAULT_FONTSIZE
        fontParams.letterspace = fontConst.DEFAULT_LETTERSPACE or 0
        fontParams.uppercase = fontConst.DEFAULT_UPPERCASE
        fontParams.linespace = fontConst.DEFAULT_LINESPACE
        fontParams.wordspace = 0
        fontParams.color = -1
        fontParams.underline = 0
        fontParams.bold = 0
        fontParams.italic = 0
        fontParams.flags = FT_LOAD_TARGET_LIGHT
        fontParams.face = None
        return fontParams



    def GetRenderer(self):
        return CMRenderer(self.fontcache, None, 0, 1)



    def GetMeasurer(self):
        return CMMeasurer(self.fontcache)



    def GetGlyphString(self):
        return CMGlyphString(self.fontcache)



    def Clear_Buffer(self, data, width, height, pitch):
        Clear_Buffer(data, width, height, pitch)



    def GetFallbackFonts(self, new = 0):
        if self.fallbackFonts and not new:
            return self.fallbackFonts
        syspref = ['arialuni.ttf', 'arialuni.ttc']
        fontDir = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS)
        valid = []
        for name in syspref:
            fullname = fontDir + '/' + name
            try:
                f = self.freetype.New_Res_Face(fullname)
                valid.append((fullname, f.Get_Charmap_Index(FT_ENCODING_UNICODE)))
            except Exception as e:
                continue

        if not valid:
            return self.GetFallbackFontsBrutally()
        self.fallbackFonts = valid
        self.AppSetSetting('fontCache_v4', self.fallbackFonts)
        return self.fallbackFonts



    def GetFallbackFontsBrutally(self, new = 0):
        if self.fallbackFonts and not new:
            return self.fallbackFonts
        if not new and self.CheckCache():
            return self.fallbackFonts
        fontDir = blue.win32.SHGetFolderPath(blue.win32.CSIDL_FONTS)
        fonts = os.listdir(fontDir)
        cands = [ font for font in fonts if font.lower().endswith('ttf') or font.lower().endswith('ttc') ]
        fontsByGlyphCount = []
        for name in cands:
            fullname = fontDir + '/' + name
            try:
                f = self.freetype.New_Res_Face(fullname)
                if f.num_glyphs > 1000:
                    fontsByGlyphCount.append((f.num_glyphs, fullname, f.Get_Charmap_Index(FT_ENCODING_UNICODE)))
            except:
                continue

        fontsByGlyphCount.sort()
        fontsByGlyphCount.reverse()
        fontsByGlyphCount = fontsByGlyphCount[:10]
        self.fallbackFonts = [ (c[1], c[2]) for c in fontsByGlyphCount ]
        self.AppSetSetting('fontCache_v4', self.fallbackFonts)
        return self.fallbackFonts



    def CheckCache(self):
        cache = self.AppGetSetting('fontCache_v4', [])
        if not cache:
            return False
        for (path, idx,) in cache:
            try:
                f = self.freetype.New_Res_Face(path)
            except:
                return False

        self.fallbackFonts = cache
        return True



    def AppGetSetting(self, setting, default):
        try:
            return settings.public.ui.Get(setting, default)
        except (AttributeError, NameError):
            return default



    def AppSetSetting(self, setting, value):
        try:
            settings.public.ui.Set(setting, value)
        except (AttributeError, NameError):
            pass




