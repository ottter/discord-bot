# Wordle

Suggests the next Wordle guess from the colors on your board, in hard mode by
default. It never sees the day's answer; that's only used afterward to check
how it did.

    python -m modules.wordle crane:BBYGB slate:BGYBB   next guess from your board
    python -m modules.wordle --answer stole            watch it play a word
    python -m modules.wordle --image results.png       use other players' boards

The bot uses `solver.py`, `boards.py` and `image.py`. Word lists and digit
shapes are in `data/`, and the tuning and rebuild scripts in `tools/`.

Other players' boards come from the Wordle app's result images (`image.py`) or
can be typed with `--board BBYBB,BGGBY,GGGGG`. Only their colors are used.

Past answers in `data/past.txt` count against a word, since NYT rarely repeats. Add
each day's answer to the end once the day is over, repeats included.

## In Discord

The bot reads the Wordle app's posts, which it edits with a new image as
people play. Only finished boards count: solved, or out of guesses. Every
server's boards for a game are pooled, each counted once, and every play uses
the pool. Each server still locks in on its own: once its own posts show three
finished boards, the bot plays and posts its result, just the colored squares
and the score like a share, plus what it would have scored with no boards. A game runs about two days across timezones, so
once the game after next has started, any server that never got to three is
locked in quietly, without a post.

The commands don't need the app at all. Today's game comes from the date (US
Eastern by default), or a newer number if an image has shown one, and the bot
plays with however many boards it has, none included.

| Command | What it does |
| --- | --- |
| `/wordle play [game]` | Posts the result, colors only. Until it's locked in, it plays with the boards so far, and the last one stands if the server never reaches three. With a game number, replays that game with any boards stored for it, saving nothing; only games already released somewhere |
| `/wordle today` | The same, only for you, plus how many boards it used, what it would have scored blind from `slate`, and each guess with the four words it was picked over, how likely each looked, and the answer, all in spoilers. Saves nothing |
| `/wordle simulate word` | Plays any word with no boards and shows every guess |
| `/wordle channel` | Where locked-in results post. Unset means next to the app's message |

The first time a game number shows up, the bot looks up its answer once from
NYT (numbers count days since 19 June 2021). It's only used to color the
bot's own guesses. A game's answer counts as used for later games only, so a
game is always played as it was on its day. Answers the bot stores are added
to `data/past.txt`'s; add your own there as `1938 major` and the bot skips
its copy of that game.

## How it got here

This started as [wordle-loser](https://github.com/ottter/wordle-loser), which
ranked words by how often they show up in the Brown corpus (1960s American
text) and guessed whichever word left had the most vowels. Brown has never seen
most five-letter words, so much of the list ended up alphabetical, and a few
sorting rules buried words like `angry` near the bottom. It opened with things
like `audio` then `curia`, and averaged 4.3 guesses on a small test.

Switching to [wordfreq](https://pypi.org/project/wordfreq/), which reflects how
common words are today, and picking the guess that best splits the words left
instead of the one with the most vowels, brought that to 3.4.

After that, every change was tested in hard mode against all past answers:

- **Weights.** A steeper frequency curve, plus cutting plurals, past tenses and
  a hand-picked list of names, slang and crude words NYT never uses: 3.62 to
  3.59.
- **Opener.** `slate` beat seven other popular openers. Its anagrams showed its
  early greens help more than they hurt.
- **Traps.** A check for families like `_ATCH` took `hatch` from 8 guesses to 4,
  but only saved a couple of games overall. A deeper search and a two-letter
  version didn't help.
- **Smaller fixes.** Counting a correct guess as solved stopped it picking
  `abray` over `array`. Entropy scoring was worse.
- **Honest tuning.** Settings are picked on half the answers and checked on the
  other half. Most late tweaks turned out to be noise.

The biggest gain came from past answers. They now keep a fifth of their weight,
and less again for each repeat. In a simulated history with repeats at 1 game
in 10, the rate since reuse started in February 2026, that took the average
from about 3.54 to 3.30.

Then came other players' boards. Each row someone else got says something
about the answer. A first row is a free choice, so a rare one like ⬛🟩🟩🟩🟩
says a lot and a common one hardly anything. Later rows aren't free, since
players have to guess words that fit what they've seen, so those only ask
whether some likely word could show that row for a given answer. Reading
later rows like first ones held back answers like `strew`, which have few
common neighbors. The bench tests this with two kinds of made-up players:

- **Tidy** players open with a popular opener about a third of the time, in
  the proportions people really use them, and otherwise with a random common
  word. After that they guess one of the likeliest words that still fits.
- **Messy** players open the same way, then guess any common word that still
  fits, picked at random.

Five boards took it from about 3.34 to 2.42 with tidy players and 2.39 with
messy ones. Each board helps a little less than the last, but none stop
helping:

| Boards | 0 | 1 | 2 | 3 | 4 | 5 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Average guesses (messy players) | 3.34 | 3.04 | 2.79 | 2.63 | 2.48 | 2.39 | 2.25 |

Two boards get over half of what five do, and three about three quarters. On real images, `copse` (#1924, six boards) went from 5 guesses to
2, and `strew` (#1937, five boards) rose from 5,450th likeliest to 50th.

## What past answers look like

1,928 games so far (1,903 different words), compared with the weights in
`data/words.txt`.

**How common they are.** Frequency predicts answers well. Our top 1,000 words
include 46% of all answers, and 87% of those 1,000 have been answers:

| Our top words | Answers they cover | How many of them were answers |
| --- | --- | --- |
| 500 | 24% | 92% |
| 1,000 | 46% | 87% |
| 2,000 | 79% | 75% |
| 3,000 | 93% | 59% |
| 5,000 | 99% | 38% |

**What NYT avoids.** Only one answer, `fried`, is a plural or past tense, and
none are names, places, brands, slang or crude words. Those are still allowed
guesses, just weighted as unlikely answers (`data/unlikely.txt`).

**Letters by position.** The biggest gaps between answers and what the weights
expect:

| Letter | Answers | Weights expect |
| --- | --- | --- |
| S last | 1.5% | 4.9% |
| A second | 12.5% | 15.0% |
| A last | 2.7% | 4.9% |
| O third | 11.3% | 9.5% |

Correcting for these barely helps on held-back answers, so the weights don't.

## Settings

A quick reference from bench runs, not a study. Solver settings are at the top
of `solver.py` and `boards.py`; try one with
`python -m modules.wordle.tools.bench --set NAME=VALUE`.

| Setting | Default | What it does | Range | What we saw |
| --- | --- | --- | --- | --- |
| `OPENER` | slate | First guess | Any word | Best of 8 popular openers. Its yellow-heavy anagrams (steal, tales) did worse; least tied it |
| `hard` | True | Greens stay put, yellows must be reused | — | What we play and tune for |
| `vowels` | False | wordle-loser's most-vowels rule | — | Worse, about 4.1 against 3.8–3.9 |
| `GUESS_POOL` | 3000 | How many common words can be played as probes | 1000–5000 | No difference |
| `SAMPLE` | 300 | How many of the likeliest answers a guess is judged against | 150–600 | No difference; lower is faster |
| `SURE` | 0.5 | Guess the likeliest word once it holds this share of the weight left | 0.3–1 | No difference |
| `LOSS_COST` | 20 | How hard it avoids trap families like _ATCH; 0 is off | 10–50 | Flat from 10 to 30. 500 lost fewer games but cost 0.05 guesses |
| `SHORTLIST` | 100 | How many of the best guesses get the trap check | 50–200 | Not tested |
| `NEAR_TIE` | 0.1 | Guesses within this much of the best count as tied | 0–0.2 | Nothing held up on both halves |
| `MIN_GAIN` | 0.1 | How much likelier a tied word must be to win the tie | 0.05–0.3 | No difference |
| `SOLVED_LEAVES_NOTHING` | True | A correct guess counts as nothing left to find | — | Stops picks like abray over array |
| `ENTROPY` | False | Judge splits by information gained instead | — | Worse by 0.06–0.12 |
| `BOARD_TRUST` | 1.0 | How much other players' boards count; 0 ignores them. In `boards.py` | 0.5–2 | 1 best with 5 players: about 2.4 against 3.34 without boards. Flat up to 2 |
| `FLOOR` | 0.02 | Least share of the best fit a row leaves any answer, so nothing's ruled out. In `boards.py` | — | Not tested |
| `OPENER_SWITCH` | 0.2 | With boards, the opener is worked out like any guess, but slate stays unless the pick leaves this much less to find | — | 15 real days: 2.47 guesses against slate's 2.60. Simulated boards flatter it far more (1.64 against 2.27 at 6 boards). `PICK_OPENER` in `games.py` turns it off |
| `USED_FACTOR` | 0.2 | Share of its weight a past answer keeps | 0.1–0.5 | Biggest gain: 3.30 against 3.54 uncut. Heavier cuts fall behind as repeats rise |

The answer weights come from `python -m modules.wordle.tools.sort_words` and
are tuned with `python -m modules.wordle.tools.tune_weights`.

| Setting | Default | What it does | Range | What we saw |
| --- | --- | --- | --- | --- |
| `MIDPOINT` | 3.0 | How common a word must be to count as a 50/50 answer | 2.75–3.0 | Lower fit the tuning half but not the held-back half |
| `STEEPNESS` | 3.0 | How fast weight drops below the midpoint | 3–4 | 2 fit worse |
| `UNLIKELY_PENALTY` | 0.002 | Weight cut for plurals, past tenses and `data/unlikely.txt` | 0.002–0.01 | Lower fits better; kept above 0 so they stay possible |

## Results

Hard mode, 100 games each, replaying a made-up history so past answers count
as used, with messy made-up players for the other boards. The bot works its
opener out from the boards; always opening with `slate` is shown to compare.

| Other players' boards | 0 | 2 | 4 | 6 |
| --- | --- | --- | --- | --- |
| Opener worked out (what the bot does) | 3.31 | 2.55 | 2.01 | 1.64 |
| Always `slate` | 3.31 | 2.74 | 2.46 | 2.27 |

    python -m modules.wordle.tools.bench --used 0.2 --games 100 --players 2 --messy --start auto

Made-up boards narrow things down more cleanly than real ones. On 15 real days
from our server, mostly five or six boards each, the bot averaged 2.47 guesses
against 2.60 opening with `slate`.
