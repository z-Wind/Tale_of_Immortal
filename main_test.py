import os
import process
import pytest
import multiprocessing as mp
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skip(reason="skip this")
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


@pytest.mark.skip(reason="skip this")
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


@pytest.mark.skip(reason="skip this")
def test_main_ballon():
    print("open", "https://skeletonware.itch.io/balloon-pop")
    p = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (35, 200, 607, 350),
            "match_path": "tests/ballon.png",
            "threshold": 0.7,
            "hsv_filter": None,
            "scale_down": 2,
            "click_type": "left",
            "ignore_radius": 0,
        },
    )
    p.start()
    p.join()