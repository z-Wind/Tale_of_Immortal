import multiprocessing as mp
from time import sleep, time
import win32gui, win32api, win32con


class TOMBot:

    # constants
    IGNORE_RADIUS = 50

    # properties
    targets = []
    window_title = None
    wincap = None
    center = None
    click_type = None

    def __init__(self, window_title, wincap, click_type):
        # window infomation
        self.window_title = window_title
        self.wincap = wincap
        if self.wincap.cropped_w:
            self.center = (self.wincap.cropped_w // 2, self.wincap.cropped_h // 2)
        else:
            self.center = (self.wincap.w // 2, self.wincap.h // 2)
        self.click_type = click_type

    def click(self, x, y, click_type="left"):
        if click_type == "left":
            down = win32con.MOUSEEVENTF_LEFTDOWN
            up = win32con.MOUSEEVENTF_LEFTUP
        elif click_type == "right":
            down = win32con.MOUSEEVENTF_RIGHTDOWN
            up = win32con.MOUSEEVENTF_RIGHTUP
        else:
            raise f"click_type not define {click_type}"

        win32api.SetCursorPos((x, y))
        win32api.mouse_event(down, 0, 0)
        sleep(0.02)
        win32api.mouse_event(up, 0, 0)

    def click_targets(self):
        # 1. order targets by distance from center
        # loop:
        #   2. click the farest target
        # endloop
        # 3. if no target was found return false
        # 4. click on the found target and return true
        targets = self._targets_ordered_by_distance(self.targets[0])
        for target in targets:
            # load up the next target in the list and convert those coordinates
            # that are relative to the game screenshot to a position on our
            # screen
            screen_x, screen_y = self.wincap.get_screen_position(target)
            print("click to x:{} y:{}".format(screen_x, screen_y))

            self.click(screen_x, screen_y, self.targets[1])

        self.targets = []

    def _targets_ordered_by_distance(self, targets):
        # our character is always in the center of the screen
        my_pos = self.center
        # searched "python order points by distance from point"
        # simply uses the pythagorean theorem
        # https://stackoverflow.com/a/30636138/4655368
        def pythagorean_distance(pos):
            return (pos[0] - my_pos[0]) * (pos[0] - my_pos[0]) + (pos[1] - my_pos[1]) * (
                pos[1] - my_pos[1]
            )

        targets.sort(key=pythagorean_distance, reverse=True)

        # print(my_pos)
        # print(targets)
        # for t in targets:
        #    print(pythagorean_distance(t))

        # ignore targets at are too close to our character (within IGNORE_RADIUS) to avoid
        # wrong clicking
        threhold = self.IGNORE_RADIUS * self.IGNORE_RADIUS
        targets = [t for t in targets if pythagorean_distance(t) > threhold]

        return targets

    # threading methods

    def update_targets(self, targets):
        self.targets = [targets, self.click_type]
