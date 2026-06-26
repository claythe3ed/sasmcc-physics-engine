# Keller-Miksis Equation

## Status
PENDING simulation — theory documented 2026-05-26

## Why We Need It

RPE assumes incompressible liquid.
Near collapse Ṙ approaches speed of sound (confirmed: 1457 m/s = 0.97c_L).
At Ṙ/c_L > 0.1 compressibility errors exceed 10%.
Keller-Miksis corrects this with acoustic radiation terms.

## Core Equation

(1 − Ṙ/c_L)·R·R̈ + (3/2)(1 − Ṙ/3c_L)·Ṙ²
  = (1 + Ṙ/c_L)·(1/ρ)·[Pg − P₀ − P(t)]
  + (R/ρc_L)·dPg/dt
  − 4η·Ṙ/(ρR)
  − 2γ/(ρR)

New terms vs RPE:
  (1 − Ṙ/c_L)    — compressibility correction on inertia
  (1 − Ṙ/3c_L)   — compressibility correction on kinetic energy
  (1 + Ṙ/c_L)    — compressibility correction on pressure
  (R/ρc_L)·dPg/dt — acoustic radiation damping (energy lost as sound)

## Physical Meaning

When bubble collapses it radiates sound outward.
This carries energy away — the bubble loses energy faster than RPE predicts.
Result: slightly less violent collapse than RPE suggests.
But more physically accurate near and after collapse.

## Parameters Added

  c_L = 1497 m/s   — speed of sound in water at 20°C

## Mach Number at Collapse

  M = Ṙ/c_L

RPE valid for M << 1
KM valid for M < 1 (subsonic collapse)
For supersonic collapse: Gilmore equation needed

From our RPE simulation:
  M_max = 1457/1497 = 0.974  ← right at the KM validity limit

## Derivation Path

1. Start with wave equation in liquid (not Laplace — includes c_L)
2. Assume pressure wave emitted at bubble wall propagates outward
3. Retarded potential: pressure at infinity felt R/c_L seconds later
4. Expand to first order in Ṙ/c_L
5. Result: KM equation

## Numerical Notes

- Still stiff — use Radau
- dPg/dt term requires computing gas pressure derivative
  For VdW gas:
  dPg/dt = −3γ·Pg·Ṙ·R²/(R³ − Rv³)
- Slightly more expensive than RPE per step
- Compare outputs: KM gives lower peak temperature than RPE
  (acoustic radiation removes energy before full compression)

## Expected Differences vs RPE

  Rmax/Rmin  : KM < RPE  (less compression)
  Tmax       : KM < RPE  (less heating)
  V_wall_max : KM < RPE  (radiation damping)
  Flash timing: KM more accurate

## SDT Relevance

KM accuracy matters for SDT parameter optimization:
- RPE overpredicts ROS yield → unsafe dosing estimates
- KM gives conservative (safer) estimates
- For therapeutic ultrasound at 1-3 MHz:
  c_L corrections become even more significant
  (higher frequency → faster dynamics → higher M)

## Connected Files

- Previous  : 01_theory/notes/01_rayleigh_plesset.md  ✓
- Simulation: 02_simulations/bubble_dynamics/keller_miksis.py  PENDING
- Next eq   : 01_theory/notes/03_thermodynamics.md
- Next step : 01_theory/notes/04_gilmore.md (if M > 1)

## References

1. Keller, J.B. & Miksis, M. (1980). Bubble oscillations of
   large amplitude. J. Acoust. Soc. Am. 68, 628.
2. Prosperetti, A. & Lezzi, A. (1986). Bubble dynamics in a
   compressible liquid. J. Fluid Mech. 168, 457.
3. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
