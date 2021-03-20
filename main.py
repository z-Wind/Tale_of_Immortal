import os
import process
import multiprocessing as mp
import vision
import cv2 as cv
import numpy as np
from windowcapture import WindowCapture
from hsvfilter import HsvFilter

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# WindowCapture.list_window_names()
# exit()


def show_area(window_title, rectangles):
    wincap = WindowCapture(window_name=window_title)
    # these colors are actually BGR
    line_color = (0, 255, 0)
    line_type = cv.LINE_4
    name = "Area, press 'q' or 'esc' to quit, 'r' to run autoclick, 'c' to clear, 'p' to print"
    scale_down = 2

    font = cv.FONT_ITALIC
    font_scale = 1.3
    font_thickness = 2

    btn_down = False
    click_down_points = []
    click_up_points = []
    dragRectangle = [None, None]

    def draw_circle(event, x, y, flags, param):
        nonlocal btn_down, dragRectangle, click_down_points, click_up_points
        if event == cv.EVENT_LBUTTONDOWN:
            click_down_points.append((x * scale_down, y * scale_down))
            dragRectangle[0] = (x * scale_down, y * scale_down)
            btn_down = True
        elif event == cv.EVENT_LBUTTONUP:
            click_up_points.append((x * scale_down, y * scale_down))
            dragRectangle = [None, None]
            btn_down = False
        elif event == cv.EVENT_MOUSEMOVE and btn_down:
            dragRectangle[1] = (x * scale_down, y * scale_down)

    cv.namedWindow(name)
    cv.setMouseCallback(name, draw_circle)

    while True:
        screenshot = wincap.get_screenshot()
        h_screen, w_screen = screenshot.shape[:2]

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(
                screenshot, top_left, bottom_right, line_color, lineType=line_type, thickness=4
            )
            # draw transparent box
            sub_img = screenshot[y : y + h, x : x + w]
            rect = np.zeros(sub_img.shape, dtype=np.uint8) * 255
            res = cv.addWeighted(sub_img, 0.5, rect, 0.5, 0.0)
            screenshot[y : y + h, x : x + w] = res

        for down_p, up_p in zip(click_down_points, click_up_points):
            x1, y1 = down_p
            x2, y2 = up_p
            cv.circle(screenshot, (x1, y1), 8, (0, 0, 255), thickness=-1)
            cv.rectangle(
                screenshot, (x1, y1), (x2, y2), (0, 0, 255), lineType=line_type, thickness=2
            )
            cv.putText(
                screenshot,
                f"({x1},{y1},{x2-x1},{y2-y1})",
                (x1, y1 - 20),
                font,
                font_scale,
                (0, 0, 255),
                thickness=font_thickness,
                lineType=cv.LINE_AA,
            )

        if dragRectangle[0] and dragRectangle[1]:
            x1, y1 = dragRectangle[0]
            x2, y2 = dragRectangle[1]
            cv.rectangle(
                screenshot, (x1, y1), (x2, y2), (255, 0, 255), lineType=line_type, thickness=2
            )
            cv.putText(
                screenshot,
                f"({x1},{y1},{x2-x1},{y2-y1})",
                (x1, y1 - 20),
                font,
                font_scale,
                (255, 0, 255),
                thickness=font_thickness,
                lineType=cv.LINE_AA,
            )

        img = cv.resize(screenshot, (w_screen // 2, h_screen // 2), interpolation=cv.INTER_AREA)
        cv.imshow(name, img)
        # waits 1 ms every loop to process
        # imshow() only works with waitKey()
        key = cv.waitKey(1)
        if key == ord("q") or key == 27:  # Esc key to stop:
            cv.destroyAllWindows()
            exit()
        elif key == ord("r"):
            cv.destroyAllWindows()
            break
        elif key == ord("c"):
            click_down_points = []
            click_up_points = []
            dragRectangle = [None, None]
        elif key == ord("p"):
            print("\nrectangles:")
            for down_p, up_p in zip(click_down_points, click_up_points):
                x1, y1 = down_p
                x2, y2 = up_p
                print(f"({x1},{y1},{x2-x1},{y2-y1})")


# 因 window spawn 的緣故
# 必須在 __name__ == '__main__' 之內執行
if __name__ == "__main__":
    cropped_rectangles = vision.Vision.hollow_rectangle((20, 166, 1024, 768), (484, 536, 80, 120))
    window_title = None
    show_area(window_title, cropped_rectangles)

    p_evils = []
    for cropped_rectangle in cropped_rectangles:
        p_evil = mp.Process(
            target=process.main,
            kwargs={
                "window_title": window_title,
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
                "window_title": window_title,
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
