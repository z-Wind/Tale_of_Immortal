import os
import process
import multiprocessing as mp
import vision
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# WindowCapture.list_window_names()
# exit()


# 因 window spawn 的緣故
# 必須在 __name__ == '__main__' 之內執行
if __name__ == "__main__":
    cropped_rectangles = vision.Vision.hollow_rectangle((105, 213, 880, 682), (484, 536, 80, 120))

    p_evils = []
    for cropped_rectangle in cropped_rectangles:
        p_evil = mp.Process(
            target=process.main,
            kwargs={
                "window_title": None,
                "cropped_rectangle": cropped_rectangle,
                "match_path": "evil.png",
                "threshold": 0.7,
                "hsv_filter": None,
                "scale_down": 1.5,
                "click_type": "right",
                "ignore_radius": 0,
            },
        )
        p_evil.start()
        p_evils.append(p_evil)

    p_gets = []
    for cropped_rectangle in cropped_rectangles:
        p_get = mp.Process(
            target=process.main,
            kwargs={
                "window_title": None,
                "cropped_rectangle": cropped_rectangle,
                "match_path": "get.png",
                "threshold": 0.5,
                "hsv_filter": HsvFilter(52, 0, 100, 112, 255, 255, 36, 0, 0, 0),
                "scale_down": 1.5,
                "click_type": "left",
                "ignore_radius": 0,
            },
        )
        p_get.start()
        p_gets.append(p_get)

    for p_evil in p_evils:
        p_evil.join()
    for p_get in p_gets:
        p_get.join()
