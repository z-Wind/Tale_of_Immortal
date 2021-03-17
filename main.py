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
    # p_evil = mp.Process(
    #     target=process.f, args=(None, (100, 200, 800, 800), "evil.png", "right", 0.6, None)
    # )
    # p_evil.start()

    # p_get = mp.Process(
    #     target=process.f,
    #     args=(
    #         None,
    #         (100, 200, 800, 800),
    #         "get.png",
    #         "left",
    #         0.5,
    #         HsvFilter(52, 0, 100, 112, 255, 255, 36, 0, 0, 0),
    #     ),
    # )
    # p_get.start()

    # p_evil.join()
    # p_get.join()
    # p = mp.Process(target=process.f, args=(None, (100, 200, 800, 800), "tt.png", "left", 0.6, None))
    # p.start()
    # p.join()
    p = mp.Process(
        target=process.main,
        kwargs={
            "window_title": None,
            "cropped_rectangle": (18, 355, 360, 360),
            "match_path": "frog.png",
            "threshold": 0.4,
            "hsv_filter": None,
            "scale_down": 2,
            "click_type": "left",
            "ignore_radius": 0,
        },
    )
    p.start()
    p.join()
