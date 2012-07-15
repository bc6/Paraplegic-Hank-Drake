#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/igsUtil.py
import types
import log
MAXEVENTS = 250
IDX_DATETIME = 0
IDX_ITEMID = 1
IDX_ITEMID2 = 2
IDX_INT1 = 3
IDX_INT2 = 4
IDX_INT3 = 5
IDX_CHAR1 = 6
IDX_CHAR2 = 7
IDX_CHAR3 = 8
IDX_FLOAT1 = 9
IDX_FLOAT2 = 10
IDX_FLOAT3 = 11
LISTINDEXDICT = {'infoDate': IDX_DATETIME,
 'itemID': IDX_ITEMID,
 'itemID2': IDX_ITEMID2,
 'int_1': IDX_INT1,
 'int_2': IDX_INT2,
 'int_3': IDX_INT3,
 'char_1': IDX_CHAR1,
 'char_2': IDX_CHAR2,
 'char_3': IDX_CHAR3,
 'float_1': IDX_FLOAT1,
 'float_2': IDX_FLOAT2,
 'float_3': IDX_FLOAT3}

def AggregateEvent(eventTypeID, event, storage, aggregatePath, aggregateKeys, valueIx):
    prevPath = None
    prevKey = None
    for key in aggregateKeys:
        prevPath = aggregatePath
        if event[key] not in aggregatePath:
            aggregatePath[event[key]] = {}
        aggregatePath = aggregatePath[event[key]]
        prevKey = event[key]

    if not len(aggregatePath):
        log.LogInfo('IGS has no record for the current aggregate event. IGS will create a new record for aggregation.')
        prevPath[prevKey] = event
        storage[eventTypeID].append(prevPath[prevKey])
    else:
        log.LogInfo('IGS already has a record for the current aggregate event. IGS will aggregate on non grouping columns.')
        for ix in valueIx.difference([IDX_DATETIME]):
            if type(event[ix]) == types.IntType:
                log.LogInfo('IGS Treating aggregate event parameter at idx=', ix, 'as an Integer')
                if prevPath[prevKey][ix] + event[ix] <= const.maxInt:
                    prevPath[prevKey][ix] += event[ix]
                else:
                    log.LogException('Integer Overflow error on event! Event discarded: Consider using float!')
            elif type(event[ix]) == types.LongType:
                log.LogInfo('IGS Treating aggregate event parameter at idx=', ix, 'as Bigint')
                if prevPath[prevKey][ix] + event[ix] <= const.maxBigint:
                    prevPath[prevKey][ix] += event[ix]
                else:
                    log.LogException('Integer Overflow error on event! Event discared: Consider using float!')
            elif type(event[ix]) == types.FloatType:
                log.LogInfo('IGS Treating aggregate event parameter at idx=', ix, 'as an Float')
                prevPath[prevKey][ix] += event[ix]
            elif ix > 0:
                log.LogException('IGS received data of unhandled datatype!')


exports = {'igsUtil.AggregateEvent': AggregateEvent,
 'igsUtil.LISTINDEXDICT': LISTINDEXDICT,
 'igsUtil.IDX_DATETIME': IDX_DATETIME,
 'igsUtil.IDX_ITEMID': IDX_ITEMID,
 'igsUtil.IDX_ITEMID2': IDX_ITEMID2,
 'igsUtil.IDX_INT1': IDX_INT1,
 'igsUtil.IDX_INT2': IDX_INT2,
 'igsUtil.IDX_INT3': IDX_INT3,
 'igsUtil.IDX_CHAR1': IDX_CHAR1,
 'igsUtil.IDX_CHAR2': IDX_CHAR2,
 'igsUtil.IDX_CHAR3': IDX_CHAR3,
 'igsUtil.IDX_FLOAT1': IDX_FLOAT1,
 'igsUtil.IDX_FLOAT2': IDX_FLOAT2,
 'igsUtil.IDX_FLOAT3': IDX_FLOAT3,
 'igsUtil.MAXEVENTS': MAXEVENTS}