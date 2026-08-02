# Build Asteroids: Local Two-Player Deathmatch

An extension course for your existing Asteroids game.

Player 1 flies with `WASD` + `Space`, Player 2 with the arrows + `Enter`. Each
ship has its own color. You can die to an asteroid or to the other player's
bullet. Last ship flying wins.

8 lessons. Every one leaves you with a game you can run — if `uv run main.py` is
broken at the end of a lesson, go back before moving on.

## Rules

- **No friendly fire.** Your own bullet cannot kill you. Don't be tempted to skip
  the owner check on geometric grounds: shots spawn at `self.position`
  (`player.py:66`), which sits inside the hitbox under *every* option in L1, so
  you'd die the instant you pull the trigger. Moving the spawn to the nose (L5)
  only rescues you under the inscrit circle — with the current or circonscrit
  hitbox a nose-spawned shot still starts inside its own shooter. The owner check
  is the only thing that holds regardless of what you pick in L1.
- **Asteroid kills have no killer.** Fly into a rock and you're just dead. You win
  by being the last one alive, however the other player died.
- **Both die on the same frame → draw.**
- **One life per round.** No respawning.
- **Nothing wraps.** Fly off the edge and you're gone. Note the consequence:
  a player who runs away is unreachable, so a round can end in a stalemate that
  never resolves. Closing the window is the way out of one.

---

# Chapter 1: The Hitbox

## L1: Choose the collision circle

Before adding a second ship, settle what a ship *is* to the collision code —
because in a duel this decides who dies, and right now it's an accident.

`collides_with` (`circleshape.py:27`) uses `self.position` and `self.radius`. For
the player that circle is **neither the cercle inscrit nor the cercle circonscrit**
of the drawn triangle. It fails both tests, with `r = 20`:

| test | requires | actual |
|---|---|---|
| circonscrit | all 3 vertices equidistant | nose 20.000, wings 24.037 ✗ |
| inscrit | all 3 sides equidistant | base 20.000, flanks 6.325 ✗ |

What it *is*: the circle whose **diameter is the triangle's altitude**. `triangle()`
puts the apex at `+r * forward` and the base at `-r * forward`, so the height is
`2r` by construction and `self.position` is its midpoint. The base half-width
(`r / 1.5`) never enters the radius — which is exactly why the wingtips stick out
4.04px and are ghosts, while the flanks kill you 13px before contact.

### The two options

Both are off-center — they sit *behind* `self.position`, toward the tail. I
verified both closed forms:

| | radius | center offset along `forward` |
|---|---|---|
| **inscrit** | `2r/(1+√10)` ≈ `0.4805 r` | `-0.5195 r` |
| **circonscrit** | `10r/9` ≈ `1.1111 r` | `-0.1111 r` |

What each does to the feel, against a triangle of area 533.3:

| | radius | hitbox area | vs triangle |
|---|---|---|---|
| inscrit | 9.610 | 290.1 | **0.54×** — forgiving; rocks visibly overlap the hull and you live |
| *current* | 20.000 | 1256.6 | 2.36× |
| circonscrit | 22.222 | 1551.4 | **2.91×** — punishing; nothing that touches the hull is ever missed |

### Assignment

1. **Do not just change `self.radius`.** `triangle()` uses it to build the shape,
   so changing it resizes the drawn ship. The hitbox and the geometry need to be
   separate numbers.

2. In `CircleShape`, add two properties and route `collides_with` through them:

   ```python
   @property
   def collision_center(self) -> pygame.Vector2:
       return self.position

   @property
   def collision_radius(self) -> float:
       return self.radius
   ```

   `collides_with` should compare `self.collision_center` to
   `other.collision_center`, and sum the two `collision_radius` values. Asteroids
   and shots inherit the defaults and are unaffected.

3. Pick one option and add its two factors to `constants.py`.

4. Override both properties in `Player`. The offset runs along `forward`, so it
   rotates with the ship:

   ```python
   forward = pygame.Vector2(0, 1).rotate(self.rotation)
   return self.position + forward * PLAYER_HITBOX_OFFSET * self.radius
   ```

### Tips

- Check your work: with the inscrit circle the distance from `collision_center` to
  all three *sides* should come out equal (9.6101 at `r = 20`); with the circonscrit
  one the distance to all three *vertices* should (22.2222).
- The drawn triangle must not change. If the ship looks different, you edited
  `self.radius` instead of adding the properties.
- These are the honest options you asked for, but neither is obviously right — a
  circle can't match a triangle. Inscrit under-covers the nose, which is the part
  you aim with; circonscrit makes ships fatter than they already are. Play a round
  before committing.

---

# Chapter 2: Two Ships

## L2: Identity and color

`Player.draw()` hardcodes `color="white"` (`player.py:30`) — two white triangles
would be unplayable. And once bullets can kill, players need a stable identity so
you can answer "who fired this?"

Use an `int` for the ID, not the `Player` object. It costs nothing now and
survives a socket later.

### Assignment

1. Add `PLAYER_1_COLOR` and `PLAYER_2_COLOR` to `constants.py`. `"cyan"` and
   `"orange"` read well against black and against the white asteroids. pygame
   accepts color names as plain strings.
2. Add `player_id: int` and `color: str` parameters to `Player.__init__`.
3. Use `self.color` in `Player.draw()`.
4. Update the call at `main.py:35`.

---

## L3: The input seam

The most important lesson here. Slow down for it.

`Player.update()` calls `pygame.key.get_pressed()` itself (`player.py:40`) and
checks hardcoded keys. That welds "what this player wants" to "what this keyboard
is doing," so two players can't share the method.

Split it in two: **key bindings** (which keys belong to whom, static) and **input
state** (what a player wants this frame, five booleans). `Player` stops knowing
about keyboards entirely.

### Assignment

1. Create `controls.py`. **Not `input.py`** — that shadows the builtin.

2. Define:

   ```python
   from dataclasses import dataclass

   @dataclass
   class InputState:
       turn_left: bool = False
       turn_right: bool = False
       thrust: bool = False
       reverse: bool = False
       shoot: bool = False

   @dataclass(frozen=True)
   class KeyBindings:
       turn_left: int
       turn_right: int
       thrust: int
       reverse: int
       shoot: int

   def read_input(bindings: KeyBindings, pressed) -> InputState:
       ...
   ```

   `read_input` takes the result of `pygame.key.get_pressed()` and returns an
   `InputState`. Five lookups.

3. Define `PLAYER_1_KEYS` with the current keys: `K_a`, `K_d`, `K_w`, `K_s`,
   `K_SPACE`.

4. Change the signature to `update(self, dt: float, player_input: InputState)`.
   Replace each `keys[pygame.K_x]` with the matching field. `Player` should no
   longer reference `pygame.key` at all.

5. Add a `bindings: KeyBindings` parameter to `Player.__init__`.

6. **Fix the group problem.** `updatable.update(dt)` passes identical arguments to
   every sprite, but `Player.update` now needs an `InputState` and
   `Asteroid.update` doesn't. Take players out of `updatable`:

   - Add `players = pygame.sprite.Group()` in `main()`.
   - Set `Player.containers = (players, drawable)` — **no `updatable`**.
   - Before `updatable.update(dt)`:

     ```python
     pressed = pygame.key.get_pressed()
     for p in players:
         p.update(dt, read_input(p.bindings, pressed))
     ```

The game should play *exactly* as before. Any visible difference means a bug —
this lesson is pure refactor.

### Tips

- Call `pygame.key.get_pressed()` once per frame and pass that snapshot to every
  player.
- Getting step 6 wrong is the likely failure: leave `updatable` in `containers`
  and `update()` gets called twice with the wrong signature; forget the `players`
  group and your ship freezes.

---

## L4: Player two

### Assignment

1. Define `PLAYER_2_KEYS` in `controls.py`: `K_LEFT`, `K_RIGHT`, `K_UP`, `K_DOWN`,
   `K_RETURN`.

2. Spawn two players either side of center — `SCREEN_WIDTH * 0.25` and
   `SCREEN_WIDTH * 0.75`.

3. Make them face each other. Your rotation convention is not the obvious one — I
   checked it against pygame 2.6.1:

   | `self.rotation` | `forward` | on screen |
   |---|---|---|
   | `0`   | `(0, 1)`  | **down** |
   | `90`  | `(-1, 0)` | **left** |
   | `-90` | `(1, 0)`  | **right** |
   | `180` | `(0, -1)` | **up** |

   Screen `y` grows downward, so rotation `0` points at the *bottom* of the
   window. The left-hand player wants `rotation = -90`, the right-hand player
   `rotation = 90`. Add a `rotation` parameter to `__init__` (default `0`).

### Tips

- The game still `sys.exit()`s when either player hits an asteroid
  (`main.py:52-55`). Expected — L6 fixes it.
- Related to the table above: `K_a` increases `rotation`, which turns the ship
  **clockwise** on screen — inverted from the Asteroids convention. Harmless in
  single-player, noticeable when two people are leading shots. To flip it, swap
  which of `turn_left`/`turn_right` calls `self.rotate(dt)` vs `self.rotate(-dt)`.

---

# Chapter 3: Combat

## L5: Shots with owners

A bullet knows position and velocity and nothing else. To decide "did P2's bullet
hit P1?" it needs an owner. Color it to match the shooter while you're in there —
one extra field, and firefights become readable.

### Assignment

1. Add `owner_id: int` and `color: str` to `Shot.__init__`.
2. Use `self.color` in `Shot.draw()`.
3. Pass `self.player_id` and `self.color` from `Player.shoot()`.
4. Spawn the shot at the nose instead of the center:

   ```python
   forward = pygame.Vector2(0, 1).rotate(self.rotation)
   spawn = self.position + forward * self.radius
   ```

   You already compute this in `triangle()` — point `a`.

### Tips

- Step 4 is mostly cosmetic — bullets look like they leave the gun rather than the
  middle of the ship. Whether it also clears you of your own shot depends on what
  you picked in L1: at `r = 20` the nose sits 20.00 from the default collision
  center against a threshold of 25.00 (still a hit), 22.22 vs 27.22 under
  circonscrit (still a hit), but 30.39 vs 14.61 under inscrit (clear). Don't rely
  on it either way — the owner check in L7 is what makes this unconditional.

---

## L6: Elimination instead of exit

`main.py:52-55` calls `sys.exit()` on a player hit. With two players, one death is
the end of *one player's* game.

`sprite.kill()` removes it from every group, so a dead player instantly stops
updating, drawing, and colliding. Group membership *is* the alive flag — you don't
need a boolean.

I verified the group semantics you're leaning on: `Group.__iter__` returns
`iter(self.sprites())` and `sprites()` returns `list(self.spritedict)`, a
**snapshot**. So `kill()` mid-loop is safe, and sprites added mid-loop (as
`Asteroid.split()` does) just aren't visited until next frame. `sprite.alive()`
returns `False` after `kill()`.

### Assignment

1. Split the collision block into separate passes — players vs asteroids, then
   shots vs asteroids.
2. Replace `print` + `sys.exit()` with `player.kill()` and a richer log:
   `log_event("player_died", player_id=player.player_id, cause="asteroid")`.
3. Leave the shots-vs-asteroids logic alone; it was already correct.

One ship vanishes, the other keeps flying. The game doesn't end yet — that's L8.

### Tips

- After `kill()`, stop testing that player against more asteroids this frame —
  `break`, or check `player.alive()`.
- Your new `players` group will start showing up in `game_state.jsonl`;
  `log_state` introspects caller locals for anything group-shaped. Nothing breaks,
  the log shape just changes.

---

## L7: Death by gunfire

The headline feature. One more pass. The rule: **a shot kills any player except
the one who fired it.**

### Assignment

1. Add a shots-vs-players pass.
2. Skip the pair when `shot.owner_id == player.player_id`.
3. On a hit, kill both and log it: `log_event("player_shot", victim=..., shooter=...)`.
4. **Guard the double-consume bug.** A shot that already hit an asteroid in the
   previous pass is dead, but your loop variable still points at it — without a
   check it gets a second kill. Use `shot.alive()`, or order the passes so it
   can't happen.

Test: hold `Space` while spinning hard and confirm you can't kill yourself.

---

# Chapter 4: Winning

## L8: The win condition

Three situations after collisions resolve:

| players alive | meaning |
|---|---|
| 2 | still playing |
| 1 | that player wins |
| 0 | draw |

`len(players)` gives you this for free. The draw row is real, not theoretical —
`players.sprites()[0]` without a length check is an `IndexError` waiting to happen.

The round ends by ending the program. No game state, no freeze, no restart: as
soon as someone wins, the window closes for both players and you read the result
from the terminal.

### Assignment

1. After the collision passes, check `len(players)`.
2. If it's `1`, that player wins. If it's `0`, it's a draw. Otherwise carry on.
3. Either way: `log_event("round_over", winner=...)`, print the result, and
   `sys.exit(0)`.

### Tips

- **`sys.exit(0)`, not `exit(1)`.** `exit` is injected by the `site` module for
  the interactive REPL and isn't guaranteed to exist in a script. And `1` means
  *the program failed* — a finished game isn't a failure.
- Do the check *after* all three collision passes, not inside them. Check midway
  and a player who dies in a later pass on the same frame gets missed, turning a
  draw into a win.
- `print()` the winner as well as logging it, since the window is about to vanish
  and the terminal is all you'll have left.
- `sys` is still imported in `main.py` — you'll keep needing it.

---

# Where this leaves you

Every gameplay rule now lives in the collision passes and the win check in
`main.py`. Two things you built here are what a networked version would need:
`InputState` (a player's intent is five booleans, no keyboard attached — feed one
from a socket and `player.py` doesn't change) and integer IDs (`shot.owner_id`
serializes; a `Player` reference wouldn't).

Latency, simulation authority, and serializing pygame groups are still ahead. But
they're now separable from "what are the rules of the game."
