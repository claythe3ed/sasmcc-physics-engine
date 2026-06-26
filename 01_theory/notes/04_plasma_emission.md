# Plasma Emission & Light Generation

## Status
PENDING simulation — theory documented 2026-05-26

## The Central Question

Bubble collapses → plasma forms → light emitted.
Which mechanism produces the photons?
Answer: all three below contribute, proportions debated.

## Mechanism 1: Bremsstrahlung (Braking Radiation)

Free electron accelerates near ion → emits photon.

Power emitted per unit volume:
  P_brem = C_b · n_e · n_i · Z² · sqrt(T)

  C_b  = 1.69×10⁻³² W·m³·K^(-1/2)
  n_e  = electron number density [m⁻³]
  n_i  = ion number density [m⁻³]
  Z    = ion charge number
  T    = electron temperature [K]

Spectral distribution:
  P(ν) ∝ n_e·n_i · exp(−hν/k_BT) / sqrt(T)

Key feature: exponential cutoff at hν = k_BT
  At T = 20,000 K: cutoff at λ = 720 nm (visible red)
  At T = 50,000 K: cutoff at λ = 290 nm (UV)
  → Explains why SL peaks in UV

## Mechanism 2: Blackbody Radiation

Hot dense plasma radiates as near-ideal thermal emitter.

Planck distribution:
  B(λ,T) = (2hc²/λ⁵) · 1/(exp(hc/λk_BT) − 1)

Peak wavelength (Wien's law):
  λ_max = 2.898×10⁻³ / T  [meters]

  At T = 10,000 K: λ_max = 290 nm  (UV)
  At T = 20,000 K: λ_max = 145 nm  (deep UV)
  At T = 50,000 K: λ_max =  58 nm  (extreme UV)

SL observed peak: ~200-300 nm → consistent with 10,000-15,000 K

Total power (Stefan-Boltzmann):
  P = σ·A·T⁴
  σ = 5.67×10⁻⁸ W·m⁻²·K⁻⁴
  A = 4πR² at collapse ≈ 4π(0.5×10⁻⁶)² = 3.14×10⁻¹² m²

  At T = 20,000 K:
  P = 5.67×10⁻⁸ × 3.14×10⁻¹² × (2×10⁴)⁴
    = 5.67×10⁻⁸ × 3.14×10⁻¹² × 1.6×10¹⁷
    = 28.5 W  (instantaneous peak)

  Over flash duration ~100 ps:
  E_flash = 28.5 × 100×10⁻¹² = 2.85×10⁻⁹ J
  Photons per flash ≈ E/(hc/λ) ≈ 10⁶ photons ✓

## Mechanism 3: Collisional Excitation

Noble gas atoms excited by electron collisions → radiative decay.

For argon:
  Ar + e⁻ → Ar* + e⁻  (excitation)
  Ar*     → Ar + hν    (emission at specific wavelengths)

Key Ar emission lines: 696 nm, 706 nm, 727 nm, 738 nm, 751 nm
Ar⁺ ionic lines appear above 15,000 K (Flannigan & Suslick 2005)
Detection of Ar⁺ lines = direct proof of plasma formation

## Ionization Equilibrium: Saha Equation

Degree of ionization at temperature T:

  n_e·n_i / n_a = (2·Z_i/Z_a) · (2πm_e·k_BT/h²)^(3/2) · exp(−E_i/k_BT)

  n_e  = electron density
  n_i  = ion density
  n_a  = neutral atom density
  E_i  = ionization energy
  Z_i  = ionic partition function
  Z_a  = atomic partition function

For argon (E_i = 15.76 eV):
  At T = 10,000 K: ionization fraction ~ 10⁻⁴  (weakly ionized)
  At T = 20,000 K: ionization fraction ~ 0.1   (partially ionized)
  At T = 50,000 K: ionization fraction ~ 0.99  (fully ionized)

## Flash Duration

SL flash duration: 35 ps – few ns (source dependent)
Shorter than acoustic period by factor of ~10⁶

Why so short:
  1. Bubble reaches minimum radius for only picoseconds
  2. At minimum: plasma forms, emits, reexpands
  3. Reexpansion rapidly cools plasma below emission threshold
  4. Light stops

Time-resolved measurements (Gompf et al. 1997):
  FWHM ≈ 100–300 ps for SBSL in water+Ar

## Quantum SL — New Frontier (2022)

Rezaee et al. (arXiv:2203.11337) — INDEXED in 03_papers/frontier/

Measured photon statistics of SBSL flashes:
  Classical thermal source: Poissonian statistics (g²(0) = 1)
  Quantum (non-classical) : sub-Poissonian (g²(0) < 1)

Result: g²(0) < 1 detected in SBSL
Implication: emission has quantum optical component
Not fully explained by thermal plasma alone
Active research area 2022–present

## Emission Spectrum Summary

  Region          λ (nm)    Mechanism
  ─────────────────────────────────────
  Extreme UV      50–120    Blackbody >50,000 K
  Vacuum UV      120–200    Blackbody 20,000–50,000 K
  Near UV        200–380    Bremsstrahlung + Blackbody  ← SL peak
  Visible        380–700    Blackbody tail + Ar lines
  Near IR        700–1000   Ar emission lines

Water absorbs below ~180 nm so observed SL peaks around 200-300 nm.

## SDT Relevance

SL emission spectrum overlaps sonosensitizer absorption:
  Porphyrins absorb at: 400–420 nm (Soret band) + 500–650 nm (Q bands)
  TiO₂ absorbs at:      <390 nm (bandgap = 3.2 eV)
  NaNbO₃ absorbs at:    <400 nm

Sonosensitizer activation pathway:
  S + hν(SL) → S*         (electronic excitation)
  S* + O₂    → S + ¹O₂   (singlet oxygen generation)
  ¹O₂        → cell damage (oxidative stress → apoptosis)

Key design question for your tool:
  Which sonosensitizer absorption peak best matches SL spectrum?
  → Optimize driving parameters to shift SL peak toward target λ
  → Higher T → bluer spectrum → better TiO₂ activation
  → Lower T → redder spectrum → better porphyrin activation

## Connected Files

- Simulation : 02_simulations/emission/blackbody_spectrum.py   PENDING
- Simulation : 02_simulations/emission/bremsstrahlung.py       PENDING
- Previous   : 01_theory/notes/03_thermodynamics.md  ✓
- Next       : 01_theory/notes/05_stability_conditions.md
- Papers     : 2203.11337 (Rezaee 2022 — Quantum SL)
               Flannigan & Suslick 2005 (Ar⁺ plasma proof)

## References

1. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
2. Flannigan, D.J. & Suslick, K.S. (2005). Plasma formation
   and temperature measurement during single-bubble
   sonoluminescence. Nature 434, 52.
3. Rezaee et al. (2022). Observation of Nonclassical Photon
   Statistics in SBSL. arXiv:2203.11337.
4. Gompf et al. (1997). Resolving sonoluminescence pulse width
   with time-correlated single photon counting. PRL 79, 1405.
