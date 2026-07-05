S-ASM-CC Physics Engine
Superconductive ASM Memorial Computational Core

Dedicated to Ali Sayed Muhammad Osman (1957-2022). Every equation. Every simulation. Every result.


What This Is

A complete six-layer first-principles physics engine for selective cancer cell destruction via low-intensity pulsed ultrasound. Cancer cells contain a higher fraction of free intracellular water, which lowers their acoustic cavitation threshold and makes them selectively vulnerable to a precisely tuned ultrasound pulse that leaves surrounding healthy tissue unharmed.

Built entirely on a mobile Android device (Termux) in a conflict-affected environment. Not a clinical device. A validated computational physics engine ready for wet-lab validation.


The Physics

The cavitation threshold depends primarily on intracellular cytoplasmic viscosity, which depends on free water content. Cancer cells consistently show higher free water fractions than normal cells, creating a therapeutic window. Bubble collapse generates a plasma core above 7000 K releasing hydroxyl radicals 87 times above the lethal threshold within 7.5 nm of the collapse site. Non-thermal, non-invasive, selective based on cell biology not spatial targeting.


Physics Engine

Layer 1: Acoustic field
  Status: Complete
  Key Result: c=1529 m/s, window 0.5-3 MHz

Layer 2: Bubble nucleation
  Status: Validated
  Key Result: Window=146 kPa, selectivity 88x vs 88.38x literature

Layer 3: Water sonolysis ROS
  Status: Complete
  Key Result: 87590 OH per collapse, 87.6x lethal threshold

Layer 4: Blackbody emission
  Status: Complete
  Key Result: peak=396 nm at 7321 K, matches PPIX 405 nm

Layer 5: Multi-bubble cloud
  Status: Complete
  Key Result: dT=0.106 K non-thermal, 2 cm tumor in 1.4 s

Layer 6: Pan-cancer targeting
  Status: Complete
  Key Result: 9 types, 0.52-0.74 MPa, 450-2000 kHz


Cancer Database (All 9 Types Now Complete with f_water)

Type: OSCC
  E_cancer: 2.50 kPa
  E_normal: 5.00 kPa
  f_water: 0.780
  Selectivity: 73.9x
  Status: VALIDATED

Type: Breast IDC
  E_cancer: 0.60 kPa
  E_normal: 2.00 kPa
  f_water: 0.732
  Selectivity: 965.5x
  Status: STIFFNESS_VALIDATED

Type: Prostate
  E_cancer: 1.05 kPa
  E_normal: 3.50 kPa
  f_water: 0.742
  Selectivity: 1352.3x
  Status: STIFFNESS_VALIDATED

Type: Lung NSCLC
  E_cancer: 0.75 kPa
  E_normal: 2.50 kPa
  f_water: 0.812
  Selectivity: 55.5x
  Status: STIFFNESS_VALIDATED

Type: Colorectal
  E_cancer: 2.61 kPa
  E_normal: 8.70 kPa
  f_water: 0.728
  Selectivity: 269.5x
  Status: STIFFNESS_VALIDATED

Type: Pancreatic
  E_cancer: 1.80 kPa
  E_normal: 6.00 kPa
  f_water: 0.728
  Selectivity: 310.8x
  Status: STIFFNESS_VALIDATED

Type: Glioblastoma
  E_cancer: 0.169 kPa
  E_normal: 0.061 kPa
  f_water: 0.752
  Selectivity: 26.1x
  Status: STIFFNESS_VALIDATED
  Note: GBM stiffer than normal brain (Ciesluk 2020 PMC7547774). Stiffness opposes selectivity; water fraction carries selectivity alone.

Type: Cervical
  E_cancer: 0.44 kPa
  E_normal: 1.26 kPa
  f_water: 0.729
  Selectivity: 95.7x
  Status: STIFFNESS_VALIDATED

Type: Liver HCC
  E_cancer: 1.20 kPa
  E_normal: 3.00 kPa
  f_water: 0.787
  Selectivity: 190.4x
  Status: STIFFNESS_VALIDATED

f_water values derived from ADC literature for 8 types (plus OSCC validated). All 9 types now have complete biophysical parameters. QENS validation pending via Martins/Bordallo collaboration.


Quick Start

  pip install numpy scipy matplotlib
  python3 02_simulations/targeting/impedance_model.py
  python3 02_simulations/bubble_dynamics/rp_solver.py
  python3 02_simulations/water_physics/nucleation_threshold.py
  python3 02_simulations/water_physics/sonolysis_ros.py
  pytest -q


Key Numbers

  Optimal OSCC: 0.640 MPa at 450 kHz
  Therapeutic window: 146.1 kPa
  Selectivity: 83.5x model vs 88.4x experimental (5.5% error)
  Collapse temperature: 7321 K air / 16173 K Argon
  OH radicals per collapse: 87590 (87.6x lethal)
  Temperature rise: 0.106 K non-thermal confirmed
  Treatment time for 2 cm tumor: 1.4 s multi-bubble


References

  Mittelstein et al. (2020). APL 116, 013701. doi:10.1063/1.5128627
  Cross et al. (2007). Nature Nanotechnology 2, 780.
  Martins et al. (2019). Scientific Reports 9, 8704. PMC6591518
  Heyden & Ortiz (2016). JMPS 92, 164.
  Diagnostics 2022. DOI: 10.3390/diagnostics12020332 (Breast IDC f_water)
  OncoTargets 2022. DOI: 10.2147/OTT.S366723 (Prostate f_water)
  Cancers 2020. DOI: 10.3390/cancers12061493 (Lung NSCLC f_water)
  Insights Imaging 2022. DOI: 10.1007/s13244-022-01268-7 (Pancreatic f_water)
  Insights Imaging 2019. DOI: 10.1186/s13244-019-0719-6 (Glioblastoma f_water)
  PLOS ONE 2023. DOI: 10.1371/journal.pone.0285786 (Cervical f_water)
  PLOS ONE 2016. DOI: 10.1371/journal.pone.0153944 (Colorectal f_water)
  Meta-analysis (HCC f_water)


Companion Repo

  sasmcc-platform: https://github.com/claythe3ed/sasmcc-platform
  Contains S-ASM-CC v5.3 treatment engine and complete preclinical hardware blueprint.


License

  MIT. See LICENSE.

  Dedicated to Ali Sayed Muhammad Osman (1957-2022).