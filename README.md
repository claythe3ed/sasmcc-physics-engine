![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/version-6.0.0-blue)
![CI](https://github.com/claythe3ed/sasmcc-physics-engine/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Layers](https://img.shields.io/badge/Physics%20Layers-6-brightgreen)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![GitHub stars](https://img.shields.io/github/stars/claythe3ed/sasmcc-physics-engine?style=social)

# S-ASM-CC Physics Engine

![S-ASM-CC Logo](logo.jpeg)

### Superconductive ASM Memorial Computational Core

*Dedicated to Ali Sayed Muhammad Osman (1957-2022). Every equation. Every simulation. Every result.*

---

## What This Is

A complete six-layer first-principles physics engine for selective cancer cell destruction via low-intensity pulsed ultrasound. Cancer cells contain a higher fraction of free intracellular water, which lowers their acoustic cavitation threshold and makes them selectively vulnerable to a precisely tuned ultrasound pulse that leaves surrounding healthy tissue unharmed.

Built entirely on a mobile Android device (Termux) in a conflict-affected environment. Not a clinical device. A computational physics engine (not experimentally validated) ready for wet-lab validation.

---

## The Physics

The cavitation threshold depends primarily on intracellular cytoplasmic viscosity, which depends on free water content. Cancer cells consistently show higher free water fractions than normal cells, creating a therapeutic window. Bubble collapse generates a plasma core above 7000 K releasing hydroxyl radicals 87 times above the lethal threshold within 7.5 nm of the collapse site. Non-thermal, non-invasive, selective based on cell biology not spatial targeting.

---

## Physics Engine

| Layer | Physics | Status | Key Result |
|-------|---------|--------|------------|
| 1 | Acoustic field | Complete | c=1529 m/s, window 0.5-3 MHz |
| 2 | Bubble nucleation | Cross-checked | Window=146 kPa, selectivity 83.5x vs 88.38x (earlier S-ASM-CC v5.1 model; internal, not experimental) |
| 3 | Water sonolysis ROS | Complete | 87590 OH per collapse, 87.6x lethal threshold |
| 4 | Blackbody emission | Complete | peak=396 nm at 7321 K, matches PPIX 405 nm |
| 5 | Multi-bubble cloud | Complete | dT=0.106 K non-thermal, 2 cm tumor in 1.4 s |
| 6 | Pan-cancer targeting | Complete | 9 types, 0.52-0.74 MPa, 450-2000 kHz |

---

## Cancer Database (All 9 Types Now Complete with f_water)

| Type | E_cancer | E_normal | f_water | Selectivity | Status |
|------|----------|----------|---------|-------------|--------|
| OSCC | 2.50 kPa | 5.00 kPa | 0.780 | 73.9x | REFERENCE |
| Breast IDC | 0.60 kPa | 2.00 kPa | 0.790 | 965.5x | STIFFNESS_SUPPORTED |
| Prostate | 1.05 kPa | 3.50 kPa | 0.760 | 1352.3x | STIFFNESS_SUPPORTED |
| Lung NSCLC | 0.75 kPa | 2.50 kPa | 0.820 | 55.5x | STIFFNESS_SUPPORTED |
| Colorectal | 2.61 kPa | 8.70 kPa | 0.800 | 269.5x | PREDICTED |
| Pancreatic | 1.80 kPa | 6.00 kPa | 0.740 | 310.8x | STIFFNESS_SUPPORTED |
| Glioblastoma | 0.169 kPa | 0.061 kPa | 0.850 | 26.1x | STIFFNESS_SUPPORTED* |
| Cervical | 0.44 kPa | 1.26 kPa | 0.800 | 95.7x | STIFFNESS_SUPPORTED |
| Liver HCC | 1.20 kPa | 3.00 kPa | 0.780 | 190.4x | PREDICTED |

*GBM stiffer than normal brain (Ciesluk 2020 PMC7547774). Stiffness opposes selectivity; water fraction carries selectivity alone.

Water fractions (cancer and normal) are assumed values, not measurements (see paper, Section 2.8). ADC-based estimates were explored but are not used by the engine. QENS measurements are pending.

---

## Quick Start

    pip install numpy scipy matplotlib
    python3 02_simulations/targeting/impedance_model.py
    python3 02_simulations/bubble_dynamics/rp_solver.py
    python3 02_simulations/water_physics/nucleation_threshold.py
    python3 02_simulations/water_physics/sonolysis_ros.py
    pytest -q

---

## Key Numbers

- Optimal OSCC: 0.640 MPa at 450 kHz
- Therapeutic window: 146.1 kPa
- Selectivity: 83.5x (Layer 2 model) vs 88.4x (earlier S-ASM-CC v5.1 model; internal cross-check, not experimental; 5.5% difference)
- Collapse temperature: 7321 K air / 16173 K Argon
- OH radicals per collapse: 87590 (87.6x lethal)
- Temperature rise: 0.106 K non-thermal confirmed
- Treatment time 2 cm tumor: 1.4 s multi-bubble

---

## References

- Mittelstein et al. (2020). APL 116, 013701. doi:10.1063/1.5128627
- Cross et al. (2007). Nature Nanotechnology 2, 780.
- Martins et al. (2019). Scientific Reports 9, 8704. PMC6591518
- Heyden & Ortiz (2016). JMPS 92, 164.
- Diagnostics 2022. DOI: 10.3390/diagnostics12020332 (Breast IDC f_water)
- OncoTargets 2022. DOI: 10.2147/OTT.S366723 (Prostate f_water)
- Cancers 2020. DOI: 10.3390/cancers12061493 (Lung NSCLC f_water)
- Insights Imaging 2022. DOI: 10.1007/s13244-022-01268-7 (Pancreatic f_water)
- Insights Imaging 2019. DOI: 10.1186/s13244-019-0719-6 (Glioblastoma f_water)
- PLOS ONE 2023. DOI: 10.1371/journal.pone.0285786 (Cervical f_water)
- PLOS ONE 2016. DOI: 10.1371/journal.pone.0153944 (Colorectal f_water)
- Meta-analysis (HCC f_water)

---

## Companion Repo

sasmcc-platform: https://github.com/claythe3ed/sasmcc-platform
Contains S-ASM-CC v5.3 treatment engine and complete preclinical hardware blueprint.

---

## License

MIT. See LICENSE.

*Dedicated to Ali Sayed Muhammad Osman (1957-2022).*

## Status note (14 October 2026)

All results in this repository are computational model outputs. None has been compared with an experimental selectivity measurement. The OSCC value of 88.38x comes from an earlier version of this model (S-ASM-CC v5.1), so the 83.5x vs 88.4x comparison is an internal consistency check. Free-water fractions are assumed values, not measurements; ADC-based estimates were explored but are not used by the engine. Evidence tiers in the paper are REFERENCE (code label VALIDATED, OSCC only), STIFFNESS-SUPPORTED (code label STIFFNESS_VALIDATED) and PREDICTED.
