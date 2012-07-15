#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/paperDoll/paperDollConfiguration.py
import paperDoll as PD

class PerformanceOptions:
    __guid__ = 'paperDoll.PerformanceOptions'
    useLodForRedfiles = False
    if hasattr(const, 'PAPERDOLL_LOD_RED_FILES'):
        useLodForRedfiles = const.PAPERDOLL_LOD_RED_FILES
    collapseShadowMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_SHADOWMESH'):
        collapseShadowMesh = const.PAPERDOLL_COLLAPSE_SHADOWMESH
    collapseMainMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_MAINMESH'):
        collapseMainMesh = const.PAPERDOLL_COLLAPSE_MAINMESH
    collapsePLPMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_PLPMESH'):
        collapsePLPMesh = const.PAPERDOLL_COLLAPSE_PLPMESH
    preloadNudeAssets = False
    if hasattr(const, 'PAPERDOLL_PRELOAD_NUDE_ASSETS'):
        preloadNudeAssets = const.PAPERDOLL_PRELOAD_NUDE_ASSETS
    preloadGenericHeadModifiers = False
    shadowLod = 2
    collapseVerbose = False
    lodTextureSizes = [(2048, 1024), (512, 256), (256, 128)]
    textureSizeFactors = {PD.DIFFUSE_MAP: 1,
     PD.NORMAL_MAP: 1,
     PD.SPECULAR_MAP: 1}
    maskMapTextureSize = (1024, 512)
    updateFreq = {}
    useLod2DDS = False
    logLodPerformance = False
    maxLodQueueActiveUp = 3
    maxLodQueueActiveDown = 6
    EnsureCompleteBody = True
    singleBoneLod = 2

    @staticmethod
    def SetEnableYamlCache(enable, resData = None):
        yamlPreloader = PD.YamlPreloader()
        if enable:
            yamlPreloader.SetVerbosity(True)
            extensions = ['.yaml',
             '.pose',
             '.type',
             '.color']
            if resData:
                yamlPreloader.SetResData(resData)
                yamlPreloader.Preload(extensions=extensions)
            else:
                yamlPreloader.Preload(rootFolder=PD.FEMALE_BASE_PATH, extensions=extensions)
                yamlPreloader.Preload(rootFolder=PD.FEMALE_BASE_LOD_PATH, extensions=extensions)
                yamlPreloader.Preload(rootFolder=PD.MALE_BASE_PATH, extensions=extensions)
                yamlPreloader.Preload(rootFolder=PD.MALE_BASE_LOD_PATH, extensions=extensions)
        else:
            yamlPreloader.Clear()

    @staticmethod
    def SetEnableLodQueue(enable):
        if enable:
            PD.LodQueue.instance = PD.LodQueue()
        else:
            PD.LodQueue.instance = None

    @staticmethod
    def EnableOptimizations():
        PerformanceOptions.collapseShadowMesh = False
        PerformanceOptions.collapseMainMesh = False
        PerformanceOptions.collapsePLPMesh = False
        PerformanceOptions.shadowLod = 1
        PerformanceOptions.singleBoneLod = 1
        PerformanceOptions.updateFreq = {0: 0,
         1: 20,
         2: 8}
        try:
            import trinity
            trinity.settings.SetValue('skinnedLowDetailThreshold', 250)
            trinity.settings.SetValue('skinnedMediumDetailThreshold', 650)
            trinity.settings.SetValue('skinnedMediumLowMargin', 70)
            trinity.settings.SetValue('skinnedHighMediumMargin', 100)
            PD.Factory.PreloadShaders()
        except (ImportError, AttributeError):
            pass

        PerformanceOptions.SetEnableLodQueue(True)
        PerformanceOptions.logLodPerformance = True

    @staticmethod
    def EnableEveOptimizations():
        PerformanceOptions.useLodForRedfiles = True
        PerformanceOptions.useLod2DDS = True