import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS
from logger import log_event
import random



class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        if self.is_off_screen(ASTEROID_MAX_RADIUS):
            log_event("asteroid_despawned")
            self.kill()

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        alpha = random.uniform(20, 50)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        v1 = self.velocity.rotate(alpha)
        v2 = self.velocity.rotate(-alpha)
        a1 = Asteroid(self.position[0], self.position[1], new_radius)
        a2 = Asteroid(self.position[0], self.position[1], new_radius)
        a1.velocity = v1 * 1.2
        a2.velocity = v2 * 1.2


        




