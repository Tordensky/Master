

def calc_fps(t0, t1):
    """
    Calculates the current update rate from the two given time samples
    @param t0:
    @param t1:
    @return: current fps
    """
    try:
        return 1.0 / (t1 - t0)
    except ZeroDivisionError:
        return -1.