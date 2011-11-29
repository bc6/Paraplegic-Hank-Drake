import util
import uicls
import uiutil
import uiconst
import cameras
import animation
ORIGINAL_SETTINGS = {}

class DebugChangeCameraSettingsWindow(uicls.Window):
    __guid__ = 'cameras.DebugChangeCameraSettingsWindow'
    default_width = 550
    default_height = 595
    default_minSize = (550, 595)
    default_windowID = 'DebugChangeCameraSettingsWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)
        self.SetWndIcon('40_11')
        self.heading = uicls.Label(text='Change Camera Settings', parent=self.sr.main, align=uiconst.TOPLEFT, left=65, top=-40, width=self.width - 10, height=self.height - 10, fontsize=25, singleline=True, uppercase=1)
        self.camClient = sm.GetService('cameraClient')
        camera = self.camClient.GetActiveCamera()
        rowPos = 15
        colPos = 15
        self.editControls = []
        rowPos = self.AddEntry(rowPos, colPos, 'minZoom', 'Min Zoom', camera)
        rowPos = self.AddEntry(rowPos, colPos, 'maxZoom', 'Max Zoom', camera)
        rowPos = self.AddEntry(rowPos, colPos, 'minPitch', 'Min Pitch', camera)
        rowPos = self.AddEntry(rowPos, colPos, 'maxPitch', 'Max Pitch', camera)
        rowPos = self.AddEntry(rowPos, colPos, 'fieldOfView', 'Field of View', camera)
        rowPos = self.AddEntry(rowPos, colPos, 'MAX_SPIN_SPEED', 'Max Spin Speed', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'SPIN_RESISTANCE', 'Spin Resistance', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'SPIN_DELTA_MODIFIER', 'Spin Delta Modifier', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'ZOOM_SPEED_MODIFIER', 'Zoom Speed Modifier', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'SPIN_FALLOFF_RATIO', 'Spin Falloff Ratio', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'AVATAR_SHOULDER_HEIGHT', 'Avatar Shoulder Height', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'CHARACTER_OFFSET_FACTOR', 'Avatar Offset', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'ZOOM_TOGGLE_TRANSITION_SPEEDUP_FACTOR', 'Zoom toggle speedup factor', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'ZOOM_TOGGLE_TRANSITION_SPEEDUP_TEMPERING', 'Zoom toggle tempering', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'MAX_MOUSE_DELTA', 'Max mouse move speed', cameras)
        rowPos = 15
        colPos += 265
        rowPos = self.AddEntry(rowPos, colPos, 'OPTIMAL_SCREEN_ASPECT_RATIO', 'Optimal Screen Ratio', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'PITCH_OFFSET_LENGTH_MODIFIER', 'Pitch Offset Length Modifier', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'AVATAR_COLLISION_RESTRICTION_ANGLE', 'Avatar coll. restriction angle', animation)
        rowPos = self.AddEntry(rowPos, colPos, 'FLY_CAMERA_ACCELERATION', 'Fly camera speed', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'CLOSEST', 'Collision Closest Point', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'ZOOM_POWER_FAR', 'Zoom In Speed (Far)', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'ZOOM_POWER_CLOSE', 'Zoom In Speed (Close)', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'NORMAL_COLLISION_SPHERE', 'Normal Collision Radius', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'CAMERA_BUFFER_SPHERE_RADIUS', 'Collision Buffer', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'AVATAR_MIN_DISPLAY_DISTANCE', 'Avatar Min Display Distance', cameras)
        rowPos = self.AddEntry(rowPos, colPos, 'CRITICAL_COLLISION_SMOOTHING_STEPS', 'Critical Collision Smoothing Steps', cameras)
        player = sm.GetService('entityClient').GetPlayerEntity()
        rowPos = self.AddEntry(rowPos, colPos, 'collisionDetectionFeelerLength', 'Animation collision look-ahead', player.movement.characterController)
        sb = uicls.Button(parent=self.sr.main, label='Submit', func=self.Submit, pos=(212,
         rowPos + 5,
         90,
         25))
        uicls.Button(parent=self.sr.main, label='Reset', func=self.Reset, pos=(sb.left + sb.width + 2,
         rowPos + 5,
         90,
         25))



    def AddEntry(self, rowPos, colPos, variableName, humanName, associatedObject):
        if not hasattr(associatedObject, variableName):
            uicls.EveLabelMedium(text=humanName + ': Not on current camera', parent=self.sr.main, align=uiconst.RELATIVE, left=colPos, top=rowPos)
        elif variableName not in cameras.ORIGINAL_SETTINGS:
            cameras.ORIGINAL_SETTINGS[variableName] = getattr(associatedObject, variableName)
        uicls.EveLabelMedium(text=humanName + ':', parent=self.sr.main, align=uiconst.RELATIVE, left=colPos, top=rowPos)
        edit = uicls.SinglelineEdit(name=variableName, readonly=False, parent=self.sr.main, singleline=True, align=uiconst.RELATIVE, pos=(colPos + 145,
         rowPos - 5,
         100,
         25), padding=(0, 0, 0, 0))
        edit.OnReturn = self.EditEnterPressed
        edit.associatedObject = associatedObject
        self.editControls.append(edit)
        edit.SetValue(str(getattr(associatedObject, variableName)))
        rowPos += 30
        return rowPos



    def EditEnterPressed(self, *args):
        self.Submit(args)



    def Reset(self, *args):
        for edit in self.editControls:
            variableName = edit.name
            originalValue = cameras.ORIGINAL_SETTINGS[variableName]
            edit.SetValue(str(originalValue))
            if hasattr(edit.associatedObject, variableName):
                setattr(edit.associatedObject, variableName, originalValue)




    def Submit(self, *args):
        for edit in self.editControls:
            try:
                variableName = edit.name
                value = float(edit.GetValue())
            except:
                eve.Message('CustomInfo', {'info': '%s: Incorrect input, please only use floating point values.' % edit.name})
                return 
            if hasattr(edit.associatedObject, variableName):
                setattr(edit.associatedObject, variableName, value)
            else:
                eve.Message('CustomInfo', {'info': 'Current camera has been changed, the current camera does not support %s.' % variableName})




exports = util.AutoExports('cameras', locals())

