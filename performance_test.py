from windowcapture import WindowCapture
from vision import Vision
from bot import TOMBot
import cv2 as cv


def test_screenshot(benchmark):
    window_title = None
    cropped_rectangle = None

    @benchmark
    def f():
        wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
        screenshot = wincap.get_screenshot()


def test_vision(benchmark):
    match_path = "tests/frog.png"
    threshold = 0.6
    hsv_filter = None

    # initialize the Vision class
    vision = Vision(match_path, threshold, hsv_filter)
    # 不同的 process 皆需重建 control gui
    vision.init_control_gui()

    window_title = None
    cropped_rectangle = None
    wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
    screenshot = wincap.get_screenshot()

    @benchmark
    def f():
        # pre-process the image
        processed_image = vision.apply_hsv_filter(screenshot)

        # do object detection
        rectangles = vision.find(processed_image)

        if rectangles.size != 0:
            targets = vision.get_click_points(rectangles)

        # for control gui
        cv.waitKey(1)


def test_vision_scale(benchmark):
    match_path = "tests/frog.png"
    threshold = 0.6
    hsv_filter = None

    # initialize the Vision class
    vision = Vision(match_path, threshold, hsv_filter, scale_down=2)
    # 不同的 process 皆需重建 control gui
    vision.init_control_gui()

    window_title = None
    cropped_rectangle = None
    wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
    screenshot = wincap.get_screenshot()

    @benchmark
    def f():
        # pre-process the image
        processed_image = vision.apply_hsv_filter(screenshot)

        # do object detection
        rectangles = vision.find(processed_image)

        if rectangles.size != 0:
            targets = vision.get_click_points(rectangles)

        # for control gui
        cv.waitKey(1)


def test_bot(benchmark):
    window_title = None
    cropped_rectangle = None

    wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
    # initialize the bot
    bot = TOMBot(wincap, "left", 0)

    @benchmark
    def f():
        targets = [(1000, 350)]
        bot.update_targets(targets)
        bot.click_targets()


# ------------------------------------------------------------------------------------------------- benchmark: 4 tests ------------------------------------------------------------------------------------------------
# Name (time in us)              Min                     Max                    Mean                 StdDev                  Median                   IQR            Outliers         OPS            Rounds  Iterations
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# test_bot                   52.8932 (1.0)       21,501.8663 (1.0)          339.2342 (1.0)       1,496.3673 (1.22)          54.0774 (1.0)         60.5903 (1.0)        45;140   2,947.8160 (1.0)        1567          1
# test_screenshot        24,791.1114 (468.70)    30,316.4749 (1.41)      26,004.6012 (76.66)     1,228.6220 (1.0)       25,838.1200 (477.80)   1,525.6129 (25.18)         4;2     38.4547 (0.01)          34          1
# test_vision_scale      51,883.8655 (980.92)    65,986.6078 (3.07)      55,472.5098 (163.52)    3,934.9696 (3.20)      54,851.0149 (>1000.0)  2,460.7169 (40.61)         2;2     18.0269 (0.01)          16          1
# test_vision           145,093.8814 (>1000.0)  185,160.4637 (8.61)     153,879.7879 (453.61)   13,982.7188 (11.38)    149,915.4499 (>1000.0)  4,399.2124 (72.61)         1;1      6.4986 (0.00)           7          1
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
