import random
import sys
import types
floatType = types.FloatType
rand = random.random
rang = random.randrange
choice = random.choice
maxint = sys.maxint

def ChooseAccum(accumList, roll):
    for (accum, item,) in accumList:
        if accum > roll:
            return item

    raise AssertionError



def SumWeights(weightList):
    sum = 0
    accumList = []
    for i in range(len(weightList)):
        sum += weightList[i][0]
        accumList.append((sum, weightList[i][1]))

    return (sum, accumList)



def ChooseWeighted(weightList):
    (tot, accumList,) = SumWeights(weightList)
    if not tot:
        return random.choice(map(lambda i: i[1], weightList))
    if type(tot) == floatType:
        roll = rand() * tot
    else:
        maxi = maxint
        roll = rang(maxi) * maxi + rang(maxi)
        roll = roll * tot / (maxi * maxi)
    return ChooseAccum(accumList, roll)


exports = {'util.weightedChoice': ChooseWeighted}

