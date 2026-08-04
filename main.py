# import sys
import pygame
from logger import log_state, log_event

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
                              
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

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

def run_game(screen: pygame.Surface, clock: pygame.time.Clock) -> Player | None:
    """Plays one round. Returns the winner's name, or None if the window was closed."""
    dt = 0.0

    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable  = pygame.sprite.Group()
    shots     = pygame.sprite.Group()

    Shot.containers = (shots, updatable, drawable)
                       
    Asteroid.containers = (asteroids, updatable, drawable)

    Player.containers = (updatable, drawable)
    player1 = Player(
        x=SCREEN_WIDTH / 4.0, y=SCREEN_HEIGHT / 4.0, color="red", name="Red Player"
    )
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
    players = [player1, player2]

    AsteroidField.containers = (updatable,)
    AsteroidField()


    #THE GAME LOOP
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")

        updatable.update(dt)

        for asteroid in asteroids:
            for hit_player in players:
                if hit_player.collides_with(asteroid):
                    log_event("player_hit", player=hit_player.name)
                    winner = player1 if hit_player is player2 else player2
                    return winner
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()

        for shot in player1.shots_group:
            if shot.collides_with(player2):
                log_event("player_hit", player=player2.name)
                return player1

        for shot in player2.shots_group:
            if shot.collides_with(player1):
                log_event("player_hit", player=player1.name)
                return player2

        for drawable_item in drawable:
                drawable_item.draw(screen)

        pygame.display.flip()  


        dt = clock.tick(60) / 1000.0  
        # dt is the time in seconds since `clock.tick()` was last called
        # because we pass `60`ms to `clock.tick()` at every iteration,
        # we must have `dt >= 60 / 1000.0`

# End the game immediately with sys.exit(). (Don't forget to import sys!)


def show_game_over_screen(
    screen: pygame.Surface, clock: pygame.time.Clock, winner: Player
) -> bool:
    """Shows the winner and waits. Returns True to replay, False to quit."""
    font = pygame.font.Font(None, 64)
    title_text = font.render(f"{winner.name} wins!", True, winner.color)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))

    prompt_text = font.render("[R]eplay or [Q]uit", True, "white")
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False

        screen.fill("black")
        screen.blit(title_text, title_rect)
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()
        clock.tick(60)


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

    while True:
        winner = run_game(screen, clock)
        if winner is None:
            return
        if not show_game_over_screen(screen, clock, winner):
            return


if __name__ == "__main__":
    main()




