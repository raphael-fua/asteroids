import random

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Stylized asterism shapes (not precise astronomical coordinates): each is a set
# of points in a local unit square, with edges connecting them into the familiar
# shape. Positioned and scaled onto the screen in Starfield._place_constellations.
_CONSTELLATIONS = {
    "La Grande Ourse": {
        # Handle (0-3) bending down into the bowl (3-4-5-6 loop), matching the
        # familiar Big Dipper silhouette.
        "points": [
            (0.02, 0.00), (0.13, 0.20), (0.11, 0.37), (0.13, 0.58),
            (0.00, 0.68), (0.13, 0.99), (0.35, 0.89),
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)],
    },
    "La Petite Ourse": {
        "points": [
            (0.00, 0.00), (0.14, 0.08), (0.24, 0.20), (0.34, 0.34),
            (0.48, 0.30), (0.54, 0.14), (0.40, 0.08),
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)],
    },
    "Le Dragon": {
        "points": [
            (0.00, 0.00), (0.10, 0.10), (0.16, 0.24), (0.10, 0.38),
            (0.00, 0.46), (0.10, 0.56), (0.26, 0.58), (0.40, 0.50),
            (0.50, 0.36), (0.44, 0.22), (0.30, 0.16), (0.34, 0.02),
            (0.48, -0.02), (0.40, 0.10),
        ],
        "edges": [(i, i + 1) for i in range(10)] + [(10, 11), (11, 12), (12, 13), (13, 10)],
    },
    "Céphée": {
        "points": [
            (0.00, 0.32), (0.00, 0.00), (0.22, -0.12), (0.44, 0.00), (0.44, 0.32),
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
        "rotation": 110,
    },
}


class Starfield:
    def __init__(self, star_count: int = 150) -> None:
        self.background_stars = [
            (
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(0, SCREEN_HEIGHT),
                random.uniform(1, 2),
                random.randint(120, 255),
            )
            for _ in range(star_count)
        ]
        self.constellations = self._place_constellations()
        self.font = pygame.font.Font(None, 24)

        margin = 24
        # One corner per constellation, in the same order as _CONSTELLATIONS/anchors,
        # so labels sit far from the centered game-over text instead of on the shape.
        self.label_corners = [
            ("topleft", (margin, margin)),
            ("topright", (SCREEN_WIDTH - margin, margin)),
            ("bottomleft", (margin, SCREEN_HEIGHT - margin)),
            ("bottomright", (SCREEN_WIDTH - margin, SCREEN_HEIGHT - margin)),
        ]

    def _place_constellations(self) -> list[tuple[str, list[pygame.Vector2], list[tuple[int, int]], tuple[int, int, int]]]:
        anchors = [
            (SCREEN_WIDTH * 0.10, SCREEN_HEIGHT * 0.12),
            (SCREEN_WIDTH * 0.72, SCREEN_HEIGHT * 0.20),
            (SCREEN_WIDTH * 0.16, SCREEN_HEIGHT * 0.68),
            (SCREEN_WIDTH * 0.82, SCREEN_HEIGHT * 0.70),
        ]
        scale = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.22

        placed = []
        for (name, shape), (ax, ay) in zip(_CONSTELLATIONS.items(), anchors):
            rotation = shape.get("rotation", 0)
            points = [
                pygame.Vector2(ax, ay) + pygame.Vector2(px, py).rotate(rotation) * scale
                for px, py in shape["points"]
            ]
            color = shape.get("color", (90, 110, 160))
            placed.append((name, points, shape["edges"], color))
        return placed

    def draw(self, screen: pygame.Surface, show_labels: bool = False) -> None:
        for x, y, radius, brightness in self.background_stars:
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), radius)

        for (name, points, edges, line_color), (corner_attr, corner_pos) in zip(
            self.constellations, self.label_corners
        ):
            for i, j in edges:
                pygame.draw.line(screen, line_color, points[i], points[j], 1)
            for p in points:
                pygame.draw.circle(screen, "white", p, 3)
            if show_labels:
                label = self.font.render(name, True, (150, 170, 210))
                screen.blit(label, label.get_rect(**{corner_attr: corner_pos}))
