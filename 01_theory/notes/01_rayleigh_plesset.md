# Rayleigh-Plesset Equation

## Status
COMPLETE — Simulated and verified 2026-05-26
Rmax/Rmin = 300× | Tmax ~ 6000 K | V_wall = 0.97× speed of sound

## Core Equation

R·R̈ + (3/2)·Ṙ² = (1/ρ)[Pg − P₀ − P(t) − 4η(Ṙ/R) − 2γ/R]

Terms:
  R        — bubble radius [m]
  R̈        — bubble wall acceleration [m/s²]
  Ṙ        — bubble wall velocity [m/s]
  ρ        — liquid density [kg/m³]        → 998.0 for water
  Pg       — gas pressure inside bubble [Pa]
  P₀       — ambient liquid pressure [Pa]  → 101325 (1 atm)
  P(t)     — acoustic driving pressure [Pa] = Pa·sin(2πft)
  η        — dynamic viscosity [Pa·s]      → 1.002e-3 for water
  γ        — surface tension [N/m]         → 0.0728 for water

## Physical Meaning of Each Term

| Term           | Meaning                                      |
|----------------|----------------------------------------------|
| R·R̈            | Inertial resistance of bubble wall           |
| (3/2)·Ṙ²      | Kinetic energy of inward-rushing liquid      |
| Pg/ρ           | Gas pressure pushing wall outward            |
| −P₀/ρ         | Ambient pressure pushing wall inward         |
| −P(t)/ρ       | Acoustic driving — alternately expands/collapses |
| −4η(Ṙ/R)/ρ   | Viscous damping — energy loss to liquid      |
| −2γ/(ρR)      | Surface tension — resists expansion          |

## Gas Pressure Model

### Ideal gas (simple):
  Pg = P0·(R0/R)^(3γ)    — polytropic, γ=1.4 for adiabatic

### Van der Waals (used in simulation):
  Pg = P0·(R0³ − h³R0³)/(R³ − h³R0³)^γ
  h  = 0.0802  (hard core ratio for air)
  Prevents R → 0 singularity at collapse

## Derivation Path

1. Start with Navier-Stokes in spherical symmetry
2. Assume incompressible liquid (ρ = const)
3. Apply continuity: r²·u(r) = R²·Ṙ  (velocity field)
4. Integrate radial momentum from R to ∞
5. Apply boundary conditions:
   - P(r→∞) = P₀ + P(t)
   - P(r=R)  = Pg − 2γ/R − 4η·Ṙ/R
6. Result: the RPE

## Key Limitations

1. Assumes perfectly spherical bubble — ignores shape instabilities
2. Assumes incompressible liquid — breaks down near speed of sound
   → Fix: Keller-Miksis equation (next file)
3. Uniform internal temperature — ignores thermal gradients
   → Fix: Prosperetti thermal model
4. Single bubble — ignores bubble-bubble interactions
   → Fix: Bjerknes force models

## Numerical Notes

- Equation is STIFF near collapse — R changes by 300× in nanoseconds
- Must use stiff solver: Radau or LSODA (NOT RK45)
- Tolerances: rtol=1e-10, atol=1e-12 minimum
- Van der Waals floor prevents singularity
- max_step = T/5000 where T = 1/freq

## Simulation Results (2026-05-26)

Parameters:
  R0   = 5 µm
  Pa   = 1.30 atm
  freq = 26.5 kHz

Results:
  Rmax        = 65.38 µm
  Rmin        = ~200 nm (estimated from 300× ratio)
  Rmax/Rmin   = 300.6×
  Tmax        = 6055 K  (adiabatic estimate, real ~3-10× higher)
  V_wall_max  = 1457 m/s (0.97× speed of sound in water)
  Collapses   = 3 events over 4 acoustic cycles

## SDT Relevance

The RPE tells us:
- At Pa > 1.0 atm → bubble becomes unstable → violent collapse
- Violent collapse → plasma → ROS generation → cell death
- Frequency determines bubble resonance size:
  Resonance radius: R_res ≈ 3/(2πf) × sqrt(3γP₀/ρ)
  At 26.5 kHz → R_res ≈ 120 µm
- For SDT at tumor depth (5-10 cm):
  Lower frequencies (20-40 kHz) penetrate deeper
  Higher frequencies (1-3 MHz) focus more precisely

## Connected Files

- Simulation : 02_simulations/bubble_dynamics/rp_solver.py  ✓
- Next eq    : 01_theory/notes/02_keller_miksis.md
- Papers     : chao-dyn/9805016 (Hilgenfeldt 1998)
               1407.5531 (Vignoli 2014)

## References

1. Rayleigh, L. (1917). On the pressure developed in a liquid
   during the collapse of a spherical cavity. Phil. Mag. 34.
2. Plesset, M.S. (1949). The dynamics of cavitation bubbles.
   J. Appl. Mech. 16, 277.
3. Brenner, Hilgenfeldt, Lohse (2002). Rev. Mod. Phys. 74, 425.
4. Hilgenfeldt et al. (1998). arXiv:chao-dyn/9805016
