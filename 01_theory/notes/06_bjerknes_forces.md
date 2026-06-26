# Bjerknes Forces

## Status
PENDING simulation — theory documented 2026-05-26

## Overview

Bjerknes forces are acoustic radiation forces on bubbles.
Named after Vilhelm Bjerknes (1906).
Two types:
  Primary  — force from external acoustic field
  Secondary — force between two bubbles

Both critical for SBSL trap stability and MBSL cloud structure.

## Primary Bjerknes Force

Force on bubble in an acoustic pressure field:

  F_1 = −<V(t) · ∇P(t)>

  V(t)  = instantaneous bubble volume = (4/3)πR³(t)
  ∇P(t) = pressure gradient of acoustic field
  <>    = time average over one cycle

For standing wave:  P(x,t) = P_a·cos(kx)·sin(ωt)
  ∇P = −P_a·k·sin(kx)·sin(ωt)

  F_1 = P_a·k·sin(kx) · <V(t)·sin(ωt)>

Sign of <V(t)·sin(ωt)> determines direction:
  Bubble below resonance size (R₀ < R_res):
    Expands in phase with rarefaction (sin(ωt) < 0)
    <V·sin(ωt)> < 0
    F_1 points toward antinode (sin(kx) = 0 minimum)
    → TRAPPED at pressure antinode ✓

  Bubble above resonance size (R₀ > R_res):
    Phase reverses
    <V·sin(ωt)> > 0
    F_1 points toward node
    → EXPELLED from trap ✗

## Bjerknes Force Magnitude

Approximate magnitude near antinode:
  |F_1| ≈ (2π/3) · R₀³ · P_a² · k / (ρ·c_L²) · |ω² − ω_0²|⁻¹

  ω_0 = natural frequency of bubble
      = (1/R₀)·sqrt(3γP₀/ρ)

  At R₀ = 5 µm, f = 26.5 kHz:
  ω_0 = (1/5×10⁻⁶)·sqrt(3×1.4×101325/998)
      = 2×10⁵ × 20.6
      = 4.12×10⁶ rad/s
  f_0 = 655 kHz

  f_drive = 26.5 kHz << f_0 = 655 kHz
  → Well below resonance → strong trapping force ✓

## Secondary Bjerknes Force

Force between two bubbles 1 and 2 separated by distance d:

  F_12 = −(ρ/4πd²) · <V̇₁·V̇₂>

  V̇ = dV/dt = 4πR²·Ṙ  (volume velocity)

Sign determines attraction or repulsion:
  <V̇₁·V̇₂> > 0  (in phase oscillation)  → ATTRACTION
  <V̇₁·V̇₂> < 0  (out of phase)          → REPULSION

Same-size bubbles driven by same field:
  Oscillate in phase → attract each other
  → Explains bubble coalescence in MBSL clouds

Different-size bubbles:
  May oscillate out of phase → repel
  → Explains spatial structure of cavitation clouds

## Bjerknes Force vs Surface Tension

For bubble to remain trapped need:
  |F_1| > F_buoyancy + F_drag

  F_buoyancy = (4/3)πR₀³·ρ·g ≈ 5×10⁻¹⁶ N  (negligible for µm bubbles)
  F_drag     = 6πη·R₀·v_terminal

Bjerknes force typically 10⁻¹²–10⁻¹⁰ N for SBSL conditions.
>> buoyancy and drag for R₀ < 10 µm
→ Bubble held firmly at antinode ✓

## Levitation Position

Bubble does not sit exactly at pressure antinode.
Gravity pulls it slightly off-center.
Equilibrium: Bjerknes force balances gravity.

Levitation position x_lev satisfies:
  F_1(x_lev) = F_buoyancy

  x_lev ≈ x_antinode − (ρ·g)/(P_a·k²) · (small correction)

For typical SBSL: x_lev within 10–100 µm of antinode.
Visible as tiny glowing dot slightly below antinode in flask.

## Effect on Collapse Dynamics

Bubble not exactly at antinode → asymmetric pressure field
→ Slight asymmetry in collapse
→ Can trigger non-spherical collapse modes
→ Limits maximum Pa for stable SBSL

This is why SBSL flasks are carefully designed:
  Spherical flask → clean standing wave
  Antinode at exact center → symmetric collapse
  Temperature controlled → stable dissolved gas

## MBSL Cloud Structure

Secondary Bjerknes forces organize bubble clouds:
  Large bubbles at center (pressure antinode)
  Small bubbles form streamers between antinodes
  Filamentary structures seen in high-speed photography

Cloud dynamics relevant to SDT:
  Dense bubble clouds → more ROS per unit volume
  But inter-bubble shielding reduces individual collapse intensity
  Optimal: sparse cloud of well-separated bubbles

## Bjerknes Forces in SDT Context

For focused ultrasound SDT (clinical setting):
  Transducer focuses to spot ~1 mm diameter at tumor
  Standing wave not present → traveling wave
  Traveling wave Bjerknes force:
    F_rad = −(2πR³/3c_L) · ∂I/∂x
    I = acoustic intensity [W/m²]
    → Bubbles pushed toward focus ✓
    → Natural concentration at tumor site

Microbubble contrast agents (lipid shell):
  Resonance frequency tuned to imaging frequency (1–10 MHz)
  Near resonance → huge Bjerknes force → precise focusing
  Shell rupture releases drug at focus
  → Targeted drug delivery + SDT combined

## Key Numbers Summary

  Quantity              Value           Notes
  ──────────────────────────────────────────────────────
  R_res at 26.5 kHz     124 µm          Trap size limit
  f_0 for R₀=5 µm       655 kHz         Natural frequency
  f_drive/f_0 ratio      0.040           Well below resonance
  Primary F_1 magnitude  ~10⁻¹¹ N       Strong trap
  Buoyancy force         ~5×10⁻¹⁶ N     Negligible
  Trap depth             ~10⁻¹² J        kT at 300K = 4×10⁻²¹ J
                                         Trap >> thermal energy ✓

## Connected Files

- Previous  : 01_theory/notes/05_stability_conditions.md  ✓
- Next      : 02_simulations/bubble_dynamics/keller_miksis.py  PENDING
- Papers    : chao-dyn/9805016 (Hilgenfeldt 1998)
              2408.16142 (Gatica 2024 — ML cavitation)
              pubmed SDT papers — traveling wave focusing

## References

1. Bjerknes, V. (1906). Fields of Force. Columbia Univ. Press.
2. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
3. Leighton, T.G. (1994). The Acoustic Bubble. Academic Press.
4. Lauterborn, W. & Kurz, T. (2010). Physics of bubble
   oscillations. Rep. Prog. Phys. 73, 106501.
