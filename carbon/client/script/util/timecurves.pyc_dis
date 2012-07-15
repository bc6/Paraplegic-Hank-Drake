#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/util/timecurves.py
import blue

def ReadTimeAndSoundCurvesF(tf):
    allCurves = tf.Find(('trinity.TriScalarCurve', 'trinity.TriVectorCurve', 'trinity.TriRotationCurve', 'trinity.TriColorCurve'), -1, 1)
    curves = []
    for curve in allCurves:
        if curve.__typename__[0] == 'T':
            curves.append(curve)

    return curves


def ReadTimeCurvesF(tf):
    return tf.Find(('trinity.TriScalarCurve', 'trinity.TriVectorCurve', 'trinity.TriRotationCurve', 'trinity.TriColorCurve'), -1, 1)


def ResetTimeCurvesF(curves, now = None):
    if not now:
        now = blue.os.GetSimTime()
    for curve in curves:
        curve.start = now


def ResetTimeAndSoundCurvesF(curves):
    mainctx = blue.pyos.taskletTimer.EnterTasklet('ResetTimeAndSoundCurvesF')
    try:
        now = blue.os.GetSimTime()
        prev = blue.pyos.taskletTimer.EnterTasklet('ResetTimeAndSoundCurvesF::Curves')
        try:
            for curve in curves:
                curve.start = now

        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(prev)

    finally:
        blue.pyos.taskletTimer.ReturnFromTasklet(mainctx)


def ReverseTimeCurvesF(curves):
    for curve in curves:
        length = curve.length
        if length > 0.0:
            curve.Sort()
            curve.ScaleTime(-1.0)
            for key in curve.keys:
                key.time = key.time + length

            curve.Sort()


def ScaleTimeF(curves, scaling):
    for curve in curves:
        if curve.length > 0.0:
            curve.ScaleTime(float(scaling))


def SetCurveExtrapolationF(curves, value):
    for curve in curves:
        curve.extrapolation = value


def SetDurationF(curves, duration):
    maxLen = MaxLen(curves)
    if maxLen == 0.0:
        print 'maxlen is less than 0. SetDuration aborted'
        return
    ScaleTime(curves, duration / maxLen)


def MaxLenF(curves):
    maxLen = 0.0
    for curve in curves:
        if curve.length > maxLen:
            maxLen = curve.length

    return maxLen


curvetypes = ['trinity.TriScalarCurve',
 'trinity.TriVectorCurve',
 'trinity.TriRotationCurve',
 'trinity.TriColorCurve']

def ReadCurves(tf):
    return tf.Find(curvetypes)


def ResetTimeCurves(curves, starttime = None, scaling = None):
    if not curves:
        return
    if type(curves) != type([]):
        curves = ReadCurves(curves)
    if starttime is None:
        starttime = blue.os.GetSimTime()
    for curve in curves:
        curve.start = starttime
        if scaling:
            curve.ScaleTime(scaling)


def ResetTimeAndSoundCurves(tf, starttime = None):
    if tf is None:
        return
    if type(tf) != type([]):
        curves = tf.Find(('trinity.TriScalarCurve', 'trinity.TriVectorCurve', 'trinity.TriRotationCurve', 'trinity.TriColorCurve', 'audio.Node', 'audio.SoundNode'), -1, 1)
    else:
        curves = tf
    if starttime is None:
        now = blue.os.GetSimTime()
    else:
        now = starttime
    for curve in curves:
        if curve.__typename__ == 'Node' or curve.__typename__ == 'SoundNode':
            curve.Play()
        else:
            curve.start = now


def ResetTimeAndSoundCurvesAndCuePoints(tf, starttime = None):
    if tf is None:
        return
    if type(tf) != type([]):
        curves = tf.Find(('trinity.TriScalarCurve', 'trinity.TriVectorCurve', 'trinity.TriRotationCurve', 'trinity.TriColorCurve', 'audio.Node', 'audio.SoundNode', 'trinity.TriCuePoints'), -1, 1)
    else:
        curves = tf
    if starttime is None:
        now = blue.os.GetSimTime()
    else:
        now = starttime
    for curve in curves:
        if curve.__typename__ == 'Node' or curve.__typename__ == 'SoundNode':
            curve.Play()
        else:
            curve.start = now


def PlaySounds(tf):
    pass


def ReverseTimeCurves(tf):
    if tf is None:
        return
    if type(tf) != type([]):
        curves = ReadCurves(tf)
    else:
        curves = tf
    if len(curves) == 0:
        return
    for curve in curves:
        length = curve.length
        if length > 0.0:
            curve.Sort()
            curve.ScaleTime(-1.0)
            for key in curve.keys:
                key.time = key.time + length

            curve.Sort()


def ScaleTime(tf, scaling):
    if tf is None:
        return
    now = blue.os.GetSimTime()
    if type(tf) != type([]):
        curves = ReadCurves(tf)
    else:
        curves = tf
    for curve in curves:
        if curve.length > 0.0:
            curve.ScaleTime(float(scaling))


def SetCurveExtrapolation(tf, value):
    if tf is None:
        return
    now = blue.os.GetSimTime()
    if type(tf) != type([]):
        curves = ReadCurves(tf)
    else:
        curves = tf
    for curve in curves:
        curve.extrapolation = value


def SetDuration(tf, duration):
    if type(tf) != type([]):
        curves = ReadCurves(tf)
        maxlen = MaxLen(tf)
    else:
        curves = tf
        maxlen = 0.0
        for curve in curves:
            if curve.length > maxlen:
                maxlen = curve.length

    if maxlen == 0.0:
        print 'maxlen is less than 0. SetDuration aborted'
        return
    scaling = duration / maxlen
    ScaleTime(tf, dscaling)


def MaxLen(tf):
    if type(tf) != type([]):
        curves = ReadCurves(tf)
    else:
        curves = tf
    maxlen = 0.0
    for curve in curves:
        if curve.length > maxlen:
            maxlen = curve.length

    return maxlen


exports = {'timecurves.ReadTimeAndSoundCurvesF': ReadTimeAndSoundCurvesF,
 'timecurves.ReadTimeCurvesF': ReadTimeCurvesF,
 'timecurves.ResetTimeCurvesF': ResetTimeCurvesF,
 'timecurves.ResetTimeAndSoundCurvesF': ResetTimeAndSoundCurvesF,
 'timecurves.ReverseTimeCurvesF': ReverseTimeCurvesF,
 'timecurves.ScaleTimeF': ScaleTimeF,
 'timecurves.SetCurveExtrapolationF': SetCurveExtrapolationF,
 'timecurves.SetDurationF': SetDurationF,
 'timecurves.MaxLenF': MaxLenF,
 'timecurves.ReadCurves': ReadCurves,
 'timecurves.ResetTimeCurves': ResetTimeCurves,
 'timecurves.ResetTimeAndSoundCurves': ResetTimeAndSoundCurves,
 'timecurves.ResetTimeAndSoundCurvesAndCuePoints': ResetTimeAndSoundCurvesAndCuePoints,
 'timecurves.PlaySounds': PlaySounds,
 'timecurves.ReverseTimeCurves': ReverseTimeCurves,
 'timecurves.ScaleTime': ScaleTime,
 'timecurves.SetCurveExtrapolation': SetCurveExtrapolation,
 'timecurves.SetDuration': SetDuration,
 'timecurves.MaxLen': MaxLen}