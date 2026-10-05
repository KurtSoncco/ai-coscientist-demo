# Literature: the original sources

Three 17th-century works, all in the public domain. The discovery stages
(1 to 3) never see this folder. It is used only in Stage 4, after the reveal,
so the write-up can set the blind result against what was claimed at the time.

Quotations below are copied from the public-domain editions linked under each
entry. Where no public-domain English text was available, the claim is
paraphrased and marked as such. Check any quotation against its source before
reusing it.

## [G1610] Galileo, *Sidereus Nuncius* (1610)

Galileo Galilei. *Sidereus Nuncius*. Venice, 1610. English: *The Sidereal
Messenger of Galileo Galilei*, translated by Edward Stafford Carlos. London:
Rivingtons, 1880.
Text: <https://www.gutenberg.org/ebooks/46036> ·
Scan: <https://archive.org/details/siderealmessenge80gali>

What it claims: Jupiter has four satellites, and the ones closer to it go
round faster. No formula is given.

> Moreover, it may be detected that the revolutions of the satellites which
> describe the smallest circles round Jupiter are the most rapid, for the
> satellites nearest to Jupiter are often to be seen in the east, when the day
> before they have appeared in the west, and contrariwise. Also the satellite
> moving in the greatest orbit seems to me, after carefully weighing the
> occasions of its returning to positions previously noticed, to have a
> periodic time of half a month.

Testable against our data: in every group, `y` increases with `x1`. Galileo's
"half a month" for the outermost satellite can be compared with Callisto's
period in `data/orbits.csv` (16.689 days).

## [K1619] Kepler, *Harmonices Mundi* (1619)

Johannes Kepler. *Harmonices Mundi libri V*. Linz: Johannes Plancus for
Gottfried Tampach, 1619. Book V, chapter 3.
Scan (Latin): <https://archive.org/details/ioanniskepplerih00kepl>

What it claims (paraphrase; the English translations are still in copyright):
the ratio between the periodic times of any two planets is exactly the
sesquialterate ratio, that is the 3/2 power, of the ratio of their mean
distances from the Sun. Kepler states this for the planets of the Sun only.
The central body does not appear in the law.

Testable against our data: this is hypothesis **H2** with `p = 3/2`. It
should hold inside one group and fail across groups.

## [N1687] Newton, *Principia*, Book III (1687)

Isaac Newton. *Philosophiæ Naturalis Principia Mathematica*. London, 1687.
English: *The Mathematical Principles of Natural Philosophy*, translated by
Andrew Motte (1729); first American edition, New York: Daniel Adee, 1846.
Text: <https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_(1846)/BookIII-Phaenomena>

What it claims: the same 3/2 rule holds separately around the Sun, around
Jupiter and around Saturn. Phænomenon I states it for the satellites of
Jupiter; II and IV read:

> PHÆNOMENON II. That the circumsaturnal planets, by radii drawn to Saturn's
> centre, describe areas proportional to the times of description; and that
> their periodic times, the fixed stars being at rest, are in the
> sesquiplicate proportion of their distances from its centre.

> PHÆNOMENON IV. That the fixed stars being at rest, the periodic times of the
> five primary planets, and (whether of the sun, about the earth, or) of the
> earth about the sun, are in the sesquiplicate proportion of their mean
> distances from the sun. This proportion, first observed by Kepler, is now
> received by all astronomers

Where the central body enters (paraphrase of Book III, Proposition VIII and
its corollaries,
<https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_(1846)/BookIII-Prop1>):
Newton uses the periods and distances of bodies circling the Sun, Jupiter,
Saturn and the Earth to compare the quantities of matter in those four central
bodies. In modern notation that is the mass term in `T = 2π √(a³ / GM)`.

Testable against our data: this is hypothesis **H4**, `p = 3/2` and
`q = −1/2`, with one constant shared by every group.

## What these sources could not know

- The constant G was not measured until Cavendish's experiment (1798).
  Stage 3 estimates it only because `data/orbits.csv` uses modern masses.
- Uranus (1781), Neptune (1846) and all of their moons, and the moons of
  Mars (1877), were unknown. Newton had the Sun, Jupiter, Saturn and the
  Earth: four central bodies against our seven.
