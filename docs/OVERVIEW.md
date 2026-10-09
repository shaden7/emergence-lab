# Emergence Lab — Scientific Overview

## Research vision

**Can the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—arise from simpler underlying principles, relations, or processes?**

Emergence Lab is an open, reproducible computational research project. The long-term ambition is to contribute to foundational physics and understanding *why* observed physical laws take their particular form. We do **not** presuppose that the substrate is discrete, computational, informational, or even uniquely identifiable.

The ambition is deliberately larger than conventional microscopic-to-macroscopic phenomena. Our first benchmarks in statistical physics are training and validation grounds for research methods, not answers to quantum gravity.

## Research stance

The starting point is often a well-established **macroscopic property**, not an arbitrary microscopic rule. We seek to determine which underlying assumptions are:
- **Sufficient:** guarantee an observable under stated conditions.
- **Necessary:** cannot be removed without losing the observable (within a well-defined model class).
- **Universal:** shared by apparently different models that yield the same large-scale behavior.
- **Discriminating:** produce observable predictions that distinguish candidate models.

The inverse problem is typically nonunique: many substrates yield the same emergent laws. An elegant model is not automatically a description of nature.

## Main scientific questions

1. **Space and dimension:** Under which relational structures does a robust effective dimension and metric emerge?
2. **Time and causality:** Which local update rules support coherent causal order, bounded signal propagation, and potentially Lorentz symmetry?
3. **Fields and particles:** Can persistent excitations and effective field descriptions arise without postulating particles as primitive objects?
4. **Gravity and geometry:** Are there mathematically controlled limits yielding gravitational dynamics? Distinguish merely reproducing geometry from deriving Einstein equations.
5. **Universality:** Which large-scale laws depend only on general properties of an underlying substrate rather than its microscopic details?

These are exploratory questions, not claims of feasibility or predictions of discovery.

## Method: validated discovery pipeline

1. Define an observable and an operational test before model search.
2. Identify known analytic results and competing baseline models.
3. Specify a constrained class of candidate models and a computation budget.
4. Run seeded experiments with replicate variation, controls, finite-size checks, and appropriate uncertainty estimates.
5. Discard numerical artifacts; evaluate sensitivity to parameters and implementation choices.
6. Formulate precise mathematical statements; prove suitable statements using analytic mathematics and/or Lean 4.
7. Compare robust mathematical findings to established physics, literature, and where possible independent empirical data.
8. Record negative results, ambiguity, limitations, and the next discriminating experiment.

AI may propose hypotheses, experimental designs and analyses, but is **not** the final arbiter of mathematical truth or empirical validity. Formal verification establishes consequences of axioms, not that those axioms describe nature.

## Scientific evidence levels

- **Definition or assumption:** stipulation in a model.
- **Hypothesis:** plausible and explicitly falsifiable conjecture.
- **Numerical observation:** computational result with parameters and uncertainty; not a theorem.
- **Mathematical theorem:** precisely stated and proven proposition, with stated axioms and scope.
- **Empirical support:** independently tested correspondence to physical measurements.
- **Speculation:** suggestive but currently untested connection.

Never promote a result between these levels implicitly.

## Research path

### Phase 0 — Calibration
Reproduce known emergent behavior, starting with the 2D Ising model; establish error bars, finite-size scaling, and controls. This validates our instruments, not a new theory.

### Phase 1 — Geometry and causality
Compare graph and local-dynamics families against predeclared metrics: effective dimension, locality, propagation bounds, coarse-graining stability. Include counterexamples and null models.

### Phase 2 — Structural principles
Seek invariant conditions and universality classes; investigate necessary/sufficient assumptions, candidate analytical derivations and Lean formalizations.

### Phase 3 — Foundational candidates
Only when foundations warrant it, investigate correspondence to relativistic / quantum behavior and existing foundational approaches. Reproducing light cones or graph curvature alone does not establish general relativity.

### Phase 4 — Contact with observation
Identify genuine novel, discriminating predictions or rigorous limits on what can be inferred; compare to empirical constraints. A complete theory of reality is not a scheduled deliverable.

## Practical system

- GitHub is the canonical record of code, decisions, state and experiment metadata.
- Python / NumPy are the initial simulation stack; Lean 4 may verify sharply defined mathematical statements.
- Shared AWS Lightsail (4 GB RAM, 2 vCPUs) executes bounded experiments; no GPU or local LLM is assumed.
- Existing ChatGPT and Claude subscriptions can assist with interactive research and implementation. Unattended paid API calls require separate authorization and budget.
- The computational pipeline should run reproducibly without an LLM.

## Documentation map

- [README](../README.md): quick start, code, execution.
- [AGENTS.md](../AGENTS.md): binding rules for automated researchers.
- [RESEARCH_STATE.md](RESEARCH_STATE.md): verified current status, results, blockers, and next experiment.
- [research-plan.md](research-plan.md): near-term research plan.
- [deployment.md](deployment.md): operational constraints.

## What success looks like

Near-term success is a **reproducible, falsifiable result**—including a well-supported negative result—that clarifies which microscopic assumptions govern an emergent phenomenon. Larger success is a rigorous general principle, new model class, or prediction that survives independent scrutiny. Neither a compelling visualization nor agreement with a single benchmark constitutes a fundamental discovery.
