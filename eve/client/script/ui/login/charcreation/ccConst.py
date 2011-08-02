import uiconst
import uiutil
CHARACTER_CREATION_NETWORK = 'res:/Animation/MorphemeIncarna/Export/CharCreation_runtimeBinary/CharacterCreation.mor'
GENDERID_FEMALE = 0
GENDERID_MALE = 1
NUM_PORTRAITS = 4
BODYGROUP = 0
SKINGROUP = 1
HAIRGROUP = 2
EYESGROUP = 3
MAKEUPGROUP = 4
SKINDETAILSGROUP = 5
CLOTHESGROUP = 6
BACKGROUNDGROUP = 7
POSESGROUP = 8
LIGHTSGROUP = 9
PIERCINGGROUP = 10
TATTOOGROUP = 11
SCARSGROUP = 12
MAINFRAME = ('ui_105_32_1', 8, -4)
MAINFRAME_INV = ('ui_105_32_10', 8, -4)
MAINFRAME_WITHTABS = ('ui_105_32_9', 8, -4)
FRAME_SOFTSHADE = ('ui_105_32_26', 15, 0)
FILL_BEVEL = ('ui_105_32_31', 0, 0)
ICON_EXPANDED = 'ui_105_32_4'
ICON_COLLAPSED = 'ui_105_32_5'
ICON_EXPANDEDSINGLE = 'ui_105_32_20'
ICON_COLLAPSEDSINGLE = 'ui_105_32_21'
ICON_RANDOMSMALL = 'ui_105_32_6'
ICON_RANDOM = 'ui_105_32_7'
ICON_FOCUSFRAME = 'ui_105_32_36'
ICON_CLOSE = 'ui_105_32_12'
ICON_NEXT = 'ui_105_32_16'
ICON_BACK = 'ui_105_32_15'
ICON_CAM_PRESSED = 'ui_105_32_23'
ICON_CAM_IDLE = 'ui_105_32_24'
ICON_TOGGLECLOTHES = 'ui_105_32_8'
ICON_HELP = 'ui_105_32_32'
POSERANGE = 6
TEXTURE_RESOLUTIONS = [(4096, 2048), (2048, 1024), (512, 256)]
ZONEMAP = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCLEFTRIGHT}
ZONEMAP_SIDE = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCALLDIRECTIONS,
 1: uiconst.UICURSOR_CCALLDIRECTIONS,
 2: uiconst.UICURSOR_CCALLDIRECTIONS,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCALLDIRECTIONS,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCALLDIRECTIONS,
 8: uiconst.UICURSOR_CCALLDIRECTIONS,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCALLDIRECTIONS,
 12: uiconst.UICURSOR_CCALLDIRECTIONS,
 13: uiconst.UICURSOR_CCALLDIRECTIONS,
 14: uiconst.UICURSOR_CCUPDOWN,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_DEFAULT}
ZONEMAP_ANIM = {-1: uiconst.UICURSOR_DEFAULT,
 0: uiconst.UICURSOR_CCHEADALL,
 1: uiconst.UICURSOR_CCHEADALL,
 2: uiconst.UICURSOR_CCHEADALL,
 3: uiconst.UICURSOR_CCALLDIRECTIONS,
 4: uiconst.UICURSOR_CCHEADTILT,
 5: uiconst.UICURSOR_CCALLDIRECTIONS,
 6: uiconst.UICURSOR_CCALLDIRECTIONS,
 7: uiconst.UICURSOR_CCHEADALL,
 8: uiconst.UICURSOR_CCHEADALL,
 9: uiconst.UICURSOR_CCALLDIRECTIONS,
 10: uiconst.UICURSOR_CCALLDIRECTIONS,
 11: uiconst.UICURSOR_CCHEADTILT,
 12: uiconst.UICURSOR_CCHEADALL,
 13: uiconst.UICURSOR_CCHEADALL,
 14: uiconst.UICURSOR_CCHEADALL,
 15: uiconst.UICURSOR_CCALLDIRECTIONS,
 16: uiconst.UICURSOR_CCALLDIRECTIONS,
 17: uiconst.UICURSOR_CCALLDIRECTIONS}
ZONEMAP_ANIMBODY = {-1: uiconst.UICURSOR_DEFAULT,
 3: uiconst.UICURSOR_CCSHOULDERTWIST,
 4: uiconst.UICURSOR_CCSHOULDERTWIST,
 5: uiconst.UICURSOR_CCSHOULDERTWIST,
 6: uiconst.UICURSOR_CCSHOULDERTWIST}
eyes = 'makeup/eyes'
eyeshadow = 'makeup/eyeshadow'
eyelashes = 'makeup/eyelashes'
eyeliner = 'makeup/eyeliner'
lipstick = 'makeup/lipstick'
blush = 'makeup/blush'
hair = 'hair'
eyebrows = 'makeup/eyebrows'
beard = 'beard'
bottomouter = 'bottomouter'
topmiddle = 'topmiddle'
topouter = 'topouter'
feet = 'feet'
outer = 'outer'
bottominner = 'bottominner'
topinner = 'topinner'
tattoo = 'tattoo'
skintone = 'skintone'
skinaging = 'makeup/aging'
scarring = 'makeup/scarring'
freckles = 'makeup/freckles'
glasses = 'accessories/glasses'
muscle = 'bodyshapes/muscularshape'
weight = 'bodyshapes/fatshape'
bottomunderwear = 'bottomunderwear'
topunderwear = 'topunderwear'
p_earslow = 'accessories/earslow'
p_earshigh = 'accessories/earshigh'
p_nose = 'accessories/nose'
p_nostril = 'accessories/nostril'
p_brow = 'accessories/brow'
p_lips = 'accessories/lips'
p_chin = 'accessories/chin'
s_head = 'scars/head'
t_head = 'tattoo/head'
BASEBEARD = 'beard/stubble'
MASTER_COLORS = [hair, eyes]
invisibleModifiers = ['feet_nude']
maleModifierDisplayNames = {eyes: mls.UI_CHARCREA_EYES,
 eyeshadow: mls.UI_CHARCREA_EYEDETAILS,
 eyeliner: mls.UI_CHARCREA_LASHTHICKNESS,
 lipstick: mls.UI_CHARCREA_LIPTONE,
 blush: mls.UI_CHARCREA_CHEEKCOLOR,
 hair: mls.UI_CHARCREA_HAIRSTYLE,
 eyebrows: mls.UI_CHARCREA_EYEBROWS,
 beard: mls.UI_CHARCREA_FACIALHAIR,
 skintone: mls.UI_CHARCREA_SKINTONE,
 skinaging: mls.UI_CHARCREA_AGING,
 scarring: mls.UI_CHARCREA_SCARRING,
 freckles: mls.UI_CHARCREA_FRECKLES,
 glasses: mls.UI_CHARCREA_GLASSES,
 muscle: mls.UI_CHARCREA_MUSCULARITY,
 weight: mls.UI_CHARCREA_WEIGHT,
 topmiddle: mls.UI_CHARCREA_TOP,
 topouter: mls.UI_CHARCREA_TOPOUTER,
 bottomouter: mls.UI_CHARCREA_BOTTOM,
 outer: mls.UI_CHARCREA_OUTER,
 feet: mls.UI_CHARCREA_FEET,
 p_earslow: mls.UI_CHARCREA_P_EARSLOW,
 p_earshigh: mls.UI_CHARCREA_P_EARSHIGH,
 p_nose: mls.UI_CHARCREA_P_NOSE,
 p_nostril: mls.UI_CHARCREA_P_NOSTRIL,
 p_brow: mls.UI_CHARCREA_P_BROW,
 p_lips: mls.UI_CHARCREA_P_LIPS,
 p_chin: mls.UI_CHARCREA_P_CHIN,
 t_head: mls.UI_CHARCREA_T_HEAD,
 s_head: mls.UI_CHARCREA_S_HEAD}
femaleModifierDisplayNames = {eyes: mls.UI_CHARCREA_EYES,
 eyeshadow: mls.UI_CHARCREA_EYESHADOW,
 eyeliner: mls.UI_CHARCREA_EYELINER,
 lipstick: mls.UI_CHARCREA_LIPSTICK,
 blush: mls.UI_CHARCREA_BLUSH,
 hair: mls.UI_CHARCREA_HAIRSTYLE,
 eyebrows: mls.UI_CHARCREA_EYEBROWS,
 skintone: mls.UI_CHARCREA_SKINTONE,
 skinaging: mls.UI_CHARCREA_AGING,
 scarring: mls.UI_CHARCREA_SCARRING,
 freckles: mls.UI_CHARCREA_FRECKLES,
 glasses: mls.UI_CHARCREA_GLASSES,
 muscle: mls.UI_CHARCREA_MUSCULARITY,
 weight: mls.UI_CHARCREA_WEIGHT,
 topmiddle: mls.UI_CHARCREA_TOP,
 topouter: mls.UI_CHARCREA_TOPOUTER,
 bottomouter: mls.UI_CHARCREA_BOTTOM,
 outer: mls.UI_CHARCREA_OUTER,
 feet: mls.UI_CHARCREA_FEET,
 p_earslow: mls.UI_CHARCREA_P_EARSLOW,
 p_earshigh: mls.UI_CHARCREA_P_EARSHIGH,
 p_nose: mls.UI_CHARCREA_P_NOSE,
 p_nostril: mls.UI_CHARCREA_P_NOSTRIL,
 p_brow: mls.UI_CHARCREA_P_BROW,
 p_lips: mls.UI_CHARCREA_P_LIPS,
 p_chin: mls.UI_CHARCREA_P_CHIN,
 t_head: mls.UI_CHARCREA_T_HEAD,
 s_head: mls.UI_CHARCREA_S_HEAD}
maleRandomizeItems = {eyes: EYESGROUP,
 eyeshadow: SKINDETAILSGROUP,
 eyeliner: SKINDETAILSGROUP,
 lipstick: SKINDETAILSGROUP,
 blush: SKINDETAILSGROUP,
 hair: HAIRGROUP,
 eyebrows: HAIRGROUP,
 beard: HAIRGROUP,
 skintone: SKINGROUP,
 skinaging: SKINGROUP,
 scarring: SKINGROUP,
 freckles: SKINGROUP,
 muscle: BODYGROUP,
 weight: BODYGROUP,
 bottomouter: CLOTHESGROUP,
 topmiddle: CLOTHESGROUP,
 topouter: CLOTHESGROUP,
 feet: CLOTHESGROUP,
 outer: CLOTHESGROUP,
 topinner: CLOTHESGROUP,
 glasses: CLOTHESGROUP,
 p_earslow: PIERCINGGROUP,
 p_earshigh: PIERCINGGROUP,
 p_nose: PIERCINGGROUP,
 p_nostril: PIERCINGGROUP,
 p_brow: PIERCINGGROUP,
 p_lips: PIERCINGGROUP,
 p_chin: PIERCINGGROUP,
 t_head: TATTOOGROUP,
 s_head: SCARSGROUP}
femaleRandomizeItems = {eyes: EYESGROUP,
 eyeshadow: MAKEUPGROUP,
 eyeliner: MAKEUPGROUP,
 lipstick: MAKEUPGROUP,
 blush: MAKEUPGROUP,
 hair: HAIRGROUP,
 eyebrows: HAIRGROUP,
 skintone: SKINGROUP,
 skinaging: SKINGROUP,
 freckles: SKINGROUP,
 scarring: SKINGROUP,
 muscle: BODYGROUP,
 weight: BODYGROUP,
 bottomouter: CLOTHESGROUP,
 topmiddle: CLOTHESGROUP,
 topouter: CLOTHESGROUP,
 feet: CLOTHESGROUP,
 outer: CLOTHESGROUP,
 glasses: CLOTHESGROUP,
 p_earslow: PIERCINGGROUP,
 p_earshigh: PIERCINGGROUP,
 p_nose: PIERCINGGROUP,
 p_nostril: PIERCINGGROUP,
 p_brow: PIERCINGGROUP,
 p_lips: PIERCINGGROUP,
 p_chin: PIERCINGGROUP,
 t_head: TATTOOGROUP,
 s_head: SCARSGROUP}
randomizerBlacklist = {'makeup/eyes': ['eyes_10']}
recustomizationRandomizerBlacklist = [skintone,
 skinaging,
 freckles,
 scarring,
 muscle,
 weight]
randomizerCategoryBlacklist = [p_earslow,
 p_earshigh,
 p_nose,
 p_nostril,
 p_brow,
 p_lips,
 p_chin,
 t_head,
 s_head]
maleOddsOfSelectingNone = {glasses: 0.75,
 beard: 0.5,
 topouter: 0.5,
 outer: 0.5,
 t_head: 0.0,
 s_head: 0.0}
maleOddsOfSelectingNoneFullRandomize = {eyeshadow: 0.95,
 eyeliner: 0.95,
 lipstick: 0.95,
 blush: 0.95,
 skinaging: 0.95,
 scarring: 0.95,
 freckles: 0.95,
 glasses: 0.95}
femaleOddsOfSelectingNone = {glasses: 0.75,
 topouter: 0.5,
 outer: 0.5,
 p_earslow: 0.8,
 p_earshigh: 0.8,
 p_nose: 0.8,
 p_nostril: 0.8,
 p_brow: 0.8,
 p_lips: 0.8,
 p_chin: 0.8,
 t_head: 0.0,
 s_head: 0.0}
femaleOddsOfSelectingNoneFullRandomize = {eyeshadow: 0.9,
 eyeliner: 0.9,
 lipstick: 0.9,
 blush: 0.9,
 skinaging: 0.95,
 freckles: 0.95,
 glasses: 0.95}
addWeightToCategories = [eyeshadow,
 eyeliner,
 lipstick,
 blush,
 skinaging]
RACESTEP = 1
BLOODLINESTEP = 2
CUSTOMIZATIONSTEP = 3
PORTRAITSTEP = 4
NAMINGSTEP = 5
COLORMAPPING = {eyes: (False, False),
 hair: (False, False),
 eyeshadow: (True, False),
 eyeliner: (True, False),
 blush: (True, False),
 lipstick: (True, True),
 t_head: (True, False)}
TUCKMAPPING = {topmiddle: ('dependants/drape', (topmiddle,), 'standard'),
 outer: ('dependants/hood', (outer,), 'robeam1'),
 feet: ('dependants/boottucking', (bottomouter,), 'standard'),
 bottomouter: ('dependants/waisttucking', (topmiddle, topouter), 'standard')}
TUCKCATEGORIES = ['dependants/drape',
 'dependants/hood',
 'dependants/boottucking',
 'dependants/waisttucking']
HELPTEXTS = {BODYGROUP: mls.UI_CHARCREA_SCULPTINGHELP,
 SKINGROUP: mls.UI_CHARCREA_SKINHELP,
 HAIRGROUP: mls.UI_CHARCREA_HAIRHELP,
 EYESGROUP: mls.UI_CHARCREA_EYESHELP,
 MAKEUPGROUP: mls.UI_CHARCREA_MAKEUPHELP,
 SKINDETAILSGROUP: mls.UI_CHARCREA_SKINDETAILSHELP,
 CLOTHESGROUP: mls.UI_CHARCREA_CLOTHESHELP,
 BACKGROUNDGROUP: mls.UI_CHARCREA_BACKGROUNDSHELP,
 POSESGROUP: mls.UI_CHARCREA_POSESHELP,
 LIGHTSGROUP: mls.UI_CHARCREA_LIGHTSHELP,
 PIERCINGGROUP: mls.UI_CHARCREA_PIERCINGSHELP,
 TATTOOGROUP: mls.UI_CHARCREA_TATTOOSHELP,
 SCARSGROUP: mls.UI_CHARCREA_SCARSHELP}
GROUPNAMES = {SKINGROUP: mls.UI_CHARCREA_SKIN,
 HAIRGROUP: mls.UI_CHARCREA_HAIR,
 EYESGROUP: mls.UI_CHARCREA_EYES,
 MAKEUPGROUP: mls.UI_CHARCREA_MAKEUP,
 SKINDETAILSGROUP: mls.UI_CHARCREA_SKINDETAILS,
 CLOTHESGROUP: mls.UI_CHARCREA_CLOTHES,
 BODYGROUP: mls.UI_CHARCREA_SHAPE,
 BACKGROUNDGROUP: mls.UI_CHARCREA_BACKGROUNDS,
 POSESGROUP: mls.UI_CHARCREA_POSES,
 LIGHTSGROUP: mls.UI_CHARCREA_LIGHTS,
 LIGHTSGROUP: mls.UI_CHARCREA_LIGHTS,
 PIERCINGGROUP: mls.UI_CHARCREA_PIERCINGS,
 TATTOOGROUP: mls.UI_CHARCREA_TATTOOS,
 SCARSGROUP: mls.UI_CHARCREA_SCARS}
PICKMAPPING = {('sculpt', 12): eyes,
 ('hair', 0): hair,
 ('hair', 1): eyebrows,
 ('hair', 2): beard,
 ('makeup', 0): eyeshadow,
 ('makeup', 1): blush,
 ('makeup', 2): lipstick,
 ('clothes', 0): topmiddle,
 ('clothes', 1): topmiddle,
 ('clothes', 2): bottomouter,
 ('clothes', 3): bottomouter,
 ('clothes', 4): feet}
REMOVEABLE = (glasses,
 topouter,
 topmiddle,
 outer,
 eyebrows,
 beard,
 eyeshadow,
 eyeliner,
 blush,
 lipstick,
 bottomouter,
 feet,
 p_earslow,
 p_earshigh,
 p_nose,
 p_nostril,
 p_brow,
 p_lips,
 p_chin,
 t_head,
 s_head)
RACIALBACKGROUND = {const.raceCaldari: 'res:/UI/Texture/CharacterCreation/bg/Background_Caldari.dds',
 const.raceMinmatar: 'res:/UI/Texture/CharacterCreation/bg/Background_Minmatar.dds',
 const.raceAmarr: 'res:/UI/Texture/CharacterCreation/bg/Background_Amarr.dds',
 const.raceGallente: 'res:/UI/Texture/CharacterCreation/bg/Background_Gallente.dds'}
SCENE_PATH_CUSTOMIZATION = 'res:/Graphics/Interior/characterCreation/Customization.red'
SCENE_PATH_RACE_SELECTION = 'res:/Graphics/Interior/characterCreation/RaceSelection.red'
CUSTOMIZATION_FLOOR = 'res:/Graphics/Interior/characterCreation/Plane/Floor.red'
COLOR = (1.0, 1.0, 1.0)
COLOR50 = (1.0, 1.0, 1.0, 0.5)
COLOR75 = (1.0, 1.0, 1.0, 0.75)
COLOR100 = (1.0, 1.0, 1.0, 1.0)
LIGHT_SETTINGS_ID = [10866,
 10742,
 10743,
 10744,
 10745,
 10746,
 10747]
LIGHT_COLOR_SETTINGS_ID = [10866,
 10748,
 10749,
 10750,
 10751,
 10752,
 10753]
backgroundOptions = ['res:/UI/Texture/CharacterCreation/backdrops/Background_1.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_2.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_3.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_4.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_5.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_6.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_7.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_8.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_9.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_10.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_11.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_12.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_13.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_14.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_15.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_16.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_17.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_18.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_19.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_20.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_21.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_22.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_23.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_24.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_25.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_26.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_27.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_28.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_29.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_30.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_31.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_32.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_33.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_34.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_35.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_36.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_37.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_38.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_39.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_40.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_41.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_42.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_43.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_44.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_45.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_46.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_47.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_48.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_49.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_50.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_51.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_52.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_53.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_54.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_55.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_56.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_57.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_58.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_59.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_60.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_61.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_62.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_63.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_64.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_65.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_66.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_67.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_68.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_69.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_70.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_71.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_72.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_73.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_74.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_75.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_76.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_77.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_78.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_79.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_80.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_81.dds']
BASE_HAIR_COLOR_FEMALE = 'res:/Graphics/Character/Modular/Female/hair/Colors/BaseColor.base'
BASE_HAIR_COLOR_MALE = 'res:/Graphics/Character/Modular/Male/hair/Colors/BaseColor.base'
HAIRCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Modular/Female/hair/Colors/restrictions'
HAIRCOLOR_RESTRICTION_MALE = 'res:/Graphics/Character/Modular/Male/hair/Colors/restrictions'
HAIRCOLORS = ['res:/Graphics/Character/Modular/Female/hair/Colors/', 'res:/Graphics/Character/Modular/Male/hair/Colors/']
BASE_HAIR_TYPE_FEMALE = 'res:/Graphics/Character/Modular/Female/hair/Hair_Stubble_01/Types/Hair_Stubble_01.type'
BASE_HAIR_TYPE_MALE = 'res:/Graphics/Character/Modular/Male/hair/Hair_Stubble_02/Types/Hair_Stubble_02.type'
EYESHADOWCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Modular/Female/Makeup/EyeShadow/Colors/restrictions'
EYESHADOWCOLORS = ['res:/Graphics/Character/Modular/Female/Makeup/EyeShadow/Colors/', 'res:/Graphics/Character/Modular/Male/Makeup/EyeShadow/Colors/']
HEADTATTOOCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Modular/Female/Tattoo/Head/Colors/restrictions'
HEADTATTOOCOLOR_RESTRICTION_MALE = 'res:/Graphics/Character/Modular/Male/Tattoo/Head/Colors/restrictions'
HEADTATTOOCOLORS = ['res:/Graphics/Character/Modular/Female/Tattoo/Head/Colors/', 'res:/Graphics/Character/Modular/Male/Tattoo/Head/Colors/']
weightLimits = {t_head: {'default': [0.62, 0.91],
          ('white_A', None): [0.44, 0.73]}}
defaultIntensity = {t_head: 1.0}
FACE_POSE_CONTROLPARAMS = [['ControlParameters|BrowLeftCurl', 0.5],
 ['ControlParameters|BrowRightCurl', 0.5],
 ['ControlParameters|BrowLeftUpDown', 0.5],
 ['ControlParameters|BrowRightUpDown', 0.5],
 ['ControlParameters|BrowLeftTighten', 0.5],
 ['ControlParameters|BrowRightTighten', 0.5],
 ['ControlParameters|SquintLeft', 0.0],
 ['ControlParameters|SquintRight', 0.0],
 ['ControlParameters|FrownLeft', 0.0],
 ['ControlParameters|FrownRight', 0.0],
 ['ControlParameters|SmileLeft', 0.0],
 ['ControlParameters|SmileRight', 0.0],
 ['ControlParameters|HeadTilt', 0.0],
 ['ControlParameters|JawSideways', 0.5],
 ['ControlParameters|JawUp', 1.0],
 ['ControlParameters|EyesLookVertical', 0.5],
 ['ControlParameters|EyesLookHorizontal', 0.5],
 ['ControlParameters|EyeClose', 0.0],
 ['ControlParameters|OrientChar', 0.5]]
MODE_FULLINITIAL_CUSTOMIZATION = 1
MODE_LIMITED_RECUSTOMIZATION = 2
MODE_FULL_RECUSTOMIZATION = 3
MODE_FULL_BLOODLINECHANGE = 4
CAMERA_MODE_DEFAULT = 0
CAMERA_MODE_FACE = 1
CAMERA_MODE_BODY = 2
CAMERA_MODE_PORTRAIT = 3
exports = uiutil.AutoExports('ccConst', locals())

