from circleshape import CircleShape
from shot import Shot
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
import pygame

class Player(CircleShape):

    def __init__(
        self,
        x: float,
        y: float,
        color: str = "white",
        name: str = "Player",
        turn_left_key: int = pygame.K_a,
        turn_right_key: int = pygame.K_d,
        forward_key: int = pygame.K_w,
        backward_key: int = pygame.K_s,
        shoot_keys: tuple[int, ...] = (pygame.K_SPACE,),
    ) -> None:
        super().__init__(x, y, PLAYER_RADIUS, color)
        self.rotation = 0
        self.time_till_can_shoot = 0
        self.name = name
        self.shots_group = pygame.sprite.Group()
        self.turn_left_key = turn_left_key
        self.turn_right_key = turn_right_key
        self.forward_key = forward_key
        self.backward_key = backward_key
        self.shoot_keys = shoot_keys

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
            color=self.color,
            points=self.triangle(),
            width=LINE_WIDTH
        )

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:

        keys = pygame.key.get_pressed()

        if keys[self.turn_left_key]:
            self.rotate(-dt)
        if keys[self.turn_right_key]:
            self.rotate(dt)
        if keys[self.forward_key]:
            self.move(dt)
        if keys[self.backward_key]:
            self.move(-dt)
        if any(keys[k] for k in self.shoot_keys):
            self.shoot()

        self.time_till_can_shoot -= dt

    def move(self, dt: float):
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= dt * PLAYER_SPEED
        self.position += v
        self.position.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.position.x))
        self.position.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.position.y))


    def shoot(self):
        if self.time_till_can_shoot > 0:
            return 
        self.time_till_can_shoot = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position[0], self.position[1], self.color)
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= PLAYER_SHOOT_SPEED
        shot.velocity = v
        self.shots_group.add(shot)








