import random

# Sourced from the xcolor dvipsnames RGB conversions (en.wikibooks.org/wiki/LaTeX/Colors)
_APRICOT = (251, 187, 130)
_BURNT_ORANGE = (247, 146, 29)
_BITTERSWEET = (192, 79, 23)
_BRICK_RED = (182, 50, 28)


def _blend(color: tuple[int, int, int], target: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    r, g, b = (round(color[i] + (target[i] - color[i]) * factor) for i in range(3))
    return (r, g, b)


_COLOR_STOPS = [
    _blend(_APRICOT, (255, 255, 255), 0.5),  # 1: pale apricot
    _BURNT_ORANGE,
    _BITTERSWEET,
    _blend(_BRICK_RED, (0, 0, 0), 0.35),  # 100: deep brick red
]


def random_asteroid_color() -> tuple[int, int, int]:
    t = (random.randint(1, 100) - 1) / 99  # 1 -> pale apricot, 100 -> deep brick red
    num_segments = len(_COLOR_STOPS) - 1
    segment_length = 1 / num_segments
    segment = min(int(t // segment_length), num_segments - 1)
    local_t = (t - segment * segment_length) / segment_length
    start, end = _COLOR_STOPS[segment], _COLOR_STOPS[segment + 1]
    r, g, b = (round(start[i] + (end[i] - start[i]) * local_t) for i in range(3))
    return (r, g, b)
