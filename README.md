# Business Master

Business Master is an autonomous economic control system.

It continuously maintains economic hypotheses, observes external and internal evidence, chooses the next experiments, allocates local compute and platform capacity, measures real-world outcomes, and kills, mutates, graduates or scales hypotheses according to evidence.

The normal operating mode does **not** require a human to request the next task. Human intervention is treated as a scarce resource reserved for bootstrap, KYC/2FA, irreversible or high-blast-radius actions, and exceptional review.

## Core loop

```text
observe -> update world model -> generate/rank hypotheses -> allocate resources
       -> execute -> measure -> learn -> kill/mutate/graduate/scale -> repeat
```

## Engineering rule

Use deterministic code wherever the decision is deterministic. Use statistical policies where uncertainty can be quantified. Use AI only where semantic judgment, synthesis, generation, perception, or ambiguous interface interaction is actually required.

## Status

Bootstrap in progress. See the implementation branch and RFCs for the initial autonomous core.
