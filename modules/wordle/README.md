# Wordle

Suggests the next Wordle guess from the colors on your board, in hard mode by
default. It never sees the day's answer, which is only used afterward to check
how it did.

    python -m modules.wordle crane:BBYGB slate:BGYBB   next guess from your board
    python -m modules.wordle --answer stole            watch it play a word
    python -m modules.wordle --image results.png       use other players' boards

The bot uses `solver.py`, `boards.py` and `image.py`. Word lists and digit
shapes are in `data/`, and the tuning and rebuild scripts are in `tools/`.

There are two word lists, with the same 14,855 words NYT accepts, weighted for
different questions:

- **`words.txt`: what the answer is likely to be.** Common words weigh more,
  and plurals, past tenses and the words in `unlikely.txt` are cut 500 times,
  since NYT almost never uses them as answers. The bot's own guesses come from
  these weights.
- **`guesses.txt`: what other players are likely to guess.** Just how common
  each word is, with nothing cut. People guess `tired` and `fired` all the
  time even though they're never answers, so this is what reading other
  players' boards uses.

Both are rebuilt by `python -m modules.wordle.tools.sort_words`.

`answers.txt` is Wordle's original answer list from the game's code, 2,315
words. About 97% of answers so far are on it; NYT adds the odd word like
`yodel`. It's only used when `LIST_TRUST` is on, which it isn't by default.

Other players' boards come from the Wordle app's result images (`image.py`), or
can be typed with `--board BBYBB,BGGBY,GGGGG`. Only their colors are used.

Past answers in `data/past.txt` count against a word, since NYT rarely
repeats. Add each day's answer to the end once the day is over, including
repeats.

## In Discord

### Posting results

The bot reads the Wordle app's posts. The app edits each post with a new image
as people play. Only finished boards count, meaning solved or out of guesses.

Boards from every server are pooled for each game, each counted once, and
every play uses the whole pool. Each server still locks in on its own. Once a
server's own posts show three finished boards, the bot plays and posts its
result: the colored squares and the score, like a share, plus what it would
have scored with no boards.

A game runs for about two days across timezones. Once the game after next has
started, any server that never reached three boards is locked in without a
post.

### Commands

The commands don't need the app. Today's game comes from the date (US Eastern
by default), or from a newer number if an image has shown one. The bot plays
with however many boards it has, including none.

Each play is saved by game and the exact set of boards it used, so the same
boards are never worked out twice. Saved plays are dropped when the solver
code or word lists change.

| Command | What it does |
| --- | --- |
| `/wordle play [game] [boards]` | Posts the result with each guess and how likely it looked, the four words it was picked over, how many words still fitted before it (in brackets), and the answer, all in spoilers. It also says how many boards it used and what it would have scored opening blind with `slate`. It plays with every board so far. Set `boards` to False to play just that once without them; that play isn't saved. If more boards have come in since the server locked in, it also gives the locked result as the official score. Before the lock, the last result stands if the server never reaches three. With a game number, it replays that game with any stored boards and saves nothing. Only games already released somewhere can be played |
| `/wordle stats` | Shows how many games this server has locked in, the average official score, and the average for the same games played blind from `slate`. A game it didn't solve counts as 7 |
| `/wordle simulate word` | Plays any word with no boards and shows every guess |
| `/wordle channel` | Sets where locked-in results post. If unset, they post next to the app's message |

### Answers

The first time a game number appears, the bot looks up its answer once from
NYT (game numbers count days since 19 June 2021). The answer is only used to
color the bot's own guesses. It counts as used for later games only, so each
game is played as it was on its day. Answers the bot stores are added to those
in `data/past.txt`. If you add one there yourself, as `1938 major`, the bot
skips its own copy of that game.

## How it got here

### Where it started

This began as [wordle-loser](https://github.com/ottter/wordle-loser), which
ranked words by how often they appear in the Brown corpus (1960s American
text) and guessed the remaining word with the most vowels. Brown has never seen
most five-letter words, so much of the list ended up alphabetical, and a few
sorting rules put words like `angry` near the bottom. It opened with words like
`audio`, then `curia`, and averaged 4.3 guesses on a small test.

Two changes brought that to 3.4: switching to
[wordfreq](https://pypi.org/project/wordfreq/), which reflects how common words
are today, and picking the guess that best splits the remaining words instead
of the one with the most vowels.

### Tuning

After that, every change was tested in hard mode against all past answers.
Most made only small differences:

- **Weights.** A steeper frequency curve, and cutting plurals, past tenses and
  a hand-picked list of names, slang and crude words NYT never uses: 3.62 to
  3.59.
- **Opener.** `slate` beat seven other popular openers. Testing its anagrams
  showed its early greens help more than they hurt.
- **Traps.** A check for families like `_ATCH` took `hatch` from 8 guesses to
  4, but only saved a couple of games overall. A deeper search and a
  two-letter version didn't help.
- **Smaller fixes.** Counting a correct guess as solved stopped it picking
  `abray` over `array`. Entropy scoring was worse.
- **Honest tuning.** Settings are picked on half the answers and checked on
  the other half. Most late tweaks turned out to be noise.

### Past answers

The biggest gain came from past answers. NYT rarely repeats, so a past
answer keeps a fifth of its weight, and less again for each repeat. In a
simulated history with repeats at 1 game in 10, the rate since reuse started
in February 2026, that took the average from about 3.54 to 3.30.

### Other players' boards

Each row another player got says something about the answer. A first row is
a free choice, so a rare one like ⬛🟩🟩🟩🟩 says a lot and a common one hardly
anything. Later rows aren't free, since players have to guess words that fit
what they've seen, so for those the question is only whether some likely word
could show that row for a given answer. Reading later rows like first ones
held back answers like `strew`, which have few common neighbors.

"Likely" here means common in `guesses.txt`, not likely as an answer. This
used to come from the answer weights, and #1942 showed why that was wrong.
One player's second row could only have come from `tired`, `fired` or a word
like them. The answer weights put past tenses near the bottom, so the bot
decided no likely word could have made that row, and cut the real answer,
`wider`, 50 times. That happened on three rows, which dropped `wider` from
2nd to 31st. People also play odd words, like opening with `penis`, so a
later row that no likely word explains now only cuts an answer to a tenth,
not a fiftieth.

The rarer a first row, the more it says. The table shows single rows, and
the share of the 3,000 likeliest answers each one cuts to the floor (the least
a row leaves any answer, so nothing is ruled out completely):

| First row | At the floor | Likeliest answers after |
| --- | --- | --- |
| ⬛⬛⬛⬛⬛ | 0% | puppy, mommy, fuzzy, buddy |
| ⬛⬛🟨⬛⬛ | 0% | audio, pizza, vodka, avoid |
| 🟩⬛⬛⬛⬛ | 15% | apply, alpha, sunny, swing |
| ⬛⬛⬛⬛🟩 | 26% | judge, queue, dodge, wedge |
| 🟨🟨🟨⬛⬛ | 69% | radio, diary, rapid, drain |
| 🟩🟩🟩⬛⬛ | 87% | stand, staff, stamp, stack |
| ⬛🟩🟩🟩🟩 | 94% | plate, brain, grain, drain |

- **All grey** rules nothing out but favors rare letters. Most openers show
  all grey against `fluff`, so it keeps 68% of its weight. `crane` and
  `stole` share letters with most openers and keep 5–7%.
- **Where a yellow sits** matters, because popular openers put certain letters
  in certain spots. A yellow in the middle suggests an A elsewhere, as in
  `audio`. A yellow at the start suggests `_atch` words. `hatch` keeps 93% of
  its weight after 🟨⬛⬛⬛⬛ but only 16% after ⬛⬛🟨⬛⬛.
- **Greens** fix letters in place, so they cut the most. ⬛🟩🟩🟩🟩 leaves
  mostly words like `_rate` and `_rain`.

### Testing with made-up players

The bench has no real boards, so it generates them from two kinds of player.
Both pick words by how common they are (`guesses.txt`), plurals and past
tenses included:

- **Tidy** players open with a popular opener about a third of the time, in
  the proportions people really use them, and otherwise with a random common
  word. After that they guess one of the likeliest words that still fits.
- **Messy** players open the same way, then guess any common word that still
  fits, picked at random.

With `--odd 0.1`, a tenth of either kind's guesses are any word at all that
fits, for the people who open with something silly. Until #1942, the made-up
players guessed from the answer weights, so they almost never played `tired`
either, and the bench couldn't see the problem.

Tidy and messy came out about the same, so the numbers below use messy players
with odd guesses.

`--off-list 0.15` swaps that share of replayed answers for plausible words
off Wordle's original list, drawn from where real ones like `yodel` sit. Past
answers came mostly from that list by construction, so this is how to check
a setting still holds up if NYT strays from it. Opening
with `slate` every time, each board helps a little less than the last, but
every board helps. Two boards give about two thirds of the gain of six.

### Picking the opener

Once the boards have changed the weights, `slate` is no longer always the
best start. With boards, the opener is worked out like any other guess, but
`slate` stays unless the pick leaves a fifth less to find. On made-up boards
this gives a clear gain:

| `BOARD_TRUST` | Opener | 0 boards | 2 boards | 4 boards | 6 boards |
| --- | --- | --- | --- | --- | --- |
| 0 | Always `slate` | 3.31 | 3.31 | 3.31 | 3.31 |
| 1 (Default configuration) | Worked out | 3.31 | 2.59 | 2.21 | 1.94 |
| 1 | Always `slate` | 3.31 | 2.68 | 2.48 | 2.40 |
| 2 | Worked out | 3.31 | 2.54 | 2.21 | 2.01 |
| 2 | Always `slate` | 3.31 | 2.71 | 2.56 | 2.47 |

    python -m modules.wordle.tools.bench --used 0.2 --games 100 --players 2 --messy --odd 0.1 --start auto --set BOARD_TRUST=2

That's hard mode, 100 games each, replaying a made-up history so past answers
count as used. `BOARD_TRUST` is how hard each row counts. At 0 the boards are
ignored, so every column plays like the first. At 2, results change by a few
hundredths either way, which is within the noise of 100 games. These players
are messier than the ones the table used before #1942, so every column with
boards is a little higher than it was; the old numbers flattered the bot.

### On real games

Made-up boards narrow things down more cleanly than real ones. On 15 real
days from our server, mostly five or six boards each, the bot averaged 2.47
guesses against 2.60 opening with `slate`. The effect varies by day: `copse`
(#1924, six boards) went from 5 guesses to 2, and `strew` (#1937, five boards)
rose from 5,450th likeliest to 50th. On #1942, six boards took `wider` from
2nd to 31st before the fix above, and to 8th after it.

## What past answers look like

This compares 1,928 games so far (1,903 different words) with the weights in
`data/words.txt`.

### How common they are

Frequency predicts answers well. The top 1,000 words by weight include 46% of
all answers, and 87% of those 1,000 have been answers:

| Top words by weight | Share of answers they cover | Share of them that were answers |
| --- | --- | --- |
| 500 | 24% | 92% |
| 1,000 | 46% | 87% |
| 2,000 | 79% | 75% |
| 3,000 | 93% | 59% |
| 5,000 | 99% | 38% |

### What NYT avoids

Only one answer, `fried`, is a plural or past tense, and none are names,
places, brands, slang or crude words. These are still allowed as guesses, but
weighted as unlikely answers (`data/unlikely.txt`).

### Letters by position

The biggest gaps between answers and what the weights expect:

| Letter | Answers | Weights expect |
| --- | --- | --- |
| S last | 1.5% | 4.9% |
| A second | 12.5% | 15.0% |
| A last | 2.7% | 4.9% |
| O third | 11.3% | 9.5% |

Correcting for these barely helps on held-back answers, so the weights don't
include it.

## Settings

These notes come from bench runs and are a quick reference, not a study.
Solver settings are at the top of `solver.py` and `boards.py`. To try a
different value, run `python -m modules.wordle.tools.bench --set NAME=VALUE`.

### Solver

| Setting | Default | What it does | Range | What we saw |
| --- | --- | --- | --- | --- |
| `OPENER` | slate | First guess | Any word | Best of 8 popular openers. Its anagrams with more yellows (steal, tales) did worse, and least tied it |
| `hard` | True | Greens stay in place and yellows must be reused | — | What we play and tune for |
| `vowels` | False | wordle-loser's most-vowels rule | — | Worse, about 4.1 against 3.8–3.9 |
| `GUESS_POOL` | 3000 | How many common words can be played as probes | 1000–5000 | No difference |
| `SAMPLE` | 300 | How many of the likeliest answers a guess is judged against | 150–600 | No difference. Lower is faster |
| `SURE` | 0.5 | Guess the likeliest word once it holds this share of the weight left | 0.3–1 | No difference |
| `LOSS_COST` | 20 | How strongly it avoids trap families like _ATCH. 0 turns it off | 10–50 | Flat from 10 to 30. 500 lost fewer games but cost 0.05 guesses |
| `SHORTLIST` | 100 | How many of the best guesses get the trap check | 50–200 | Not tested |
| `NEAR_TIE` | 0.1 | Guesses within this much of the best count as tied | 0–0.2 | Nothing held up on both halves |
| `MIN_GAIN` | 0.1 | How much likelier a tied word must be to win the tie | 0.05–0.3 | No difference |
| `SOLVED_LEAVES_NOTHING` | True | A correct guess counts as nothing left to find | — | Stops picks like abray over array |
| `ENTROPY` | False | Judge splits by information gained instead | — | Worse by 0.06–0.12 |
| `BOARD_TRUST` | 1.0 | How much other players' boards count. 0 ignores them. In `boards.py` | 0.5–2 | At 6 boards, 1.94 against 3.31 without boards. 2 was no better (2.01) |
| `FLOOR` | 0.02 | The least share of the best fit a first row leaves any answer, so nothing is ruled out. In `boards.py` | 0.02–0.1 | 0.1 was worse: 2.09 against 1.94 at 6 boards |
| `LATER_FLOOR` | 0.1 | The same for later rows, which no likely word explaining only means an odd guess. In `boards.py` | 0.02–0.3 | Held-back seed, 6 boards: 2.00 against 2.09 for 0.02 when a fifth of guesses are odd, and level with none. 0.3 no better |
| `PLAIN_GUESSES` | True | Judge what players guess by `guesses.txt`, not the answer weights. In `boards.py` | — | Held-back seed: 2.01 against 2.31 at 6 boards, 2.56 against 2.74 at 3 |
| `OPENER_SWITCH` | 0.2 | With boards, the opener is worked out like any guess, but slate stays unless the pick leaves this much less to find | — | 15 real days: 2.47 guesses against slate's 2.60. Simulated boards overstate the gain (1.94 against 2.40 at 6 boards). `PICK_OPENER` in `games.py` turns it off |
| `USED_FACTOR` | 0.2 | Share of its weight a past answer keeps | 0.1–0.5 | Biggest gain: 3.30 against 3.54 uncut. Heavier cuts fall behind as repeats rise |
| `LIST_TRUST` | 0 | How much to trust `answers.txt`. Words off it keep 1 minus this of their weight; 0 is off | 0–0.99 | Blind, held-back seed: 0.99 gave 3.29 against 3.38 at today's off-list rate, level at 15% off-list (`--off-list 0.15`), 0.1 worse at 30%. Off until it's clear NYT keeps drawing from the list; 473 words were left in October 2026 |

### Answer weights

The answer weights are built by `python -m modules.wordle.tools.sort_words`
and tuned with `python -m modules.wordle.tools.tune_weights`. The same run
writes `guesses.txt` with the penalty left off.

| Setting | Default | What it does | Range | What we saw |
| --- | --- | --- | --- | --- |
| `MIDPOINT` | 3.0 | How common a word must be to count as a 50/50 answer | 2.75–3.0 | Lower fit the tuning half but not the held-back half |
| `STEEPNESS` | 3.0 | How fast weight drops below the midpoint | 3–4 | 2 fit worse |
| `UNLIKELY_PENALTY` | 0.002 | Weight cut for plurals, past tenses and `data/unlikely.txt` | 0.002–0.01 | Lower fits better; kept above 0 so they stay possible |
