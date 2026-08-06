import pygame

from constants import SCREEN_WIDTH, HUD_FONT_SIZE, HUD_MARGIN
from player import Player


class Hud:
    """Health and ammo for each player, in their own colour, in their own corner."""

    def __init__(self, font_size: int = HUD_FONT_SIZE) -> None:
        self.font = pygame.font.Font(None, font_size)
        # One corner per player, mirroring Starfield.label_corners.
        self.corners: list[tuple[str, tuple[int, int]]] = [
            ("topleft", (HUD_MARGIN, HUD_MARGIN)),
            ("topright", (SCREEN_WIDTH - HUD_MARGIN, HUD_MARGIN)),
        ]

    def draw(self, screen: pygame.Surface, players: list[Player]) -> None:
        for player, (corner_attr, corner_pos) in zip(players, self.corners):
            label = player.name.split()[0]  # "Red Player" -> "Red"
            text = f"{label}   HP {player.health}   AMMO {player.ammo}"
            if player.ammo == 0:
                text += "   EMPTY"
            surface = self.font.render(text, True, player.color)
            screen.blit(surface, surface.get_rect(**{corner_attr: corner_pos}))
