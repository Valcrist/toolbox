import bisect
from typing import Union
from toolbox.utils import debug


def calc_delta(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    if a == b:
        return 0
    else:
        return b - a


def select_nearest(
    target: Union[int, float], options: list[Union[int, float]]
) -> Union[int, float]:
    debug(target, lvl=2)
    debug(options, lvl=2)
    opts = sorted(options)
    if len(opts) == 1:
        return opts[0]
    if target in opts:
        return target
    idx = bisect.bisect_left(opts, target)
    if idx == 0:
        nearest = opts[0]
    elif idx == len(opts):
        nearest = opts[-1]
    else:
        left, right = opts[idx - 1], opts[idx]
        nearest = left if abs(target - left) <= abs(right - target) else right
    debug(nearest, lvl=2)
    return nearest
