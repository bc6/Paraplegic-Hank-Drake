#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/guidUtils.py
import zlib
import uuid

def MakeGUID():
    return uuid.uuid4().int


def MakePUID():
    uuidstr = uuid.uuid4().hex
    return zlib.crc32(uuidstr)


exports = {'util.MakeGUID': MakeGUID,
 'util.MakePUID': MakePUID}