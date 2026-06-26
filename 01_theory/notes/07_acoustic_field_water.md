# Acoustic Field in Pure Water — Layer 1

## Status
ACTIVE — Session 3 — 2026-05-27

## Why This Layer Exists

Before a bubble can form, collapse, or generate ROS —
an acoustic field must exist in the water.
The field determines:
  Where pressure maxima occur     → bubble nucleation sites
  How much energy reaches depth   → therapeutic penetration
  What frequency survives tissue  → clinical parameter selection
  Where standing waves form       → bubble trap locations

Everything in Layers 2-7 depends on Layer 1 being correct.

## Fundamental Parameters of Water (20°C, 1 atm)

  Property                  Symbol    Value           Units
  ──────────────────────────────────────────────────────────
  Density                   ρ₀        998.2           kg/m³
  Speed of sound            c₀        1482.3          m/s
  Acoustic impedance        Z₀        1.481×10⁶       Pa·s/m (Rayl)
  Dynamic viscosity         η         1.002×10⁻³      Pa·s
  Bulk viscosity            η_b       2.87×10⁻³       Pa·s
  Thermal conductivity      κ         0.5984          W/m·K
  Specific heat (const P)   Cp        4182            J/kg·K
  Thermal diffusivity       α_th      1.435×10⁻⁷      m²/s
  Surface tension           γ         0.0728          N/m
  Compressibility           β         4.477×10⁻¹⁰     Pa⁻¹
  Nonlinearity parameter    B/A       5.0             dimensionless

## Speed of Sound in Water

Temperature dependence (0-100°C):
  c(T) = 1402.7 + 4.88T − 0.0482T² + 2.41×10⁻⁴T³  [m/s]
  T in Celsius

  At 20°C: c = 1482 m/s
  At 37°C: c = 1523 m/s  (body temperature — important for SDT)
  At 100°C: c = 1543 m/s (near boiling)

Pressure dependence:
  c(P) ≈ c₀ + (∂c/∂P)·P
  (∂c/∂P) ≈ 1.6×10⁻⁶ m/s/Pa  (weak effect at therapeutic pressures)

## Acoustic Impedance

  Z = ρ·c  [Pa·s/m = Rayl]

  Water at 20°C: Z = 998.2 × 1482.3 = 1.480×10⁶ Rayl
  Water at 37°C: Z = 993.3 × 1523.0 = 1.513×10⁶ Rayl

  Tissue impedance varies by type:
  Fat      : Z = 1.34×10⁶ Rayl
  Muscle   : Z = 1.70×10⁶ Rayl
  Bone     : Z = 7.80×10⁶ Rayl
  Blood    : Z = 1.61×10⁶ Rayl
  Oropharynx (mucosa): Z ≈ 1.63×10⁶ Rayl  ← primary target

  Impedance mismatch → reflection at interface:
  Reflection coefficient R = ((Z₂−Z₁)/(Z₂+Z₁))²

  Water→Muscle: R = ((1.70−1.48)/(1.70+1.48))² = 0.0048  (0.48%)
  Water→Bone:   R = ((7.80−1.48)/(7.80+1.48))² = 0.463   (46.3%)

## Wave Equation in Water

Linear wave equation:
  ∇²P − (1/c²)·∂²P/∂t² = 0

With viscous absorption:
  ∇²P − (1/c²)·∂²P/∂t² + (δ/c⁴)·∂³P/∂t³ = 0

  δ = (2η/ρ) + (2η_b/ρ) + (2κ/ρ)(1/Cv − 1/Cp)  [m²/s]
    = diffusivity of sound

  δ_water at 20°C ≈ 4.0×10⁻⁶ m²/s

Nonlinear wave equation (Westervelt):
  ∇²P − (1/c²)·∂²P/∂t² + (δ/c⁴)·∂³P/∂t³ + (β/ρc⁴)·∂²P²/∂t² = 0

  β = 1 + B/2A = 1 + 5.0/2 = 3.5  (nonlinearity coefficient)

  Nonlinear effects become important when:
  Mach number M = v_particle/c > 0.01
  v_particle = P_a/(ρc) = 1.3×101325/(998×1482) = 0.089 m/s
  M = 0.089/1482 = 6×10⁻⁵  (linear regime for our parameters)

## Plane Wave Solution

  P(x,t) = P_a · exp(−αx) · cos(kx − ωt)

  k = ω/c = 2πf/c  (wave number)
  α = absorption coefficient [Np/m]
  ω = 2πf           (angular frequency)

  At f = 26.5 kHz in water:
  k = 2π × 26500 / 1482 = 112.3 rad/m
  λ = 2π/k = 0.0559 m = 5.59 cm

  At f = 1 MHz (therapeutic):
  k = 4232 rad/m
  λ = 1.48 mm

## Absorption in Pure Water

Classical absorption (viscous + thermal):
  α_classical = (ω²/2ρc³)·[4η/3 + η_b + κ(1/Cv − 1/Cp)]

  At 26.5 kHz: α = 8.9×10⁻⁵ Np/m = 7.7×10⁻⁴ dB/m
  At 1 MHz:    α = 0.127 Np/m    = 1.10 dB/m

  Pure water is extremely low absorption.
  Penetration depth (1/α):
  At 26.5 kHz: 11,200 m  (negligible absorption)
  At 1 MHz:    7.9 m      (still deep)
  At 10 MHz:   7.9 cm     (significant)

## Absorption in Biological Tissue

Tissue absorption >> water absorption (protein + structure):
  α_tissue ≈ α₀ · f^n

  α₀ and n depend on tissue type:

  Tissue          α₀ (dB/cm/MHz^n)   n
  ──────────────────────────────────────
  Water           0.002               2.0
  Blood           0.14                1.21
  Fat             0.48                1.0
  Muscle          0.57                1.0
  Liver           0.45                1.05
  Oropharynx      0.55                1.0   ← estimate

  At 1 MHz through 5cm oropharyngeal tissue:
  Attenuation = 0.55 × 1.0 × 5 = 2.75 dB
  Remaining pressure = 10^(−2.75/20) = 0.73  (73% survives)

  At 1 MHz through 10cm:
  Remaining = 10^(−5.5/20) = 0.53  (53% survives)

## Standing Wave Formation

Two opposing waves → standing wave:
  P(x,t) = 2P_a · cos(kx) · sin(ωt)

  Pressure antinodes at: kx = 0, π, 2π, ...
  x = 0, λ/2, λ, ...

  Pressure nodes at: kx = π/2, 3π/2, ...
  x = λ/4, 3λ/4, ...

  At 26.5 kHz: antinodes every 2.8 cm
  At 1 MHz:    antinodes every 0.74 mm

  For SBSL: bubble trapped at pressure antinode
  For SDT:  tumor targeted by focusing (traveling wave)

## Focused Ultrasound (Clinical SDT)

Spherical transducer focuses to point:
  Focal pressure gain: G = (πr/λ)²  (geometric focus gain)

  r = transducer radius
  λ = wavelength

  For therapeutic transducer:
  r = 25 mm, f = 1 MHz, λ = 1.48 mm
  G = (π × 25/1.48)² = (53.1)² = 2820×

  Peak focal pressure = G × P_source
  If P_source = 0.1 MPa → P_focus = 282 MPa (transient)

  More realistic with absorption/diffraction:
  Effective gain ~ 100-500×
  Therapeutic focal pressures: 1-10 MPa

## Acoustic Intensity

  I = P²/(2ρc)  [W/m²]

  At P_a = 1.3 atm = 131,722 Pa:
  I = (131722)²/(2 × 998 × 1482)
    = 1.735×10¹⁰ / 2.961×10⁶
    = 5861 W/m² = 0.586 W/cm²

  Therapeutic SDT intensities: 0.1–10 W/cm²
  Our SBSL parameters are in therapeutic range ✓

## Wavelength vs Biological Targets

  Frequency    λ in water    λ in tissue    Target resolution
  ──────────────────────────────────────────────────────────
  26.5 kHz     5.59 cm       ~3.5 cm        Flask-scale SBSL
  100 kHz      1.48 cm       ~0.9 cm        Organ-scale
  500 kHz      2.96 mm       ~1.8 mm        Tumor-scale
  1 MHz        1.48 mm       ~0.9 mm        Tumor margin
  3 MHz        0.49 mm       ~0.3 mm        Cell cluster scale
  10 MHz       0.15 mm       ~0.09 mm       Single cell scale

  For oropharyngeal SDT: 500 kHz – 3 MHz optimal range
  Balance: penetration depth vs spatial resolution

## Cavitation Threshold in Water

Blake threshold (static):
  P_Blake = P₀ + (2γ/R₀)·(1 − (P₀R₀³/P_v+2γR₀)/(P−P_v))^(1/2)

Simplified acoustic cavitation threshold:
  P_th ≈ P₀ + 2γ/R₀  (for R₀ << resonance size)

  For R₀ = 1 µm nucleation site:
  P_th = 101325 + 2×0.0728/1×10⁻⁶
       = 101325 + 145,600
       = 246,925 Pa = 2.44 atm

  Our driving Pa = 1.3 atm < 2.44 atm for 1µm nuclei
  → Need larger nucleation sites OR higher Pa for cavitation

  For R₀ = 5 µm (our simulation):
  P_th = 101325 + 2×0.0728/5×10⁻⁶
       = 101325 + 29,120
       = 130,445 Pa = 1.29 atm

  Our Pa = 1.30 atm ≈ P_th for R₀ = 5µm ✓
  This is why R₀ = 5µm was chosen — right at threshold

## SDT Relevance — Layer 1 Conclusions

1. Frequency selection:
   500 kHz – 3 MHz for oropharyngeal SDT
   Higher f → better resolution, lower penetration
   Lower f → deeper penetration, larger cavitation bubbles

2. Pressure selection:
   Pa > P_th(R₀_cancer) but < P_th(R₀_normal)
   This IS the selective destruction window
   Requires knowing R₀ distribution in cancer vs normal cells

3. Impedance matching:
   Water coupling gel between transducer and tissue
   Minimizes reflection at skin surface
   Standard clinical ultrasound practice

4. Standing wave vs traveling wave:
   SBSL lab: standing wave (flask resonance)
   Clinical SDT: focused traveling wave
   Physics identical at bubble scale

## Files to Create Next

  02_simulations/water_physics/acoustic_field.py
    → Compute P(x,t), I(x), α(f), λ(f)
    → Plot absorption vs frequency
    → Plot penetration depth vs frequency
    → Mark therapeutic window for oropharyngeal SDT

## Connected Files

  Previous : 01_theory/notes/06_bjerknes_forces.md ✓
  Next     : 01_theory/notes/08_bubble_nucleation.md
  Simulation: 02_simulations/water_physics/acoustic_field.py PENDING
  Papers   : 2408.16142 (Gatica 2024 — cavitation classification)

## References

1. Kinsler et al. (2000). Fundamentals of Acoustics. 4th ed. Wiley.
2. Duck, F.A. (1990). Physical Properties of Tissue. Academic Press.
3. Leighton, T.G. (1994). The Acoustic Bubble. Academic Press.
4. Szabo, T.L. (2014). Diagnostic Ultrasound Imaging. 2nd ed.
5. ter Haar, G. & Coussios, C. (2007). High intensity focused
   ultrasound: past, present and future. Int. J. Hyperthermia.
