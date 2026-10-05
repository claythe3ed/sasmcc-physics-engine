cat > ~/sasmcc-physics-engine/MAP.md << 'EOF'
# MAP — S-ASM-CC Project Model

## L0 Essence
S-ASM-CC: A six-layer first-principles physics engine for selective
ultrasound-induced cancer cell destruction, exploiting the higher
intracellular free-water fraction in malignant cells. Dedicated to
Ali Sayed Muhammad Osman (1957–2022).

## L1 Chunks (7)
1. Acoustics — pulse generation, propagation, attenuation, targeting
2. Bubble Dynamics — Rayleigh-Plesset, Keller-Miksis, Van der Waals floor
3. Water Physics — free-water fraction, sonolysis, ROS generation
4. Selectivity — cancer vs normal cavitation thresholds, Blake equation
5. Cancer Database — 9 types, stiffness, f_water, evidence tiers
6. Simulation — six-layer engine, validation hooks, pan-cancer targeting
7. Papers — manuscript, claims, evidence, submission status

## L2 Per Chunk
For each: responsibility / entities / interface / data / deps /
invariants / failure / pointers

## Flows
Pulse → Nucleation → Sonolysis → Emission → Cell Death
Input → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5 → Layer 6 → Output

## Invariants
- Selectivity ratio > threshold for each cancer type
- Free-water fraction drives cavitation threshold (60% contribution)
- Healthy tissue spared at optimal driving pressure
- All three validation hooks must pass

## Decisions
Why ultrasound: non-invasive, tunable, low-cost.
Why low-intensity pulsed: avoids thermal damage, uses mechanochemical pathway.
Why free-water as discriminator: biophysical difference confirmed by QENS/AFM.
Why open-source: Sadaqah Jariyah, accessible to any researcher worldwide.

## Failure Modes
No nucleation (pressure below threshold).
Healthy damage (pressure above normal-cell threshold).
Param drift (f_water values diverge from QENS validation).
Hook failure (threshold agreement > 5%, direction check fails).

## Pointers
01_theory/           — theoretical foundations
02_simulations/      — six-layer engine code
03_papers/           — reference papers, index.json
papers/              — submitted manuscript (full + blind)
env/                 — environment setup
knowledge_graph_data.json — session state, 44 nodes
future_dev_plans.md  — three future research directions
editorial_contacts.txt — journal contact information (local use)
correspondence/      — submission log (gitignored, local only)
README.md            — project overview
CITATION.cff         — citation metadata
LICENSE              — MIT

## Open Questions
1. QENS validation of ADC-derived water fractions for 8 cancer types
   (pending: Martins/Bordallo, University of Copenhagen; Mamontov, ORNL)
2. Peer review outcome at EAJBCS (submitted 4 Sept 2026, ID 2608)
3. Wet-lab Phase 0: selective cell kill confirmation in monolayer culture
4. Whether 50-fold predicted selectivity spread reflects biology or
   input uncertainty (resolvable only with direct QENS measurements)

## Milestones
- 2026-06-23: Knowledge graph v17, all hooks pass
- 2026-09-04: Manuscript submitted to EAJBCS (ID 2608)
- 2026-09-11: Full + blind Word files accepted by Managing Editor
- 2026-09-11T18:29:06: Milestone node added to knowledge graph

## Repositories
Physics Engine: https://github.com/claythe3ed/sasmcc-physics-engine
Hardware Platform: https://github.com/claythe3ed/sasmcc-platform

*Dedicated to Ali Sayed Muhammad Osman (1957–2022).*
EOF

echo "✅ MAP.md replaced successfully."
