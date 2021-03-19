import os
import process
import multiprocessing as mp
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# WindowCapture.list_window_names()
# exit()


# 因 window spawn 的緣故
# 必須在 __name__ == '__main__' 之內執行
if __name__ == "__main__":
    p_evil = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (100, 200, 800, 800),
            "match_path": "evil.png",
            "threshold": 0.6,
            "hsv_filter": None,
            "scale_down": 2,
            "click_type": "right",
            "ignore_radius": 50,
        },
    )
    p_evil.start()

    p_get = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (100, 200, 800, 800),
            "match_path": "get.png",
            "threshold": 0.5,
            "hsv_filter": HsvFilter(52, 0, 100, 112, 255, 255, 36, 0, 0, 0),
            "scale_down": 2,
            "click_type": "left",
            "ignore_radius": 50,
        },
    )
    p_get.start()

    p_evil.join()
    p_get.join()
