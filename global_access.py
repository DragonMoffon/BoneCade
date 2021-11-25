# global_access.py has any basic variables with no other valid location to reside. Placed to the side where they can't
# cause circular import errors. Very few imports should be found here, and those that do should be external or utility

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


def clamp(val, min_x, max_x):
    return min(max(val, min_x), max_x)


def floor_by_x(val, x):
    return (val // x) * x
