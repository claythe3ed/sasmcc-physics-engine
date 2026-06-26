# Thermodynamics of Bubble Collapse

## Status
PENDING simulation — theory documented 2026-05-26

## The Core Problem

RPE and KM treat gas as a black box — just a pressure.
Thermodynamics asks: what actually happens INSIDE the bubble?
Answer determines: temperature, light emission, ROS yield.

## Three Regimes of Bubble Dynamics

### 1. Isothermal (slow oscillations)
  T_inside = T_ambient = const
  Heat escapes as fast as compression generates it
  Polytropic index: γ_eff = 1.0
  Valid when: R·f << thermal diffusion length

### 2. Adiabatic (fast collapse — SL regime)
  No heat exchange with liquid
  All compression energy stays inside bubble
  Polytropic index: γ_eff = γ = 1.4 (air), 1.67 (noble gas)
  Valid when: collapse timescale << thermal diffusion time
  THIS IS THE SL REGIME

### 3. Polytropic (intermediate)
  γ_eff between 1.0 and γ
  Partial heat exchange
  Most of the expansion phase is polytropic

## Adiabatic Temperature Formula

  T_collapse = T₀ · (V₀/V)^(γ−1)
             = T₀ · (R₀/R)^(3(γ−1))

For air (γ=1.4):
  T_collapse = T₀ · (R₀/R)^1.2

For argon (γ=5/3):
  T_collapse = T₀ · (R₀/R)^2.0  ← hotter, why Ar used in SBSL

## Simulation Results (from rp_solver.py)

  R₀/R_min = 300.6
  T₀       = 293.15 K
  γ        = 1.4

  T_adiabatic = 293.15 × 300.6^1.2
              = 293.15 × 20.67
              = 6055 K

  With argon (γ=5/3):
  T_argon = 293.15 × 300.6^2.0
          = 293.15 × 90,360
          = 26,480,000 K  ← unphysical, real limit: ionization

## Real Temperature Limit: Ionization

Adiabatic formula breaks down at ionization:
  Air ionization:   ~10,000–15,000 K
  Argon ionization: ~15,000 K
  Above this: energy goes into ionization, not heating
  Real SBSL temperatures: 10,000–50,000 K (from spectroscopy)

## Van der Waals Correction

Ideal gas: PV = nRT
At extreme compression ideal gas fails.
VdW: (P + a/V²)(V − b) = nRT

For bubble:
  Pg = (nRT)/(V − nb) − a·n²/V²

Hard core radius h = 0.0802·R₀ means:
  Minimum volume = (4/3)π(hR₀)³
  Sets physical floor on compression

## Thermal Diffusion Length

  l_th = sqrt(κ_g / (π·f))

  κ_g = thermal diffusivity of gas
      ≈ 2×10⁻⁵ m²/s for air at STP

  At f = 26.5 kHz:
  l_th = sqrt(2×10⁻⁵ / (π × 26500))
       = sqrt(2.4×10⁻¹⁰)
       = 15.5 µm

  R₀ = 5 µm < l_th = 15.5 µm
  → Bubble is in thermal diffusion regime during expansion
  → But collapse is so fast it becomes adiabatic near minimum

## Peclet Number

  Pe = R·Ṙ / κ_g

  Pe >> 1 → adiabatic (collapse phase)
  Pe << 1 → isothermal (slow expansion)

  At collapse: R~0.5µm, Ṙ~1500 m/s
  Pe = (0.5×10⁻⁶ × 1500) / 2×10⁻⁵ = 37.5 → adiabatic ✓

## Heat Capacity Ratio γ by Gas

  Gas       γ      T_max factor (R/R₀=300)
  ────────────────────────────────────────
  Monatomic (Ar,He,Xe)  5/3 ≈ 1.667   300^1.333 = 4,657×
  Diatomic  (N₂,O₂,air) 7/5 = 1.400   300^1.200 =   953×
  Triatomic (CO₂,H₂O)   4/3 ≈ 1.333   300^1.000 =   300×

  → Noble gases produce hottest collapses
  → SBSL experiments use Ar-saturated water for this reason

## Energy Budget at Collapse

  Input energy (acoustic cycle):
    E_in = ∫ P(t)·4πR²·Ṙ dt  ≈ 10⁻¹² J per collapse

  Output channels:
    Light emission  : ~10⁻¹⁴ J  (~1% of collapse energy)
    Sound radiation : ~10⁻¹³ J  (~10%)
    Heat to liquid  : ~10⁻¹² J  (~89%)
    Chemical (ROS)  : ~10⁻¹⁴ J  (~1%)

  SDT efficiency: maximize ROS yield fraction

## SDT Relevance

  ROS yield ∝ peak temperature
  Peak temperature ∝ (R_max/R_min)^(3(γ−1))
  R_max/R_min controlled by:
    - Driving pressure Pa  (higher Pa → larger expansion)
    - Frequency f          (lower f → more expansion time)
    - Gas type             (Ar → hotter than air)
    - Dissolved gas conc   (affects bubble nucleation)

  For SDT optimization:
    Maximize Pa within stable cavitation regime
    Use noble gas saturation if possible
    Target R_max/R_min > 100 for therapeutic ROS levels

## Connected Files

- Simulation : 02_simulations/thermodynamics/temperature_estimator.py PENDING
- Simulation : 02_simulations/thermodynamics/adiabatic_collapse.py    PENDING
- Previous   : 01_theory/notes/02_keller_miksis.md  ✓
- Next       : 01_theory/notes/04_plasma_emission.md

## References

1. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
2. Prosperetti, A. (1991). The thermal behaviour of oscillating
   gas bubbles. J. Fluid Mech. 222, 587.
3. Hilgenfeldt et al. (1999). Temperature calculation for
   sonoluminescing bubbles. J. Fluid Mech. 395, 399.
