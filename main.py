# import sys
import pygame
from logger import log_state, log_event

from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASTEROID_SPAWN_RATE_SECONDS,
    ASTEROID_SPAWN_RATE_SECONDS_SOLO,
)
                              
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from claude_generated.starfield import Starfield
from claude_generated.game_flow import show_start_screen, show_game_over_screen

# def main():
#     print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
#     print(f"Screen width: {SCREEN_WIDTH}")
#     print(f"Screen height: {SCREEN_HEIGHT}")
#
#     pygame.init()
#
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#
#     clock = pygame.time.Clock()

def run_game(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    num_players: int,
    starfield: Starfield,
) -> tuple[str, Player | None]:
    """Plays one round. Returns ("quit", None) or ("game_over", winner-or-None)."""
    dt = 0.0

    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable  = pygame.sprite.Group()
    shots     = pygame.sprite.Group()

    Shot.containers = (shots, updatable, drawable)

    Asteroid.containers = (asteroids, updatable, drawable)

    Player.containers = (updatable, drawable)
    player1_x = SCREEN_WIDTH / 2.0 if num_players == 1 else SCREEN_WIDTH / 4.0
    player1_y = SCREEN_HEIGHT / 2.0 if num_players == 1 else SCREEN_HEIGHT / 4.0
    player1 = Player(x=player1_x, y=player1_y, color="red", name="Red Player")
    players = [player1]

    player2 = None
    if num_players == 2:
        player2 = Player(
            x=3.0 * SCREEN_WIDTH / 4.0,
            y=3.0 * SCREEN_HEIGHT / 4.0,
            color="blue",
            name="Blue Player",
            turn_left_key=pygame.K_LEFT,
            turn_right_key=pygame.K_RIGHT,
            forward_key=pygame.K_UP,
            backward_key=pygame.K_DOWN,
            shoot_keys=(pygame.K_RCTRL, pygame.K_RALT),
        )
        player2.rotation = 180
        players.append(player2)

    AsteroidField.containers = (updatable,)
    spawn_rate = ASTEROID_SPAWN_RATE_SECONDS if num_players == 2 else ASTEROID_SPAWN_RATE_SECONDS_SOLO
    AsteroidField(spawn_rate)


    #THE GAME LOOP
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ("quit", None)
        screen.fill("black")
        starfield.draw(screen)

        updatable.update(dt)

        for asteroid in asteroids:
            for hit_player in players:
                if hit_player.collides_with(asteroid):
                    log_event("player_hit", player=hit_player.name)
                    winner = None
                    if player2 is not None:
                        winner = player1 if hit_player is player2 else player2
                    return ("game_over", winner)
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()

        if player2 is not None:
            for shot in player1.shots_group:
                if shot.collides_with(player2):
                    log_event("player_hit", player=player2.name)
                    return ("game_over", player1)

            for shot in player2.shots_group:
                if shot.collides_with(player1):
                    log_event("player_hit", player=player1.name)
                    return ("game_over", player2)

        for drawable_item in drawable:
                drawable_item.draw(screen)

        pygame.display.flip()  


        dt = clock.tick(60) / 1000.0  
        # dt is the time in seconds since `clock.tick()` was last called
        # because we pass `60`ms to `clock.tick()` at every iteration,
        # we must have `dt >= 60 / 1000.0`

# End the game immediately with sys.exit(). (Don't forget to import sys!)


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE | pygame.SCALED | pygame.FULLSCREEN,
    )
    clock = pygame.time.Clock()
    starfield = Starfield()

    num_players = show_start_screen(screen, clock, starfield)
    if num_players is None:
        return

    while True:
        outcome, winner = run_game(screen, clock, num_players, starfield)
        if outcome == "quit":
            return
        if not show_game_over_screen(screen, clock, winner, starfield):
            return


if __name__ == "__main__":
    main()




