# Next steps

## Fullscreen resolution is blurry

`pygame.SCALED` stretches the fixed 1280x720 game surface up to fill the physical
display, which looks blurry on larger/high-DPI screens.

Raising `SCREEN_WIDTH`/`SCREEN_HEIGHT` (e.g. to 1920x1080) would sharpen the image, but
it would also change gameplay dynamics: `PLAYER_SPEED`, `PLAYER_TURN_SPEED`, asteroid
speeds, and radii (`PLAYER_RADIUS`, `ASTEROID_MIN_RADIUS`, `SHOT_RADIUS`) are all
absolute pixel values, not scaled relative to screen size. A 1.5x resolution bump alone
would make everything take 1.5x longer to cross the screen and make sprites relatively
smaller against the bigger play area.

Options to revisit:
- Bump resolution and scale all gameplay constants by the same factor, to preserve feel.
- Bump resolution only, and accept the pacing/difficulty change.
- Leave resolution as-is and address the blur another way (e.g. change `SCALED`
  filtering/quality, or render at native resolution instead of a fixed logical surface).


## Shot restrictions

In its current form, the player has no reason not to shoot constantly. 

Should be able to run out of bullets

in which case he should have to wait for the next 'delivery' of bullets.
