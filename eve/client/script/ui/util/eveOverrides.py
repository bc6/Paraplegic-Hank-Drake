import uiutil
import blue
import log
import uicls
import uix
import xtriui
import uiconst
VALID_ICON_ROOTS = ['corps', 'alliance', 'icons']

def PrepareDrag_Standard(dragContainer, dragSource, *args):
    dad = dragContainer
    x = 0
    y = 0
    iconSize = 64
    for node in dragContainer.dragData:
        (nameSpace, className,) = node.__guid__.split('.')
        ns = Import(nameSpace)
        decoClass = getattr(ns, className, None)
        icon = uicls.DraggableIcon(align=uiconst.TOPLEFT, pos=(0, 0, 64, 64))
        icon.left = x * (iconSize + 10)
        icon.top = y * (iconSize + 10)
        if decoClass is not None and issubclass(decoClass, xtriui.InvItem) or node.__guid__ in ('xtriui.FittingSlot', 'xtriui.ModuleButton', 'xtriui.ShipUIModule', 'xtriui.CertSlot'):
            typeID = node.rec.typeID
            MakeTypeIcon(icon, dad, typeID, iconSize, isCopy=getattr(node, 'isCopy', False))
        if node.__guid__ in ('xtriui.TypeIcon', 'listentry.DraggableItem'):
            icon.LoadIconByTypeID(node.typeID)
        elif node.__guid__ in ('listentry.User', 'listentry.Sender', 'listentry.ChatUser', 'listentry.SearchedUser'):
            charinfo = node.info or cfg.eveowners.Get(node.charID)
            uix.GetOwnerLogo(icon, node.charID, iconSize, noServerCall=False)
        elif node.__guid__ in ('listentry.PlaceEntry',):
            icon.LoadIcon('ui_9_64_1')
        elif node.__guid__ in ('listentry.NoteItem',):
            icon.LoadIcon('ui_49_64_3')
        elif node.__guid__ in ('listentry.QuickbarItem', 'listentry.GenericMarketItem'):
            typeID = node.typeID
            MakeTypeIcon(icon, dad, typeID, iconSize)
        elif node.__guid__ in ('listentry.VirtualAgentMissionEntry',):
            icon.LoadIcon('ui_25_64_3')
        elif node.__guid__.startswith('listentry.ContractEntry'):
            iconName = 'ui_64_64_10'
            if 'Auction' in node.__guid__:
                iconName = 'ui_64_64_16'
            elif 'ItemExchange' in node.__guid__:
                iconName = 'ui_64_64_9'
            elif 'Courier' in node.__guid__:
                iconName = 'ui_64_64_13'
            icon.LoadIcon(iconName)
        elif node.__guid__ in ('listentry.FleetFinderEntry',):
            icon.LoadIcon('ui_53_64_16')
        elif node.__guid__ == 'xtriui.ListSurroundingsBtn':
            icon.LoadIconByTypeID(node.typeID, itemID=node.itemID)
        elif node.__guid__ == 'listentry.PaletteEntry':
            icon.LoadIconByTypeID(node.id, itemID=node.id)
        elif node.__guid__ == 'listentry.DungeonTemplateEntry':
            icon.LoadIcon('ui_74_64_15')
        elif node.__guid__ in ('listentry.SkillEntry', 'listentry.SkillQueueSkillEntry'):
            icon.LoadIconByTypeID(node.invtype.typeID)
        elif node.__guid__ in ('listentry.FittingEntry',):
            icon.LoadIcon('ui_17_128_4')
        elif node.__guid__ in ('listentry.MailEntry',):
            icon.LoadIcon('ui_94_64_1')
        elif node.__guid__ in ('listentry.CorpAllianceEntry',):
            icon.LoadIcon('ui_7_64_10')
        elif node.__guid__ in ('neocom.BtnDataNode',):
            icon.LoadIcon(node.iconPath)
        x += 1
        if x >= 3:
            x = 0
            y += 1
        dad.children.append(icon)
        icon.state = uiconst.UI_DISABLED
        if y > 2:
            break

    sm.GetService('audio').StartSoundLoop('DragDropLoop')
    dragContainer.dragSound = 'DragDropLoop'
    return (0, 0)



def MakeTypeIcon(icon, dad, typeID, iconSize, isCopy = False):
    techIcon = uix.GetTechLevelIcon(None, typeID=typeID)
    if techIcon:
        techIcon.left = icon.left
        techIcon.top = icon.top
        dad.children.append(techIcon)
    icon.LoadIconByTypeID(typeID=typeID, size=iconSize, isCopy=isCopy)


uiutil.PrepareDrag_Standard = PrepareDrag_Standard

