from typing import Tuple
import cv2 as cv
import os
from time import time, sleep
from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
from bot import TOMBot
from pynput import keyboard
import numpy as np
import multiprocessing as mp
from enum import Enum


class State(Enum):
    INITIALIZING = 0
    SEARCHING = 1
    CLICKING = 2


DEBUG = True
wincap = None


def init(window_title, cropped_rectangle, match_path, click_type, threshold, hsv_filter=None):
    # initialize the WindowCapture class
    global wincap
    wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)

    # initialize the Vision class
    vision = Vision(match_path, threshold, hsv_filter=hsv_filter)
    # initialize the trackbar window
    vision.init_control_gui()

    # initialize the bot
    bot = TOMBot(window_title, wincap, click_type)

    return wincap, vision, bot


def on_release(key):
    print("{0} released".format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        main.run = False
        print("Exit")
        return False
    elif key == keyboard.Key.f1:
        main.state = State.INITIALIZING
        main.pause = False
        print("Start")
    elif key == keyboard.Key.f2:
        main.pause = True
        print("Stop")
    elif key == keyboard.Key.f3:
        cv.imwrite("screenshot/{}.jpg".format(time()), wincap.get_screenshot())
        print("save screenshot")


def main(wincap, vision, bot):
    wincap.active_window(wincap.hwnd)
    # reload hsv_filter for multiprocessing
    vision.set_hsv_filter_from_controls()

    main.state = State.INITIALIZING
    # control program
    main.run = True
    main.pause = False

    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    loop_time = time()
    screenshot = None
    rectangles = np.array([], dtype=np.int32).reshape(0, 4)
    processed_image = None

    ch_recv, ch_send = mp.Pipe(False)
    p = mp.Process(target=click_targets, args=(bot, ch_recv))
    p.start()

    while main.run:
        if main.pause:
            pass
        # update the bot with the data it needs right now
        elif main.state == State.INITIALIZING:
            main.state = State.SEARCHING
        elif main.state == State.SEARCHING:
            # get an updated image of the game
            screenshot = wincap.get_screenshot()

            # pre-process the image
            processed_image = vision.apply_hsv_filter(screenshot, DEBUG)

            # do object detection
            rectangles = vision.find(processed_image)

            if rectangles.size != 0:
                targets = vision.get_click_points(rectangles)
                ch_send.send(targets)
                main.state = State.CLICKING

        elif main.state == State.CLICKING:
            main.state = State.SEARCHING

        if DEBUG and screenshot is not None and rectangles is not None:
            # draw the detection results onto the original image
            output_image = vision.draw_rectangles(screenshot, rectangles)
            output_image = vision.draw_crosshairs(output_image, [bot.center])
            output_image = vision.draw_circles(output_image, [bot.center], bot.IGNORE_RADIUS)

            # display the processed image
            cv.imshow("Processed", processed_image)
            cv.imshow("Matches", output_image)
            # waits 1 ms every loop to process key presses
            # imshow() only works with waitKey()
            key = cv.waitKey(1)

            # debug the loop rate
            print("{:15s}: FPS {}".format(main.state.name, 1 / (time() - loop_time)))
            loop_time = time()

    p.terminate()
    cv.destroyAllWindows()
    listener.stop()
    print("Done.")


# 需在另一個 module 中，multiprocess 才會正常工作
def f(window_title, cropped_rectangle, match_path, click_type, threshold, hsv_filter=None):
    wincap, vision, bot = init(
        window_title,
        cropped_rectangle,
        match_path,
        click_type,
        threshold=threshold,
        hsv_filter=hsv_filter,
    )
    main(wincap, vision, bot)


def click_targets(bot, ch_recv):
    while True:
        targets = ch_recv.recv()
        bot.update_targets(targets)
        bot.click_targets()
