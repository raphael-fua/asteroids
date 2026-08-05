import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(
        self,
        x: float,
        y: float,
        radius: float,
        color: str | tuple[int, int, int] = "white",
    ) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.color = color

    def draw(self, screen: pygame.Surface) -> None:
        # must override
        pass

    def update(self, dt: float) -> None:
        # must override
        pass

    def collides_with(self, other) -> bool:
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def is_off_screen(self, margin: float | None = None) -> bool:
        m = self.radius if margin is None else margin
        return (
            self.position.x + m < 0
            or self.position.x - m > SCREEN_WIDTH
            or self.position.y + m < 0
            or self.position.y - m > SCREEN_HEIGHT
        )







