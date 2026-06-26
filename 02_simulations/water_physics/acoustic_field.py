#!/usr/bin/env python3
"""
Acoustic Field in Pure Water — Layer 1 Simulation
===================================================
Computes and visualizes:
  1. Speed of sound vs temperature
  2. Acoustic impedance — water vs tissues
  3. Absorption coefficient vs frequency
  4. Penetration depth vs frequency
  5. Wavelength vs frequency
  6. Cavitation threshold vs bubble radius
  7. Therapeutic window for oropharyngeal SDT

Usage:
  python3 acoustic_field.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from pathlib import Path

OUT = Path.home() / "sonoluminescence/02_simulations/outputs"
OUT.mkdir(parents=True, exist_ok=True)

# ── Water constants (20°C) ─────────────────────────────────
RHO0    = 998.2       # density kg/m³
C0      = 1482.3      # speed of sound m/s
Z0      = RHO0 * C0   # acoustic impedance Rayl
ETA     = 1.002e-3    # dynamic viscosity Pa·s
ETA_B   = 2.87e-3     # bulk viscosity Pa·s
KAPPA   = 0.5984      # thermal conductivity W/m·K
CP      = 4182.0      # specific heat J/kg·K
CV      = 4157.0      # specific heat at const V J/kg·K
GAMMA_S = 0.0728      # surface tension N/m
P0      = 101325.0    # ambient pressure Pa
BA      = 5.0         # nonlinearity B/A

# ── Tissue impedance table ─────────────────────────────────
TISSUES = {
    'Water (20°C)':     {'Z': 1.480e6, 'color': '#00e5ff'},
    'Water (37°C)':     {'Z': 1.513e6, 'color': '#00b8d4'},
    'Fat':              {'Z': 1.340e6, 'color': '#ffe57f'},
    'Blood':            {'Z': 1.610e6, 'color': '#ff4081'},
    'Muscle':           {'Z': 1.700e6, 'color': '#7c4dff'},
    'Liver':            {'Z': 1.650e6, 'color': '#ff9100'},
    'Oropharynx':       {'Z': 1.630e6, 'color': '#00e676'},
    'Bone':             {'Z': 7.800e6, 'color': '#ffffff'},
}

# ── Tissue absorption table (α₀ in dB/cm/MHz^n, n) ────────
TISSUE_ABS = {
    'Water':        {'a0': 0.002, 'n': 2.0,  'color': '#00e5ff', 'ls': '-'},
    'Blood':        {'a0': 0.140, 'n': 1.21, 'color': '#ff4081', 'ls': '--'},
    'Fat':          {'a0': 0.480, 'n': 1.0,  'color': '#ffe57f', 'ls': '--'},
    'Muscle':       {'a0': 0.570, 'n': 1.0,  'color': '#7c4dff', 'ls': '--'},
    'Liver':        {'a0': 0.450, 'n': 1.05, 'color': '#ff9100', 'ls': '--'},
    'Oropharynx':   {'a0': 0.550, 'n': 1.0,  'color': '#00e676', 'ls': '-'},
}

COLORS = {
    'bg':    '#04060f',
    'panel': '#080f20',
    'grid':  '#1a2a4a',
    'text':  '#c8d8f0',
    'core':  '#00e5ff',
    'win':   '#00e676',
}

def style_ax(ax, title):
    ax.set_facecolor(COLORS['panel'])
    ax.tick_params(colors=COLORS['text'], labelsize=8)
    ax.xaxis.label.set_color(COLORS['text'])
    ax.yaxis.label.set_color(COLORS['text'])
    ax.set_title(title, color=COLORS['text'], fontsize=9, pad=6)
    for sp in ax.spines.values():
        sp.set_edgecolor(COLORS['grid'])
    ax.grid(True, color=COLORS['grid'], lw=0.5, alpha=0.7)

# ══════════════════════════════════════════════════════════
# CALCULATIONS
# ══════════════════════════════════════════════════════════

def speed_of_sound(T_C):
    """Speed of sound in water vs temperature (0-100°C)."""
    return 1402.7 + 4.88*T_C - 0.0482*T_C**2 + 2.41e-4*T_C**3

def absorption_water(f_Hz):
    """
    Classical absorption in pure water [Np/m].
    α = (ω²δ)/(2c³)
    δ = diffusivity of sound
    """
    omega = 2 * np.pi * f_Hz
    delta = (2*ETA/RHO0
             + 2*ETA_B/RHO0
             + 2*KAPPA/RHO0 * (1/CV - 1/CP))
    return omega**2 * delta / (2 * C0**3)

def absorption_tissue(f_MHz, a0, n):
    """Tissue absorption [dB/cm] at frequency f_MHz."""
    return a0 * f_MHz**n

def penetration_depth(alpha_Npm):
    """1/e penetration depth in meters."""
    return 1.0 / (alpha_Npm + 1e-30)

def wavelength(f_Hz, c=C0):
    return c / f_Hz

def cavitation_threshold(R0_m):
    """
    Blake threshold pressure [Pa] for bubble radius R0.
    Simplified: P_th = P0 + 2γ/R0
    """
    return P0 + 2 * GAMMA_S / R0_m

def reflection_coefficient(Z1, Z2):
    return ((Z2 - Z1) / (Z2 + Z1))**2

def transmission_coefficient(Z1, Z2):
    return 1 - reflection_coefficient(Z1, Z2)

# ══════════════════════════════════════════════════════════
# PRINT DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*60)
    print("  ACOUSTIC FIELD IN WATER — Layer 1 Diagnostics")
    print("═"*60)

    print("\n── Speed of Sound ──────────────────────────────")
    for T in [0, 20, 37, 60, 100]:
        c = speed_of_sound(T)
        print(f"  T={T:3d}°C  c = {c:.1f} m/s")

    print("\n── Acoustic Impedance & Reflection ─────────────")
    Z_water = TISSUES['Water (20°C)']['Z']
    for name, t in TISSUES.items():
        R = reflection_coefficient(Z_water, t['Z'])
        T_coef = transmission_coefficient(Z_water, t['Z'])
        print(f"  {name:20s}  Z={t['Z']/1e6:.3f} MRayl  "
              f"R={R*100:.2f}%  T={T_coef*100:.2f}%")

    print("\n── Absorption in Water ──────────────────────────")
    for f_kHz in [26.5, 100, 500, 1000, 3000, 10000]:
        f = f_kHz * 1e3
        a = absorption_water(f)
        a_dB = a * 8.686  # Np/m to dB/m
        pen = penetration_depth(a)
        lam = wavelength(f)
        print(f"  f={f_kHz:6.0f} kHz  "
              f"α={a_dB:.4f} dB/m  "
              f"depth={pen:.1f} m  "
              f"λ={lam*100:.3f} cm")

    print("\n── Oropharynx Absorption (0.55 dB/cm/MHz) ──────")
    for f_MHz in [0.1, 0.5, 1.0, 3.0]:
        a = absorption_tissue(f_MHz, 0.55, 1.0)
        for depth_cm in [3, 5, 10]:
            remaining = 10**(-a * depth_cm / 20)
            print(f"  f={f_MHz:.1f} MHz  depth={depth_cm:2d}cm  "
                  f"α={a:.2f} dB/cm  "
                  f"remaining={remaining*100:.1f}%")

    print("\n── Cavitation Threshold vs Bubble Radius ────────")
    for R_um in [0.5, 1, 2, 5, 10, 20, 50]:
        R = R_um * 1e-6
        P_th = cavitation_threshold(R)
        print(f"  R₀={R_um:4.1f} µm  "
              f"P_th={P_th/P0:.3f} atm  "
              f"({P_th/1e6:.3f} MPa)")

    print("\n── Therapeutic Window for Oropharyngeal SDT ────")
    print("  Frequency  : 500 kHz – 3 MHz")
    print("  Wavelength : 0.49 – 2.96 mm in tissue")
    print("  Penetration: 3–10 cm (sufficient for oropharynx)")
    print("  Intensity  : 0.1 – 10 W/cm²")
    print("  Peak Pa    : 0.5 – 3 MPa at focus")
    print("═"*60 + "\n")

# ══════════════════════════════════════════════════════════
# PLOTTING
# ══════════════════════════════════════════════════════════
def plot_all():
    fig = plt.figure(figsize=(15, 10), facecolor=COLORS['bg'])
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.5, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.92, bottom=0.07)

    f_range  = np.logspace(3, 8, 2000)      # 1 kHz – 100 MHz
    f_MHz    = f_range / 1e6
    T_range  = np.linspace(0, 100, 200)
    R_range  = np.logspace(-7, -4, 500)     # 0.1 µm – 100 µm

    # ── 1. Speed of sound vs temperature ──────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    c_vals = speed_of_sound(T_range)
    ax1.plot(T_range, c_vals, color=COLORS['core'], lw=2)
    ax1.axvline(20, color='#ffe57f', lw=1, ls='--', label='20°C lab')
    ax1.axvline(37, color='#ff4081', lw=1, ls='--', label='37°C body')
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('c (m/s)')
    ax1.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'Speed of Sound in Water')

    # ── 2. Acoustic impedance comparison ──────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    names = list(TISSUES.keys())
    zvals = [TISSUES[n]['Z']/1e6 for n in names]
    colors_z = [TISSUES[n]['color'] for n in names]
    bars = ax2.barh(names, zvals, color=colors_z, alpha=0.85)
    ax2.axvline(TISSUES['Water (20°C)']['Z']/1e6,
                color='#ff4081', lw=1.2, ls='--', label='Water ref')
    ax2.set_xlabel('Z (MRayl)')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Acoustic Impedance')
    ax2.tick_params(axis='y', labelsize=7)

    # ── 3. Absorption vs frequency ─────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    for name, t in TISSUE_ABS.items():
        a_vals = absorption_tissue(f_MHz, t['a0'], t['n'])
        ax3.loglog(f_MHz, a_vals,
                   color=t['color'], lw=1.5,
                   ls=t['ls'], label=name)
    ax3.axvspan(0.5, 3.0, alpha=0.08,
                color=COLORS['win'],
                label='SDT window')
    ax3.set_xlabel('Frequency (MHz)')
    ax3.set_ylabel('α (dB/cm)')
    ax3.set_xlim([0.01, 20])
    ax3.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8,
               loc='upper left')
    style_ax(ax3, 'Absorption vs Frequency')

    # ── 4. Penetration depth in oropharynx ────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    a_oro = absorption_tissue(f_MHz, 0.55, 1.0)
    a_oro_npm = a_oro / 8.686 * 100  # dB/cm → Np/m
    pen_oro = 1.0 / (a_oro_npm + 1e-30) * 100  # m → cm
    ax4.semilogx(f_MHz, pen_oro,
                 color='#00e676', lw=2, label='Oropharynx')
    ax4.axhspan(3, 10, alpha=0.08,
                color=COLORS['win'],
                label='3–10 cm target depth')
    ax4.axvspan(0.5, 3.0, alpha=0.06,
                color='#ff9100')
    ax4.set_xlabel('Frequency (MHz)')
    ax4.set_ylabel('1/e depth (cm)')
    ax4.set_ylim([0, 80])
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'Penetration Depth — Oropharynx')

    # ── 5. Wavelength vs frequency ─────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    lam_water  = wavelength(f_range, C0) * 1000      # mm
    lam_tissue = wavelength(f_range, 1540.0) * 1000  # mm (avg tissue)
    ax5.loglog(f_MHz, lam_water,
               color=COLORS['core'], lw=1.5, label='Water')
    ax5.loglog(f_MHz, lam_tissue,
               color='#00e676', lw=1.5, ls='--', label='Tissue ~1540m/s')
    ax5.axhspan(0.3, 3.0, alpha=0.08, color=COLORS['win'],
                label='Tumor resolution range')
    ax5.axvspan(0.5, 3.0, alpha=0.06, color='#ff9100')
    ax5.set_xlabel('Frequency (MHz)')
    ax5.set_ylabel('λ (mm)')
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'Wavelength vs Frequency')

    # ── 6. Cavitation threshold vs bubble radius ───────────
    ax6 = fig.add_subplot(gs[1, 2])
    P_th = cavitation_threshold(R_range) / P0  # in atm
    ax6.semilogx(R_range*1e6, P_th,
                 color='#ff4081', lw=2, label='Blake threshold')
    ax6.axhline(1.3, color='#ffe57f', lw=1.2, ls='--',
                label='Our Pa = 1.3 atm')
    ax6.axhline(3.0, color='#ff9100', lw=1.2, ls=':',
                label='SDT focus Pa = 3 atm')
    # Mark our R0 = 5 µm
    ax6.axvline(5.0, color=COLORS['core'], lw=1, ls=':',
                alpha=0.7, label='R₀=5µm (simulation)')
    ax6.fill_betweenx([0, 20],
                      R_range[P_th < 1.3].min()*1e6 if np.any(P_th < 1.3) else 5,
                      R_range.max()*1e6,
                      alpha=0.06, color=COLORS['win'])
    ax6.set_xlabel('R₀ (µm)')
    ax6.set_ylabel('P_threshold (atm)')
    ax6.set_ylim([0, 20])
    ax6.set_xlim([0.1, 100])
    ax6.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'Cavitation Threshold vs Bubble Size')

    # ── 7. Reflection at tissue interfaces ────────────────
    ax7 = fig.add_subplot(gs[2, 0])
    Z_water = TISSUES['Water (20°C)']['Z']
    t_names = [n for n in TISSUES if 'Water' not in n]
    r_vals  = [reflection_coefficient(Z_water, TISSUES[n]['Z'])*100
               for n in t_names]
    cols    = [TISSUES[n]['color'] for n in t_names]
    ax7.barh(t_names, r_vals, color=cols, alpha=0.85)
    ax7.set_xlabel('Reflection (%)')
    style_ax(ax7, 'Reflection: Water → Tissue Interface')
    ax7.tick_params(axis='y', labelsize=8)

    # ── 8. Intensity vs pressure amplitude ────────────────
    ax8 = fig.add_subplot(gs[2, 1])
    Pa_range = np.linspace(0, 5e6, 500)  # 0 to 5 MPa
    I_range  = Pa_range**2 / (2 * RHO0 * C0) / 1e4  # W/cm²
    ax8.plot(Pa_range/1e6, I_range,
             color=COLORS['core'], lw=2)
    ax8.axhspan(0.1, 10, alpha=0.08, color=COLORS['win'],
                label='Therapeutic SDT range')
    ax8.axvline(1.3*P0/1e6, color='#ffe57f', lw=1, ls='--',
                label=f'SBSL Pa={1.3*P0/1e6:.3f} MPa')
    ax8.set_xlabel('Pressure amplitude (MPa)')
    ax8.set_ylabel('Intensity (W/cm²)')
    ax8.set_xlim([0, 5])
    ax8.set_ylim([0, 100])
    ax8.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax8, 'Acoustic Intensity vs Pressure')

    # ── 9. SDT therapeutic window summary ─────────────────
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.set_xlim([0, 1]); ax9.set_ylim([0, 1])
    ax9.axis('off')

    lines = [
        ("OROPHARYNGEAL SDT", COLORS['core'], 12, 0.92, True),
        ("THERAPEUTIC WINDOW", '#00e676', 9, 0.82, True),
        ("Frequency  : 0.5 – 3 MHz",    COLORS['text'], 8, 0.72, False),
        ("Wavelength : 0.5 – 3.0 mm",   COLORS['text'], 8, 0.63, False),
        ("Penetration: 3 – 10 cm",       COLORS['text'], 8, 0.54, False),
        ("Intensity  : 0.1 – 10 W/cm²", COLORS['text'], 8, 0.45, False),
        ("Peak Pa    : 0.5 – 3 MPa",     COLORS['text'], 8, 0.36, False),
        ("Reflection : <1% (no bone)",   COLORS['text'], 8, 0.27, False),
        ("TARGETING PRINCIPLE",          '#ff4081', 9, 0.17, True),
        ("Z_cancer ≠ Z_normal",          '#ff9100', 8, 0.08, False),
    ]
    for txt, col, size, y, bold in lines:
        ax9.text(0.05, y, txt,
                 color=col, fontsize=size,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Acoustic Field in Water  —  Layer 1  |  SDT Physics Engine",
        color=COLORS['core'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "layer1_acoustic_field.png"
    plt.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")
    return outfile

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  Open: termux-open ~/sonoluminescence/02_simulations/outputs/")
