from circleshape import CircleShape
from shot import Shot
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS
)
import pygame

class Player(CircleShape):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS) 
        self.rotation = 0
        self.time_till_can_shoot = 0

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(
            surface=screen,
            color="white",
            points=self.triangle(),
            width=LINE_WIDTH
        )

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(dt)
        if keys[pygame.K_d]:
            self.rotate(-dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.time_till_can_shoot -= dt

    def move(self, dt: float):
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= dt * PLAYER_SPEED
        self.position += v


    def shoot(self):
        if self.time_till_can_shoot > 0:
            return 
        self.time_till_can_shoot = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position[0], self.position[1])
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= PLAYER_SHOOT_SPEED
        shot.velocity = v








