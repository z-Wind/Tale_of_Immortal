import cv2 as cv
import numpy as np
from hsvfilter import HsvFilter


class Vision:
    # constants
    TRACKBAR_WINDOW = "Trackbars"

    # properties
    needle_img = None
    needle_img_scale_down = None
    method = None
    hsv_filter = None
    threshold = 0.9

    # constructor
    def __init__(
        self, needle_img_path, threshold, hsv_filter, method=cv.TM_CCOEFF_NORMED, scale_down=None
    ):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.scale_down = scale_down
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        # remove alpha channel
        self.needle_img = self.needle_img[:, :, :3]
        self.needle_img_scale_down = self.resize(
            self.needle_img, self.scale_down, interpolation=cv.INTER_AREA
        )

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

        # property
        if hsv_filter:
            self.hsv_filter = hsv_filter
        else:
            self.hsv_filter = HsvFilter(0, 0, 0, 179, 255, 255, 0, 0, 0, 0)
        self.threshold = threshold

    def resize(self, img, scale_down, interpolation=cv.INTER_NEAREST):
        if scale_down:
            h, w = img.shape[:2]
            w = int(w // scale_down)
            h = int(h // scale_down)

            return cv.resize(img, (w, h), interpolation=interpolation)

        return img

    def find(self, haystack_img, max_results=10):
        needle_img = self.needle_img_scale_down
        if self.scale_down:
            haystack_img = self.resize(haystack_img, self.scale_down)

        needle_w, needle_h = needle_img.shape[:2]
        # run the OpenCV algorithm
        result = cv.matchTemplate(haystack_img, needle_img, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= self.threshold)
        locations = list(zip(*locations[::-1]))
        # print(locations)

        # if we found no results, return now. this reshape of the empty array allows us to
        # concatenate together results without causing an error
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
        # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # in the result. I've set eps to 0.5, which is:
        # "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        # print(rectangles)

        # for performance reasons, return a limited number of results.
        # these aren't necessarily the best results.
        if len(rectangles) > max_results:
            print("Warning: too many results, raise the threshold.")
            rectangles = rectangles[:max_results]

        if self.scale_down:
            rectangles = rectangles * self.scale_down
        return rectangles

    # given a list of [x, y, w, h] rectangles returned by find(), convert those into a list of
    # [x, y] positions in the center of those rectangles where we can click on those found items
    def get_click_points(self, rectangles):
        points = []

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w / 2)
            center_y = y + int(h / 2)
            # Save the points
            points.append((center_x, center_y))

        return points

    # given a list of [x, y, w, h] rectangles and a canvas image to draw on, return an image with
    # all of those rectangles drawn
    def draw_rectangles(self, haystack_img, rectangles):
        # these colors are actually BGR
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(haystack_img, top_left, bottom_right, line_color, lineType=line_type)

        return haystack_img

    # given a list of [x, y] positions and a canvas image to draw on, return an image with all
    # of those click points drawn on as crosshairs
    def draw_crosshairs(self, haystack_img, points):
        # these colors are actually BGR
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(haystack_img, (center_x, center_y), marker_color, marker_type)

        return haystack_img

    # given a list of [x, y] positions, radius, and a canvas image to draw on, return an image with all
    # of those click points drawn on as crosshairs
    def draw_circles(self, haystack_img, points, radius):
        # these colors are actually BGR
        circle_color = (255, 0, 0)
        circle_width = 5

        for (center_x, center_y) in points:
            # draw the center point
            cv.circle(haystack_img, (center_x, center_y), radius, circle_color, circle_width)

        return haystack_img

    # create gui window with controls for adjusting arguments in real-time
    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv.createTrackbar("HMin", self.TRACKBAR_WINDOW, self.hsv_filter.hMin, 179, nothing)
        cv.createTrackbar("SMin", self.TRACKBAR_WINDOW, self.hsv_filter.sMin, 255, nothing)
        cv.createTrackbar("VMin", self.TRACKBAR_WINDOW, self.hsv_filter.vMin, 255, nothing)
        cv.createTrackbar("HMax", self.TRACKBAR_WINDOW, self.hsv_filter.hMax, 179, nothing)
        cv.createTrackbar("SMax", self.TRACKBAR_WINDOW, self.hsv_filter.sMax, 255, nothing)
        cv.createTrackbar("VMax", self.TRACKBAR_WINDOW, self.hsv_filter.vMax, 255, nothing)
        # # Set default value for Max HSV trackbars
        # cv.setTrackbarPos("HMax", self.TRACKBAR_WINDOW, 179)
        # cv.setTrackbarPos("SMax", self.TRACKBAR_WINDOW, 255)
        # cv.setTrackbarPos("VMax", self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv.createTrackbar("SAdd", self.TRACKBAR_WINDOW, self.hsv_filter.sAdd, 255, nothing)
        cv.createTrackbar("SSub", self.TRACKBAR_WINDOW, self.hsv_filter.sSub, 255, nothing)
        cv.createTrackbar("VAdd", self.TRACKBAR_WINDOW, self.hsv_filter.vAdd, 255, nothing)
        cv.createTrackbar("VSub", self.TRACKBAR_WINDOW, self.hsv_filter.vSub, 255, nothing)

    # returns an HSV filter object based on the control GUI values
    def get_hsv_filter_from_controls(self):
        # Get current positions of all trackbars
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv.getTrackbarPos("HMin", self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv.getTrackbarPos("SMin", self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv.getTrackbarPos("VMin", self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv.getTrackbarPos("HMax", self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv.getTrackbarPos("SMax", self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv.getTrackbarPos("VMax", self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv.getTrackbarPos("SAdd", self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv.getTrackbarPos("SSub", self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv.getTrackbarPos("VAdd", self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv.getTrackbarPos("VSub", self.TRACKBAR_WINDOW)
        return hsv_filter

    # returns an HSV filter object based on the control GUI values
    def set_hsv_filter_from_controls(self):
        # set current positions of all trackbars
        if self.hsv_filter:
            cv.setTrackbarPos("SMin", self.TRACKBAR_WINDOW, self.hsv_filter.sMin)
            cv.setTrackbarPos("HMin", self.TRACKBAR_WINDOW, self.hsv_filter.hMin)
            cv.setTrackbarPos("VMin", self.TRACKBAR_WINDOW, self.hsv_filter.vMin)
            cv.setTrackbarPos("HMax", self.TRACKBAR_WINDOW, self.hsv_filter.hMax)
            cv.setTrackbarPos("SMax", self.TRACKBAR_WINDOW, self.hsv_filter.sMax)
            cv.setTrackbarPos("VMax", self.TRACKBAR_WINDOW, self.hsv_filter.vMax)
            cv.setTrackbarPos("SAdd", self.TRACKBAR_WINDOW, self.hsv_filter.sAdd)
            cv.setTrackbarPos("SSub", self.TRACKBAR_WINDOW, self.hsv_filter.sSub)
            cv.setTrackbarPos("VAdd", self.TRACKBAR_WINDOW, self.hsv_filter.vAdd)
            cv.setTrackbarPos("VSub", self.TRACKBAR_WINDOW, self.hsv_filter.vSub)

    # given an image and an HSV filter, apply the filter and return the resulting image.
    # if a filter is not supplied, the control GUI trackbars will be used
    def apply_hsv_filter(self, original_image, finetune=False):
        # convert image to HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        # if we haven't been given a defined filter, use the filter values from the GUI
        if finetune:
            self.hsv_filter = self.get_hsv_filter_from_controls()

        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, self.hsv_filter.sAdd)
        s = self.shift_channel(s, -self.hsv_filter.sSub)
        v = self.shift_channel(v, self.hsv_filter.vAdd)
        v = self.shift_channel(v, -self.hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([self.hsv_filter.hMin, self.hsv_filter.sMin, self.hsv_filter.vMin])
        upper = np.array([self.hsv_filter.hMax, self.hsv_filter.sMax, self.hsv_filter.vMax])
        # Apply the thresholds
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR for imshow() to display it properly
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img

    # apply adjustments to an HSV channel
    # https://stackoverflow.com/questions/49697363/shifting-hsv-pixel-values-in-python-using-numpy
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c

    # create hollow rectangle with 4 (x,y,w,h) by outer rectangle and inner rectangle
    @staticmethod
    def hollow_rectangle(outer, inner):
        outer_x, outer_y, outer_w, outer_h = outer
        inner_x, inner_y, inner_w, inner_h = inner

        top_h = inner_y - outer_y
        left_w = inner_x - outer_x
        right_w = (outer_x + outer_w) - (inner_x + inner_w)
        bottom_h = (outer_y + outer_h) - (inner_y + inner_h)

        topper = (outer_x, outer_y, outer_w, top_h)
        lefter = (outer_x, outer_y + top_h, left_w, inner_h)
        righter = (
            outer_x + outer_w - right_w,
            outer_y + top_h,
            right_w,
            inner_h,
        )
        bottomer = (outer_x, outer_y + outer_h - bottom_h, outer_w, bottom_h)

        return (topper, lefter, righter, bottomer)
