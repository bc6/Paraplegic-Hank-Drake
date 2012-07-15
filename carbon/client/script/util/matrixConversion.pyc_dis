#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/util/matrixConversion.py
import geo2
import trinity

def ConvertGeoToTriMatrix(geoMatrix):
    return ConvertTupleToTriMatrix(geoMatrix)


def ConvertTriToGeoMatrix(triMatrix):
    return ConvertTriToTupleMatrix(triMatrix)


def ConvertTupleToTriMatrix(tupleMatrix):
    return trinity.TriMatrix(tupleMatrix[0][0], tupleMatrix[0][1], tupleMatrix[0][2], tupleMatrix[0][3], tupleMatrix[1][0], tupleMatrix[1][1], tupleMatrix[1][2], tupleMatrix[1][3], tupleMatrix[2][0], tupleMatrix[2][1], tupleMatrix[2][2], tupleMatrix[2][3], tupleMatrix[3][0], tupleMatrix[3][1], tupleMatrix[3][2], tupleMatrix[3][3])


def ConvertTriToTupleMatrix(triMatrix):
    return ((triMatrix._11,
      triMatrix._12,
      triMatrix._13,
      triMatrix._14),
     (triMatrix._21,
      triMatrix._22,
      triMatrix._23,
      triMatrix._24),
     (triMatrix._31,
      triMatrix._32,
      triMatrix._33,
      triMatrix._34),
     (triMatrix._41,
      triMatrix._42,
      triMatrix._43,
      triMatrix._44))


exports = {'util.ConvertGeoToTriMatrix': ConvertGeoToTriMatrix,
 'util.ConvertTriToGeoMatrix': ConvertTriToGeoMatrix,
 'util.ConvertTupleToTriMatrix': ConvertTupleToTriMatrix,
 'util.ConvertTriToTupleMatrix': ConvertTriToTupleMatrix}