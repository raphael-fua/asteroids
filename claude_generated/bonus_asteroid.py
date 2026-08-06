import pygame

from asteroid import Asteroid
from constants import BONUS_RADIUS, LINE_WIDTH, PLAYER_MAX_HEALTH, PLAYER_MAX_AMMO
from logger import log_event
from player import Player

# Both pickups are non-lethal asteroids: they drift and despawn like any other rock
# (inherited Asteroid.update), but are claimed rather than shot apart. run_game keeps
# them out of the `asteroids` group by giving them their own `containers`, so the rock
# collision logic never sees them.
#
# Asteroids are filled discs on a warm apricot -> brick-red ramp (see asteroid_colors),
# so each pickup overwrites self.color with one well outside that gamut and cannot be
# mistaken for a rock even in peripheral vision. The glyph separates the two kinds.


def _rect(center: pygame.Vector2, width: float, height: float, dy: float) -> pygame.Rect:
    # pygame 2.6.1 has no FRect, and Rect truncates floats: round explicitly, or a
    # 7.5 px bar silently becomes 7 px while its 8.0 px neighbour stays 8.
    rect = pygame.Rect(0, 0, round(width), round(height))
    rect.center = (round(center.x), round(center.y + dy))
    return rect


class HealthAsteroid(Asteroid):
    """Red cross on white. Grants health to whoever claims it."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, BONUS_RADIUS)
        self.color = (240, 240, 240)  # replaces the random rock colour
        self.glyph_color = (200, 30, 40)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, self.radius, 0)
        pygame.draw.circle(screen, self.glyph_color, self.position, self.radius, LINE_WIDTH)
        # Greek cross: two equal bars crossing at the centre, arm tips at 0.70 * radius.
        for rect in (
            _rect(self.position, 1.40 * self.radius, 0.44 * self.radius, 0.0),
            _rect(self.position, 0.44 * self.radius, 1.40 * self.radius, 0.0),
        ):
            pygame.draw.rect(screen, self.glyph_color, rect)

    def claim(self, player: Player) -> None:
        """Heals the player and disappears. Consumed even at full health -- claiming a
        cross you cannot use still denies it to the other player.
        """
        wasted = player.health >= PLAYER_MAX_HEALTH
        player.add_health()
        log_event(
            "bonus_claimed", kind="health", player=player.name,
            wasted=wasted, health=player.health,
        )
        self.kill()


class AmmoAsteroid(Asteroid):
    """Gold croix de Lorraine on navy. Grants ammo to whoever claims it."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, BONUS_RADIUS)
        self.color = (20, 30, 70)  # replaces the random rock colour
        self.glyph_color = (245, 200, 80)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, self.radius, 0)
        pygame.draw.circle(screen, self.glyph_color, self.position, self.radius, LINE_WIDTH)
        # One staff and two bars, the upper one shorter.
        for rect in (
            _rect(self.position, 0.30 * self.radius, 1.60 * self.radius, 0.0),
            _rect(self.position, 0.80 * self.radius, 0.30 * self.radius, -0.52 * self.radius),
            _rect(self.position, 1.30 * self.radius, 0.30 * self.radius, 0.04 * self.radius),
        ):
            pygame.draw.rect(screen, self.glyph_color, rect)

    def claim(self, player: Player) -> None:
        """Reloads the player and disappears."""
        wasted = player.ammo >= PLAYER_MAX_AMMO
        player.add_ammo()
        log_event(
            "bonus_claimed", kind="ammo", player=player.name,
            wasted=wasted, ammo=player.ammo,
        )
        self.kill()
