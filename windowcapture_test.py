from windowcapture import WindowCapture


def test_get_screen_position():
    wincap = WindowCapture(None, None)
    assert (0, 0) == wincap.get_screen_position((0, 0))
    assert (1000, 2000) == wincap.get_screen_position((1000, 2000))

    wincap = WindowCapture(None, (10, 10, 100, 100))
    assert (10, 10) == wincap.get_screen_position((0, 0))
    assert (1010, 2010) == wincap.get_screen_position((1000, 2000))
