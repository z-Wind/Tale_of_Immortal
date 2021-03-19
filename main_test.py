import os
import process
import pytest
import cv2 as cv
import multiprocessing as mp
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

debug_only = pytest.mark.skipif(True, reason="skip this")


@debug_only
def test_main_normal():
    p = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (100, 200, 800, 800),
            "match_path": "tests/tt.png",
            "threshold": 0.6,
            "hsv_filter": None,
            "scale_down": 2,
            "click_type": "left",
            "ignore_radius": 50,
        },
    )
    p.start()
    p.join()


@debug_only
def test_main_frog():
    print("open", "tests/whack-a-mole/index.html")
    p = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (27, 260, 470, 430),
            "match_path": "tests/frog.png",
            "threshold": 0.4,
            "hsv_filter": None,
            "scale_down": 2,
            "click_type": "left",
            "ignore_radius": 0,
        },
    )
    p.start()
    p.join()


@debug_only
def test_main_balloon():
    print("open", "https://future-games.itch.io/balloon-battles")
    ps = []
    for match_path in [
        "tests/balloon/balloon_blue.png",
        # "tests/balloon/balloon_white.png",
        # "tests/balloon/balloon_red.png",
        "tests/balloon/balloon_purple.png",
        "tests/balloon/balloon_green.png",
        "tests/balloon/balloon_coffee.png",
    ]:
        p = mp.Process(
            target=process.main,
            kwargs={
                "window_title": None,
                "cropped_rectangle": (21, 400, 600, 100),
                "match_path": match_path,
                "threshold": 0.98,
                "hsv_filter": None,
                "scale_down": 2,
                "click_type": "left",
                "ignore_radius": 0,
                "matchTemplate_method": cv.TM_CCORR_NORMED,
            },
        )
        p.start()
        ps.append(p)

    for p in ps:
        p.join()


def test_matchTemplate():
    from windowcapture import WindowCapture

    wincap = WindowCapture()
    import cv2 as cv

    screenshot = wincap.get_screenshot()
    needle_img = cv.imread("tests/balloon/balloon_red.png", cv.IMREAD_UNCHANGED)
    needle_img = needle_img[:, :, :3]
    result = cv.matchTemplate(screenshot, needle_img, cv.TM_CCORR_NORMED)
    print(result)