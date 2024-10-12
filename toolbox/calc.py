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
    if len(options) == 1:
        return options[0]
    if target in options:
        nearest = target
    else:
        idx = bisect.bisect_left(options, target)
        nearest = options[min(idx, len(options) - 1)]
    debug(nearest, lvl=2)
    options.remove(nearest)
    return nearest
