import const
CRIMINAL_FACTIONS = (500010, 500011, 500012, 500019, 500020)

def GetStandingBonus(fromStanding, fromFactionID, skills):
    bonus = 0.0
    bonusType = None
    if fromStanding < 0.0:
        bonus = skills.get(const.typeDiplomacy, 0.0) * 0.4
        bonusType = const.typeDiplomacy
    elif fromStanding > 0.0:
        if fromFactionID is not None and fromFactionID in (500010, 500011, 500012, 500019, 500020):
            bonus = skills.get(const.typeCriminalConnections, 0.0) * 0.4
            bonusType = const.typeCriminalConnections
        else:
            bonus = skills.get(const.typeConnections, 0.0) * 0.4
            bonusType = const.typeConnections
    return (bonusType, bonus)


exports = {'standingUtil.GetStandingBonus': GetStandingBonus}

