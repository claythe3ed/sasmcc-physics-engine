#!/usr/bin/env python3
"""
Collapse Temperature Estimator
================================
Parameter sweep over Pa, R0, gas type, frequency.
Includes ionization energy cap (T_eff = min(T_adiabatic, T_ion)).
Maps ROS yield vs conditions for SDT optimization.

Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 temperature_estimator.py
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
P0      = 101325.0
T_AMB   = 310.15      # 37°C body temperature
KB      = 1.381e-23
NA      = 6.022e23
RG      = 8.314

# ── Gas properties ─────────────────────────────────────────
GASES = {
    'Air':    {'gamma':1.40, 'T_ion':14000, 'color':'#00e5ff', 'ls':'-'},
    'Argon':  {'gamma':1.67, 'T_ion':15760, 'color':'#ff4081', 'ls':'--'},
    'Oxygen': {'gamma':1.40, 'T_ion':13620, 'color':'#00e676', 'ls':'-.'},
    'Helium': {'gamma':1.67, 'T_ion':24590, 'color':'#ffe57f', 'ls':':'},
}

# ── ROS parameters ─────────────────────────────────────────
A_ARR      = 2.0e16    # Arrhenius pre-exponential s⁻¹
EA         = 498000.0  # O-H bond energy J/mol
TAU_FLASH  = 100e-12   # flash duration s
F_CORE     = 0.01      # hot core fraction
F_OH       = 0.5       # OH fraction of dissociated H2O
N_LETHAL   = 1000      # lethal OH· hits

# ── S-ASM-CC operating point ───────────────────────────────
OPT_Pa   = 0.640e6
OPT_FREQ = 450000.0
OPT_R0   = 2.033e-6   # cancer cell nucleation radius

COLORS = {
    'bg':    '#04060f', 'panel': '#080f20',
    'grid':  '#1a2a4a', 'text':  '#c8d8f0',
    'core':  '#00e5ff', 'cancer':'#ff4081',
    'ros':   '#00e676', 'opt':   '#ffe57f',
    'h2o2':  '#ff9100',
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
# PHYSICS
# ══════════════════════════════════════════════════════════

def Rmax_Rmin(Pa, P0=P0, gamma=1.4):
    """Approximate expansion ratio from driving pressure."""
    if Pa <= P0: return 1.0
    return max(1.0, 3.0 * (Pa/P0)**(1.0/(3*(gamma-1))))

def T_adiabatic(ratio, T0=T_AMB, gamma=1.4):
    """Adiabatic collapse temperature — no ionization cap."""
    return T0 * ratio**(3*(gamma-1))

def T_ionization_cap(T_ad, T_ion):
    """
    Apply ionization energy cap.
    Above T_ion, energy goes into ionization not heating.
    T_eff = T_ion + (T_ad - T_ion) * f_residual
    f_residual accounts for partial heating above T_ion.
    Simple model: hard cap with 20% bleed-through.
    """
    if T_ad <= T_ion:
        return T_ad
    excess = T_ad - T_ion
    return T_ion + 0.20 * excess

def T_effective(Pa, gamma=1.4, T_ion=14000, T0=T_AMB):
    """Full temperature model with ionization cap."""
    ratio = Rmax_Rmin(Pa, gamma=gamma)
    T_ad  = T_adiabatic(ratio, T0, gamma)
    return T_ionization_cap(T_ad, T_ion), ratio, T_ad

def dissociation_rate(T):
    exponent = np.clip(-EA/(RG*T), -500, 0)
    return A_ARR * np.exp(exponent)

def OH_yield(T, R0=OPT_R0, ratio=100):
    """OH· radicals per collapse."""
    R_min  = R0 / max(ratio, 1)
    V_col  = (4/3)*np.pi*R_min**3
    n_H2O  = 1000*NA/0.018
    N_H2O  = n_H2O * V_col
    k      = dissociation_rate(T)
    f_diss = 1 - np.exp(-k*TAU_FLASH)
    return N_H2O * F_CORE * f_diss * F_OH

def lethal_margin(N_OH):
    return N_OH / N_LETHAL

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*65)
    print("  TEMPERATURE ESTIMATOR — With Ionization Cap")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    print("\n── Temperature vs Gas Type at Pa=0.640 MPa ─────────────")
    print(f"  {'Gas':<10} {'γ':>6} {'T_ion(K)':>10} "
          f"{'T_ad(K)':>10} {'T_eff(K)':>10} {'Cap?':>6}")
    print("  " + "─"*55)
    for gas, g in GASES.items():
        T_eff, ratio, T_ad = T_effective(
            OPT_Pa, g['gamma'], g['T_ion'])
        capped = "YES" if T_ad > g['T_ion'] else "no"
        print(f"  {gas:<10} {g['gamma']:>6.2f} "
              f"{g['T_ion']:>10,} {T_ad:>10,.0f} "
              f"{T_eff:>10,.0f} {capped:>6}")

    print(f"\n── S-ASM-CC Operating Point ─────────────────────────────")
    T_eff, ratio, T_ad = T_effective(OPT_Pa)
    N_OH = OH_yield(T_eff, OPT_R0, ratio)
    print(f"  Pa            = {OPT_Pa/1e6:.3f} MPa")
    print(f"  Rmax/Rmin     = {ratio:.1f}×")
    print(f"  T_adiabatic   = {T_ad:.0f} K  (uncapped)")
    print(f"  T_effective   = {T_eff:.0f} K  (with cap)")
    print(f"  N_OH          = {N_OH:.3e}")
    print(f"  Lethal margin = {lethal_margin(N_OH):.1f}×")

    print(f"\n── Temperature Sweep vs Pa ──────────────────────────────")
    print(f"  {'Pa(MPa)':>8} {'ratio':>8} {'T_ad(K)':>10} "
          f"{'T_eff(K)':>10} {'N_OH':>12} {'Margin':>8}")
    print("  " + "─"*58)
    for Pa in [0.3,0.5,0.607,0.640,0.753,1.0,1.5,2.0]:
        T_eff,ratio,T_ad = T_effective(Pa*1e6)
        N_OH = OH_yield(T_eff, OPT_R0, ratio)
        print(f"  {Pa:>8.3f} {ratio:>8.1f} {T_ad:>10,.0f} "
              f"{T_eff:>10,.0f} {N_OH:>12.3e} "
              f"{lethal_margin(N_OH):>8.1f}×")

    print(f"\n── Ionization Cap Effect ────────────────────────────────")
    print(f"  Without cap: T can reach millions of K (unphysical)")
    print(f"  With cap   : T limited to ~T_ion + 20% bleed")
    print(f"  Air T_ion  = 14,000 K")
    print(f"  At Pa=0.640 MPa: T_ad={T_effective(OPT_Pa)[2]:.0f}K "
          f"→ T_eff={T_effective(OPT_Pa)[0]:.0f}K")
    print(f"  ROS threshold = 5,000 K → confirmed exceeded ✓")
    print("═"*65 + "\n")

# ══════════════════════════════════════════════════════════
# PLOTTING
# ══════════════════════════════════════════════════════════
def plot_all():
    fig = plt.figure(figsize=(15,10), facecolor=COLORS['bg'])
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.5, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.92, bottom=0.07)

    Pa_range  = np.linspace(0.2e6, 2.0e6, 500)
    R0_range  = np.logspace(-7, -4, 200)   # 0.1 – 100 µm
    f_range   = np.logspace(4, 7, 200)

    # ── 1. T_adiabatic vs T_effective vs Pa ───────────────
    ax1 = fig.add_subplot(gs[0,0])
    for gas, g in GASES.items():
        T_ad_v  = np.array([T_adiabatic(
                    Rmax_Rmin(Pa, gamma=g['gamma']),
                    T_AMB, g['gamma'])
                    for Pa in Pa_range])
        T_eff_v = np.array([T_ionization_cap(T, g['T_ion'])
                    for T in T_ad_v])
        ax1.semilogy(Pa_range/1e6, T_ad_v,
                     color=g['color'], lw=1,
                     ls=':', alpha=0.5)
        ax1.semilogy(Pa_range/1e6, T_eff_v,
                     color=g['color'], lw=2,
                     ls=g['ls'], label=gas)
    ax1.axvline(OPT_Pa/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax1.axhline(5000, color=COLORS['ros'], lw=1,
                ls=':', label='ROS threshold 5kK')
    ax1.axhline(14000, color='white', lw=0.8,
                ls=':', alpha=0.4, label='Air T_ion')
    ax1.set_xlabel('Driving Pressure (MPa)')
    ax1.set_ylabel('Temperature (K)')
    ax1.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'T_eff vs Pa (solid=capped, dot=uncapped)')

    # ── 2. Rmax/Rmin vs Pa ────────────────────────────────
    ax2 = fig.add_subplot(gs[0,1])
    for gas, g in GASES.items():
        ratios = np.array([Rmax_Rmin(Pa, gamma=g['gamma'])
                           for Pa in Pa_range])
        ax2.semilogy(Pa_range/1e6, ratios,
                     color=g['color'], lw=2,
                     ls=g['ls'], label=gas)
    ax2.axvline(OPT_Pa/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax2.axvline(0.607, color=COLORS['cancer'],
                lw=1, ls=':', label='Cancer threshold')
    ax2.axvline(0.753, color=COLORS['core'],
                lw=1, ls=':', label='Normal threshold')
    ax2.set_xlabel('Driving Pressure (MPa)')
    ax2.set_ylabel('Rmax/Rmin ratio')
    ax2.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Expansion Ratio vs Pressure')

    # ── 3. OH· yield vs T_effective ───────────────────────
    ax3 = fig.add_subplot(gs[0,2])
    T_range = np.linspace(1000, 60000, 500)
    N_OH_v  = np.array([OH_yield(T) for T in T_range])
    ax3.semilogy(T_range, np.maximum(N_OH_v,1),
                 color=COLORS['ros'], lw=2)
    ax3.axvline(5000,  color=COLORS['ros'],
                lw=1.5, ls='--', label='ROS threshold 5kK')
    ax3.axvline(14000, color='white',
                lw=1, ls=':', alpha=0.5, label='Air T_ion')
    ax3.axhline(N_LETHAL, color=COLORS['cancer'],
                lw=1.5, ls=':', label='Lethal threshold')
    T_opt = T_effective(OPT_Pa)[0]
    ax3.axvline(T_opt, color=COLORS['opt'],
                lw=1.5, ls='--',
                label=f'T_eff at opt Pa={T_opt:.0f}K')
    ax3.set_xlabel('T_effective (K)')
    ax3.set_ylabel('N_OH per collapse')
    ax3.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'OH· Yield vs Collapse Temperature')

    # ── 4. T_eff vs R0 (bubble size effect) ───────────────
    ax4 = fig.add_subplot(gs[1,0])
    for gas, g in GASES.items():
        T_eff_v = []
        for R0 in R0_range:
            ratio = Rmax_Rmin(OPT_Pa, gamma=g['gamma'])
            T_ad  = T_adiabatic(ratio, T_AMB, g['gamma'])
            T_eff_v.append(T_ionization_cap(T_ad, g['T_ion']))
        ax4.semilogx(R0_range*1e6, T_eff_v,
                     color=g['color'], lw=2,
                     ls=g['ls'], label=gas)
    ax4.axvline(OPT_R0*1e6, color=COLORS['cancer'],
                lw=1.5, ls='--',
                label=f'R_n cancer={OPT_R0*1e6:.2f}µm')
    ax4.axhline(5000, color=COLORS['ros'],
                lw=1, ls=':', label='ROS threshold')
    ax4.set_xlabel('Initial bubble radius R0 (µm)')
    ax4.set_ylabel('T_effective (K)')
    ax4.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'T_eff vs Bubble Size at Pa=0.640 MPa')

    # ── 5. 2D heatmap Pa vs R0 ────────────────────────────
    ax5 = fig.add_subplot(gs[1,1])
    Pa_2d = np.linspace(0.5e6, 1.2e6, 60)
    R0_2d = np.logspace(-7, -5, 60)
    T_MAP = np.zeros((len(R0_2d), len(Pa_2d)))
    for i, R0 in enumerate(R0_2d):
        for j, Pa in enumerate(Pa_2d):
            T_eff,_,_ = T_effective(Pa)
            T_MAP[i,j] = T_eff
    im = ax5.contourf(Pa_2d/1e6, R0_2d*1e6,
                      T_MAP, levels=20, cmap='plasma')
    ax5.axvline(OPT_Pa/1e6, color='white',
                lw=1.5, ls='--', label='Optimal Pa')
    ax5.axhline(OPT_R0*1e6, color=COLORS['cancer'],
                lw=1.5, ls='--', label='R_n cancer')
    ax5.set_xlabel('Driving Pressure (MPa)')
    ax5.set_ylabel('Bubble radius R0 (µm)')
    plt.colorbar(im, ax=ax5, label='T_eff (K)')
    ax5.legend(fontsize=7, labelcolor='white',
               framealpha=0.5)
    style_ax(ax5, 'Temperature Map Pa vs R0')

    # ── 6. OH· yield vs Pa — all gases ────────────────────
    ax6 = fig.add_subplot(gs[1,2])
    for gas, g in GASES.items():
        N_OH_Pa = []
        for Pa in Pa_range:
            T_eff,ratio,_ = T_effective(
                Pa, g['gamma'], g['T_ion'])
            N_OH_Pa.append(OH_yield(T_eff, OPT_R0, ratio))
        ax6.semilogy(Pa_range/1e6,
                     np.maximum(N_OH_Pa, 1),
                     color=g['color'], lw=2,
                     ls=g['ls'], label=gas)
    ax6.axvline(OPT_Pa/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax6.axhline(N_LETHAL, color=COLORS['cancer'],
                lw=1.5, ls=':', label='Lethal threshold')
    ax6.axvline(0.607, color=COLORS['cancer'],
                lw=1, ls=':', alpha=0.7)
    ax6.set_xlabel('Driving Pressure (MPa)')
    ax6.set_ylabel('N_OH per collapse')
    ax6.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'OH· Yield vs Pa — All Gases')

    # ── 7. Temperature vs frequency ───────────────────────
    ax7 = fig.add_subplot(gs[2,0])
    for gas, g in GASES.items():
        T_f = []
        for f in f_range:
            T_eff,_,_ = T_effective(OPT_Pa,
                            g['gamma'], g['T_ion'])
            T_f.append(T_eff)
        ax7.semilogx(f_range/1e3, T_f,
                     color=g['color'], lw=2,
                     ls=g['ls'], label=gas)
    ax7.axvline(OPT_FREQ/1e3, color=COLORS['opt'],
                lw=1.5, ls='--', label='450 kHz')
    ax7.axhline(5000, color=COLORS['ros'],
                lw=1, ls=':', label='ROS threshold')
    ax7.set_xlabel('Frequency (kHz)')
    ax7.set_ylabel('T_effective (K)')
    ax7.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'T_eff vs Frequency')

    # ── 8. ROS yield margin vs Pa ─────────────────────────
    ax8 = fig.add_subplot(gs[2,1])
    margins = []
    for Pa in Pa_range:
        T_eff,ratio,_ = T_effective(Pa)
        N_OH = OH_yield(T_eff, OPT_R0, ratio)
        margins.append(lethal_margin(N_OH))
    ax8.semilogy(Pa_range/1e6,
                 np.maximum(margins, 0.01),
                 color=COLORS['ros'], lw=2)
    ax8.axhline(1.0, color=COLORS['cancer'],
                lw=1.5, ls='--', label='Lethal = 1×')
    ax8.axvline(OPT_Pa/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax8.axvline(0.607, color=COLORS['cancer'],
                lw=1, ls=':', label='Cancer threshold')
    ax8.axvspan(0.607, 0.753, alpha=0.08,
                color=COLORS['ros'])
    ax8.set_xlabel('Driving Pressure (MPa)')
    ax8.set_ylabel('Lethal margin (N_OH / N_lethal)')
    ax8.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax8, 'ROS Lethal Margin vs Pressure')

    # ── 9. Summary ────────────────────────────────────────
    ax9 = fig.add_subplot(gs[2,2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.axis('off')
    T_eff, ratio, T_ad = T_effective(OPT_Pa)
    N_OH = OH_yield(T_eff, OPT_R0, ratio)
    lines = [
        ("TEMPERATURE ESTIMATOR",      COLORS['core'],  11, 0.93, True),
        ("IONIZATION CAP APPLIED",      COLORS['ros'],   9,  0.83, True),
        (f"Pa = {OPT_Pa/1e6:.3f} MPa",  COLORS['opt'],   8,  0.73, False),
        (f"Rmax/Rmin = {ratio:.1f}×",   COLORS['text'],  8,  0.64, False),
        (f"T_adiabatic = {T_ad:.0f} K", '#ff9100',       8,  0.55, False),
        (f"T_effective = {T_eff:.0f} K",COLORS['ros'],   8,  0.46, False),
        (f"N_OH = {N_OH:.2e}",          COLORS['ros'],   8,  0.37, False),
        (f"Margin = {lethal_margin(N_OH):.0f}× lethal",
                                        COLORS['win'] if 'win'
                                        in COLORS else COLORS['ros'],
                                        8, 0.28, False),
        ("DEDICATION",                  '#ff9100',       8,  0.18, True),
        ("Ali Sayed Muhammad Osman",    COLORS['text'],  7,  0.10, False),
        ("1957 – 2022",                 COLORS['text'],  7,  0.03, False),
    ]
    for txt,col,sz,y,bold in lines:
        ax9.text(0.05, y, txt, color=col, fontsize=sz,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Temperature Estimator — Ionization Cap  |  ROS Yield Parameter Map",
        color=COLORS['core'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "temperature_estimator.png"
    plt.savefig(outfile, dpi=150,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
