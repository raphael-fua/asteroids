from circleshape import CircleShape
from shot import Shot
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_START_HEALTH,
    PLAYER_MAX_HEALTH,
    PLAYER_INVULNERABLE_SECONDS,
    PLAYER_PALE_AT_LOW_HEALTH,
    PLAYER_START_AMMO,
    PLAYER_MAX_AMMO,
    BONUS_HEALTH_AMOUNT,
    BONUS_AMMO_AMOUNT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from logger import log_event
import pygame

# Endpoints of the ammo ring's ramp. Pushed well past pygame's "darkgreen"/"palegreen"
# at both ends so a full magazine and an empty one are unmistakable at a glance.
AMMO_FULL_COLOR = (0, 50, 0)
AMMO_EMPTY_COLOR = (220, 255, 220)


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
        self.health: int = PLAYER_START_HEALTH
        self.ammo: int = PLAYER_START_AMMO
        self.invulnerable_time: float = 0.0
        self.shots_group = pygame.sprite.Group()
        self.turn_left_key = turn_left_key
        self.turn_right_key = turn_right_key
        self.forward_key = forward_key
        self.backward_key = backward_key
        self.shoot_keys = shoot_keys

    def triangle(self) -> list[pygame.Vector2]:
        # Isosceles triangle inscribed exactly in the circle at (self.position, self.radius):
        # the nose plus two base vertices symmetric about the forward axis, all at distance
        # self.radius from self.position by construction.
        spread = 40  # degrees; controls how narrow/wide the base vertices sit from the nose
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        a = self.position + forward * self.radius
        b = self.position + forward.rotate(180 - spread) * self.radius
        c = self.position + forward.rotate(-(180 - spread)) * self.radius
        return [a, b, c]

    def display_color(self) -> pygame.Color:
        """The ship's colour, washed out in proportion to the health it has lost, so
        damage is legible on the ship itself and not only in the HUD. self.color is
        left alone: shots and the HUD keep the player's full-strength colour.
        """
        lost = (PLAYER_MAX_HEALTH - self.health) / max(1, PLAYER_MAX_HEALTH - 1)
        return pygame.Color(self.color).lerp(
            "white", PLAYER_PALE_AT_LOW_HEALTH * min(1.0, lost)
        )

    def ammo_color(self) -> pygame.Color:
        """The ring around the ship doubles as an ammo gauge: near-black green with a
        full magazine, fading to near-white green as it empties, so the count can be
        read without looking away to the HUD. Measured against PLAYER_MAX_AMMO, so a
        ship carrying the starting 20 of a possible 40 already sits mid-ramp.
        """
        spent = 1.0 - min(1.0, self.ammo / PLAYER_MAX_AMMO)
        return pygame.Color(*AMMO_FULL_COLOR).lerp(pygame.Color(*AMMO_EMPTY_COLOR), spent)

    def draw(self, screen: pygame.Surface) -> None:
        color = self.display_color()
        pygame.draw.polygon(
            surface=screen,
            color=color,
            points=self.triangle(),
            width=0
        )
        # Empirically tuned: pygame.draw.polygon (fill) and pygame.draw.circle (stroke) each
        # round the exact triangle/circle geometry to pixels differently, so a small margin
        # on top of self.radius is needed to reliably cover the corners.
        pygame.draw.circle(screen, self.ammo_color(), self.position, self.radius + 2.0, 2)

    def rotate(self, dt: float) -> None:
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
        # Clamped at 0 (unlike the cooldown above) so is_invulnerable stays a plain > 0.
        self.invulnerable_time = max(0.0, self.invulnerable_time - dt)

    def move(self, dt: float) -> None:
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= dt * PLAYER_SPEED
        self.position += v
        self.position.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.position.x))
        self.position.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.position.y))


    def is_invulnerable(self) -> bool:
        return self.invulnerable_time > 0.0

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int = 1) -> bool:
        """Applies damage unless invulnerable. Returns True if the damage landed."""
        if self.is_invulnerable():
            return False
        self.health -= amount
        self.invulnerable_time = PLAYER_INVULNERABLE_SECONDS
        log_event("player_damaged", player=self.name, health=self.health)
        return True

    def add_health(self, amount: int = BONUS_HEALTH_AMOUNT) -> None:
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)

    def add_ammo(self, amount: int = BONUS_AMMO_AMOUNT) -> None:
        self.ammo = min(PLAYER_MAX_AMMO, self.ammo + amount)

    def shoot(self) -> None:
        if self.time_till_can_shoot > 0:
            return
        if self.ammo <= 0:
            # Second, so that an empty gun does not keep resetting the cooldown.
            return
        self.ammo -= 1
        self.time_till_can_shoot = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position[0], self.position[1], self.color)
        v = pygame.Vector2(0,1)
        v = v.rotate(self.rotation)
        v *= PLAYER_SHOOT_SPEED
        shot.velocity = v
        self.shots_group.add(shot)








