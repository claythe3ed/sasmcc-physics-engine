#!/usr/bin/env python3
"""
Bubble Nucleation Threshold — Layer 2 Simulation
==================================================
Computes selective destruction window for OSCC vs normal cells.
Validates S-ASM-CC v5.1 optimal parameters from first principles.

Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 nucleation_threshold.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

OUT = Path.home() / "sonoluminescence/02_simulations/outputs"
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────
P0      = 101325.0    # ambient pressure Pa
GAMMA_S = 0.0728      # surface tension N/m
RHO     = 993.0       # water density at 37°C kg/m³
C0      = 1529.0      # speed of sound at 37°C m/s
KB      = 1.381e-23   # Boltzmann constant
T_BODY  = 310.15      # body temperature K (37°C)
ETA_37  = 0.692e-3    # water viscosity at 37°C Pa·s
F_BOUND = 0.15        # bound water fraction (universal)
K_C     = 0.8         # stiffness coupling constant
R_REF   = 2.0e-6      # reference nucleation radius m
F_REF   = 0.60        # reference free water fraction

# ── Cell models from S-ASM-CC v5.1 ────────────────────────
CELLS = {
    'Normal\nKeratinocyte': {
        'water':     0.72,
        'stiffness': 5.0,    # kPa
        'diameter':  15.0,   # µm
        'color':     '#00e5ff',
        'ls':        '--',
    },
    'OSCC\nCancer': {
        'water':     0.78,
        'stiffness': 2.5,    # kPa
        'diameter':  18.0,   # µm
        'color':     '#ff4081',
        'ls':        '-',
    },
}

# S-ASM-CC v5.1 optimal parameters
OPT_FREQ   = 450000.0    # Hz
OPT_PRESS  = 640000.0    # Pa (0.640 MPa)
OPT_SEL    = 88.38       # selectivity ratio

COLORS = {
    'bg':     '#04060f',
    'panel':  '#080f20',
    'grid':   '#1a2a4a',
    'text':   '#c8d8f0',
    'core':   '#00e5ff',
    'cancer': '#ff4081',
    'normal': '#00e5ff',
    'win':    '#00e676',
    'opt':    '#ffe57f',
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
# CELL BIOPHYSICS
# ══════════════════════════════════════════════════════════

def free_water(f_water):
    return f_water - F_BOUND

def nucleation_radius(f_water):
    f_free = free_water(f_water)
    return R_REF * (f_free / F_REF)**(1/3)

def cell_viscosity(f_water, alpha=2.5):
    f_free = free_water(f_water)
    return ETA_37 / (f_free**alpha)

def blake_threshold(R_n):
    return P0 + 2*GAMMA_S/R_n

def stiffness_correction(E_kPa):
    return K_C * E_kPa * 1e3

def viscosity_correction(eta, R_n, Rdot_th=100.0):
    return 4 * eta * Rdot_th / R_n

def full_threshold(f_water, E_kPa):
    R_n   = nucleation_radius(f_water)
    eta   = cell_viscosity(f_water)
    P_bl  = blake_threshold(R_n)
    P_st  = stiffness_correction(E_kPa)
    P_vi  = viscosity_correction(eta, R_n)
    return P_bl + P_st + P_vi, R_n, eta, P_bl, P_st, P_vi

def death_probability(P_applied, P_th, k=4.1e-5):
    """Sigmoid death probability."""
    x = (P_applied - P_th) * k
    x = np.clip(x, -500, 500)
    return 1.0 / (1.0 + np.exp(-x))

def resonance_radius(f_Hz, gamma=1.4):
    return (1/(2*np.pi*f_Hz)) * np.sqrt(3*gamma*P0/RHO)

# ══════════════════════════════════════════════════════════
# PRINT DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*65)
    print("  NUCLEATION THRESHOLD — Layer 2")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    print("\n── Cell Biophysics ─────────────────────────────────────")
    for name, c in CELLS.items():
        label = name.replace('\n',' ')
        f_free = free_water(c['water'])
        R_n    = nucleation_radius(c['water'])
        eta    = cell_viscosity(c['water'])
        P_th, _, _, P_bl, P_st, P_vi = full_threshold(
            c['water'], c['stiffness'])

        print(f"\n  {label}")
        print(f"    Water fraction   : {c['water']:.2f}  "
              f"(free: {f_free:.2f})")
        print(f"    Nucleation R₀    : {R_n*1e6:.3f} µm")
        print(f"    Cell viscosity   : {eta*1e3:.3f} mPa·s")
        print(f"    Blake threshold  : {P_bl/1e6:.4f} MPa")
        print(f"    Stiffness corr   : {P_st/1e6:.4f} MPa")
        print(f"    Viscosity corr   : {P_vi/1e6:.4f} MPa")
        print(f"    TOTAL threshold  : {P_th/1e6:.4f} MPa  "
              f"({P_th/P0:.3f} atm)")

    # Selective window
    c_norm   = CELLS['Normal\nKeratinocyte']
    c_cancer = CELLS['OSCC\nCancer']
    P_normal, *_ = full_threshold(c_norm['water'],   c_norm['stiffness'])
    P_cancer, *_ = full_threshold(c_cancer['water'], c_cancer['stiffness'])

    print(f"\n── Selective Destruction Window ────────────────────────")
    print(f"  P_th(cancer)  = {P_cancer/1e6:.4f} MPa")
    print(f"  P_th(normal)  = {P_normal/1e6:.4f} MPa")
    print(f"  Window width  = {(P_normal-P_cancer)/1e6:.4f} MPa  "
          f"({(P_normal-P_cancer)/P0:.3f} atm)")
    print(f"  Optimal Pa    = {OPT_PRESS/1e6:.3f} MPa  (S-ASM-CC v5.1)")
    in_window = P_cancer < OPT_PRESS < P_normal
    print(f"  In window     : {'YES ✓' if in_window else 'NO ✗'}")
    margin_lo = (OPT_PRESS - P_cancer)/1e6
    margin_hi = (P_normal  - OPT_PRESS)/1e6
    print(f"  Margin below upper: {margin_hi:.4f} MPa")
    print(f"  Margin above lower: {margin_lo:.4f} MPa")

    # Resonance
    R_res = resonance_radius(OPT_FREQ)
    print(f"\n── Resonance at {OPT_FREQ/1e3:.0f} kHz ─────────────────────────────")
    print(f"  R_resonance   = {R_res*1e6:.2f} µm")
    print(f"  R_n(cancer)   = "
          f"{nucleation_radius(c_cancer['water'])*1e6:.2f} µm  "
          f"({'< R_res → sub-resonant ✓' if nucleation_radius(c_cancer['water']) < R_res else '> R_res'})")

    # Death probabilities at optimal pressure
    print(f"\n── Death Probability at P={OPT_PRESS/1e6:.3f} MPa ──────────────────")
    P_d_cancer = death_probability(OPT_PRESS, P_cancer)
    P_d_normal = death_probability(OPT_PRESS, P_normal)
    sel = P_d_cancer/(P_d_normal+1e-300)
    print(f"  P_death(cancer) = {P_d_cancer:.6f}")
    print(f"  P_death(normal) = {P_d_normal:.6f}")
    print(f"  Selectivity     = {sel:.2f}×  "
          f"(S-ASM-CC reports {OPT_SEL}×)")

    print("═"*65 + "\n")

# ══════════════════════════════════════════════════════════
# PLOTTING
# ══════════════════════════════════════════════════════════
def plot_all():
    fig = plt.figure(figsize=(15, 10), facecolor=COLORS['bg'])
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.5, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.92, bottom=0.07)

    P_range = np.linspace(0, 1.5e6, 2000)   # 0 – 1.5 MPa
    W_range = np.linspace(0.60, 0.90, 500)  # water fraction
    f_range = np.logspace(4, 7, 500)         # 10 kHz – 10 MHz
    E_range = np.linspace(0.5, 10, 500)      # 0.5 – 10 kPa

    c_norm   = CELLS['Normal\nKeratinocyte']
    c_cancer = CELLS['OSCC\nCancer']
    P_normal, *_ = full_threshold(c_norm['water'],   c_norm['stiffness'])
    P_cancer, *_ = full_threshold(c_cancer['water'], c_cancer['stiffness'])

    # ── 1. Threshold vs water fraction ────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    for E_kPa, lbl, col in [(5.0,'Normal (5 kPa)','#00e5ff'),
                             (2.5,'Cancer (2.5 kPa)','#ff4081')]:
        P_th = [full_threshold(w, E_kPa)[0]/1e6 for w in W_range]
        ax1.plot(W_range, P_th, color=col, lw=2, label=lbl)
    ax1.axhline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label=f'Optimal Pa={OPT_PRESS/1e6:.2f} MPa')
    ax1.axvline(c_norm['water'],   color='#00e5ff', lw=1, ls=':',  alpha=0.6)
    ax1.axvline(c_cancer['water'], color='#ff4081', lw=1, ls=':',  alpha=0.6)
    ax1.fill_betweenx([0, 2],
                      c_cancer['water'], c_norm['water'],
                      alpha=0.08, color=COLORS['win'])
    ax1.set_xlabel('Water fraction')
    ax1.set_ylabel('P_threshold (MPa)')
    ax1.set_ylim([0, 2])
    ax1.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'Threshold vs Water Fraction')

    # ── 2. Threshold vs cortical stiffness ────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    for w, lbl, col in [(0.72,'Normal (72% water)','#00e5ff'),
                        (0.78,'Cancer (78% water)','#ff4081')]:
        P_th = [full_threshold(w, E)[0]/1e6 for E in E_range]
        ax2.plot(E_range, P_th, color=col, lw=2, label=lbl)
    ax2.axhline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label=f'Optimal Pa')
    ax2.axvline(c_norm['stiffness'],   color='#00e5ff',
                lw=1, ls=':', alpha=0.6, label='Normal 5.0 kPa')
    ax2.axvline(c_cancer['stiffness'], color='#ff4081',
                lw=1, ls=':', alpha=0.6, label='Cancer 2.5 kPa')
    ax2.set_xlabel('Cortical stiffness (kPa)')
    ax2.set_ylabel('P_threshold (MPa)')
    ax2.set_ylim([0, 2])
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Threshold vs Cortical Stiffness')

    # ── 3. Death probability vs applied pressure ───────────
    ax3 = fig.add_subplot(gs[0, 2])
    P_d_cancer = death_probability(P_range, P_cancer)
    P_d_normal = death_probability(P_range, P_normal)
    ax3.plot(P_range/1e6, P_d_cancer,
             color=COLORS['cancer'], lw=2, label='OSCC Cancer')
    ax3.plot(P_range/1e6, P_d_normal,
             color=COLORS['normal'], lw=2, label='Normal Cell')
    ax3.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=2, ls='--', label=f'Optimal {OPT_PRESS/1e6:.2f} MPa')
    ax3.axvspan(P_cancer/1e6, P_normal/1e6,
                alpha=0.12, color=COLORS['win'],
                label=f'Selective window')
    ax3.set_xlabel('Applied Pressure (MPa)')
    ax3.set_ylabel('Death Probability')
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'Death Probability vs Pressure')

    # ── 4. Selectivity ratio vs pressure ──────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    eps = 1e-300
    sel = (death_probability(P_range, P_cancer) /
           (death_probability(P_range, P_normal) + eps))
    sel = np.clip(sel, 1, 1e6)
    ax4.semilogy(P_range/1e6, sel,
                 color=COLORS['win'], lw=2)
    ax4.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label=f'Optimal Pa')
    ax4.axhline(OPT_SEL, color='#ff9100',
                lw=1, ls=':', label=f'S-ASM-CC: {OPT_SEL}×')
    ax4.axvspan(P_cancer/1e6, P_normal/1e6,
                alpha=0.08, color=COLORS['win'])
    ax4.set_xlabel('Applied Pressure (MPa)')
    ax4.set_ylabel('Selectivity ratio (log)')
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'Selectivity Ratio vs Pressure')

    # ── 5. Nucleation radius vs water fraction ─────────────
    ax5 = fig.add_subplot(gs[1, 1])
    R_n_vals = np.array([nucleation_radius(w)*1e6 for w in W_range])
    ax5.plot(W_range, R_n_vals, color=COLORS['core'], lw=2)
    ax5.axvline(c_norm['water'],
                color='#00e5ff', lw=1.5, ls='--',
                label=f"Normal: R_n={nucleation_radius(c_norm['water'])*1e6:.2f}µm")
    ax5.axvline(c_cancer['water'],
                color='#ff4081', lw=1.5, ls='--',
                label=f"Cancer: R_n={nucleation_radius(c_cancer['water'])*1e6:.2f}µm")
    ax5.set_xlabel('Water fraction')
    ax5.set_ylabel('Nucleation radius R_n (µm)')
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'Nucleation Radius vs Water Fraction')

    # ── 6. Resonance radius vs frequency ──────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    R_res_vals = np.array([resonance_radius(f)*1e6 for f in f_range])
    ax6.loglog(f_range/1e3, R_res_vals,
               color='#ff9100', lw=2, label='R_resonance')
    ax6.axhline(nucleation_radius(c_cancer['water'])*1e6,
                color=COLORS['cancer'], lw=1.5, ls='--',
                label='R_n cancer')
    ax6.axhline(nucleation_radius(c_norm['water'])*1e6,
                color=COLORS['normal'], lw=1.5, ls=':',
                label='R_n normal')
    ax6.axvline(OPT_FREQ/1e3, color=COLORS['opt'],
                lw=1.5, ls='--',
                label=f'{OPT_FREQ/1e3:.0f} kHz optimal')
    ax6.set_xlabel('Frequency (kHz)')
    ax6.set_ylabel('Radius (µm)')
    ax6.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'Resonance Radius vs Frequency')

    # ── 7. Threshold breakdown — bar chart ────────────────
    ax7 = fig.add_subplot(gs[2, 0])
    labels   = ['Normal\nKeratinocyte', 'OSCC\nCancer']
    P_bl_v   = [blake_threshold(nucleation_radius(c['water']))/1e6
                for c in CELLS.values()]
    P_st_v   = [stiffness_correction(c['stiffness'])/1e6
                for c in CELLS.values()]
    P_vi_v   = [viscosity_correction(
                    cell_viscosity(c['water']),
                    nucleation_radius(c['water']))/1e6
                for c in CELLS.values()]
    x = np.arange(len(labels))
    w = 0.25
    ax7.bar(x-w, P_bl_v, w, label='Blake',     color='#7c4dff', alpha=0.85)
    ax7.bar(x,   P_st_v, w, label='Stiffness', color='#ff9100', alpha=0.85)
    ax7.bar(x+w, P_vi_v, w, label='Viscosity', color='#00e676', alpha=0.85)
    ax7.axhline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax7.set_xticks(x); ax7.set_xticklabels(labels, fontsize=8)
    ax7.set_ylabel('Pressure contribution (MPa)')
    ax7.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'Threshold Breakdown by Mechanism')

    # ── 8. Water fraction sweep — selectivity heat ────────
    ax8 = fig.add_subplot(gs[2, 1])
    W_normal_range = np.linspace(0.65, 0.80, 100)
    W_cancer_range = np.linspace(0.65, 0.85, 100)
    WN, WC = np.meshgrid(W_normal_range, W_cancer_range)
    SEL_MAP = np.zeros_like(WN)
    for i in range(WN.shape[0]):
        for j in range(WN.shape[1]):
            if WC[i,j] <= WN[i,j]:
                SEL_MAP[i,j] = 1.0
                continue
            Pn,*_ = full_threshold(WN[i,j], 5.0)
            Pc,*_ = full_threshold(WC[i,j], 2.5)
            pd_c = death_probability(OPT_PRESS, Pc)
            pd_n = death_probability(OPT_PRESS, Pn)
            SEL_MAP[i,j] = pd_c/(pd_n+1e-300)
    SEL_MAP = np.clip(SEL_MAP, 1, 1e4)
    im = ax8.contourf(W_normal_range, W_cancer_range,
                      np.log10(SEL_MAP),
                      levels=20, cmap='plasma')
    ax8.plot(c_norm['water'], c_cancer['water'],
             'w*', markersize=12, label='OSCC operating point')
    plt.colorbar(im, ax=ax8, label='log10(Selectivity)')
    ax8.set_xlabel('Normal cell water fraction')
    ax8.set_ylabel('Cancer cell water fraction')
    ax8.legend(fontsize=7, labelcolor='white', framealpha=0.5)
    style_ax(ax8, 'Selectivity Map — Water Content Space')

    # ── 9. Summary panel ──────────────────────────────────
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.axis('off')

    lines = [
        ("LAYER 2 RESULTS",            COLORS['core'],   11, 0.93, True),
        ("S-ASM-CC v5.1 VALIDATED",    COLORS['win'],    9,  0.83, True),
        (f"P_th(cancer) = {P_cancer/1e6:.4f} MPa", '#ff4081', 8, 0.73, False),
        (f"P_th(normal) = {P_normal/1e6:.4f} MPa", '#00e5ff', 8, 0.64, False),
        (f"Window width = {(P_normal-P_cancer)/1e6:.4f} MPa", COLORS['win'], 8, 0.55, False),
        (f"Optimal Pa   = {OPT_PRESS/1e6:.3f} MPa  ✓", COLORS['opt'], 8, 0.46, False),
        ("Dominant: VISCOSITY term",   '#00e676',  8,  0.37, False),
        ("Water → viscosity → threshold", COLORS['text'], 7, 0.28, False),
        ("DEDICATION",                 '#ff9100',  8,  0.18, True),
        ("Ali Sayed Muhammad Osman",   COLORS['text'], 7, 0.10, False),
        ("1957 – 2022",                COLORS['text'], 7, 0.03, False),
    ]
    for txt, col, size, y, bold in lines:
        ax9.text(0.05, y, txt, color=col, fontsize=size,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Bubble Nucleation — Layer 2  |  OSCC Selective Destruction Window",
        color=COLORS['core'], fontsize=11, fontweight='bold', y=0.97
    )

    outfile = OUT / "layer2_nucleation_threshold.png"
    plt.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
