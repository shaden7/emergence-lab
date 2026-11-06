# Exact finite-N D=2 ordering-fraction reference

**Status:** an elementary mathematical reference and exact-arithmetic code, not
new physics, a simulated calibration result or a CS0 run authorization. The
proof below is informal mathematics, not Lean/formal verification. No CS0 gate,
replicate count or seed policy is changed.

## Assumptions and reduction to a permutation

Assume N>=2 independent, continuously uniform points in the given flat 2D
diamond |t|+|x|<=1/2. In light-cone coordinates u=t+x, v=t-x this is the square
[-1/2,1/2]^2, because max(|u|,|v|)=|t|+|x|. The Jacobian is constant, so u and v
are independent uniform coordinates. Coordinate ties have probability zero.

Sort the points by increasing u. The ranks of their v coordinates form a uniform
permutation pi of 1,...,N. A pair i<j is comparable precisely when pi(i)<pi(j).
If I counts inversions pi(i)>pi(j) and C=N(N-1)/2, the related-pair count is
therefore **R=C-I**, and the ordering fraction is r=R/C. Relabeling by the first
of two independent uniform linear orders gives the same construction for the
random 2-order model.

This reduction is about the ideal continuous probability model. A finite-bit
PRNG and floating-point relation implementation are not a mathematical source
of independent continuous reals. Their agreement with this reference remains an
implementation-validation question; no exact-distribution claim about a PRNG is
made here.

## Exact integer distribution

Let M(n,k) count permutations of n elements with k inversions. Insert the largest
element n into a permutation of n-1 elements. Its position creates each possible
additional inversion count j=0,...,n-1 exactly once. Hence, with zero values
outside the preceding support,

\[
M(n,k)=\sum_{j=0}^{n-1}M(n-1,k-j),\qquad M(1,0)=1.
\]

Consequently P(R=k)=M(N,C-k)/N!. The associated generating polynomial is
product_{j=1}^N(1+q+...+q^{j-1}), the standard permutation-inversion or Mahonian
distribution. This is established enumerative combinatorics, not a new result.
For an author-hosted reference see Gessel and Stanley, *Algebraic Enumeration*,
section 3, printed page 5 (PDF page 5), inversion-table construction and product
formula: https://math.mit.edu/~rstan/pubs/pubfiles/79.pdf . The recurrence above
is also justified directly by insertion, independently of that reference.

The implementation uses an integer sliding window for the recurrence and
returns immutable integer weights or exact Fraction probabilities. It caps
distribution tables at N=32: O(N^3) integer operations and O(N^2) stored integers,
with no factorial permutation enumeration in production. Closed-form moments
do not construct a table and support any integer N>=2.

## Mean and covariance proof of the variance

Write I=sum_{i<j}X_ij, where X_ij is the inversion indicator. Each is Bernoulli
with probability 1/2 and variance 1/4. Thus E[I]=C/2 and **E[r]=1/2**.

Indicators whose pairs share no index are independent: among the 24 equally
likely relative orders of four distinct ranks, the four joint orientation
combinations each have probability 1/4. For a triple i<j<k, enumeration of its six equiprobable rank
orders gives:

| Indicator pair | Joint inversion probability | Covariance |
| --- | --- | --- |
| X_ij, X_ik | 1/3 | +1/12 |
| X_ij, X_jk | 1/6 | -1/12 |
| X_ik, X_jk | 1/3 | +1/12 |

Their covariance sum is 1/12. Every pair of distinct indicators sharing an index
belongs to exactly one triple. The off-diagonal covariance terms occur twice
in the variance of the sum. Therefore

\[
\operatorname{Var}(I)=\frac{\binom N2}{4}
  +2\binom N3\frac1{12}
  =\frac{N(N-1)(2N+5)}{72}.
\]

Because R=C-I and r=R/C,

\[
\boxed{\operatorname{Var}(r)=\frac{2N+5}{18N(N-1)}}.
\]

For m independent realizations, Var(mean r)=Var(r)/m. This gives an independent
finite-N variance benchmark for D=2; it does not make the estimated-variance
t statistic exactly Student-t, establish family-wise coverage, or extend to
D=3,4. No claim about the nonlinear dimension inverse or its bias follows
without a separate calculation.

## An exact sparse-occupancy selection warning

Only one permutation has zero comparable pairs. Hence, in this same ideal
fixed-N model, P(R=0)=1/N!. Dropping those OUT_OF_RANGE realizations changes
the ordering-fraction mean to

\[
 E[r\mid R>0]=\frac{1}{2(1-1/N!)}.
\]

For N=2, half the samples are antichains (r=0, no finite MM estimate); the
remaining half are chains (r=1, d_MM=1). Reporting only finite estimates would
therefore report dimension 1 for a control whose input dimension is 2. This is
an exact finite-occupancy/selection counterexample, not an observed CS1 result
or a claim about the nonlinear inverse at general N. It motivates reporting
occupancy and excluded cases rather than silently filtering them.

The assumptions matter: these are i.i.d. points inside a fixed diamond without
mandatory interval endpoints. A later CS1 sub-interval design that includes or
conditions on related endpoints may have a different finite-N law and must establish
its own null reference. Do not transfer this formula to it automatically.

## Verification and limits

Tests compare the recurrence with direct inversion enumeration over all
permutations for N=2,...,7, check N=2 and N=3 by hand, and verify exact rational
normalization, symmetry and moments through N=32. A six-permutation triple check
independently verifies the signs and values in the covariance table. These are
finite arithmetic checks supporting the implementation; the general statements
rest on the arguments above, not on enumerating selected N.

The production module imports neither the causal-set producer nor NumPy/SciPy
and draws no randomness. No gated seed, study grid, deployment or physical
observation is involved. CS0 still requires its reviewed execution envelope and
separate entropy-pinned authorization.
