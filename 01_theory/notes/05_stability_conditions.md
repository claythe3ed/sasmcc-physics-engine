# Stability Conditions for SBSL

## Status
PENDING simulation — theory documented 2026-05-26

## The Core Problem

Not every bubble sonoluminesces.
Three independent stability conditions must ALL be satisfied:
  1. Acoustic (Bjerknes) stability   — bubble stays trapped
  2. Diffusive stability             — bubble neither grows nor dissolves
  3. Shape stability                 — bubble stays spherical

Miss any one → no stable SBSL.

## Condition 1: Acoustic (Bjerknes) Stability

Primary Bjerknes force on bubble in standing wave:
  F_B = −(4π/3)·R³·∇P

  ∇P = pressure gradient of standing wave
  R  = bubble radius

For a bubble smaller than resonance size:
  Bubble contracts when pressure is high
  Bubble expands when pressure is low
  → Net force toward pressure ANTINODE (maximum pressure)
  → Bubble is trapped at antinode ✓

For a bubble larger than resonance size:
  Phase of oscillation reverses
  → Net force toward pressure NODE
  → Bubble is expelled from trap ✗

Resonance radius:
  R_res = (1/2πf) · sqrt(3γP₀/ρ)

  At f = 26.5 kHz:
  R_res = (1/166,500) · sqrt(3×1.4×101325/998)
        = 6×10⁻⁶ · sqrt(425.6)
        = 6×10⁻⁶ × 20.6
        = 124 µm

  R₀ = 5 µm << R_res = 124 µm → acoustically stable ✓

## Condition 2: Diffusive Stability

Bubble exchanges gas with liquid via diffusion.
Net transport over one cycle determines if bubble grows or shrinks.

Rectified diffusion: during expansion surface area large →
gas flows IN. During collapse surface area small → gas flows OUT.
Asymmetry → net inflow → bubble grows.

Diffusive equilibrium condition:
  <Pg>·R₀³ = P₀·R_eq³

  <Pg> = time-averaged internal pressure
  R_eq = equilibrium radius at diffusive balance

For SBSL stability need:
  c_∞/c_0 < threshold(Pa, R₀, f)

  c_∞ = dissolved gas concentration in liquid
  c_0 = saturation concentration

Experimentally: SBSL requires degassed water
  c_∞/c_0 ≈ 0.2–0.4  (20–40% saturation)
  Fully saturated water → bubble grows → explodes → no SBSL

## Condition 3: Shape Stability

Bubble wall is a fluid interface — subject to instabilities.
Two mechanisms threaten spherical symmetry:

### 3a. Parametric (Faraday) Instability
Surface modes driven by periodic wall acceleration.
Mode n unstable when:
  |R̈/R| > ω_n²/4  during collapse

  ω_n = natural frequency of mode n
      = sqrt(n(n−1)(n+1)·γ/ρR³·2γ_s)

High Pa → large R̈ at collapse → surface modes grow → bubble destroyed.
Sets UPPER limit on driving pressure.

### 3b. Rayleigh-Taylor Instability
Occurs when heavy fluid (liquid) decelerates into light fluid (gas).
During collapse: liquid rushes inward, then decelerates abruptly.
Condition for instability:
  R̈ < 0  AND  (ρ_liquid − ρ_gas)·|R̈| > surface tension restoring force

At collapse: R̈ can reach 10¹² m/s² → highly destabilizing.
Surface tension γ = 0.0728 N/m provides restoring force.
Smaller bubbles more stable (higher Laplace pressure 2γ/R).

## Stability Window (Parameter Space)

SBSL exists only in a narrow window:

  Pa (atm)    R₀ (µm)    Stability
  ─────────────────────────────────
  < 1.0       any        No collapse — too gentle
  1.0–1.2     3–6        Stable SBSL window ✓
  1.2–1.5     3–6        Marginal — shape unstable
  > 1.5       any        Shape unstable — bubble destroyed
  any         < 1        Dissolves (diffusive instability)
  any         > 10       Bjerknes unstable at 26.5 kHz

Our simulation: Pa=1.30 atm, R₀=5 µm → right in the window ✓

## Stability Diagram

  High Pa
    |  [Shape unstable — no SBSL]
    |─────────────────────────────
    |  [STABLE SBSL WINDOW]
    |─────────────────────────────
    |  [No collapse — gentle oscillation]
  Low Pa
    └──────────────────────────────→ R₀
       Small              Large
       (dissolves)        (Bjerknes unstable)

## Lyapunov Stability of SBSL Attractor

Phase portrait from rp_solver.py shows tight spiral → stable attractor.
Small perturbations → bubble returns to same orbit.
This is why SBSL flashes are so regular (same flash every cycle).
Attractor stability = clock-like regularity = measurable in lab.

## SDT Relevance

For therapeutic cavitation want CONTROLLED instability:
  Stable cavitation  → gentle oscillation → low ROS → ineffective
  Transient cavitation → violent collapse → high ROS → therapeutic
  Uncontrolled cavitation → tissue damage → dangerous

SDT operating point:
  Pa just above shape stability threshold
  Bubble collapses violently but not so violently it destroys tissue
  Pulsed ultrasound: burst of cavitation then recovery period

Key SDT parameters from stability theory:
  Duty cycle: 10–50% (on/off ratio)
  Pulse duration: 1–10 ms
  Repetition frequency: 1–100 Hz
  Peak Pa: 0.5–3 MPa at focus (higher than lab SBSL)

## Connected Files

- Previous : 01_theory/notes/04_plasma_emission.md  ✓
- Next     : 01_theory/notes/06_bjerknes_forces.md
- Papers   : chao-dyn/9805016 (Hilgenfeldt 1998 — stability analysis)
             2408.16142 (Gatica 2024 — ML cavitation classification)

## References

1. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
2. Hilgenfeldt et al. (1998). arXiv:chao-dyn/9805016.
3. Prosperetti, A. (1977). Viscous effects on small-amplitude
   surface waves. Phys. Fluids 19, 195.
4. Blake, F.G. (1949). The onset of cavitation in liquids.
   Harvard Acoustics Research Lab Tech Memo 12.
