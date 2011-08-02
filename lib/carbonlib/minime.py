import sys
import ctypes
import blue
import trinity
import geo2
import math
import time
import log
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int)
OnKeyDown = None
OnKeyUp = None
OnChar = None

class Camera(object):

    def __init__(self, fov, front, back, asp):
        self.minZoomDistance = 0.05
        self.maxZoomDistance = 100000.0
        self.fieldOfView = fov
        self.frontClip = front
        self.backClip = back
        self.aspectRatio = asp
        self.viewMatrix = geo2.MatrixIdentity()
        self.SetPosition((0.0, 50.0, -100.0))
        self.Focus((0.0, 0.0, 0.0))



    def Update(self):
        trinity.SetViewTransform(self.viewMatrix)
        trinity.SetPerspectiveProjection(self.fieldOfView, self.frontClip, self.backClip, self.aspectRatio)



    def Zoom(self, val):
        dev = trinity.GetDevice()
        pos = self.GetPosition()
        target = self.GetPointOfInterest()
        view = geo2.Vec3Subtract(pos, target)
        length = geo2.Vec3Length(view)
        geo2.Vec3Normalize(view)
        nextPos = geo2.Vec3Add(pos, geo2.Vec3Scale(view, length * val))
        nextLength = geo.Vec3Length(geo2.Vec3Subtract(nextPos, target))
        if nextLength < self.minZoomDistance:
            nextPos = geo2.Vec3Add(target, geo2.Vec3Scale(view, self.minZoomDistance))
        elif nextLength > self.maxZoomDistance:
            nextPos = geo2.Vec3Add(target, geo2.Vec3Scale(view, self.maxZoomDistance))
        self.SetPosition(nextPos)



    def Orbit(self, yaw, pitch):
        dev = trinity.GetDevice()
        self.Focus(self.pointOfInterest)
        up = (0.0, 1.0, 0.0)
        t = (self.viewMatrix[1][0], self.viewMatrix[1][1], self.viewMatrix[1][2])
        if geo2.Vec3Dot(t, up) <= 0.0:
            pitch = -pitch
            yaw = -yaw
        pos = self.GetPosition()
        target = self.pointOfInterest
        view = geo2.Vec3Subtract(pos, target)
        view = geo2.Vec3Normalize(view)
        right = geo2.Vec3Cross(view, up)
        ipmat = geo2.MatrixTranslation(-target[0], -target[1], -target[2])
        pmat = geo2.MatrixTranslation(target[0], target[1], target[2])
        mat = geo2.MatrixInverse(self.viewMatrix)
        yrotMat = geo2.MatrixRotationAxis(up, yaw)
        rrotMat = geo2.MatrixRotationAxis(right, pitch)
        yrotMat = geo2.MatrixMultiply(yrotMat, rrotMat)
        mat = geo2.MatrixMultiply(mat, ipmat)
        mat = geo2.MatrixMultiply(mat, yrotMat)
        mat = geo2.MatrixMultiply(mat, pmat)
        self._position = (mat[3][0], mat[3][1], mat[3][2])
        self.viewMatrix = geo2.MatrixInverse(mat)



    def Focus(self, point, dist = -1.0):
        dev = trinity.GetDevice()
        pos = self.GetPosition()
        up = (0.0, 1.0, 0.0)
        t = (self.viewMatrix[1][0], self.viewMatrix[1][1], self.viewMatrix[1][2])
        if geo2.Vec3Dot(t, up) <= 0.0:
            up.y = -1.0
        self.pointOfInterest = point
        if hasattr(trinity, 'IsRightHanded') and trinity.IsRightHanded():
            self.viewMatrix = geo2.MatrixLookAtRH(pos, point, up)
        else:
            self.viewMatrix = geo2.MatrixLookAtLH(pos, point, up)
        if dist > 0.0:
            view = geo2.Vec3Subtract(pos, point)
            view = geo2.Vec3Normalize(view)
            self.SetPosition(geo2.Vec3Add(point, geo2.Vec3Scale(view, dist)))



    def Pan(self, diff):
        pos = self.GetPosition()
        self.SetPosition(geo2.Vec3Add(pos, diff))
        self.pointOfInterest = geo2.Vec3Add(self.pointOfInterest, diff)



    def SetPosition(self, pos):
        mat = list(geo2.MatrixInverse(self.viewMatrix))
        mat[3] = (pos[0],
         pos[1],
         pos[2],
         1.0)
        self.viewMatrix = geo2.MatrixInverse(mat)
        self._position = pos



    def GetPosition(self):
        return self._position



    def GetPointOfInterest(self):
        return self.pointOfInterest



CS_HREDRAW = 2
CS_VREDRAW = 1
NULL = 0
IDI_APPLICATION = 32512
IDC_ARROW = 32512
WHITE_BRUSH = 0
BLACK_BRUSH = 4
WS_OVERLAPPEDWINDOW = 13565952
CW_USEDEFAULT = -2147483648L
SW_SHOWNORMAL = 1
WM_PAINT = 15
DT_SINGLELINE = 32
DT_CENTER = 1
DT_VCENTER = 4
WM_DESTROY = 2
GWL_STYLE = -16
WS_POPUP = -2147483648L
WS_SYSMENU = 524288
WS_VISIBLE = 268435456
WS_MINIMIZEBOX = 131072
WS_CAPTION = 12582912
WM_CLOSE = 16
WM_QUIT = 18
WM_SIZE = 5
WM_SETCURSOR = 32
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_ACTIVATE = 6
WM_SYSCOMMAND = 274
WM_ERASEBKGND = 20
SC_KEYMENU = 61696
WA_ACTIVE = 1
WA_CLICKACTIVE = 2
WS_EX_TOPMOST = 8
WM_KEYDOWN = 256
WM_KEYUP = 257
WM_CHAR = 258
VK_RETURN = 13
VK_SHIFT = 16
VK_CONTROL = 17
VK_ESCAPE = 27
VK_SPACE = 32
VK_PRIOR = 33
VK_NEXT = 34
VK_END = 35
VK_HOME = 36
VK_LEFT = 37
VK_UP = 38
VK_RIGHT = 39
VK_DOWN = 40
VK_SELECT = 41
VK_PRINT = 42
VK_EXECUTE = 43
VK_SNAPSHOT = 44
VK_INSERT = 45
VK_DELETE = 46
VK_HELP = 47
SWP_NOSIZE = 1
SWP_NOMOVE = 2
SWP_NOZORDER = 4
uilib = None

def SetWindowSize(w, h):
    dev = trinity.GetDevice()
    hwnd = dev.GetWindow()
    ctypes.windll.user32.SetWindowPos(ctypes.c_int(hwnd), 0, 0, 0, w, h, SWP_NOZORDER | SWP_NOMOVE)



def SetWindowPos(x, y):
    dev = trinity.GetDevice()
    hwnd = dev.GetWindow()
    ctypes.windll.user32.SetWindowPos(ctypes.c_int(hwnd), 0, x, y, 0, 0, SWP_NOZORDER | SWP_NOSIZE)



def StartUI():
    uilib = uicls.UIlib()



class WNDCLASS(ctypes.Structure):
    _fields_ = [('style', ctypes.c_uint),
     ('lpfnWndProc', WNDPROC),
     ('cbClsExtra', ctypes.c_int),
     ('cbWndExtra', ctypes.c_int),
     ('hInstance', ctypes.c_int),
     ('hIcon', ctypes.c_int),
     ('hCursor', ctypes.c_int),
     ('hbrBackground', ctypes.c_int),
     ('lpszMenuName', ctypes.c_char_p),
     ('lpszClassName', ctypes.c_char_p)]


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
     ('top', ctypes.c_long),
     ('right', ctypes.c_long),
     ('bottom', ctypes.c_long)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [('hdc', ctypes.c_int),
     ('fErase', ctypes.c_int),
     ('rcPaint', RECT),
     ('fRestore', ctypes.c_int),
     ('fIncUpdate', ctypes.c_int),
     ('rgbReserved', ctypes.c_char * 32)]


class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]


class MSG(ctypes.Structure):
    _fields_ = [('hwnd', ctypes.c_int),
     ('message', ctypes.c_uint),
     ('wParam', ctypes.c_int),
     ('lParam', ctypes.c_int),
     ('time', ctypes.c_int),
     ('pt', POINT)]


def ErrorIfZero(handle):
    if handle == 0:
        raise ctypes.WinError()
    else:
        return handle



def SetConstantYawRotation(rad_per_sec):
    global START_TIME
    START_TIME = time.clock()

    def render_cb(dev):
        global START_TIME
        current = time.clock()
        m = geo2.MatrixRotationY((current - START_TIME) * rad_per_sec)
        trinity.SetViewTransform(geo2.MatrixMultiply(m, trinity.GetViewTransform()))
        START_TIME = current


    trinity.device.preRenderCallback = render_cb



def Main(postCreateCallback = None, fullscreen = False, size = None):
    CreateWindowEx = ctypes.windll.user32.CreateWindowExA
    CreateWindowEx.argtypes = [ctypes.c_int,
     ctypes.c_char_p,
     ctypes.c_char_p,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int]
    CreateWindowEx.restype = ErrorIfZero
    wndclass = WNDCLASS()
    wndclass.style = CS_HREDRAW | CS_VREDRAW
    wndclass.lpfnWndProc = WNDPROC(WndProc)
    wndclass.cbClsExtra = wndclass.cbWndExtra = 0
    wndclass.hInstance = ctypes.windll.kernel32.GetModuleHandleA(ctypes.c_int(NULL))
    wndclass.hIcon = ctypes.windll.user32.LoadIconA(ctypes.c_int(NULL), ctypes.c_int(IDI_APPLICATION))
    wndclass.hCursor = ctypes.windll.user32.LoadCursorA(ctypes.c_int(NULL), ctypes.c_int(IDC_ARROW))
    wndclass.lpszMenuName = None
    wndclass.lpszClassName = 'MainWin'
    wndclass.hbrBackground = ctypes.windll.gdi32.GetStockObject(ctypes.c_int(BLACK_BRUSH))
    if not ctypes.windll.user32.RegisterClassA(ctypes.byref(wndclass)):
        raise ctypes.WinError()
    if fullscreen:
        dspmode = trinity.d3d.GetAdapterDisplayMode()
        if size is None:
            width = dspmode['Width']
            height = dspmode['Height']
        else:
            (width, height,) = size
        hwnd = CreateWindowEx(0, wndclass.lpszClassName, 'MINI ME', WS_EX_TOPMOST | WS_POPUP, 0, 0, width, height, NULL, NULL, wndclass.hInstance, NULL)
    else:
        hwnd = CreateWindowEx(0, wndclass.lpszClassName, 'MINI ME', WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, NULL, NULL, wndclass.hInstance, NULL)
    ctypes.windll.user32.ShowWindow(ctypes.c_int(hwnd), ctypes.c_int(SW_SHOWNORMAL))
    ctypes.windll.user32.UpdateWindow(ctypes.c_int(hwnd))
    rect = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    asp = float(rect.right) / float(rect.bottom)
    if fullscreen:
        trinity.device.CreateFullScreenDevice(hwnd, rect.right, rect.bottom)
    else:
        trinity.device.CreateWindowedDevice(hwnd, rect.right, rect.bottom)
    trinity.SetPerspectiveProjection(1.57, 1.0, 1000.0, asp)
    if postCreateCallback and callable(postCreateCallback):
        postCreateCallback()
    msg = MSG()
    pMsg = ctypes.pointer(msg)
    running = True
    TranslateMessage = ctypes.windll.user32.TranslateMessage
    DispatchMessageA = ctypes.windll.user32.DispatchMessageA
    PeekMessageA = ctypes.windll.user32.PeekMessageA
    while running:
        while PeekMessageA(pMsg, NULL, 0, 0, 1):
            if msg.message == WM_QUIT:
                running = False
                break
            TranslateMessage(pMsg)
            DispatchMessageA(pMsg)

        blue.os.Pump()

    ctypes.windll.user32.PostQuitMessage(0)
    return msg.wParam



def WndProc(hwnd, message, wParam, lParam):
    dev = trinity.device
    if message == WM_DESTROY:
        ctypes.windll.user32.PostQuitMessage(0)
        return 0
    else:
        if message == WM_CLOSE:
            ctypes.windll.user32.PostQuitMessage(0)
            return 0
        if message == WM_SIZE:
            if dev.GetWindow():
                rect = RECT()
                ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
                viewTrans = trinity.GetViewTransform()
                fov = trinity.GetFieldOfView()
                front = trinity.GetFrontClip()
                back = trinity.GetBackClip()
                (w, h,) = (rect.right, rect.bottom)
                asp = float(w) / float(h)
                dev.ChangeBackBufferSize(w, h)
                trinity.SetPerspectiveProjection(fov, front, back, asp)
                trinity.SetViewTransform(viewTrans)
        elif message == WM_LBUTTONDOWN:
            rect = RECT()
            ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
            offset = POINT()
            ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(offset))
            ctypes.windll.user32.OffsetRect(ctypes.byref(rect), offset.x, offset.y)
            ctypes.windll.user32.ClipCursor(ctypes.byref(rect))
        elif message == WM_LBUTTONUP:
            ctypes.windll.user32.ClipCursor(0)
        elif message == WM_ACTIVATE:
            if not (wParam == WA_ACTIVE and wParam == WA_CLICKACTIVE):
                ctypes.windll.user32.ClipCursor(0)
        elif message == WM_SYSCOMMAND:
            if wParam == SC_KEYMENU:
                return 0
        elif message == WM_ERASEBKGND:
            return 0
        if message == WM_KEYDOWN:
            if OnKeyDown is not None and callable(OnKeyDown):
                OnKeyDown(wParam)
        elif message == WM_KEYUP:
            if OnKeyUp is not None and callable(OnKeyUp):
                OnKeyUp(wParam)
        elif message == WM_CHAR:
            if OnChar is not None and callable(OnChar):
                OnChar(wParam)
        if uilib is not None:
            return uilib.HandleWinMessage(hwnd, message, wParam, lParam)
        return ctypes.windll.user32.DefWindowProcA(ctypes.c_int(hwnd), ctypes.c_int(message), ctypes.c_int(wParam), ctypes.c_int(lParam))



