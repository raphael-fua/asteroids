import random

import pygame

from asteroidfield import AsteroidField
from constants import BONUS_SPAWN_RATE_SECONDS, BONUS_SPEED, BONUS_HEALTH_CHANCE
from logger import log_event
from claude_generated.bonus_asteroid import HealthAsteroid, AmmoAsteroid


class BonusField(pygame.sprite.Sprite):
    """Spawns pickups on the same schedule-and-edge pattern as AsteroidField, but on
    its own much slower timer.
    """

    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, spawn_rate_seconds: float = BONUS_SPAWN_RATE_SECONDS) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.spawn_rate_seconds = spawn_rate_seconds

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer <= self.spawn_rate_seconds:
            return
        self.spawn_timer = 0.0

        # Reuses AsteroidField's edge table: (inward direction, position along the edge).
        direction, place = random.choice(AsteroidField.edges)
        # `direction * speed` returns a new vector, so the shared edge table is safe.
        velocity = (direction * BONUS_SPEED).rotate(random.randint(-20, 20))
        position = place(random.uniform(0, 1))

        health = random.random() < BONUS_HEALTH_CHANCE
        bonus_class = HealthAsteroid if health else AmmoAsteroid
        bonus = bonus_class(position.x, position.y)
        bonus.velocity = velocity
        log_event("bonus_spawned", kind="health" if health else "ammo")
