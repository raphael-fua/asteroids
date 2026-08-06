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
from claude_generated.bonus_asteroid import HealthAsteroid, AmmoAsteroid
from claude_generated.bonus_field import BonusField
from claude_generated.hud import Hud

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

def resolve_shot_hits(shooter: Player, target: Player) -> None:
    """Applies at most one of `shooter`'s shots to `target` this frame, so a burst
    arriving together costs one point of health rather than one per shot.
    """
    if target.is_invulnerable():
        return  # shots pass through, rather than vanishing against an untouchable ship
    for shot in shooter.shots_group:
        if shot.collides_with(target):
            shot.kill()
            target.take_damage()
            log_event("player_shot", shooter=shooter.name, target=target.name)
            return


def run_game(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    num_players: int,
    starfield: Starfield,
    hud: Hud,
) -> tuple[str, Player | None]:
    """Plays one round. Returns ("quit", None) or ("game_over", winner-or-None)."""
    dt = 0.0

    asteroids = pygame.sprite.Group()
    bonuses   = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable  = pygame.sprite.Group()
    shots     = pygame.sprite.Group()

    Shot.containers = (shots, updatable, drawable)

    Asteroid.containers = (asteroids, updatable, drawable)

    # Load-bearing: without their own containers the bonus subclasses would inherit
    # Asteroid's and land in `asteroids`, where they would be treated as lethal rocks.
    HealthAsteroid.containers = (bonuses, updatable, drawable)
    AmmoAsteroid.containers = (bonuses, updatable, drawable)

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

    BonusField.containers = (updatable,)
    BonusField()


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
                    # An invulnerable player passes straight through, rock intact.
                    if hit_player.take_damage():
                        asteroid.split()
                    break
            if not asteroid.alive():
                continue  # already split: splitting it again would spawn four children
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()
                    break

        for bonus in bonuses:
            # Touching beats shooting, so a same-frame tie goes to physical contact.
            claimer = next((p for p in players if p.collides_with(bonus)), None)
            if claimer is None:
                for player in players:
                    # Iterating a player's own shots is what identifies the owner.
                    hit = next(
                        (s for s in player.shots_group if s.collides_with(bonus)), None
                    )
                    if hit is not None:
                        hit.kill()
                        claimer = player
                        break
            if claimer is not None:
                bonus.claim(claimer)

        if player2 is not None:
            resolve_shot_hits(player1, player2)
            resolve_shot_hits(player2, player1)

        dead = [p for p in players if not p.is_alive()]
        if dead:
            log_event("round_over", dead=[p.name for p in dead])
            if player2 is None or len(dead) == 2:
                return ("game_over", None)
            return ("game_over", player1 if dead[0] is player2 else player2)

        for drawable_item in drawable:
                drawable_item.draw(screen)

        hud.draw(screen, players)  # last, so the text sits above every sprite

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
    hud = Hud()

    num_players = show_start_screen(screen, clock, starfield)
    if num_players is None:
        return

    while True:
        outcome, winner = run_game(screen, clock, num_players, starfield, hud)
        if outcome == "quit":
            return
        if not show_game_over_screen(screen, clock, winner, starfield):
            return


if __name__ == "__main__":
    main()




