import util
CONTACTSGROUP = (1, 0)
TRADEGROUP = (2, 0)
CONTAINERGROUPS = (3, 0)
CHANGESGROUP = (4, 0)
DESTRUCTIVEGROUP = (5, 0)
SELECTIONGROUP = (6, 0)
SHOWINFOGROUP = (7, 0)
GMWMEXTRAS = (8, 0)
SUBGROUP1 = (9, 0)
ACTIONSGROUP = (11, 0)
CORPGROUP = (12, 0)
RAGEQUITGROUP = (13, 0)
FLEETGROUP = (14, 0)
CONFIGGROUP = (16, 0)
NAVIGATIONGROUP2 = (15, 0)
SHIPSPECIALGROUP = (17, 0)
CONTACTSGROUP2 = (18, 0)
ACTIONSGROUP2 = (19, 0)
BLUEPRINTGROUP = (20, 0)
menuGroupsFromCaption = {mls.UI_CONTACTS_ADDALLIANCECONTACT: CONTACTSGROUP,
 mls.UI_CONTACTS_ADDTOCONTACTS: CONTACTSGROUP,
 mls.UI_CONTACTS_ADDCORPCONTACT: CONTACTSGROUP,
 mls.UI_CMD_ADDTOADDRESSBOOK: CONTACTSGROUP,
 mls.UI_CMD_ADDTOADDRESSBOOK: CONTACTSGROUP,
 mls.UI_CMD_BLOCK: CONTACTSGROUP,
 mls.UI_CONTACTS_BLOCKED: CONTACTSGROUP,
 mls.UI_CONTACTS_REMOVECORPCONTACT: CONTACTSGROUP,
 mls.UI_CONTACTS_REMOVEALLIANCECONTACT: CONTACTSGROUP,
 mls.UI_CMD_REMOVEFROMADDRESSBOOK: CONTACTSGROUP,
 mls.UI_CONTACTS_REMOVEFROMCONTACTS: CONTACTSGROUP,
 mls.UI_EVEMAIL_REMOVELABEL: CONTACTSGROUP,
 mls.UI_EVEMAIL_ASSIGNLABEL: CONTACTSGROUP,
 mls.UI_CONTACTS_EDITALLIANCECONTACT: CONTACTSGROUP,
 mls.UI_CONTACTS_EDITCONTACT: CONTACTSGROUP,
 mls.UI_CONTACTS_EDITCORPCONTACT: CONTACTSGROUP,
 mls.UI_CMD_FORMFLEETWITH: CONTACTSGROUP2,
 mls.UI_CMD_CAPTUREPORTRAIT: CONTACTSGROUP2,
 mls.UI_CMD_STARTCONVERSATION: CONTACTSGROUP2,
 mls.UI_CMD_INVITETO: CONTACTSGROUP2,
 mls.UI_CMD_SENDMESSAGE: CONTACTSGROUP2,
 mls.UI_CMD_BUYTHISTYPE: TRADEGROUP,
 mls.UI_CONTRACTS_FINDMORE: TRADEGROUP,
 mls.UI_CONTRACTS_IGNOREFROMTHIS: TRADEGROUP,
 mls.UI_CMD_SELLTHISITEM: TRADEGROUP,
 mls.UI_CMD_TRADE: TRADEGROUP,
 mls.UI_CMD_TRANSFERMONEYFROM: TRADEGROUP,
 mls.UI_CMD_TRANSFERMONEYTO: TRADEGROUP,
 mls.UI_STATION_TRANSFER_OWNERSHIP: TRADEGROUP,
 mls.UI_CMD_VIEWMARKETDETAILS: TRADEGROUP,
 mls.UI_CMD_FINDINCONTRACTS: TRADEGROUP,
 mls.UI_CMD_VIEWMEMBERDETAILS: TRADEGROUP,
 mls.UI_CMD_VIEWTRANSACTIONS: TRADEGROUP,
 mls.UI_CMD_ADDTOMARKETQUICKBAR: TRADEGROUP,
 mls.UI_CMD_REMOVEFROMMARKETQUICKBAR: TRADEGROUP,
 mls.UI_CMD_CONTRACTTHISITEM: TRADEGROUP,
 mls.UI_CMD_GIVEMONEY: TRADEGROUP,
 mls.UI_CMD_ACCESSACTIVECRYSTAL: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSAMMUNITION: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSCRYSTALSTORAGE: CONTAINERGROUPS,
 mls.UI_PI_CMD_OPENIMEX: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSFUELSTORAGE: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSREFINERY: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSRSOURCES: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSSTORAGE: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSSTORAGE: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSTRONTIUMSTORAGE: CONTAINERGROUPS,
 mls.UI_CMD_ACCESSVESSELS: CONTAINERGROUPS,
 mls.UI_CMD_OPENAMMOHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENCARGO: CONTAINERGROUPS,
 mls.UI_CMD_OPENCARGO: CONTAINERGROUPS,
 mls.UI_CMD_OPENCARGOHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENCARGOHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENCONTAINER: CONTAINERGROUPS,
 mls.UI_CMD_OPENCONTAINER: CONTAINERGROUPS,
 mls.UI_CMD_OPENCORPHANGARS: CONTAINERGROUPS,
 mls.UI_CMD_OPENDESCRIPTION: CONTAINERGROUPS,
 mls.UI_CMD_OPENDRONEBAY: CONTAINERGROUPS,
 mls.UI_CMD_OPENDRONEBAY: CONTAINERGROUPS,
 mls.UI_CMD_OPENFUELBAY: CONTAINERGROUPS,
 mls.UI_CMD_OPENGASHOLD: CONTAINERGROUPS,
 mls.UI_PI_ACCESSCARGOLINK: CONTAINERGROUPS,
 mls.UI_PI_ACCESSCARGOLINK: CONTAINERGROUPS,
 mls.UI_CMD_OPENINDUSTRIALSHIPHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENLARGESHIPHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENMEDIUMSHIPHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENMINERALHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENMYCARGO: CONTAINERGROUPS,
 mls.UI_CMD_OPENMYCARGO: CONTAINERGROUPS,
 mls.UI_CMD_OPENOREHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENPLANETARYCOMMODITIESHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENSALVAGEHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENSHIPHOLD: CONTAINERGROUPS,
 mls.UI_CMD_OPENSHIPMAINTENANCEBAY: CONTAINERGROUPS,
 mls.UI_CMD_OPENSMALLSHIPHOLD: CONTAINERGROUPS,
 mls.UI_CMD_STOREVESSEL: CONTAINERGROUPS,
 mls.UI_CMD_VIEWCONTENTS: CONTAINERGROUPS,
 mls.UI_CMD_OPENCOMMANDCENTERHOLD: CONTAINERGROUPS,
 mls.UI_CMD_CANCELANCHORING: CHANGESGROUP,
 mls.UI_CMD_CANCELMUTUAL: CHANGESGROUP,
 mls.UI_CMD_CANCELORDER: CHANGESGROUP,
 mls.UI_CMD_CANCELPETITION: CHANGESGROUP,
 mls.UI_CMD_CANCELREPAIR: CHANGESGROUP,
 mls.UI_CMD_CHANGEHARVESTEDMAT: CHANGESGROUP,
 mls.UI_CMD_CHANGELABEL: CHANGESGROUP,
 mls.UI_CMD_CHANGENAME: CHANGESGROUP,
 mls.UI_CMD_CHANGESILOTYPE: CHANGESGROUP,
 mls.UI_CMD_DEACTIVATEAUTOPILOT: CHANGESGROUP,
 mls.UI_CMD_DECLAREMUTUAL: CHANGESGROUP,
 mls.UI_CMD_DELEGATECONTROL: CHANGESGROUP,
 mls.UI_FLEET_EDITREGISTRATION: CHANGESGROUP,
 mls.UI_GENERIC_EDIT_CURRENT_FILTER: CHANGESGROUP,
 mls.UI_CMD_ESCALATEPETITION: CHANGESGROUP,
 mls.UI_CMD_FORGETCHANNEL: CHANGESGROUP,
 mls.UI_CMD_FORGETLIST: CHANGESGROUP,
 mls.UI_CMD_IGNORE_OTHER_SCAN_RESULTS: CHANGESGROUP,
 mls.UI_CMD_IGNORE_SCAN_RESULT: CHANGESGROUP,
 mls.UI_CMD_LEAVEAUDIO: CHANGESGROUP,
 mls.UI_CMD_LEAVECHANNEL: CHANGESGROUP,
 mls.UI_FLEET_LEAVE: CHANGESGROUP,
 mls.UI_EVEMAIL_LEAVEMAILINGLIST: CHANGESGROUP,
 mls.UI_FLEET_LEAVEPRIVATEVOICECHANNEL: CHANGESGROUP,
 mls.UI_CMD_LEAVESHIP: CHANGESGROUP,
 mls.UI_CMD_MOVEDRONE: CHANGESGROUP,
 mls.UI_CMD_MOVETODRONEBAY: CHANGESGROUP,
 mls.UI_CMD_ABORTTRAINING: CHANGESGROUP,
 mls.UI_EVEMAIL_RENAMELABEL: CHANGESGROUP,
 mls.UI_CMD_RENAMENOTE: CHANGESGROUP,
 mls.UI_CORP_RETRACT: CHANGESGROUP,
 mls.UI_CMD_RETURNANDORBIT: CHANGESGROUP,
 mls.UI_CMD_RETURNCONTROL: CHANGESGROUP,
 mls.UI_CMD_RETURNTODRONEBAY: CHANGESGROUP,
 mls.UI_CMD_LAUNCHDRONES: CHANGESGROUP,
 mls.UI_CMD_SCOOPTOCARGOBAY: CHANGESGROUP,
 mls.UI_CMD_SCOOPTOCARGOHOLD: CHANGESGROUP,
 mls.UI_CMD_SCOOPTODRONEBAY: CHANGESGROUP,
 mls.UI_CMD_SCOOPTOMAINTENANCEBAY: CHANGESGROUP,
 mls.UI_CMD_CLOSEPETITION: CHANGESGROUP,
 mls.UI_CMD_DELETEPETITION: CHANGESGROUP,
 mls.UI_CMD_UNBLOCK: CHANGESGROUP,
 mls.UI_CMD_REMOVELOCATION: CHANGESGROUP,
 mls.UI_CMD_ABANDONALLCARGO: DESTRUCTIVEGROUP,
 mls.UI_CMD_ABANDONALLWRECKS: DESTRUCTIVEGROUP,
 mls.UI_CMD_ABANDONCARGO: DESTRUCTIVEGROUP,
 mls.UI_CMD_ABANDONDRONE: DESTRUCTIVEGROUP,
 mls.UI_CMD_ABANDONWRECK: DESTRUCTIVEGROUP,
 mls.UI_CMD_CLEAR: DESTRUCTIVEGROUP,
 mls.UI_CMD_CLEAR_ALL_IGNORED_SCAN_RESULTS: DESTRUCTIVEGROUP,
 mls.UI_SHARED_MAPCLEARALLWAYPOINTS: DESTRUCTIVEGROUP,
 mls.UI_CMD_UNLINK: DESTRUCTIVEGROUP,
 mls.UI_CMD_CLEAR_IGNORED_SCAN_RESULT: DESTRUCTIVEGROUP,
 mls.UI_CMD_SCANNER_CLEAR_RESULT: DESTRUCTIVEGROUP,
 mls.UI_SHARED_CLEAR_ROUTE: DESTRUCTIVEGROUP,
 mls.UI_CMD_CLOSE: DESTRUCTIVEGROUP,
 mls.UI_CMD_DESTROYCLONE: DESTRUCTIVEGROUP,
 mls.UI_EVEMAIL_EMPTYTRASH: DESTRUCTIVEGROUP,
 mls.UI_CMD_REMOVEFROMBIOMASSQUEUE: DESTRUCTIVEGROUP,
 mls.UI_GENERIC_REMOVEITEM: DESTRUCTIVEGROUP,
 mls.UI_CMD_REMOVENOTE: DESTRUCTIVEGROUP,
 mls.UI_CMD_REMOVEOFFER: DESTRUCTIVEGROUP,
 mls.UI_CMD_REPACKAGE: DESTRUCTIVEGROUP,
 mls.UI_CMD_REPORTISKSPAMMER: DESTRUCTIVEGROUP,
 mls.UI_CMD_REPROCESS: DESTRUCTIVEGROUP,
 mls.UI_CMD_TRASHITEMSATLOCATION: DESTRUCTIVEGROUP,
 mls.UI_CMD_UNSUBSCRIBEFROMLIST: DESTRUCTIVEGROUP,
 mls.UI_CMD_WITHDRAW: DESTRUCTIVEGROUP,
 mls.UI_CMD_JETTISON: DESTRUCTIVEGROUP,
 mls.UI_FLEET_BOSS: DESTRUCTIVEGROUP,
 mls.UI_CMD_JUMPTOMEMBER: DESTRUCTIVEGROUP,
 mls.UI_CMD_LAUNCHSHIP: DESTRUCTIVEGROUP,
 mls.UI_CMD_LAUNCHSHIPFROMBAY: DESTRUCTIVEGROUP,
 mls.UI_CMD_LAUNCHFORCORP: DESTRUCTIVEGROUP,
 mls.UI_CMD_LAUNCHFORSELF: DESTRUCTIVEGROUP,
 mls.UI_CMD_UNDOCKFROMSTATION: DESTRUCTIVEGROUP,
 mls.UI_CMD_STRIPFITTING: DESTRUCTIVEGROUP,
 mls.UI_CMD_REPORTBOT: DESTRUCTIVEGROUP,
 mls.UI_CMD_COMPLETETERMINATION: RAGEQUITGROUP,
 mls.UI_FLEET_MAKELEADER: RAGEQUITGROUP,
 mls.UI_CONTACTS_DELETENOTIFICATION: RAGEQUITGROUP,
 mls.UI_CMD_DELETENOTE: RAGEQUITGROUP,
 mls.UI_CMD_DELETECHANNEL: RAGEQUITGROUP,
 mls.UI_EVEMAIL_DELETE: RAGEQUITGROUP,
 mls.UI_CMD_DELETEFOLDER: RAGEQUITGROUP,
 mls.UI_CMD_DELGROUP: RAGEQUITGROUP,
 mls.UI_CMD_DELETELIST: RAGEQUITGROUP,
 mls.UI_EVEMAIL_DELETEMAILINGLIST: RAGEQUITGROUP,
 mls.UI_GENERIC_DELETE_CURRENT_FILTER: RAGEQUITGROUP,
 mls.UI_EVEMAIL_NOTIFICATIONS_DELETEALL: RAGEQUITGROUP,
 mls.UI_CMD_DELETE: RAGEQUITGROUP,
 mls.UI_CONTRACTS_DELETE: RAGEQUITGROUP,
 mls.UI_CONTRACTS_DISMISS: RAGEQUITGROUP,
 mls.UI_CMD_EXPELMEMBER: RAGEQUITGROUP,
 mls.UI_FLEET_KICKMEMBER: RAGEQUITGROUP,
 mls.UI_CMD_PUTOFFLINE: RAGEQUITGROUP,
 mls.UI_CMD_QUITCORP: RAGEQUITGROUP,
 mls.UI_INFLIGHT_RELINQUISHCONTROL: RAGEQUITGROUP,
 mls.UI_CMD_REMOVE: RAGEQUITGROUP,
 mls.UI_FLEET_UNREGISTER: RAGEQUITGROUP,
 mls.UI_CMD_REMOVECONNECTION: RAGEQUITGROUP,
 mls.UI_CMD_REMOVEFROMMARKETQUICKBAR: RAGEQUITGROUP,
 mls.UI_CMD_REMOVEFROMSELECTION: RAGEQUITGROUP,
 mls.UI_FLEET_REMOVEFROMWATCHLIST: RAGEQUITGROUP,
 mls.UI_CMD_REMOVEWAYPOINT: RAGEQUITGROUP,
 mls.UI_CMD_REFINE: RAGEQUITGROUP,
 mls.UI_CMD_REASIGNASCEO: RAGEQUITGROUP,
 mls.UI_CMD_SELFDESTRUCT: RAGEQUITGROUP,
 mls.UI_CMD_TERMINATE: RAGEQUITGROUP,
 mls.UI_CMD_TOHANGARANDREFINE: RAGEQUITGROUP,
 mls.UI_EVEMAIL_TRASH: RAGEQUITGROUP,
 mls.UI_EVEMAIL_TRASHALL: RAGEQUITGROUP,
 mls.UI_CMD_TRASHIT: RAGEQUITGROUP,
 mls.UI_EVEMAIL_TRASHALL: RAGEQUITGROUP,
 mls.UI_CMD_UNANCHOR: RAGEQUITGROUP,
 mls.UI_CMD_UNANCHORSTRUCTURE: RAGEQUITGROUP,
 mls.UI_CMD_UNPLUG: RAGEQUITGROUP,
 mls.UI_CMD_EJECT: RAGEQUITGROUP,
 mls.UI_CMD_BREAK: RAGEQUITGROUP,
 mls.UI_CMD_COPY: SELECTIONGROUP,
 mls.UI_CMD_COPYALL: SELECTIONGROUP,
 mls.UI_BROWSER_COPYIMAGELOCATION: SELECTIONGROUP,
 mls.UI_BROWSER_COPYLINKLOCATION: SELECTIONGROUP,
 mls.UI_CMD_COPYSELECTED: SELECTIONGROUP,
 mls.UI_CMD_COPYURL: SELECTIONGROUP,
 mls.UI_CMD_CUT: SELECTIONGROUP,
 mls.UI_CMD_CUTSELECTED: SELECTIONGROUP,
 mls.UI_CMD_PASTE: SELECTIONGROUP,
 mls.UI_CMD_SELECTALL: SELECTIONGROUP,
 mls.UI_CMD_STACKALL: SELECTIONGROUP,
 mls.UI_CMD_SORTBY: SELECTIONGROUP,
 mls.UI_CMD_INVERSESELECTION: SELECTIONGROUP,
 mls.UI_CMD_TOGGLETIMESTAMP: SELECTIONGROUP,
 mls.UI_CMD_GMEXTRAS: GMWMEXTRAS,
 mls.UI_CMD_REFRESH: GMWMEXTRAS,
 'Inactive': GMWMEXTRAS,
 mls.UI_CMD_SHOWINFO: SHOWINFOGROUP,
 mls.UI_GENERIC_CHARACTER: SUBGROUP1,
 mls.UI_GENERIC_PLANETS: SUBGROUP1,
 mls.UI_GENERIC_STARGATES: SUBGROUP1,
 mls.UI_GENERIC_STATIONS: SUBGROUP1,
 mls.GENERIC_ASTEROIDBELTS: SUBGROUP1,
 mls.UI_GENERIC_PILOT: SUBGROUP1,
 mls.UI_GENERIC_FLEET: SUBGROUP1,
 mls.UI_CMD_LOCATION: SUBGROUP1,
 mls.UI_CMD_ORBIT: ACTIONSGROUP,
 mls.UI_CMD_WARPTOWITHIN: ACTIONSGROUP,
 mls.UI_CMD_KEEPATRANGE: ACTIONSGROUP,
 mls.UI_CMD_APPROACH: ACTIONSGROUP,
 mls.UI_CMD_LOOKAT: ACTIONSGROUP,
 mls.UI_CMD_ACTIVATEAUTOPILOT: ACTIONSGROUP,
 mls.UI_CMD_DEACTIVATEAUTOPILOT: ACTIONSGROUP,
 mls.UI_CMD_STOPMYSHIP: ACTIONSGROUP,
 mls.UI_CMD_ALIGNTO: ACTIONSGROUP,
 mls.UI_CMD_RESETCAMERA: ACTIONSGROUP,
 mls.UI_CMD_BOARDSHIP: ACTIONSGROUP,
 mls.UI_CMD_WARPTOMEMBER: ACTIONSGROUP,
 mls.UI_CMD_JUMP: ACTIONSGROUP,
 mls.UI_CMD_DOCK: ACTIONSGROUP,
 mls.UI_CMD_RELOADALL: ACTIONSGROUP,
 mls.UI_CMD_RELOAD: ACTIONSGROUP,
 mls.UI_CMD_RELOAD_USED: ACTIONSGROUP,
 mls.UI_CMD_ENGAGETARGET: ACTIONSGROUP,
 mls.UI_CMD_LOCKTARGET: ACTIONSGROUP,
 mls.UI_CMD_UNLOCKTARGET: ACTIONSGROUP,
 mls.UI_CMD_BUYTHIS: ACTIONSGROUP,
 mls.UI_CMD_MODIFYORDER: ACTIONSGROUP,
 mls.UI_CMD_ACTIVATEGATE: ACTIONSGROUP,
 mls.UI_CONTRACTS_VIEWCONTRACT: ACTIONSGROUP,
 mls.UI_CMD_FITTOACTIVESHIP: ACTIONSGROUP2,
 mls.UI_CMD_PUTONLINE: ACTIONSGROUP2,
 mls.UI_INFLIGHT_ASSUMECONTROL: ACTIONSGROUP2,
 mls.UI_CMD_ASSEMBLESHIP: ACTIONSGROUP2,
 mls.UI_CMD_ASSEMBLECONTAINER: ACTIONSGROUP2,
 mls.UI_CMD_MAKEACTIVE: ACTIONSGROUP2,
 mls.UI_CMD_GETREPAIRQUOTE: ACTIONSGROUP2,
 mls.UI_PI_VIEW_IN_PLANET_MODE: NAVIGATIONGROUP2,
 mls.UI_CMD_ADDWAYPOINT: NAVIGATIONGROUP2,
 mls.UI_CMD_ADDFIRSTWAYPOINT: NAVIGATIONGROUP2,
 mls.UI_CMD_BOOKMARKLOCATION: NAVIGATIONGROUP2,
 mls.UI_CMD_APPROACHLOCATION: NAVIGATIONGROUP2,
 mls.UI_CMD_EDITVIEWLOCATION: NAVIGATIONGROUP2,
 mls.UI_CMD_SHOWSSINMAPBR: NAVIGATIONGROUP2,
 mls.UI_CMD_SHOWONMAP: NAVIGATIONGROUP2,
 mls.UI_CMD_SETDESTINATION: NAVIGATIONGROUP2,
 mls.UI_CMD_EDITMEMBER: CORPGROUP,
 mls.UI_CMD_TRANSFERCORPCASH: CORPGROUP,
 mls.UI_CMD_AWARDDECORATION: CORPGROUP,
 mls.UI_CMD_SETNAME: CONFIGGROUP,
 mls.UI_CMD_CONFIGURESHIP: CONFIGGROUP,
 mls.UI_CMD_OPENFITTING: CONFIGGROUP,
 mls.UI_CMD_BRIDGETO: CONFIGGROUP,
 mls.UI_CMD_BRIDGETOMEMBER: CONFIGGROUP,
 mls.UI_CMD_SETNEWPASSWORD: CONFIGGROUP,
 mls.UI_CMD_SETPASSWORD: CONFIGGROUP,
 mls.UI_CMD_SETNEWCONFIGURATIONPASSWORD: CONFIGGROUP,
 mls.UI_CMD_CONFIGURECONTAINER: CONFIGGROUP,
 mls.UI_CMD_RETRIEVEPASSWORD: CONFIGGROUP,
 mls.UI_CMD_MANAGE: CONFIGGROUP,
 mls.UI_CMD_OPENFITTING: SHIPSPECIALGROUP,
 mls.UI_CMD_JUMPTO: SHIPSPECIALGROUP,
 mls.UI_CMD_ENTERSTARBASEPASSWORD: SHIPSPECIALGROUP,
 mls.UI_CMD_WARPFLEET: FLEETGROUP,
 mls.UI_CMD_WARPFLEETTOLOCATION: FLEETGROUP,
 mls.UI_CMD_WARPFLEETTOMEMBER: FLEETGROUP,
 mls.UI_CMD_WARPSQUAD: FLEETGROUP,
 mls.UI_CMD_WARPSQUADTOLOCATION: FLEETGROUP,
 mls.UI_FLEET_WARPSQUADTOMEMBER: FLEETGROUP,
 mls.UI_CMD_WARPWING: FLEETGROUP,
 mls.UI_CMD_WARPWINGTOLOCATION: FLEETGROUP,
 mls.UI_FLEET_WARPWINGTOMEMBER: FLEETGROUP}
menuHierarchy = [GMWMEXTRAS,
 ACTIONSGROUP,
 SHOWINFOGROUP,
 ACTIONSGROUP2,
 FLEETGROUP,
 SHIPSPECIALGROUP,
 NAVIGATIONGROUP2,
 SUBGROUP1,
 CONFIGGROUP,
 CONTAINERGROUPS,
 TRADEGROUP,
 CHANGESGROUP,
 CONTACTSGROUP,
 CONTACTSGROUP2,
 None,
 BLUEPRINTGROUP,
 CORPGROUP,
 DESTRUCTIVEGROUP,
 RAGEQUITGROUP,
 SELECTIONGROUP]

def GetMenuGroup(caption, *args):
    group = menuGroupsFromCaption.get(caption, None)
    return group


exports = util.AutoExports('menu', locals())
