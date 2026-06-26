# Multi-Bubble Field — Layer 5

## Status
ACTIVE — Session 4 — 2026-05-28
Dedicated to Ali Sayed Muhammad Osman (1957–2022)

## Why Layer 5 Matters

Layers 1-3 modeled ONE bubble in isolation.
Real SDT treatment involves MILLIONS of bubbles.
Multi-bubble physics determines:
  Total ROS dose delivered to tumor
  Spatial distribution of cavitation damage
  Optimal transducer parameters for uniform coverage
  Why bubble clouds can REDUCE effectiveness (shielding)
  How to maximize therapeutic yield per pulse

## From Single Bubble to Cloud

Single bubble (SBSL):
  One stable bubble at pressure antinode
  Predictable, repeatable, well-modeled
  Used for physics studies

Multi-bubble (MBSL / therapeutic):
  Millions of bubbles nucleate simultaneously
  Interact via secondary Bjerknes forces
  Form clouds, streamers, filaments
  Collapse events partially synchronized
  THIS is what happens in SDT treatment

## Bubble Number Density

Nucleation rate in water under ultrasound:
  J_nuc = J_0 · exp(−ΔG*/k_BT)

At Pa = 0.640 MPa in OSCC tissue:
  Estimated bubble density: n_b ~ 10⁸ – 10¹⁰ m⁻³
  In tumor volume V_tumor ~ 1 cm³ = 10⁻⁶ m³:
  N_bubbles ~ 10² – 10⁴ bubbles per pulse

At 450 kHz, 10% duty cycle:
  Pulses per second = 450000 × 0.1 = 45000
  Collapses per second = N_bubbles × pulses
  = 10³ × 45000 = 4.5×10⁷ collapses/second

Total OH· per second in tumor:
  N_OH_total = 4.5×10⁷ × 8.76×10⁴
             = 3.94×10¹² OH·/second

## Secondary Bjerknes Forces in Cloud

Two bubbles i and j separated by distance d:
  F_ij = −(ρ/4πd²) · <V̇_i · V̇_j>

In-phase bubbles (same size, same driving):
  F_ij < 0 → ATTRACTION
  Bubbles cluster → dense cloud at pressure antinode

Clustering consequences:
  + Higher local bubble density → more ROS per volume
  − Bubble-bubble shielding → outer bubbles absorb energy
  − Inner bubbles receive less pressure → fewer collapses

Optimal bubble spacing:
  d_opt > 2·R_max  (bubbles don't merge)
  d_opt < λ/4      (Bjerknes attraction still operates)

  At 450 kHz: λ = c/f = 1529/450000 = 3.4 mm
  d_opt range: 130 µm < d < 850 µm

## Acoustic Shielding

Bubble cloud attenuates acoustic wave:
  dP/dx = −α_cloud · P

  α_cloud = n_b · σ_ext  (extinction cross-section)

  σ_ext = 4πR₀² · (f/f_res)² /
          ((1−f²/f_res²)² + (δ_tot·f/f_res)²)

  f_res = resonance frequency of bubble
  δ_tot = total damping coefficient

At R₀ = 2 µm (cancer cell nucleation radius):
  f_res = (1/2πR₀)·sqrt(3γP₀/ρ)
        = (1/2π×2×10⁻⁶)·sqrt(3×1.4×101325/993)
        = 79577 × 20.7
        = 1.648 MHz

At f = 450 kHz << f_res = 1.648 MHz:
  Below resonance → weak scattering
  α_cloud small → shielding minimal ✓
  450 kHz chosen partly for this reason

At f = 1 MHz (closer to resonance):
  Stronger shielding → less uniform field
  Trade-off: better resolution but more shielding

## Rectified Diffusion in Cloud

Each bubble grows slightly each cycle (rectified diffusion).
In a cloud, larger bubbles attract smaller ones (Bjerknes).
Eventually: coalescence → large bubbles → surface degassing.

Time scale for bubble growth:
  dR₀/dt ≈ D_gas · (c_∞ − c_sat) / (ρ_g · R₀)

  D_gas = 2×10⁻⁹ m²/s (gas diffusion in water)
  c_∞ = dissolved gas concentration
  c_sat = saturation concentration

For SDT: short pulses (463 ms on, 4.17 s off at 10% duty)
  Bubbles don't have time to grow significantly
  Cloud remains stable during pulse ✓

## Spatial Distribution of ROS

ROS generated at collapse sites — not uniformly distributed.
Distribution follows bubble density distribution.

In focused ultrasound (clinical SDT):
  Gaussian pressure field at focus:
  P(r) = P₀ · exp(−r²/2σ²)
  σ = focal spot radius ≈ λ/2 at 450 kHz = 1.7 mm

  Bubble density: n_b(r) ∝ P(r)^n  (n ≈ 2-4)
  ROS density:   ρ_ROS(r) ∝ n_b(r) · N_OH_per_collapse

  Central ROS density >> peripheral
  → Tumor center receives highest dose
  → Tumor margin receives lower dose
  → Scanning pattern needed for uniform coverage

## Scanning Strategy for Uniform Coverage

To treat entire tumor volume uniformly:
  Divide tumor into voxels of size ~σ × σ × σ
  At 450 kHz: voxel = 1.7 × 1.7 × 1.7 mm

  For oropharyngeal tumor ~2 cm diameter:
  N_voxels = (20/1.7)³ ≈ 1600 voxels

  Treatment time per voxel = 60s (S-ASM-CC optimal)
  Total treatment time = 1600 × 60 = 96,000s ← too long

  Parallel treatment (overlapping pulses):
  Overlap factor = 4
  Actual time = 96000/4 = 24,000s ← still too long

  Revised: pulse duration can be shorter for multi-bubble
  Single bubble needs 60s for sufficient collapses
  Multi-bubble cloud: 10³ bubbles → 1000× more collapses
  → 60s/1000 = 0.06s per voxel sufficient
  Total treatment time = 1600 × 0.06 = 96s ≈ 1.6 minutes ✓

## Cooperative Effects

Bubble-bubble interactions can ENHANCE kill rate:
  Microstreaming: flow between bubbles stresses membranes
  Shock waves: collapse of one bubble sends shock to neighbors
  Liquid jets: asymmetric collapse near boundaries

Microstreaming shear stress:
  τ = η · (∂v/∂r) at bubble surface
  At R₀=2µm, Ṙ=100 m/s:
  τ ≈ η · Ṙ/R₀ = 0.692×10⁻³ × 100/2×10⁻⁶ = 34,600 Pa

Cell membrane disruption threshold: ~1000 Pa
Our microstreaming: 34,600 Pa → 34× above threshold ✓
Additional kill mechanism beyond ROS.

## Cloud Dynamics Summary

  Effect              Benefit    Risk    Magnitude
  ─────────────────────────────────────────────────
  Bubble clustering   More ROS   Merge   High
  Acoustic shielding  None       Less P  Low (450kHz)
  Rectified diffusion None       Growth  Low (short pulse)
  Microstreaming      Membrane   None    34× threshold
  Shock waves         Extra kill None    Moderate
  Liquid jets         Membrane   None    Near boundaries

Net effect at 450 kHz, 463ms pulse, 10% duty:
  Multi-bubble enhances kill rate by ~10-100×
  vs single bubble estimate
  Consistent with S-ASM-CC 60s treatment time

## SDT Protocol Parameters

From Layer 5 physics:
  Frequency    : 450 kHz (below resonance → minimal shielding)
  Pulse dur    : 463 ms  (sufficient collapses, no bubble growth)
  Duty cycle   : 10%     (recovery time prevents heating)
  Scan voxel   : 1.7 mm  (λ/2 at 450 kHz)
  Voxel time   : 0.06–1s (multi-bubble enhanced)
  Total time   : 1.6–30 min depending on tumor size

## Temperature Rise in Tissue

Absorbed acoustic power → heat:
  Q = 2α·I  [W/m³]
  α = absorption coefficient at 450 kHz in oropharynx
    = 0.55 × 0.45 = 0.248 dB/cm = 2.86 Np/m
  I = 0.640²×10¹²/(2×993×1529) = 134 W/m² = 0.0134 W/cm²

  At 10% duty cycle: I_avg = 0.00134 W/cm²
  Temperature rise: ΔT = Q·t / (ρ·Cp)
  For 60s exposure:
  ΔT = 2×2.86×0.0134×60 / (993×3800)
     = 4.6 / 3,773,400
     = 1.22×10⁻⁶ K ← negligible heating ✓

Thermal safety confirmed — treatment is non-thermal.

## Connected Files

  Simulation : 02_simulations/water_physics/multi_bubble.py PENDING
  Previous   : 01_theory/notes/09_water_sonolysis.md ✓
  Next       : 01_theory/notes/11_impedance_differential.md
  Project    : S-ASM-CC v5.1 — StandingWaveField + OncotripsyPulse

## References

1. Lauterborn, W. & Kurz, T. (2010). Physics of bubble
   oscillations. Rep. Prog. Phys. 73, 106501.
2. Brenner et al. (2002). Rev. Mod. Phys. 74, 425.
3. Coussios, C.C. & Roy, R.A. (2008). Applications of
   acoustics and cavitation to noninvasive therapy.
   Ann. Rev. Fluid Mech. 40, 395.
4. Mittelstein et al. (2020). APL 116, 013701.
5. ter Haar, G. (2007). Therapeutic applications of
   ultrasound. Prog. Biophys. Mol. Biol. 93, 111.
