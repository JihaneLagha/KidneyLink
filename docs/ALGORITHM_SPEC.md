# KidneyLink — Algorithm Specification

## Research source

Maiti, A. and Dey, P. (2022).
Parameterized Algorithms for Kidney Exchange.
IJCAI 2022, pages 405-411.
DOI: 10.24963/ijcai.2022/58

Official paper:
https://www.ijcai.org/proceedings/2022/0058.pdf

## Selected algorithm

Randomized Color-Coding-Based FPT Algorithm,
parameterized by target number of patients t.

## Formal input

- Directed compatibility graph G = (V, A).
- Altruistic donor set B.
- Maximum path length lp.
- Maximum cycle length lc.
- Target number of patients t.

## Formal output

YES if a collection of vertex-disjoint feasible
cycles and altruistic-donor paths covers at least
t non-altruistic vertices.

Otherwise NO.

## Algorithm stages

1. Handle lp >= t and lc >= t using the
   deterministic long-path/long-cycle checks
   described in the paper.

2. Otherwise reduce:
   lp = min(lp, t-1)
   lc = min(lc, t-1)

3. Randomly assign each vertex one of 3t colors.

4. Define f(C', i) to test whether a valid
   colorful cycle or altruistic path covers
   exactly i non-altruistic vertices.

5. Define D(C, t') as whether disjoint colorful
   cycles and altruistic paths cover exactly
   t' non-altruistic vertices using colors C.

6. Use the recurrence:

   D(C,t') =
       OR over nonempty C' subset of C
       and 1 <= i <= t' of:

       D(C minus C', t'-i) AND f(C',i)

7. Base cases:

   D(C,0) = TRUE
   D(empty,t') = FALSE when t' > 0

8. Accept if any D(S,t') is TRUE
   for t <= t' <= 2t.

9. Repeat independent random colorings
   to amplify success probability.

## Theoretical guarantees

- Number of colors: 3t.
- Probability of a good coloring: at least e^(-3t).
- One-coloring running time: O*(2^O(t)).
- Constant success probability requires
  O(e^(3t)) independent repetitions.

## Restrictions

- Cycles must respect lc.
- Paths must start at altruistic donors.
- Paths must respect lp.
- Selected structures must be vertex-disjoint.
- Altruistic donors are not counted as patients.
- Self-loops are forbidden.
