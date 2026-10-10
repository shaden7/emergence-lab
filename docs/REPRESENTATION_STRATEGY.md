# Representation-Neutral Research Strategy

**Status:** methodology proposal, not a verified physical result.
**Decision under review:** which model families and mathematical languages should be investigated, and how to avoid selecting the answer through the representation?

## Fundamental question

Can the empirically established laws and structures of physical reality arise from more general principles, relations, or processes? The project must not presume the answer is a graph, a field, a computational process, an information substrate, or a uniquely identifiable microscopic theory.

**Three distinct claims must never be conflated:**

1. **Encodability:** one formalism can encode states or predictions of another (often at finite resolution).
2. **Faithful and economical description:** the encoding preserves observables, symmetries, limits, relevant dynamics and resources without hiding the answer in parameters.
3. **Physical explanation:** independent principles plus the formalism derive existing observations and ideally predict discriminating new ones.

A graph with sufficiently rich labels and state data can encode many *finite* systems; this does not establish compactness, efficient computation, correct continuum limits, faithful quantum structure, or physical fundamentality. An embedding of a known 3D lattice is a measurement control, not emergent 3D spacetime. Graphs may be a useful *implementation structure* without being an ontological claim.

## Begin with operational targets, not candidate substrates

Choose the **question** first. Examples:
- What interventions can influence which later observations, and how quickly or strongly?
- Which dimension, locality, or scaling indicators remain stable under coarse-graining?
- Which symmetries and conservation properties survive changes of scale?
- Which measurable correlations distinguish classical stochastic and genuinely quantum behavior?

Record the operational test before choosing a representation. Distinguish relational adjacency from assumed physical distance, and imposed causal order from derived causal order. A simple model may be a useful estimator benchmark without being an emergence claim.

For every candidate describe:
- **Primitive entities / state space** (if meaningful).
- **Allowed changes / composition rules** (a fundamental time parameter must not be assumed without disclosure).
- **Observables and interventions** (the bridge to measurable predictions).
- **Coarse-graining / scaling procedure and controlled limit.**
- **Built-in assumptions** vs. **actually derived conclusions**.
- **Known obstructions, numerical uncertainty, computational cost, and falsifying tests**.

## Competing representation families

| Family | Native strengths | Possible hidden assumptions or blind spots |
| --- | --- | --- |
| Graphs, hypergraphs, cellular automata | Relational adjacency, local updates, causal propagation, simple computational controls | Often predefined adjacency, discrete time, classical deterministic rules; dimension and locality may be encoded |
| Continuous fields, PDEs and effective field theories | Symmetries, continuous limits, known particle/field physics | Smooth background and space/time can be primitive |
| Hilbert spaces, quantum channels, tensor networks | Interference, entanglement, quantum states and processes | Network diagrams may be calculational encodings; efficient tensor networks do not capture every state efficiently |
| Causal partial orders / event structures | Temporal/causal precedence without a given metric | Causal structure or acyclicity is already assumed; geometry reconstruction has nontrivial prerequisites |
| Operational / generalized probabilistic theories | Compare classical, quantum and hypothetical correlations with less ontological commitment | Requires specified preparations, transformations, outcomes and consistent composition; does not itself furnish gravity |
| Algebraic, categorical or other compositional formalisms | Can clarify relations between theories, symmetry and composition | Expressive syntax can conceal strong axioms; abstractness alone is not explanatory power |

These are **overlapping mathematical toolkits**, not an exhaustive or mutually exclusive catalogue. A category-theoretic description can describe graph models; tensor networks can encode quantum states; an operational framework can include both classical and quantum models.

## Hypothesis/evidence matrix (mandatory before choosing a model)

Create a short table for each scientific question with:
1. **Observable:** exact measurable or mathematically defined quantity.
2. **Reference:** analytic solution, validated model, or experiment.
3. **Candidates:** at least two substantively different descriptions *if comparison is meaningful*; otherwise explicitly document why the test only validates one representation.
4. **What is assumed:** dimensions, causal ordering, locality, unitarity, probabilities, background metric, etc.
5. **What is recovered:** only properties not inserted by construction.
6. **Null and failure cases:** an intentionally misleading representation, alternative mechanism, finite-size limit.
7. **Computational and statistical budget:** time/memory, seeds, convergence and uncertainty.
8. **Discriminator:** observation or proof condition that separates candidates; if none exists, classify them as observationally underdetermined at this resolution.

**Representation scorecard** (qualitative, never a single unsupported "best theory" score): empirical fit, prediction on held-out conditions, assumption load, preservation of symmetries, controlled limiting behavior, description length *under declared coding conventions*, stability under reparameterization, computability and simplicity of proofs. Do not count lines of Python as a universal physical simplicity measure.

## Strategy when our mathematics may be inadequate

Distinguish *new coordinates*, *new concepts* and *new axiomatic structures*:

**A. Representation search:** Given observations and candidate models, learn coordinate changes, latent variables, sufficient statistics, coarse-graining maps, and operators that make dynamics simpler and predictive. Require out-of-sample predictive quality and interpretability checks; flag noninvertible transformations and lost information.

**B. Concept invention:** Let a constrained AI propose new composite observables, invariants and operations that improve compression or expose common behavior across otherwise unlike models. Each candidate must have explicit definitions, domain/codomain or types, compositional laws, executable tests, and counterexamples.

**C. Axiomatic experimentation:** Propose small changes to structural assumptions (e.g. composition, locality, probability, causal ordering) and derive the logical consequences. Use rigorous mathematics and Lean 4 for precise theorems, when feasible. Proofs validate implications, not whether the axioms describe our world.

**D. When present descriptions fail:** Document a concrete impossibility, contradiction, expressive limitation, or persistent unexplained observation before pursuing a new formalism. A theory grammar that can describe everything but predicts nothing has not succeeded.

**E. Keep multiple equivalent languages alive:** If distinct representations predict the same operational phenomena, search for the invariant relationships or duality maps; do not arbitrarily crown either representation as the ontology. If no discriminating experiment is possible, openly report underdetermination.

Predefined symbolic-regression dictionaries already constrain discoverable laws. An expandable typed grammar and learned coordinate transformation could widen searches, but no procedure guarantees the invention of fundamentally new mathematics.

## First comparison: a small, representation-neutral protocol

**No competing experiment should disrupt the in-flight Ising calibration.** After that baseline is reliable, do a *preregistered* cross-family pilot:

- **Target:** causal influence of a controlled localized perturbation on later observables, stated operationally as a difference in measured output distributions or expectation values under intervention vs. control. No claim of Lorentz invariance.
- **Family A:** local stochastic or deterministic update model with graph connectivity. Note assumed neighborhood and clock steps.
- **Family B:** coupled continuous field / oscillator model with independently specified local dynamics. Note imposed background geometry/clock.
- **Control:** model with long-range couplings or an explicit randomized influence mechanism that should violate an expected bounded-propagation pattern.
- **Measurements:** signal support/strength versus operational separation; sensitivity to resolution, initial state, boundary conditions and parameters. State in advance which space/time notions are input.
- **Success:** transparent assumptions, correctly distinguished behaviors and a robust common observable across the families; a negative finding about comparability is an acceptable result.
- **Failure:** mistaking assumed locality or a predefined spatial metric for emergent relativity, or equating an exponentially small influence tail to a strict light cone.
- **Budget:** design-only until the Ising benchmark gate is met. Then start with small CPU-bounded runs on the shared Lightsail, with independent seeds when stochastic and a fixed wall-time limit.

Treat an emergent *spacetime* claim as a much higher bar: operational geometry, causal structure, approximated Lorentz symmetry in a controlled limit, stress-energy/gravitational consistency where relevant, and independent physical predictions. **A recovered graph dimension is not a quantum-gravity result.**

## Explicit decision gates

- **Gate 0: Method calibration.** Ising known physics, error estimates and finite-size checks. Current workstream.
- **Gate 1: Representation audit.** For the next target, record at least two alternative families and all baked-in physics. May be done as research design, without compute.
- **Gate 2: Common observable.** Demonstrate one honestly comparable property across models, with explicit negative control and fit uncertainty. Do not require that all families are representable by graphs.
- **Gate 3: Novel candidate.** Only if evidence demands: generate or discover additional variables/operations, test robustness and seek a theorem.
- **Gate 4: Physics relevance.** Literature review and experimental discriminators, beyond simulations and proofs internal to a model.

## Literature starting points (research context, not proof of our hypotheses)

- Janotta & Hinrichsen, *Generalized Probability Theories*, 2014: https://arxiv.org/abs/1402.6562
- Plávala, *General probabilistic theories: An introduction*, Physics Reports 2023: https://doi.org/10.1016/j.physrep.2023.09.001 (preprint https://arxiv.org/abs/2103.07469)
- Einstein Online, *Geometry from order: causal sets*: https://www.einstein-online.info/en/spotlight/causal_sets/
- Orús, *Tensor networks for complex quantum systems*, Nature Reviews Physics 2019: https://www.nature.com/articles/s42254-019-0086-7
- Ge & Eisert, *Area laws and efficient descriptions of quantum many-body states*, 2014: https://arxiv.org/abs/1411.2995
- Champion et al., *Data-driven discovery of coordinates and governing equations*, 2019: https://pmc.ncbi.nlm.nih.gov/articles/PMC6842598/
- Koch-Janusz & Ringel, *Mutual information, neural networks and the renormalization group*, 2018: https://www.nature.com/articles/s41567-018-0081-4

## Status

A scientific strategy proposal. No new simulations, numerical findings, formal proofs, AI math-invention machinery, or inference about the fundamental ontology of reality are claimed here.
