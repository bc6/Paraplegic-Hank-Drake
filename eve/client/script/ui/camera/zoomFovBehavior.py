import cameras
MAX_FOV = 0.8
MIN_FOV = 0.7

class ZoomFovBehavior(cameras.CameraBehavior):
    __guid__ = 'cameras.ZoomFovBehavior'

    def __init__(self):
        cameras.CameraBehavior.__init__(self)



    def ProcessCameraUpdate(self, camera, now, frameTime):
        zoom = camera.zoom
        if zoom < camera.minZoom:
            zoom = camera.minZoom
        range = camera.maxZoom - camera.minZoom
        curr = camera.maxZoom - zoom
        perc = curr / range
        camera.fieldOfView = MAX_FOV - (MAX_FOV - MIN_FOV) * perc




