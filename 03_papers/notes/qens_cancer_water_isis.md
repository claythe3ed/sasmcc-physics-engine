# QENS Cancer Water Dynamics — ISIS Neutron Source

## Metadata
- **Source**  : ISIS Neutron and Muon Source (OSIRIS + LET spectrometers)
- **Cells**   : MDA-MB-231 (breast), PC-3 (prostate), lung carcinoma
- **Normal**  : MCF-12A (breast), PNT-2 (prostate), healthy lung
- **Era**     : Modern/Frontier

## Key Measured Values

### Bulk-like water diffusion coefficients
  Cancer cells (untreated): D = 1.0–1.3 × 10⁻⁹ m²/s
  Pure water:               D = 2.3 × 10⁻⁹ m²/s
  Treated (cisplatin):      D drops to 0.19 × 10⁻⁹ m²/s

### Water populations
  Cancer cells:  larger fraction of BULK-LIKE (mobile) water
  Normal cells:  larger variety — more confined water
  Elastic signal: larger in cancer → more mobile water molecules

### Tissue ranking (mobility increase normal→malignant)
  1. Lung carcinoma      (highest increase)
  2. Prostate cancer
  3. Breast cancer       (lowest of three)

## Implications for Our Model

### CONFIRMS ✓
  Cancer cells have more mobile/free water
  Our f_water differential direction is correct
  OSCC water 0.78 vs normal 0.72 is consistent

### REFINES ⚠
  Two-population model needed:
    f_bulk × η_bulk + f_confined × η_confined
  Our single f_free model is an approximation
  Effective viscosity lower than our estimate

### CRITICAL CLINICAL FINDING
  Cisplatin raises bulk water residence time 1.0→7.4 ps
  → Chemotherapy RAISES cavitation threshold
  → SDT selectivity DECREASES after chemotherapy
  → Optimal protocol: SDT FIRST, then chemotherapy

## Water Fraction Estimates Updated

Based on QENS two-population model:
  Cancer bulk-like fraction ≈ 0.65-0.70 of total water
  Normal bulk-like fraction ≈ 0.50-0.55 of total water
  (remaining is confined/bound water)

  Effective free water for cavitation:
  f_eff(cancer) = 0.78 × 0.67 = 0.523
  f_eff(normal) = 0.72 × 0.52 = 0.374
  Ratio: 0.523/0.374 = 1.40× — larger than single-population model

## Relevance to SDT
  QENS confirms our targeting mechanism is real
  Two-population refinement will increase predicted selectivity
  Lung shows highest differential → good SDT candidate
  Order our model should match: Lung > Prostate > Breast

## References
  ISIS Neutron and Muon Source publications
  MDA-MB-231 vs MCF-12A breast comparison
  PC-3 vs PNT-2 prostate comparison
  Lung carcinoma studies (OSIRIS spectrometer)
