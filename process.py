import cv2 as cv
from time import perf_counter, sleep
from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
from bot import TOMBot
from pynput import keyboard
import numpy as np
import multiprocessing as mp
from enum import Enum

DEBUG_CLICK_MODE = False


class State(Enum):
    INITIALIZING = 0
    WORK = 1
    TERMINATE = 2
    PAUSE = 2
    DEBUG_INIT = 3
    DEBUG = 4
    WAIT = 5


def on_release(key):
    print("{0} released".format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        main.run = False
        print("Exit")
        return False
    elif key == keyboard.Key.f1:
        main.prev_state = main.state
        main.state = State.INITIALIZING
        print("Start")
    elif key == keyboard.Key.f2:
        main.prev_state = main.state
        main.state = State.PAUSE
        print("Pause")
    elif key == keyboard.Key.f3:
        main.prev_state = main.state
        main.state = State.DEBUG_INIT
        print("Debug")
    elif key == keyboard.Key.f4:
        global DEBUG_CLICK_MODE
        DEBUG_CLICK_MODE = not DEBUG_CLICK_MODE
        print("Debug Switch Click Mode", DEBUG_CLICK_MODE)


# 需在另一個 module 中，multiprocess 才會正常工作
def main(
    window_title,
    cropped_rectangle,
    match_path,
    threshold,
    hsv_filter,
    scale_down,
    click_type,
    ignore_radius,
):
    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    # multiprocessing
    ch_recv_screenshot, ch_send_screenshot = mp.Pipe(False)
    ch_recv_wincap, ch_send_wincap = mp.Pipe(False)
    ch_recv_targets, ch_send_targets = mp.Pipe(False)

    main.state = State.INITIALIZING
    main.prev_state = None
    # control program
    main.run = True
    while main.run:
        # print(main.prev_state, "->", main.state)
        if main.state == State.INITIALIZING:
            if main.prev_state == State.WORK:
                main.prev_state = main.state
                main.state = State.WORK
                continue

            cv.destroyAllWindows()

            p_get_screenshot = mp.Process(
                target=get_screenshot,
                args=(window_title, cropped_rectangle, ch_send_wincap, ch_send_screenshot),
            )
            p_get_screenshot.start()

            p_img_process = mp.Process(
                target=img_process,
                args=(
                    match_path,
                    threshold,
                    hsv_filter,
                    scale_down,
                    ch_recv_screenshot,
                    ch_send_targets,
                ),
            )
            p_img_process.start()
            p_click_targets = mp.Process(
                target=click_targets,
                args=(ch_recv_wincap, click_type, ignore_radius, ch_recv_targets),
            )
            p_click_targets.start()

            main.prev_state = main.state
            main.state = State.WORK
        elif main.state == State.WORK:
            pass
        elif main.state == State.TERMINATE:
            p_click_targets.terminate()
            p_img_process.terminate()
            p_get_screenshot.terminate()

            if main.prev_state == State.DEBUG_INIT:
                main.prev_state = main.state
                main.state = State.DEBUG
            else:
                cv.destroyAllWindows()
                main.prev_state = main.state
                main.state = State.WAIT
        elif main.state == State.PAUSE:
            main.prev_state = main.state
            main.state = State.TERMINATE
        elif main.state == State.DEBUG_INIT:
            wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
            vision = Vision(match_path, threshold, hsv_filter, scale_down=scale_down)
            vision.init_control_gui()
            bot = TOMBot(wincap, click_type, ignore_radius)

            main.prev_state = main.state
            main.state = State.TERMINATE
        elif main.state == State.DEBUG:
            screenshot = wincap.get_screenshot()
            processed_image = vision.apply_hsv_filter(screenshot, finetune=True)
            scaled_image = vision.resize(processed_image, scale_down)
            rectangles = vision.find(processed_image)
            targets = vision.get_click_points(rectangles)
            if DEBUG_CLICK_MODE:
                bot.update_targets(targets)
                bot.click_targets()

            # draw the detection results onto the original image
            output_image = vision.draw_rectangles(screenshot, rectangles)
            output_image = vision.draw_crosshairs(output_image, targets + [bot.center])
            output_image = vision.draw_circles(output_image, [bot.center], bot.IGNORE_RADIUS)

            # display the processed image
            cv.imshow("Processed", processed_image)
            cv.imshow("ScaleDown Needle", vision.needle_img_scale_down)
            cv.imshow("ScaleDown Processed", scaled_image)
            cv.imshow("Matches", output_image)

        elif main.state == State.WAIT:
            pass

        # waits 1 ms every loop to process
        # imshow() only works with waitKey()
        cv.waitKey(1)

    p_click_targets.terminate()
    p_img_process.terminate()
    p_get_screenshot.terminate()
    cv.destroyAllWindows()
    listener.stop()
    print("Done.")


def get_screenshot(window_title, cropped_rectangle, ch_send_wincap, ch_send_screenshot):
    print("Get Screenshot Start...")
    # initialize the WindowCapture class
    wincap = WindowCapture(window_name=window_title, cropped_rectangle=cropped_rectangle)
    try:
        wincap.active_window()
    except:
        pass
    ch_send_wincap.send(wincap)
    pre_screenshot = None
    while True:
        screenshot = wincap.get_screenshot()
        if np.array_equal(screenshot, pre_screenshot):
            continue
        ch_send_screenshot.send(screenshot)
        pre_screenshot = screenshot


def img_process(match_path, threshold, hsv_filter, scale_down, ch_recv_screenshot, ch_send_targets):
    print("Image Process Start...")
    # initialize the Vision class
    vision = Vision(match_path, threshold, hsv_filter, scale_down=scale_down)
    # 不同的 process 皆需重建 control gui
    # vision.init_control_gui()

    while True:
        screenshot = ch_recv_screenshot.recv()

        # pre-process the image
        processed_image = vision.apply_hsv_filter(screenshot)

        # do object detection
        rectangles = vision.find(processed_image)

        if rectangles.size != 0:
            targets = vision.get_click_points(rectangles)
            ch_send_targets.send(targets)

        # # for control gui
        # cv.waitKey(1)


def click_targets(ch_recv_wincap, click_type, ignore_radius, ch_recv):
    print("Click Targets Start...")
    wincap = ch_recv_wincap.recv()
    # initialize the bot
    bot = TOMBot(wincap, click_type, ignore_radius)
    while True:
        targets = ch_recv.recv()
        bot.update_targets(targets)
        bot.click_targets()
