import uiconst
import uicls
import mathUtil
import math
import uthread
import uiutil
import log
import trinity
import random
TOPHALF = 0
BOTTOMHALF = 1
MINCOLORS = 2
MAXCOLORS = 32
LEGALCOLORAMT_FULL = [2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 10,
 12,
 14,
 16,
 18,
 20,
 22,
 24,
 26,
 28,
 30,
 32]
LEGALCOLORAMT_HALF = [1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 15,
 16]

class CharCreationColorPickerCombo(uicls.Container):
    __guid__ = 'uicls.CharCreationColorPickerCombo'
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_name = 'CharCreationColorPickerCombo'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == 'CharCreationColorPickerCombo':
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        margin = 3
        c1 = uicls.Container(parent=self, pos=(0,
         0,
         128,
         64 - margin), clipChildren=True, align=uiconst.TOPLEFT)
        colorsTop = attributes.get('colorsTop', None)
        activeColorIndexTop = attributes.get('activeColorIndexTop', 0)
        p1 = uicls.CharCreationColorPicker(parent=c1, colors=colorsTop, OnSetValue=attributes.get('OnSetValueTop', None), modifierName=attributes.get('modifierName', ''), activeColorIndex=activeColorIndexTop, enableHalf=0)
        self.sr.topPicker = p1
        c2 = uicls.Container(parent=self, pos=(0,
         64 + margin,
         128,
         64), clipChildren=True, align=uiconst.TOPLEFT)
        activeColorIndexBottom = attributes.get('activeColorIndexBottom', 0)
        colorsBottom = attributes.get('colorsBottom', None)
        p2 = uicls.CharCreationColorPicker(parent=c2, top=-64 - margin, colors=colorsBottom, OnSetValue=attributes.get('OnSetValueBottom', None), modifierName=attributes.get('modifierName', ''), activeColorIndex=activeColorIndexBottom, enableHalf=1)
        self.sr.bottomPicker = p2




class CharCreationColorPicker(uicls.Container):
    __guid__ = 'uicls.CharCreationColorPicker'
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_name = 'CharCreationColorPicker'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = 60
    default_colors = (('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)),
     ('red', (0.8,
       0.2,
       0.0,
       1.0), (0.8,
       0.2,
       0.0,
       1.0)))

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == 'CharCreationColorPicker':
                each.Close()

        uicls.Container.ApplyAttributes(self, attributes)
        self._showHalf = None
        self._lastRadian = None
        self._currentColors = None
        self._scale = attributes.scale
        if self._scale is not None:
            self.width = int(self.width * self._scale)
            self.height = int(self.height * self._scale)
        if attributes.enableHalf is not None:
            self.EnableHalf(attributes.enableHalf)
        self.LoadColorBits()
        colors = attributes.get('colors', None)
        activeColorIndex = attributes.activeColorIndex or 0
        self.modifierName = attributes.modifierName
        if colors:
            self.InitColors(colors, activeColorIndex)
        callback = attributes.get('OnSetValue', None)
        if callback:
            self.OnSetValue = callback



    def LoadColorBits(self):
        self.colorBits = {(10, 10, True): ('res:/UI/Texture/CharacterCreation/colorBits/10_10End__8_61_38_97.dds', 8, 61, 38, 97),
         (10, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_10__8_61_38_97.dds', 8, 61, 38, 97),
         (10, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/10_1End__8_30_38_66.dds', 8, 30, 38, 66),
         (10, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_1__8_30_38_66.dds', 8, 30, 38, 66),
         (10, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_2__18_11_55_45.dds', 18, 11, 55, 45),
         (10, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_3__45_8_82_33.dds', 45, 8, 82, 33),
         (10, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_4__72_11_109_45.dds', 72, 11, 109, 45),
         (10, 5, True): ('res:/UI/Texture/CharacterCreation/colorBits/10_5End__89_30_119_66.dds', 89, 30, 119, 66),
         (10, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_5__89_30_119_66.dds', 89, 30, 119, 66),
         (10, 6, True): ('res:/UI/Texture/CharacterCreation/colorBits/10_6End__89_61_119_97.dds', 89, 61, 119, 97),
         (10, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_6__89_61_119_97.dds', 89, 61, 119, 97),
         (10, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_7__72_82_109_116.dds', 72, 82, 109, 116),
         (10, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_8__45_94_82_119.dds', 45, 94, 82, 119),
         (10, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/10_9__18_82_55_116.dds', 18, 82, 55, 116),
         (12, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_10__35_91_66_119.dds', 35, 91, 66, 119),
         (12, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_11__15_78_49_112.dds', 15, 78, 49, 112),
         (12, 12, True): ('res:/UI/Texture/CharacterCreation/colorBits/12_12End__8_61_36_92.dds', 8, 61, 36, 92),
         (12, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_12__8_61_36_92.dds', 8, 61, 36, 92),
         (12, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/12_1End__8_35_36_66.dds', 8, 35, 36, 66),
         (12, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_1__8_35_36_66.dds', 8, 35, 36, 66),
         (12, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_2__15_15_49_49.dds', 15, 15, 49, 49),
         (12, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_3__35_8_66_36.dds', 35, 8, 66, 36),
         (12, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_4__61_8_92_36.dds', 61, 8, 92, 36),
         (12, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_5__78_15_112_49.dds', 78, 15, 112, 49),
         (12, 6, True): ('res:/UI/Texture/CharacterCreation/colorBits/12_6End__91_35_119_66.dds', 91, 35, 119, 66),
         (12, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_6__91_35_119_66.dds', 91, 35, 119, 66),
         (12, 7, True): ('res:/UI/Texture/CharacterCreation/colorBits/12_7End__91_61_119_92.dds', 91, 61, 119, 92),
         (12, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_7__91_61_119_92.dds', 91, 61, 119, 92),
         (12, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_8__78_78_112_112.dds', 78, 78, 112, 112),
         (12, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/12_9__61_91_92_119.dds', 61, 91, 92, 119),
         (14, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_10__69_88_99_117.dds', 69, 88, 99, 117),
         (14, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_11__49_95_78_119.dds', 49, 95, 78, 119),
         (14, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_12__28_88_58_117.dds', 28, 88, 58, 117),
         (14, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_13__14_76_44_107.dds', 14, 76, 44, 107),
         (14, 14, True): ('res:/UI/Texture/CharacterCreation/colorBits/14_14End__8_61_35_89.dds', 8, 61, 35, 89),
         (14, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_14__8_61_35_89.dds', 8, 61, 35, 89),
         (14, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/14_1End__8_38_35_66.dds', 8, 38, 35, 66),
         (14, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_1__8_38_35_66.dds', 8, 38, 35, 66),
         (14, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_2__14_20_44_51.dds', 14, 20, 44, 51),
         (14, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_3__28_10_58_39.dds', 28, 10, 58, 39),
         (14, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_4__49_8_78_32.dds', 49, 8, 78, 32),
         (14, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_5__69_10_99_39.dds', 69, 10, 99, 39),
         (14, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_6__83_20_113_51.dds', 83, 20, 113, 51),
         (14, 7, True): ('res:/UI/Texture/CharacterCreation/colorBits/14_7End__92_38_119_66.dds', 92, 38, 119, 66),
         (14, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_7__92_38_119_66.dds', 92, 38, 119, 66),
         (14, 8, True): ('res:/UI/Texture/CharacterCreation/colorBits/14_8End__92_61_119_89.dds', 92, 61, 119, 89),
         (14, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_8__92_61_119_89.dds', 92, 61, 119, 89),
         (14, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/14_9__83_76_113_107.dds', 83, 76, 113, 107),
         (16, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_10__86_74_115_103.dds', 86, 74, 115, 103),
         (16, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_11__74_86_103_115.dds', 74, 86, 103, 115),
         (16, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_12__61_93_86_119.dds', 61, 93, 86, 119),
         (16, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_13__41_93_66_119.dds', 41, 93, 66, 119),
         (16, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_14__24_86_53_115.dds', 24, 86, 53, 115),
         (16, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_15__12_74_41_103.dds', 12, 74, 41, 103),
         (16, 16, True): ('res:/UI/Texture/CharacterCreation/colorBits/16_16End__8_61_34_86.dds', 8, 61, 34, 86),
         (16, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_16__8_61_34_86.dds', 8, 61, 34, 86),
         (16, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/16_1End__8_41_34_66.dds', 8, 41, 34, 66),
         (16, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_1__8_41_34_66.dds', 8, 41, 34, 66),
         (16, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_2__12_24_41_53.dds', 12, 24, 41, 53),
         (16, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_3__24_12_53_41.dds', 24, 12, 53, 41),
         (16, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_4__41_8_66_34.dds', 41, 8, 66, 34),
         (16, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_5__61_8_86_34.dds', 61, 8, 86, 34),
         (16, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_6__74_12_103_41.dds', 74, 12, 103, 41),
         (16, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_7__86_24_115_53.dds', 86, 24, 115, 53),
         (16, 8, True): ('res:/UI/Texture/CharacterCreation/colorBits/16_8End__93_41_119_66.dds', 93, 41, 119, 66),
         (16, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_8__93_41_119_66.dds', 93, 41, 119, 66),
         (16, 9, True): ('res:/UI/Texture/CharacterCreation/colorBits/16_9End__93_61_119_86.dds', 93, 61, 119, 86),
         (16, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/16_9__93_61_119_86.dds', 93, 61, 119, 86),
         (18, 10, True): ('res:/UI/Texture/CharacterCreation/colorBits/18_10End__94_61_119_84.dds', 94, 61, 119, 84),
         (18, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_10__94_61_119_84.dds', 94, 61, 119, 84),
         (18, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_11__88_73_116_100.dds', 88, 73, 116, 100),
         (18, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_12__78_83_106_112.dds', 78, 83, 106, 112),
         (18, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_13__67_91_92_118.dds', 67, 91, 92, 118),
         (18, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_14__52_95_75_119.dds', 52, 95, 75, 119),
         (18, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_15__35_91_60_118.dds', 35, 91, 60, 118),
         (18, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_16__21_83_49_112.dds', 21, 83, 49, 112),
         (18, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_17__11_73_39_100.dds', 11, 73, 39, 100),
         (18, 18, True): ('res:/UI/Texture/CharacterCreation/colorBits/18_18End__8_61_33_84.dds', 8, 61, 33, 84),
         (18, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_18__8_61_33_84.dds', 8, 61, 33, 84),
         (18, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/18_1End__8_43_33_66.dds', 8, 43, 33, 66),
         (18, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_1__8_43_33_66.dds', 8, 43, 33, 66),
         (18, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_2__11_27_39_54.dds', 11, 27, 39, 54),
         (18, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_3__21_15_49_44.dds', 21, 15, 49, 44),
         (18, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_4__35_9_60_36.dds', 35, 9, 60, 36),
         (18, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_5__52_8_75_32.dds', 52, 8, 75, 32),
         (18, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_6__67_9_92_36.dds', 67, 9, 92, 36),
         (18, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_7__78_15_106_44.dds', 78, 15, 106, 44),
         (18, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_8__88_27_116_54.dds', 88, 27, 116, 54),
         (18, 9, True): ('res:/UI/Texture/CharacterCreation/colorBits/18_9End__94_43_119_66.dds', 94, 43, 119, 66),
         (18, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/18_9__94_43_119_66.dds', 94, 43, 119, 66),
         (20, 10, True): ('res:/UI/Texture/CharacterCreation/colorBits/20_10End__94_45_119_66.dds', 94, 45, 119, 66),
         (20, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_10__94_45_119_66.dds', 94, 45, 119, 66),
         (20, 11, True): ('res:/UI/Texture/CharacterCreation/colorBits/20_11End__94_61_119_82.dds', 94, 61, 119, 82),
         (20, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_11__94_61_119_82.dds', 94, 61, 119, 82),
         (20, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_12__89_72_116_97.dds', 89, 72, 116, 97),
         (20, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_13__82_82_109_109.dds', 82, 82, 109, 109),
         (20, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_14__72_89_97_116.dds', 72, 89, 97, 116),
         (20, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_15__61_94_82_119.dds', 61, 94, 82, 119),
         (20, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_16__45_94_66_119.dds', 45, 94, 66, 119),
         (20, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_17__30_89_55_116.dds', 30, 89, 55, 116),
         (20, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_18__18_82_45_109.dds', 18, 82, 45, 109),
         (20, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_19__11_72_38_97.dds', 11, 72, 38, 97),
         (20, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/20_1End__8_45_33_66.dds', 8, 45, 33, 66),
         (20, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_1__8_45_33_66.dds', 8, 45, 33, 66),
         (20, 20, True): ('res:/UI/Texture/CharacterCreation/colorBits/20_20End__8_61_33_82.dds', 8, 61, 33, 82),
         (20, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_20__8_61_33_82.dds', 8, 61, 33, 82),
         (20, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_2__11_30_38_55.dds', 11, 30, 38, 55),
         (20, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_3__18_18_45_45.dds', 18, 18, 45, 45),
         (20, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_4__30_11_55_38.dds', 30, 11, 55, 38),
         (20, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_5__45_8_66_33.dds', 45, 8, 66, 33),
         (20, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_6__61_8_82_33.dds', 61, 8, 82, 33),
         (20, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_7__72_11_97_38.dds', 72, 11, 97, 38),
         (20, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_8__82_18_109_45.dds', 82, 18, 109, 45),
         (20, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/20_9__89_30_116_55.dds', 89, 30, 116, 55),
         (22, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_10__90_33_117_56.dds', 90, 33, 117, 56),
         (22, 11, True): ('res:/UI/Texture/CharacterCreation/colorBits/22_11End__94_46_119_66.dds', 94, 46, 119, 66),
         (22, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_11__94_46_119_66.dds', 94, 46, 119, 66),
         (22, 12, True): ('res:/UI/Texture/CharacterCreation/colorBits/22_12End__94_61_119_81.dds', 94, 61, 119, 81),
         (22, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_12__94_61_119_81.dds', 94, 61, 119, 81),
         (22, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_13__90_71_117_94.dds', 90, 71, 117, 94),
         (22, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_14__84_80_110_106.dds', 84, 80, 110, 106),
         (22, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_15__76_87_100_114.dds', 76, 87, 100, 114),
         (22, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_16__66_93_88_118.dds', 66, 93, 88, 118),
         (22, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_17__54_95_73_119.dds', 54, 95, 73, 119),
         (22, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_18__39_93_61_118.dds', 39, 93, 61, 118),
         (22, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_19__27_87_51_114.dds', 27, 87, 51, 114),
         (22, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/22_1End__8_46_33_66.dds', 8, 46, 33, 66),
         (22, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_1__8_46_33_66.dds', 8, 46, 33, 66),
         (22, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_20__17_80_43_106.dds', 17, 80, 43, 106),
         (22, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_21__10_71_37_94.dds', 10, 71, 37, 94),
         (22, 22, True): ('res:/UI/Texture/CharacterCreation/colorBits/22_22End__8_61_33_81.dds', 8, 61, 33, 81),
         (22, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_22__8_61_33_81.dds', 8, 61, 33, 81),
         (22, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_2__10_33_37_56.dds', 10, 33, 37, 56),
         (22, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_3__17_21_43_47.dds', 17, 21, 43, 47),
         (22, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_4__27_13_51_40.dds', 27, 13, 51, 40),
         (22, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_5__39_9_61_34.dds', 39, 9, 61, 34),
         (22, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_6__54_8_73_32.dds', 54, 8, 73, 32),
         (22, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_7__66_9_88_34.dds', 66, 9, 88, 34),
         (22, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_8__76_13_100_40.dds', 76, 13, 100, 40),
         (22, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/22_9__84_21_110_47.dds', 84, 21, 110, 47),
         (24, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_10__86_24_112_49.dds', 86, 24, 112, 49),
         (24, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_11__91_35_117_57.dds', 91, 35, 117, 57),
         (24, 12, True): ('res:/UI/Texture/CharacterCreation/colorBits/24_12End__94_47_119_66.dds', 94, 47, 119, 66),
         (24, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_12__94_47_119_66.dds', 94, 47, 119, 66),
         (24, 13, True): ('res:/UI/Texture/CharacterCreation/colorBits/24_13End__94_61_119_80.dds', 94, 61, 119, 80),
         (24, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_13__94_61_119_80.dds', 94, 61, 119, 80),
         (24, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_14__91_70_117_92.dds', 91, 70, 117, 92),
         (24, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_15__86_78_112_103.dds', 86, 78, 112, 103),
         (24, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_16__78_86_103_112.dds', 78, 86, 103, 112),
         (24, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_17__70_91_92_117.dds', 70, 91, 92, 117),
         (24, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_18__61_94_80_119.dds', 61, 94, 80, 119),
         (24, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_19__47_94_66_119.dds', 47, 94, 66, 119),
         (24, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/24_1End__8_47_32_66.dds', 8, 47, 32, 66),
         (24, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_1__8_47_32_66.dds', 8, 47, 32, 66),
         (24, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_20__35_91_57_117.dds', 35, 91, 57, 117),
         (24, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_21__24_86_49_112.dds', 24, 86, 49, 112),
         (24, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_22__15_78_41_103.dds', 15, 78, 41, 103),
         (24, 23, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_23__10_70_36_92.dds', 10, 70, 36, 92),
         (24, 24, True): ('res:/UI/Texture/CharacterCreation/colorBits/24_24End__8_61_32_80.dds', 8, 61, 32, 80),
         (24, 24, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_24__8_61_32_80.dds', 8, 61, 32, 80),
         (24, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_2__10_35_36_57.dds', 10, 35, 36, 57),
         (24, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_3__15_24_41_49.dds', 15, 24, 41, 49),
         (24, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_4__24_15_49_41.dds', 24, 15, 49, 41),
         (24, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_5__35_10_57_36.dds', 35, 10, 57, 36),
         (24, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_6__47_8_66_32.dds', 47, 8, 66, 32),
         (24, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_7__61_8_80_32.dds', 61, 8, 80, 32),
         (24, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_8__70_10_92_36.dds', 70, 10, 92, 36),
         (24, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/24_9__78_15_103_41.dds', 78, 15, 103, 41),
         (26, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_10__81_18_105_43.dds', 81, 18, 105, 43),
         (26, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_11__87_26_113_50.dds', 87, 26, 113, 50),
         (26, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_12__92_37_117_58.dds', 92, 37, 117, 58),
         (26, 13, True): ('res:/UI/Texture/CharacterCreation/colorBits/26_13End__95_48_119_66.dds', 95, 48, 119, 66),
         (26, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_13__95_48_119_66.dds', 95, 48, 119, 66),
         (26, 14, True): ('res:/UI/Texture/CharacterCreation/colorBits/26_14End__95_61_119_79.dds', 95, 61, 119, 79),
         (26, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_14__95_61_119_79.dds', 95, 61, 119, 79),
         (26, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_15__92_69_117_90.dds', 92, 69, 117, 90),
         (26, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_16__87_77_113_101.dds', 87, 77, 113, 101),
         (26, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_17__81_84_105_109.dds', 81, 84, 105, 109),
         (26, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_18__73_90_96_115.dds', 73, 90, 96, 115),
         (26, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_19__65_93_85_118.dds', 65, 93, 85, 118),
         (26, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/26_1End__8_48_32_66.dds', 8, 48, 32, 66),
         (26, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_1__8_48_32_66.dds', 8, 48, 32, 66),
         (26, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_20__55_95_72_119.dds', 55, 95, 72, 119),
         (26, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_21__42_93_62_118.dds', 42, 93, 62, 118),
         (26, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_22__31_90_54_115.dds', 31, 90, 54, 115),
         (26, 23, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_23__22_84_46_109.dds', 22, 84, 46, 109),
         (26, 24, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_24__14_77_40_101.dds', 14, 77, 40, 101),
         (26, 25, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_25__10_69_35_90.dds', 10, 69, 35, 90),
         (26, 26, True): ('res:/UI/Texture/CharacterCreation/colorBits/26_26End__8_61_32_79.dds', 8, 61, 32, 79),
         (26, 26, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_26__8_61_32_79.dds', 8, 61, 32, 79),
         (26, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_2__10_37_35_58.dds', 10, 37, 35, 58),
         (26, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_3__14_26_40_50.dds', 14, 26, 40, 50),
         (26, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_4__22_18_46_43.dds', 22, 18, 46, 43),
         (26, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_5__31_12_54_37.dds', 31, 12, 54, 37),
         (26, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_6__42_9_62_34.dds', 42, 9, 62, 34),
         (26, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_7__55_8_72_32.dds', 55, 8, 72, 32),
         (26, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_8__65_9_85_34.dds', 65, 9, 85, 34),
         (26, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/26_9__73_12_96_37.dds', 73, 12, 96, 37),
         (28, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_10__76_14_99_39.dds', 76, 14, 99, 39),
         (28, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_11__83_20_107_44.dds', 83, 20, 107, 44),
         (28, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_12__88_28_113_51.dds', 88, 28, 113, 51),
         (28, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_13__92_38_117_58.dds', 92, 38, 117, 58),
         (28, 14, True): ('res:/UI/Texture/CharacterCreation/colorBits/28_14End__95_49_119_66.dds', 95, 49, 119, 66),
         (28, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_14__95_49_119_66.dds', 95, 49, 119, 66),
         (28, 15, True): ('res:/UI/Texture/CharacterCreation/colorBits/28_15End__95_61_119_78.dds', 95, 61, 119, 78),
         (28, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_15__95_61_119_78.dds', 95, 61, 119, 78),
         (28, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_16__92_69_117_89.dds', 92, 69, 117, 89),
         (28, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_17__88_76_113_99.dds', 88, 76, 113, 99),
         (28, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_18__83_83_107_107.dds', 83, 83, 107, 107),
         (28, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_19__76_88_99_113.dds', 76, 88, 99, 113),
         (28, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/28_1End__8_49_32_66.dds', 8, 49, 32, 66),
         (28, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_1__8_49_32_66.dds', 8, 49, 32, 66),
         (28, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_20__69_92_89_117.dds', 69, 92, 89, 117),
         (28, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_21__61_95_78_119.dds', 61, 95, 78, 119),
         (28, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_22__49_95_66_119.dds', 49, 95, 66, 119),
         (28, 23, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_23__38_92_58_117.dds', 38, 92, 58, 117),
         (28, 24, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_24__28_88_51_113.dds', 28, 88, 51, 113),
         (28, 25, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_25__20_83_44_107.dds', 20, 83, 44, 107),
         (28, 26, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_26__14_76_39_99.dds', 14, 76, 39, 99),
         (28, 27, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_27__10_69_35_89.dds', 10, 69, 35, 89),
         (28, 28, True): ('res:/UI/Texture/CharacterCreation/colorBits/28_28End__8_61_32_78.dds', 8, 61, 32, 78),
         (28, 28, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_28__8_61_32_78.dds', 8, 61, 32, 78),
         (28, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_2__10_38_35_58.dds', 10, 38, 35, 58),
         (28, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_3__14_28_39_51.dds', 14, 28, 39, 51),
         (28, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_4__20_20_44_44.dds', 20, 20, 44, 44),
         (28, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_5__28_14_51_39.dds', 28, 14, 51, 39),
         (28, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_6__38_10_58_35.dds', 38, 10, 58, 35),
         (28, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_7__49_8_66_32.dds', 49, 8, 66, 32),
         (28, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_8__61_8_78_32.dds', 61, 8, 78, 32),
         (28, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/28_9__69_10_89_35.dds', 69, 10, 89, 35),
         (2, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/2_1End__8_8_119_66.dds', 8, 8, 119, 66),
         (2, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/2_1__8_8_119_66.dds', 8, 8, 119, 66),
         (2, 2, True): ('res:/UI/Texture/CharacterCreation/colorBits/2_2End__8_61_119_119.dds', 8, 61, 119, 119),
         (2, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/2_2__8_61_119_119.dds', 8, 61, 119, 119),
         (30, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_10__72_11_92_36.dds', 72, 11, 92, 36),
         (30, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_11__78_15_101_40.dds', 78, 15, 101, 40),
         (30, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_12__84_22_109_45.dds', 84, 22, 109, 45),
         (30, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_13__89_30_114_52.dds', 89, 30, 114, 52),
         (30, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_14__93_40_118_59.dds', 93, 40, 118, 59),
         (30, 15, True): ('res:/UI/Texture/CharacterCreation/colorBits/30_15End__95_50_119_66.dds', 95, 50, 119, 66),
         (30, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_15__95_50_119_66.dds', 95, 50, 119, 66),
         (30, 16, True): ('res:/UI/Texture/CharacterCreation/colorBits/30_16End__95_61_119_77.dds', 95, 61, 119, 77),
         (30, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_16__95_61_119_77.dds', 95, 61, 119, 77),
         (30, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_17__93_68_118_87.dds', 93, 68, 118, 87),
         (30, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_18__89_75_114_97.dds', 89, 75, 114, 97),
         (30, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_19__84_82_109_105.dds', 84, 82, 109, 105),
         (30, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/30_1End__8_50_32_66.dds', 8, 50, 32, 66),
         (30, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_1__8_50_32_66.dds', 8, 50, 32, 66),
         (30, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_20__78_87_101_112.dds', 78, 87, 101, 112),
         (30, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_21__72_91_92_116.dds', 72, 91, 92, 116),
         (30, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_22__65_94_82_118.dds', 65, 94, 82, 118),
         (30, 23, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_23__56_95_71_119.dds', 56, 95, 71, 119),
         (30, 24, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_24__45_94_62_118.dds', 45, 94, 62, 118),
         (30, 25, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_25__35_91_55_116.dds', 35, 91, 55, 116),
         (30, 26, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_26__26_87_49_112.dds', 26, 87, 49, 112),
         (30, 27, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_27__18_82_43_105.dds', 18, 82, 43, 105),
         (30, 28, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_28__13_75_38_97.dds', 13, 75, 38, 97),
         (30, 29, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_29__9_68_34_87.dds', 9, 68, 34, 87),
         (30, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_2__9_40_34_59.dds', 9, 40, 34, 59),
         (30, 30, True): ('res:/UI/Texture/CharacterCreation/colorBits/30_30End__8_61_32_77.dds', 8, 61, 32, 77),
         (30, 30, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_30__8_61_32_77.dds', 8, 61, 32, 77),
         (30, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_3__13_30_38_52.dds', 13, 30, 38, 52),
         (30, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_4__18_22_43_45.dds', 18, 22, 43, 45),
         (30, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_5__26_15_49_40.dds', 26, 15, 49, 40),
         (30, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_6__35_11_55_36.dds', 35, 11, 55, 36),
         (30, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_7__45_9_62_33.dds', 45, 9, 62, 33),
         (30, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_8__56_8_71_32.dds', 56, 8, 71, 32),
         (30, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/30_9__65_9_82_33.dds', 65, 9, 82, 33),
         (32, 10, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_10__68_9_86_34.dds', 68, 9, 86, 34),
         (32, 11, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_11__74_12_95_37.dds', 74, 12, 95, 37),
         (32, 12, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_12__80_17_103_41.dds', 80, 17, 103, 41),
         (32, 13, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_13__86_24_110_47.dds', 86, 24, 110, 47),
         (32, 14, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_14__90_32_115_53.dds', 90, 32, 115, 53),
         (32, 15, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_15__93_41_118_59.dds', 93, 41, 118, 59),
         (32, 16, True): ('res:/UI/Texture/CharacterCreation/colorBits/32_16End__95_51_119_66.dds', 95, 51, 119, 66),
         (32, 16, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_16__95_51_119_66.dds', 95, 51, 119, 66),
         (32, 17, True): ('res:/UI/Texture/CharacterCreation/colorBits/32_17End__95_61_119_76.dds', 95, 61, 119, 76),
         (32, 17, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_17__95_61_119_76.dds', 95, 61, 119, 76),
         (32, 18, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_18__93_68_118_86.dds', 93, 68, 118, 86),
         (32, 19, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_19__90_74_115_95.dds', 90, 74, 115, 95),
         (32, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/32_1End__8_51_32_66.dds', 8, 51, 32, 66),
         (32, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_1__8_51_32_66.dds', 8, 51, 32, 66),
         (32, 20, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_20__86_80_110_103.dds', 86, 80, 110, 103),
         (32, 21, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_21__80_86_103_110.dds', 80, 86, 103, 110),
         (32, 22, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_22__74_90_95_115.dds', 74, 90, 95, 115),
         (32, 23, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_23__68_93_86_118.dds', 68, 93, 86, 118),
         (32, 24, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_24__61_95_76_119.dds', 61, 95, 76, 119),
         (32, 25, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_25__51_95_66_119.dds', 51, 95, 66, 119),
         (32, 26, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_26__41_93_59_118.dds', 41, 93, 59, 118),
         (32, 27, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_27__32_90_53_115.dds', 32, 90, 53, 115),
         (32, 28, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_28__24_86_47_110.dds', 24, 86, 47, 110),
         (32, 29, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_29__17_80_41_103.dds', 17, 80, 41, 103),
         (32, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_2__9_41_34_59.dds', 9, 41, 34, 59),
         (32, 30, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_30__12_74_37_95.dds', 12, 74, 37, 95),
         (32, 31, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_31__9_68_34_86.dds', 9, 68, 34, 86),
         (32, 32, True): ('res:/UI/Texture/CharacterCreation/colorBits/32_32End__8_61_32_76.dds', 8, 61, 32, 76),
         (32, 32, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_32__8_61_32_76.dds', 8, 61, 32, 76),
         (32, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_3__12_32_37_53.dds', 12, 32, 37, 53),
         (32, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_4__17_24_41_47.dds', 17, 24, 41, 47),
         (32, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_5__24_17_47_41.dds', 24, 17, 47, 41),
         (32, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_6__32_12_53_37.dds', 32, 12, 53, 37),
         (32, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_7__41_9_59_34.dds', 41, 9, 59, 34),
         (32, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_8__51_8_66_32.dds', 51, 8, 66, 32),
         (32, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/32_9__61_8_76_32.dds', 61, 8, 76, 32),
         (3, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/3_1__8_8_92_66.dds', 8, 8, 92, 66),
         (3, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/3_2__78_15_119_112.dds', 78, 15, 119, 112),
         (3, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/3_3__8_61_92_119.dds', 8, 61, 92, 119),
         (4, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/4_1End__8_8_66_66.dds', 8, 8, 66, 66),
         (4, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/4_1__8_8_66_66.dds', 8, 8, 66, 66),
         (4, 2, True): ('res:/UI/Texture/CharacterCreation/colorBits/4_2End__61_8_119_66.dds', 61, 8, 119, 66),
         (4, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/4_2__61_8_119_66.dds', 61, 8, 119, 66),
         (4, 3, True): ('res:/UI/Texture/CharacterCreation/colorBits/4_3End__61_61_119_119.dds', 61, 61, 119, 119),
         (4, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/4_3__61_61_119_119.dds', 61, 61, 119, 119),
         (4, 4, True): ('res:/UI/Texture/CharacterCreation/colorBits/4_4End__8_61_66_119.dds', 8, 61, 66, 119),
         (4, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/4_4__8_61_66_119.dds', 8, 61, 66, 119),
         (5, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/5_1__8_11_55_66.dds', 8, 11, 55, 66),
         (5, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/5_2__45_8_109_45.dds', 45, 8, 109, 45),
         (5, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/5_3__89_30_119_97.dds', 89, 30, 119, 97),
         (5, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/5_4__45_82_109_119.dds', 45, 82, 109, 119),
         (5, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/5_5__8_61_55_116.dds', 8, 61, 55, 116),
         (6, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/6_1End__8_15_49_66.dds', 8, 15, 49, 66),
         (6, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_1__8_15_49_66.dds', 8, 15, 49, 66),
         (6, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_2__35_8_92_36.dds', 35, 8, 92, 36),
         (6, 3, True): ('res:/UI/Texture/CharacterCreation/colorBits/6_3End__78_15_119_66.dds', 78, 15, 119, 66),
         (6, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_3__78_15_119_66.dds', 78, 15, 119, 66),
         (6, 4, True): ('res:/UI/Texture/CharacterCreation/colorBits/6_4End__78_61_119_112.dds', 78, 61, 119, 112),
         (6, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_4__78_61_119_112.dds', 78, 61, 119, 112),
         (6, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_5__35_91_92_119.dds', 35, 91, 92, 119),
         (6, 6, True): ('res:/UI/Texture/CharacterCreation/colorBits/6_6End__8_61_49_112.dds', 8, 61, 49, 112),
         (6, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/6_6__8_61_49_112.dds', 8, 61, 49, 112),
         (7, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_1__8_20_44_66.dds', 8, 20, 44, 66),
         (7, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_2__28_8_77_39.dds', 28, 8, 77, 39),
         (7, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_3__69_10_113_51.dds', 69, 10, 113, 51),
         (7, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_4__92_38_119_89.dds', 92, 38, 119, 89),
         (7, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_5__69_76_114_117.dds', 69, 76, 114, 117),
         (7, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_6__28_88_78_119.dds', 28, 88, 78, 119),
         (7, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/7_7__8_61_44_107.dds', 8, 61, 44, 107),
         (8, 1, True): ('res:/UI/Texture/CharacterCreation/colorBits/8_1End__8_24_41_66.dds', 8, 24, 41, 66),
         (8, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_1__8_24_41_66.dds', 8, 24, 41, 66),
         (8, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_2__24_8_66_41.dds', 24, 8, 66, 41),
         (8, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_3__61_8_103_41.dds', 61, 8, 103, 41),
         (8, 4, True): ('res:/UI/Texture/CharacterCreation/colorBits/8_4End__86_24_119_66.dds', 86, 24, 119, 66),
         (8, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_4__86_24_119_66.dds', 86, 24, 119, 66),
         (8, 5, True): ('res:/UI/Texture/CharacterCreation/colorBits/8_5End__86_61_119_103.dds', 86, 61, 119, 103),
         (8, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_5__86_61_119_103.dds', 86, 61, 119, 103),
         (8, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_6__61_86_103_119.dds', 61, 86, 103, 119),
         (8, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_7__24_86_66_119.dds', 24, 86, 66, 119),
         (8, 8, True): ('res:/UI/Texture/CharacterCreation/colorBits/8_8End__8_61_41_103.dds', 8, 61, 41, 103),
         (8, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/8_8__8_61_41_103.dds', 8, 61, 41, 103),
         (9, 1, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_1__8_27_39_66.dds', 8, 27, 39, 66),
         (9, 2, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_2__21_9_60_44.dds', 21, 9, 60, 44),
         (9, 3, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_3__52_8_92_36.dds', 52, 8, 92, 36),
         (9, 4, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_4__78_15_115_54.dds', 78, 15, 115, 54),
         (9, 5, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_5__94_43_119_84.dds', 94, 43, 119, 84),
         (9, 6, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_6__78_73_115_112.dds', 78, 73, 115, 112),
         (9, 7, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_7__52_91_92_119.dds', 52, 91, 92, 119),
         (9, 8, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_8__21_83_60_118.dds', 21, 83, 60, 118),
         (9, 9, False): ('res:/UI/Texture/CharacterCreation/colorBits/9_9__8_61_39_100.dds', 8, 61, 39, 100)}
        return 
        import os
        import blue
        import trinity
        from util import ResFile
        sourceRoot = blue.os.respath + 'UI/Texture/CharacterCreation/colorBits/'
        textures = os.listdir(sourceRoot)
        self.colorBits = {}
        for each in textures:
            if not each.endswith('.dds'):
                continue
            main = each.rstrip('.dds').split('__')
            (colorAmt, colorBitNo,) = main[0].split('_')
            (left, top, right, bottom,) = main[1].split('_')
            left = int(left)
            top = int(top)
            right = int(right)
            bottom = int(bottom)
            colorAmt = int(colorAmt)
            isEnd = False
            if colorBitNo.endswith('End'):
                colorBitNo = colorBitNo.rstrip('End')
                isEnd = True
            colorBitNo = int(colorBitNo)
            self.colorBits[(colorAmt, colorBitNo, isEnd)] = ('res:/UI/Texture/CharacterCreation/colorBits/' + each,
             left,
             top,
             right,
             bottom)
            print '(%s,%s,%s): ("res:/UI/Texture/CharacterCreation/colorBits/%s", %s, %s, %s, %s),' % (colorAmt,
             colorBitNo,
             isEnd,
             each,
             left,
             top,
             right,
             bottom)




    def InitColors(self, colors, activeColorIndex = 0):
        if not len(colors):
            colors = self.default_colors
        self.Flush()
        if self._showHalf is not None:
            availableSpace = 180.0
            availableColorAmount = LEGALCOLORAMT_HALF
        else:
            availableSpace = 360.0
            availableColorAmount = LEGALCOLORAMT_FULL
        colors = list(colors)
        totalColors = len(colors)
        if totalColors > max(availableColorAmount):
            print 'Color amount exceeded the maxmimum color amout'
            return 
        while totalColors not in availableColorAmount and colors:
            print 'The amount of colors provided for colorwheel is incorrent, is:',
            print totalColors,
            print 'but should be one of:',
            print availableColorAmount
            log.LogWarn('The amount of colors provided for colorwheel is incorrent, is:', totalColors, 'but should be one of:', availableColorAmount)
            colors.append(colors[-1])
            totalColors = len(colors)

        step = availableSpace / totalColors
        radianStep = mathUtil.DegToRad(step)
        angle = radianStep * 0.5
        self._currentStep = radianStep
        bitSize = totalColors
        if self._showHalf == TOPHALF:
            bitSize *= 2
        elif self._showHalf == BOTTOMHALF:
            bitSize *= 2
            angle += math.pi
        centerSize = 104
        centerPickRadius = 33
        colorParentSize = 128
        if self._scale is not None:
            centerSize = int(centerSize * self._scale)
            centerPickRadius = int(centerPickRadius * self._scale)
            colorParentSize = int(colorParentSize * self._scale)
        self.sr.centerParent = uicls.Transform(parent=self, pos=(0,
         0,
         centerSize,
         centerSize), pickRadius=centerPickRadius, align=uiconst.CENTER, state=uiconst.UI_DISABLED, name='centerTransform', idx=0)
        self.sr.colorSample = uicls.Sprite(parent=self.sr.centerParent, texturePath='res:/UI/Texture/CharacterCreation/ColorPointer.dds', ignoreSize=True, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.0))
        self.sr.colorBitsParent = uicls.Transform(parent=self, pos=(0,
         0,
         colorParentSize,
         colorParentSize), align=uiconst.TOPLEFT, name='colorBitsParent')
        activeColor = None
        for (i, (colorName, displayColor, colorValue,),) in enumerate(colors):
            if i == activeColorIndex:
                activeColor = colorValue
            self.AddColor(i, colorName, displayColor, colorValue, angle, i + 1, bitSize)
            angle += radianStep

        self._currentColors = colors
        if activeColor is not None:
            self.SetActiveColor(activeColor, initing=True)



    def AddCurveSet_t(self, cs):
        cs.Play()
        uicore.scene.curveSets.append(cs)



    def CreateBinding(self, curveSet, curve, destinationObject, attribute, sourceAttribute = 'currentValue'):
        binding = trinity.TriValueBinding()
        binding.sourceObject = curve
        binding.sourceAttribute = sourceAttribute
        binding.destinationObject = destinationObject
        binding.destinationAttribute = attribute
        curveSet.bindings.append(binding)
        return binding



    def CreateScalarCurve(self, curveSet, length, endValue, startTimeOffset = 0.0, startValue = 0.0, cycle = False):
        curve = trinity.Tr2ScalarCurve()
        if startTimeOffset:
            curve.AddKey(0.0, startValue)
        curve.AddKey(startTimeOffset, startValue)
        curve.AddKey(startTimeOffset + length, endValue)
        curve.interpolation = trinity.TR2CURVE_HERMITE
        curve.cycle = cycle
        curveSet.curves.append(curve)
        return curve



    def CreatePerlinCurve(self, curveSet, scale = 1.0, offset = 0.0, speed = 0.0):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curveSet.curves.append(curve)



    def EnableHalf(self, whathalf):
        self._showHalf = whathalf



    def AddColor(self, idx, colorName, displayColor, colorValue, radianAngle, colorNo, colorAmount):
        isEnd = False
        if self._showHalf is not None:
            if colorNo == 1 or colorAmount / 2 == colorNo:
                isEnd = True
        if self._showHalf == BOTTOMHALF:
            colorNo += colorAmount / 2
        if (colorAmount, colorNo, isEnd) not in self.colorBits:
            log.LogWarn("Couldn't find texture for", colorAmount, colorNo, 'in character creation colorwheel')
            return 
        (path, left, top, right, bottom,) = self.colorBits[(colorAmount, colorNo, isEnd)]
        if self._scale is not None:
            left = int(left * self._scale)
            top = int(top * self._scale)
            right = int(right * self._scale)
            bottom = int(bottom * self._scale)
        colorBit = uicls.Sprite(parent=self.sr.colorBitsParent, texturePath=path, ignoreSize=True, align=uiconst.TOPLEFT, pos=(left,
         top,
         right - left,
         bottom - top), hint=colorName, state=uiconst.UI_DISABLED, color=displayColor, name='colorBit_%s' % colorNo)
        colorBit.centerRadian = radianAngle
        colorBit.colorValue = colorValue
        colorBit.colorName = colorName
        colorBit.displayColor = displayColor
        if uicore.newRendererEnabled:
            cs = trinity.TriCurveSet()
            cs.name = 'color fade in'
            curve = self.CreateScalarCurve(cs, 0.3, left, startTimeOffset=0.05 * idx, startValue=64)
            self.CreateBinding(cs, curve, colorBit, 'displayX')
            curve = self.CreateScalarCurve(cs, 0.3, top, startTimeOffset=0.05 * idx, startValue=64)
            self.CreateBinding(cs, curve, colorBit, 'displayY')
            curve = self.CreateScalarCurve(cs, 0.3, right - left, startTimeOffset=0.05 * idx, startValue=(right - left) * 0.1)
            self.CreateBinding(cs, curve, colorBit, 'displayWidth')
            curve = self.CreateScalarCurve(cs, 0.3, bottom - top, startTimeOffset=0.05 * idx, startValue=(bottom - top) * 0.1)
            self.CreateBinding(cs, curve, colorBit, 'displayHeight')
            colorBit.AddCurveSet(cs)
            import random
            colorBit.depth = random.random()
            cs.Play()



    def OnMouseMove(self, *args):
        radianFromCenter = self.GetRotationAngleFromCenter()
        self._lastRadian = radianFromCenter
        setActive = self.GetColorBitFromRadian(self._lastRadian)
        self.sr.centerParent.SetOrder(0)
        lastActive = getattr(self, 'lastActive', None)
        if setActive:
            if lastActive is not setActive:
                sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_color_wheel_panel_light_play'))
                self.lastActive = setActive
            setActive.SetOrder(0)



    def OnClick(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_color_wheel_color_selected_play'))
        setActive = self.GetColorBitFromRadian(self._lastRadian)
        if setActive:
            self.SetActiveColor(setActive.colorValue)



    def OnMouseExit(self, *args):
        if self.sr.centerParent:
            self.sr.centerParent.SetOrder(0)
        self.lastActive = None



    def GetRotationAngleFromCenter(self):
        (x, y,) = (uicore.uilib.x, uicore.uilib.y)
        (l, t, w, h,) = self.GetAbsolute()
        (px, py,) = (l + w / 2, t + h / 2)
        tn = (abs(x - px) or 1e-07) / float(abs(y - py) or 1e-07)
        if y < py:
            if x > px:
                rot = math.pi * 0.5 + math.atan(tn)
            else:
                rot = math.pi * 0.5 - math.atan(tn)
        elif x > px:
            rot = math.pi * 1.5 - math.atan(tn)
        else:
            rot = math.pi * 1.5 + math.atan(tn)
        return rot



    def UpdateColors(self, *args):
        pass



    def RadToDeg(self, rad):
        return rad / math.pi * 180.0



    def SetActiveColor(self, colorValue, initing = False):
        for each in self.sr.colorBitsParent.children:
            if not hasattr(each, 'centerRadian'):
                continue
            if each.colorValue == colorValue:
                if not initing:
                    uthread.new(self.OnSetValue, self, colorValue, each.colorName)
                return self.ShowActiveColorBit(each)




    def ShowActiveColorBit(self, colorBit):
        if colorBit:
            fromRad = self.sr.centerParent.GetRotation()
            if fromRad < 0:
                fromRad += math.pi * 2
            elif fromRad > math.pi * 2:
                fromRad -= math.pi * 2
            fromDeg = self.RadToDeg(fromRad)
            toRad = math.pi - colorBit.centerRadian
            if toRad < 0:
                toRad += math.pi * 2
            elif toRad > math.pi * 2:
                toRad -= math.pi * 2
            toDeg = self.RadToDeg(toRad)
            travel = abs(fromDeg - toDeg)
            if travel > 180.0:
                if toDeg > fromDeg:
                    fromDeg += 360.0
                else:
                    toDeg += 360.0
                travel = 360.0 - travel
            uthread.new(uicore.effect.Rotate, self.sr.centerParent, time=max(0.1, travel * 0.002), fromRot=fromDeg, toRot=toDeg)
            uthread.new(uicore.effect.CombineEffects, self.sr.colorSample, rgb=colorBit.displayColor[:3], alpha=colorBit.displayColor[3])



    def OnSetValue(self, control, colorValue, colorName):
        pass



    def GetColorBitFromRadian(self, radian):
        for each in self.sr.colorBitsParent.children:
            if not hasattr(each, 'centerRadian'):
                continue
            if each.centerRadian - self._currentStep / 2 < 0:
                if each.centerRadian + math.pi * 2 - self._currentStep / 2 < radian < each.centerRadian + math.pi * 2:
                    return each
            if each.centerRadian - self._currentStep / 2 < radian < each.centerRadian + self._currentStep / 2:
                return each




    def NormalizeRadian(self, radian):
        if radian < 0:
            return radian + math.pi




