import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from claude_generated.starfield import Starfield


def show_start_screen(
    screen: pygame.Surface, clock: pygame.time.Clock, starfield: Starfield
) -> int | None:
    """Asks 1 or 2 players. Returns the chosen count, or None if the window was closed."""
    font = pygame.font.Font(None, 64)
    line1_text = font.render("[1] Player", True, "white")
    line1_rect = line1_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))

    line2_text = font.render("[2] Players", True, "white")
    line2_rect = line2_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    return 1
                if event.key in (pygame.K_2, pygame.K_KP2):
                    return 2

        screen.fill("black")
        starfield.draw(screen)
        screen.blit(line1_text, line1_rect)
        screen.blit(line2_text, line2_rect)
        pygame.display.flip()
        clock.tick(60)


def show_game_over_screen(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    winner: Player | None,
    starfield: Starfield,
) -> bool:
    """Shows the winner and waits. Returns True to replay, False to quit."""
    font = pygame.font.Font(None, 64)
    if winner is not None:
        title_text = font.render(f"{winner.name} wins!", True, winner.color)
    else:
        title_text = font.render("Game Over", True, "white")
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
        starfield.draw(screen, show_labels=True)
        screen.blit(title_text, title_rect)
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()
        clock.tick(60)
