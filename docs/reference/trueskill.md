# TrueSkill — trueskill 0.4.5 documentation

# TrueSkill[¶](#trueskill "Permalink to this headline")

the video game rating system

## What’s TrueSkill?[¶](#what-s-trueskill "Permalink to this headline")

[TrueSkill](http://research.microsoft.com/en-us/projects/trueskill) is a rating system among game players. It was developed by [Microsoft Research](http://research.microsoft.com/) and has been used on [Xbox LIVE](http://www.xbox.com/live) for ranking and matchmaking service. This system quantifies players’ **TRUE** skill points by the Bayesian inference algorithm. It also works well with any type of match rule including N:N team game or free-for-all.

This project is a Python package which implements the TrueSkill rating system:

from trueskill import Rating, quality\_1vs1, rate\_1vs1
alice, bob \= Rating(25), Rating(30)  \# assign Alice and Bob's ratings
if quality\_1vs1(alice, bob) < 0.50:
    print('This match seems to be not so fair')
alice, bob \= rate\_1vs1(alice, bob)  \# update the ratings after the match

## Installing[¶](#installing "Permalink to this headline")

The package is available in [PyPI](http://pypi.python.org/pypi/trueskill):

$ pip install trueskill

## Learning[¶](#learning "Permalink to this headline")

### Rating, the model for skill[¶](#rating-the-model-for-skill "Permalink to this headline")

In TrueSkill, rating is a Gaussian distribution which starts from N(25,2532)N(25,2532). μμ is an average skill of player, and σσ is a confidence of the guessed rating. A real skill of player is between μ±2σμ±2σ with 95% confidence.

\>>> from trueskill import Rating
\>>> Rating()  \# use the default mu and sigma
trueskill.Rating(mu=25.000, sigma=8.333)

If some player’s rating is higher ββ than another player’s, the player may have about a 76% (specifically Φ(12√)Φ(12)) chance to beat the other player. The default value of ββ is 256256.

Ratings will approach real skills through few times of the TrueSkill’s Bayesian inference algorithm. How many matches TrueSkill needs to estimate real skills? It depends on the game rule. See the below table:

 

Rule

Matches

16P free-for-all

3

8P free-for-all

3

4P free-for-all

5

2P free-for-all

12

2:2:2:2

10

4:4:4:4

20

4:4

46

8:8

91

### Head-to-head (1 vs. 1) match rule[¶](#head-to-head-1-vs-1-match-rule "Permalink to this headline")

Most competition games follows 1:1 match rule. If your game does, just use `_1vs1` shortcuts containing [`rate_1vs1()`](#trueskill.rate_1vs1 "trueskill.rate_1vs1") and [`quality_1vs1()`](#trueskill.quality_1vs1 "trueskill.quality_1vs1"). These are very easy to use.

First of all, we need 2 [`Rating`](#trueskill.Rating "trueskill.Rating") objects:

\>>> r1 \= Rating()  \# 1P's skill
\>>> r2 \= Rating()  \# 2P's skill

Then we can guess match quality which is equivalent with draw probability of this match using [`quality_1vs1()`](#trueskill.quality_1vs1 "trueskill.quality_1vs1"):

\>>> print('{:.1%} chance to draw'.format(quality\_1vs1(r1, r2)))
44.7% chance to draw

After the game, TrueSkill recalculates their ratings by the game result. For example, if 1P beat 2P:

\>>> new\_r1, new\_r2 \= rate\_1vs1(r1, r2)
\>>> print(new\_r1)
trueskill.Rating(mu=29.396, sigma=7.171)
\>>> print(new\_r2)
trueskill.Rating(mu=20.604, sigma=7.171)

Mu value follows player’s win/draw/lose records. Higher value means higher game skill. And sigma value follows the number of games. Lower value means many game plays and higher rating confidence.

So 1P, a winner’s skill grew up from 25 to 29.396 but 2P, a loser’s skill shrank to 20.604. And both sigma values became narrow about same magnitude.

Of course, you can also handle a tie game with `drawn=True`:

\>>> new\_r1, new\_r2 \= rate\_1vs1(r1, r2, drawn\=True)
\>>> print(new\_r1)
trueskill.Rating(mu=25.000, sigma=6.458)
\>>> print(new\_r2)
trueskill.Rating(mu=25.000, sigma=6.458)

### Other match rules[¶](#other-match-rules "Permalink to this headline")

There are many other match rules such as N:N team match, N:N:N multiple team match, N:M unbalanced match, free-for-all (Player vs. All), and so on. Mostly other rating systems cannot work with them but TrueSkill does. TrueSkill accepts any types of matches.

We should arrange ratings into a group by their team:

\>>> r1 \= Rating()  \# 1P's skill
\>>> r2 \= Rating()  \# 2P's skill
\>>> r3 \= Rating()  \# 3P's skill
\>>> t1 \= \[r1\]  \# Team A contains just 1P
\>>> t2 \= \[r2, r3\]  \# Team B contains 2P and 3P

Then we can calculate the match quality and rate them:

\>>> print('{:.1%} chance to draw'.format(quality(\[t1, t2\])))
13.5% chance to draw
\>>> (new\_r1,), (new\_r2, new\_r3) \= rate(\[t1, t2\], ranks\=\[0, 1\])
\>>> print(new\_r1)
trueskill.Rating(mu=33.731, sigma=7.317)
\>>> print(new\_r2)
trueskill.Rating(mu=16.269, sigma=7.317)
\>>> print(new\_r3)
trueskill.Rating(mu=16.269, sigma=7.317)

If you want to describe other game results, set the `ranks` argument like the below examples:

-   A drawn game – `ranks=[0, 0]`
-   Team B won not team A – `ranks=[1, 0]` (Lower rank is better)

Additionally, here are varied patterns of rating groups. All variables which start with `r` are [`Rating`](#trueskill.Rating "trueskill.Rating") objects:

-   N:N team match – `[(r1, r2, r3), (r4, r5, r6)]`
-   N:N:N multiple team match – `[(r1, r2), (r3, r4), (r5, r6)]`
-   N:M unbalanced match – `[(r1,), (r2, r3, r4)]`
-   Free-for-all – `[(r1,), (r2,), (r3,), (r4,)]`

### Partial play[¶](#partial-play "Permalink to this headline")

Let’s assume that there are 2 teams which each has 2 players. The game was for a hour but the one of players on the first team entered the game at 30 minutes later.

If some player wasn’t present for the entire duration of the game, use the concept of “partial play” by `weights` parameter. The above situation can be described by the following weights:

-   1P on team A – 1.0 = Full time
-   2P on team A – 0.5 = 30603060 minutes

-   3P on team B – 1.0
-   4P on team B – 1.0

As a code with a 2-dimensional list:

\# set each weights to 1, 0.5, 1, 1.
rate(\[(r1, r2), (r3, r4)\], weights\=\[(1, 0.5), (1, 1)\])
quality(\[(r1, r2), (r3, r4)\], weights\=\[(1, 0.5), (1, 1)\])

Or with a dictionary. Each keys are a tuple of `(team_index, index_or_key_of_rating)`:

\# set a weight of 2nd player in 1st team to 0.5, otherwise leave as 1.
rate(\[(r1, r2), (r3, r4)\], weights\={(0, 1): 0.5})
\# set a weight of Carol in 2nd team to 0.5, otherwise leave as 1.
rate(\[{'alice': r1, 'bob': r2}, {'carol': r3}\], weights\={(1, 'carol'): 0.5})

### Backends[¶](#backends "Permalink to this headline")

The TrueSkill algorithm uses ΦΦ, [the cumulative distribution function](http://en.wikipedia.org/wiki/Cumulative_distribution_function); ϕϕ, [the probability density function](http://en.wikipedia.org/wiki/Probability_density_function); and Φ−1Φ−1, the inverse cumulative distribution function. But standard mathematics library doesn’t provide the functions. Therefore this package implements them.

Meanwhile, there are third-party libraries which implement the functions. You may want to use another implementation because that’s more expert. Then set `backend` option of [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") to the backend you chose:

\>>> TrueSkill().cdf  \# internal implementation
<function cdf at ...>
\>>> TrueSkill(backend\='mpmath').cdf  \# mpmath.ncdf
<bound method MPContext.f\_wrapped of <mpmath.ctx\_mp.MPContext object at ...>>

Here’s the list of the available backends:

-   `None` – the internal implementation. (Default)
-   “mpmath” – requires [mpmath](https://code.google.com/p/mpmath) installed.
-   “scipy” – requires [scipy](http://www.scipy.org/) installed.

Note

When winners have too lower rating than losers, [`TrueSkill.rate()`](#trueskill.TrueSkill.rate "trueskill.TrueSkill.rate") will raise `FloatingPointError`. In this case, you need higher floating-point precision. The mpmath library offers flexible floating-point precision. You can solve the problem with mpmath as a backend and higher precision setting.

### Win probability[¶](#win-probability "Permalink to this headline")

TrueSkill provides a function ([`quality()`](#trueskill.quality "trueskill.quality")) to calculate a draw probability between arbitrary ratings. But there’s no function for a win probability.

Anyway, if you need to calculate a win probability between only 2 teams, this code snippet will help you:

import itertools
import math

def win\_probability(team1, team2):
    delta\_mu \= sum(r.mu for r in team1) \- sum(r.mu for r in team2)
    sum\_sigma \= sum(r.sigma \*\* 2 for r in itertools.chain(team1, team2))
    size \= len(team1) + len(team2)
    denom \= math.sqrt(size \* (BETA \* BETA) + sum\_sigma)
    ts \= trueskill.global\_env()
    return ts.cdf(delta\_mu / denom)

This snippet is written by [Juho Snellman](https://www.snellman.net/) in [issue #1](https://github.com/sublee/trueskill/issues/1#issuecomment-149762508).

## API[¶](#api "Permalink to this headline")

### TrueSkill objects[¶](#trueskill-objects "Permalink to this headline")

_class_ `trueskill.``Rating`(_mu=None_, _sigma=None_)[¶](#trueskill.Rating "Permalink to this definition")

Represents a player’s skill as Gaussian distrubution.

The default mu and sigma value follows the global environment’s settings. If you don’t want to use the global, use [`TrueSkill.create_rating()`](#trueskill.TrueSkill.create_rating "trueskill.TrueSkill.create_rating") to create the rating object.

 

Parameters:

-   **mu** – the mean.
-   **sigma** – the standard deviation.

`mu`[¶](#trueskill.Rating.mu "Permalink to this definition")

A property which returns the mean.

`sigma`[¶](#trueskill.Rating.sigma "Permalink to this definition")

A property which returns the the square root of the variance.

_class_ `trueskill.``TrueSkill`(_mu=25.0_, _sigma=8.333333333333334_, _beta=4.166666666666667_, _tau=0.08333333333333334_, _draw\_probability=0.1_, _backend=None_)[¶](#trueskill.TrueSkill "Permalink to this definition")

Implements a TrueSkill environment. An environment could have customized constants. Every games have not same design and may need to customize TrueSkill constants.

For example, 60% of matches in your game have finished as draw then you should set `draw_probability` to 0.60:

env \= TrueSkill(draw\_probability\=0.60)

For more details of the constants, see [The Math Behind TrueSkill](http://bit.ly/the-math-behind-trueskill) by Jeff Moser.

 

Parameters:

-   **mu** – the initial mean of ratings.
-   **sigma** – the initial standard deviation of ratings. The recommended value is a third of `mu`.
-   **beta** – the distance which guarantees about 76% chance of winning. The recommended value is a half of `sigma`.
-   **tau** – the dynamic factor which restrains a fixation of rating. The recommended value is `sigma` per cent.
-   **draw\_probability** – the draw probability between two teams. It can be a `float` or function which returns a `float` by the given two rating (team performance) arguments and the beta value. If it is a `float`, the game has fixed draw probability. Otherwise, the draw probability will be decided dynamically per each match.
-   **backend** – the name of a backend which implements cdf, pdf, ppf. See [`trueskill.backends`](#module-trueskill.backends "trueskill.backends") for more details. Defaults to `None`.

`create_rating`(_mu=None_, _sigma=None_)[¶](#trueskill.TrueSkill.create_rating "Permalink to this definition")

Initializes new [`Rating`](#trueskill.Rating "trueskill.Rating") object, but it fixes default mu and sigma to the environment’s.

\>>> env \= TrueSkill(mu\=0, sigma\=1)
\>>> env.create\_rating()
trueskill.Rating(mu=0.000, sigma=1.000)

`expose`(_rating_)[¶](#trueskill.TrueSkill.expose "Permalink to this definition")

Returns the value of the rating exposure. It starts from 0 and converges to the mean. Use this as a sort key in a leaderboard:

leaderboard \= sorted(ratings, key\=env.expose, reverse\=True)

New in version 0.4.

`make_as_global`()[¶](#trueskill.TrueSkill.make_as_global "Permalink to this definition")

Registers the environment as the global environment.

\>>> env \= TrueSkill(mu\=50)
\>>> Rating()
trueskill.Rating(mu=25.000, sigma=8.333)
\>>> env.make\_as\_global()  
trueskill.TrueSkill(mu=50.000, ...)
\>>> Rating()
trueskill.Rating(mu=50.000, sigma=8.333)

But if you need just one environment, [`setup()`](#trueskill.setup "trueskill.setup") is better to use.

`quality`(_rating\_groups_, _weights=None_)[¶](#trueskill.TrueSkill.quality "Permalink to this definition")

Calculates the match quality of the given rating groups. A result is the draw probability in the association:

env \= TrueSkill()
if env.quality(\[team1, team2, team3\]) < 0.50:
    print('This match seems to be not so fair')

 

Parameters:

-   **rating\_groups** – a list of tuples or dictionaries containing [`Rating`](#trueskill.Rating "trueskill.Rating") objects.
-   **weights** – weights of each players for “partial play”.

New in version 0.2.

`rate`(_rating\_groups_, _ranks=None_, _weights=None_, _min\_delta=0.0001_)[¶](#trueskill.TrueSkill.rate "Permalink to this definition")

Recalculates ratings by the ranking table:

env \= TrueSkill()  \# uses default settings
\# create ratings
r1 \= env.create\_rating(42.222)
r2 \= env.create\_rating(89.999)
\# calculate new ratings
rating\_groups \= \[(r1,), (r2,)\]
rated\_rating\_groups \= env.rate(rating\_groups, ranks\=\[0, 1\])
\# save new ratings
(r1,), (r2,) \= rated\_rating\_groups

`rating_groups` is a list of rating tuples or dictionaries that represents each team of the match. You will get a result as same structure as this argument. Rating dictionaries for this may be useful to choose specific player’s new rating:

\# load players from the database
p1 \= load\_player\_from\_database('Arpad Emrick Elo')
p2 \= load\_player\_from\_database('Mark Glickman')
p3 \= load\_player\_from\_database('Heungsub Lee')
\# calculate new ratings
rating\_groups \= \[{p1: p1.rating, p2: p2.rating}, {p3: p3.rating}\]
rated\_rating\_groups \= env.rate(rating\_groups, ranks\=\[0, 1\])
\# save new ratings
for player in \[p1, p2, p3\]:
    player.rating \= rated\_rating\_groups\[player.team\]\[player\]

 

Parameters:

-   **rating\_groups** – a list of tuples or dictionaries containing [`Rating`](#trueskill.Rating "trueskill.Rating") objects.
-   **ranks** – a ranking table. By default, it is same as the order of the `rating_groups`.
-   **weights** – weights of each players for “partial play”.
-   **min\_delta** – each loop checks a delta of changes and the loop will stop if the delta is less then this argument.

Returns:

recalculated ratings same structure as `rating_groups`.

Raises:

`FloatingPointError` occurs when winners have too lower rating than losers. higher floating-point precision couls solve this error. set the backend to “mpmath”.

New in version 0.2.

### Default values[¶](#default-values "Permalink to this headline")

`trueskill.``MU` _= 25.0_[¶](#trueskill.MU "Permalink to this definition")

Default initial mean of ratings.

`trueskill.``SIGMA` _= 8.333333333333334_[¶](#trueskill.SIGMA "Permalink to this definition")

Default initial standard deviation of ratings.

`trueskill.``BETA` _= 4.166666666666667_[¶](#trueskill.BETA "Permalink to this definition")

Default distance that guarantees about 76% chance of winning.

`trueskill.``TAU` _= 0.08333333333333334_[¶](#trueskill.TAU "Permalink to this definition")

Default dynamic factor.

`trueskill.``DRAW_PROBABILITY` _= 0.1_[¶](#trueskill.DRAW_PROBABILITY "Permalink to this definition")

Default draw probability of the game.

### Head-to-head shortcuts[¶](#head-to-head-shortcuts "Permalink to this headline")

`trueskill.``rate_1vs1`(_rating1_, _rating2_, _drawn=False_, _min\_delta=0.0001_, _env=None_)[¶](#trueskill.rate_1vs1 "Permalink to this definition")

A shortcut to rate just 2 players in a head-to-head match:

alice, bob \= Rating(25), Rating(30)
alice, bob \= rate\_1vs1(alice, bob)
alice, bob \= rate\_1vs1(alice, bob, drawn\=True)

 

Parameters:

-   **rating1** – the winner’s rating if they didn’t draw.
-   **rating2** – the loser’s rating if they didn’t draw.
-   **drawn** – if the players drew, set this to `True`. Defaults to `False`.
-   **min\_delta** – will be passed to [`rate()`](#trueskill.rate "trueskill.rate").
-   **env** – the [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object. Defaults to the global environment.

Returns:

a tuple containing recalculated 2 ratings.

New in version 0.2.

`trueskill.``quality_1vs1`(_rating1_, _rating2_, _env=None_)[¶](#trueskill.quality_1vs1 "Permalink to this definition")

A shortcut to calculate the match quality between just 2 players in a head-to-head match:

if quality\_1vs1(alice, bob) < 0.50:
    print('This match seems to be not so fair')

 

Parameters:

-   **rating1** – the rating.
-   **rating2** – the another rating.
-   **env** – the [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object. Defaults to the global environment.

New in version 0.2.

### Functions for the global environment[¶](#functions-for-the-global-environment "Permalink to this headline")

`trueskill.``global_env`()[¶](#trueskill.global_env "Permalink to this definition")

Gets the [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object which is the global environment.

`trueskill.``setup`(_mu=25.0_, _sigma=8.333333333333334_, _beta=4.166666666666667_, _tau=0.08333333333333334_, _draw\_probability=0.1_, _backend=None_, _env=None_)[¶](#trueskill.setup "Permalink to this definition")

Setups the global environment.

 

Parameters:

**env** – the specific [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object to be the global environment. It is optional.

\>>> Rating()
trueskill.Rating(mu=25.000, sigma=8.333)
\>>> setup(mu\=50)  
trueskill.TrueSkill(mu=50.000, ...)
\>>> Rating()
trueskill.Rating(mu=50.000, sigma=8.333)

`trueskill.``rate`(_rating\_groups_, _ranks=None_, _weights=None_, _min\_delta=0.0001_)[¶](#trueskill.rate "Permalink to this definition")

A proxy function for [`TrueSkill.rate()`](#trueskill.TrueSkill.rate "trueskill.TrueSkill.rate") of the global environment.

New in version 0.2.

`trueskill.``quality`(_rating\_groups_, _weights=None_)[¶](#trueskill.quality "Permalink to this definition")

A proxy function for [`TrueSkill.quality()`](#trueskill.TrueSkill.quality "trueskill.TrueSkill.quality") of the global environment.

New in version 0.2.

`trueskill.``expose`(_rating_)[¶](#trueskill.expose "Permalink to this definition")

A proxy function for [`TrueSkill.expose()`](#trueskill.TrueSkill.expose "trueskill.TrueSkill.expose") of the global environment.

New in version 0.4.

### Draw probability helpers[¶](#draw-probability-helpers "Permalink to this headline")

`trueskill.``calc_draw_probability`(_draw\_margin_, _size_, _env=None_)[¶](#trueskill.calc_draw_probability "Permalink to this definition")

Calculates a draw-probability from the given `draw_margin`.

 

Parameters:

-   **draw\_margin** – the draw-margin.
-   **size** – the number of players in two comparing teams.
-   **env** – the [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object. Defaults to the global environment.

`trueskill.``calc_draw_margin`(_draw\_probability_, _size_, _env=None_)[¶](#trueskill.calc_draw_margin "Permalink to this definition")

Calculates a draw-margin from the given `draw_probability`.

 

Parameters:

-   **draw\_probability** – the draw-probability.
-   **size** – the number of players in two comparing teams.
-   **env** – the [`TrueSkill`](#trueskill.TrueSkill "trueskill.TrueSkill") object. Defaults to the global environment.

### Mathematical statistics backends[¶](#module-trueskill.backends "Permalink to this headline")

`trueskill.backends.``choose_backend`(_backend_)[¶](#trueskill.backends.choose_backend "Permalink to this definition")

Returns a tuple containing cdf, pdf, ppf from the chosen backend.

\>>> cdf, pdf, ppf \= choose\_backend(None)
\>>> cdf(\-10)
7.619853263532764e-24
\>>> cdf, pdf, ppf \= choose\_backend('mpmath')
\>>> cdf(\-10)
mpf('7.6198530241605255e-24')

New in version 0.3.

`trueskill.backends.``available_backends`()[¶](#trueskill.backends.available_backends "Permalink to this definition")

Detects list of available backends. All of defined backends are `None` – internal implementation, “mpmath”, “scipy”.

You can check if the backend is available in the current environment with this function:

if 'mpmath' in available\_backends():
    \# mpmath can be used in the current environment
    setup(backend\='mpmath')

New in version 0.3.

## Changelog[¶](#changelog "Permalink to this headline")

### Version 0.4.5[¶](#version-0-4-5 "Permalink to this headline")

Released on Sep 7 2018.

Started to support Python 3.6 and 3.7. But dropped support of Python 2.5, 2.6, 3.1, 3.2, and 3.3. Thanks to [Hugo](https://github.com/hugovk).

### Version 0.4.4[¶](#version-0-4-4 "Permalink to this headline")

Released on Dec 31 2015.

Fixed documentation error. See [issue #11](https://github.com/sublee/trueskill/issues/11). Thanks to [Russel Simmons](https://github.com/rsimmons).

### Version 0.4.3[¶](#version-0-4-3 "Permalink to this headline")

Released on Sep 4 2014.

Fixed ordering bug on weights argument as a dict. This was reported at [issue #9](https://github.com/sublee/trueskill/issues/9).

### Version 0.4.2[¶](#version-0-4-2 "Permalink to this headline")

Released on Jun 13 2014.

Updated only meta code such as `setup.py`.

### Version 0.4.1[¶](#version-0-4-1 "Permalink to this headline")

Released on Jun 6 2013.

Deprecated `dynamic_draw_probability()`.

### Version 0.4[¶](#version-0-4 "Permalink to this headline")

Released on Mar 25 2013.

-   Added dynamic draw probability.
-   Replaced `Rating.exposure()` with `TrueSkill.expose()`. Because the TrueSkill settings have to adjust a fomula to calculate an exposure.
-   Deprecated head-to-head shortcut methods in `TrueSkill`. The top-level shortcut functions are still alive.

### Version 0.3.1[¶](#version-0-3-1 "Permalink to this headline")

Released on Mar 6 2013.

Changed to raise `FloatingPointError` instead of `ValueError` (math domain error) for a problem similar to [issue #5](https://github.com/sublee/trueskill/issues/5) but with more extreme input.

### Version 0.3[¶](#version-0-3 "Permalink to this headline")

Released on Mar 5 2013.

`TrueSkill` got a new option `backend` to choose cdf, pdf, ppf implementation.

When winners have too lower rating than losers, `TrueSkill.rate()` will raise `FloatingPointError` if the backend is `None` or “scipy”. But from this version, you can avoid the problem with “mpmath” backend. This was reported at [issue #5](https://github.com/sublee/trueskill/issues/5).

### Version 0.2.1[¶](#version-0-2-1 "Permalink to this headline")

Released on Dec 6 2012.

Fixed a printing bug on `TrueSkill.quality()`.

### Version 0.2[¶](#version-0-2 "Permalink to this headline")

Released on Nov 30 2012.

-   Added “Partial play” implementation.
-   Worked well in many Python versions, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3 and many interpreters, CPython, [Jython](http://jython.org/), [PyPy](http://pypy.org/).
-   Supported that using dictionaries as a `rating_group` to choose specific player’s rating simply.
-   Added shorcut functions for 2 players individual match, the most usage: `rate_1vs1()` and `quality_1vs1()`,
-   Renamed `TrueSkill.transform_ratings()` to `TrueSkill.rate()`.
-   Renamed `TrueSkill.match_quality()` to `TrueSkill.quality()`.

### Version 0.1.4[¶](#version-0-1-4 "Permalink to this headline")

Released on Oct 5 2012.

Fixed `ZeroDivisionError` issue. For more detail, see [issue#3](https://github.com/sublee/trueskill/issues/3). Thanks to [Yunwon Jeong](https://github.com/youknowone) and [Nikos Kokolakis](https://github.com/konikos).

### Version 0.1.3[¶](#version-0-1-3 "Permalink to this headline")

Released on Mar 10 2012.

Improved the match quality performance.

### Version 0.1.1[¶](#version-0-1-1 "Permalink to this headline")

Released on Jan 12 2012.

Fixed an error in “A” matrix of the match quality algorithm.

### Version 0.1[¶](#version-0-1 "Permalink to this headline")

First public preview release.

## Further more[¶](#further-more "Permalink to this headline")

There’s the list for users. To subscribe the list, just send a mail to [trueskill@librelist.com](mailto:trueskill%40librelist.com).

If you want to more details of the TrueSkill algorithm, see also:

-   [TrueSkill: A Bayesian Skill Rating System](http://research.microsoft.com/apps/pubs/default.aspx?id=67956) by Herbrich, Ralf and Graepel, Thore
-   [TrueSkill Calculator](http://atom.research.microsoft.com/trueskill/rankcalculator.aspx) by Microsoft Research
-   [Computing Your Skill](http://bit.ly/computing-your-skill) by Jeff Moser
-   [The Math Behind TrueSkill](http://bit.ly/the-math-behind-trueskill) by Jeff Moser

## Licensing and Author[¶](#licensing-and-author "Permalink to this headline")

This TrueSkill package is opened under the [BSD](http://en.wikipedia.org/wiki/BSD_licenses) license but the [TrueSkill™](http://research.microsoft.com/en-us/projects/trueskill) brand is not. Microsoft permits only Xbox Live games or non-commercial projects to use TrueSkill™. If your project is commercial, you should find another rating system. See [LICENSE](https://github.com/sublee/trueskill/blob/master/LICENSE) for the details.

I’m [Heungsub Lee](http://subl.ee/), a game developer. Any regarding questions or patches are welcomed.