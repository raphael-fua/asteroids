import sys
import pygame
from logger import log_state, log_event

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
                              
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    dt = 0.0

    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable  = pygame.sprite.Group()
    shots     = pygame.sprite.Group()

    Shot.containers = (shots, updatable, drawable)
                       
    Asteroid.containers = (asteroids, updatable, drawable)

    Player.containers = (updatable, drawable)
    player = Player(x=SCREEN_WIDTH / 2.0, y=SCREEN_HEIGHT / 2.0)

    AsteroidField.containers = (updatable,)
    asteroidfield = AsteroidField()


    #THE GAME LOOP
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")

        updatable.update(dt)

        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                print("Game over!")
                sys.exit()
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()

        for drawable_item in drawable:
                drawable_item.draw(screen)

        pygame.display.flip()  


        dt = clock.tick(60) / 1000.0  
        # dt is the time in seconds since `clock.tick()` was last called
        # because we pass `60`ms to `clock.tick()` at every iteration,
        # we must have `dt >= 60 / 1000.0`

# End the game immediately with sys.exit(). (Don't forget to import sys!)





if __name__ == "__main__":
    main()




