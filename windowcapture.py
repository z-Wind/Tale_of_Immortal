import numpy as np
import win32gui, win32ui, win32con


class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_rectangle = None
    cropped_x = 0
    cropped_y = 0
    cropped_w = None
    cropped_h = None
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None, cropped_rectangle=None):
        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = self.find_window_by_sub_string(window_name)

            if not self.hwnd:
                raise Exception("Window not found: {}".format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        if cropped_rectangle:
            self.cropped_rectangle = cropped_rectangle
            (self.cropped_x, self.cropped_y, self.cropped_w, self.cropped_h) = cropped_rectangle

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):
        # refresh
        if self.cropped_rectangle:
            w = self.cropped_w
            h = self.cropped_h
        else:
            window_rect = win32gui.GetWindowRect(self.hwnd)
            self.w = window_rect[2] - window_rect[0]
            self.h = window_rect[3] - window_rect[1]
            w = self.w
            h = self.h

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (w, h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype="uint8")
        img.shape = (h, w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[..., :3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(winEnumHandler, None)

    # give substring to find window
    def find_window_by_sub_string(self, window_name):
        def windowEnumerationHandler(hwnd, top_windows):
            top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for i in top_windows:
            if window_name in i[1]:
                return i[0]

        return None

    # active window
    def active_window(self, hwnd):
        tup = win32gui.GetWindowPlacement(hwnd)
        if tup[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, 9)
            win32gui.SetForegroundWindow(hwnd)
        elif tup[1] == win32con.SW_SHOWNORMAL:
            win32gui.ShowWindow(hwnd, 5)
            win32gui.SetForegroundWindow(hwnd)
        else:
            win32gui.SetForegroundWindow(hwnd)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        # refresh
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

        return (pos[0] + self.offset_x, pos[1] + self.offset_y)
