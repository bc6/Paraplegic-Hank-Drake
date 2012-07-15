#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/net/eveWhitelist.py


def GetWhitelist():
    eveWhitelist = '\n            foo.SlimItem\n            foo.Vector3\n            sys.Standings\n            voucher.Bookmark\n            voucher.PlayerKill\n            voucher.Share\n            voucher.Voucher\n            dbutil.RowList\n            dbutil.RowDict\n            util.Rowset\n            util.FilterRowset\n            util.IndexRowset\n            util.DataSet\n            util.IndexedRows\n            util.SparseRowset\n            util.StackSize\n            util.Singleton\n            util.RamActivityVirtualColumn\n            util.PagedResultSet\n            dogmax.EmbarkOnlineError\n            warUtil.War\n    '
    if boot.role == 'server':
        eveWhitelist += '\n            agent.StandardMissionDetails\n            agent.ResearchMissionDetails\n            agent.StorylineMissionDetails\n            agent.EpicArcMissionDetails\n            agent.OfferDetails\n            agent.LoyaltyPoints\n            agent.Agent\n            agent.Credits\n            agent.Item\n            agent.Entity\n            agent.Objective\n            agent.FetchObjective\n            agent.EncounterObjective\n            agent.DungeonObjective\n            agent.TransportObjective\n            agent.AgentObjective\n            agent.Reward\n            agent.TimeBonusReward\n            agent.MissionReferral\n            agent.Location\n            agent.ItemDeclarationError\n            agent.ItemResolutionFailure\n            agent.TransferItemFailure\n            sys.A\n            sys.AgentString\n            sys.AgentUnicode\n        '
    return eveWhitelist


exports = {'util.GetGameWhitelist': GetWhitelist}