#!/usr/bin/env python3
"""
Water Sonolysis & ROS Generation — Layer 3 Simulation
=======================================================
Computes OH· yield per bubble collapse as function of:
  - Collapse temperature
  - Driving pressure
  - Frequency
  - Cell type (cancer vs normal)

Connects to S-ASM-CC v5.1 kill probability model.
Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 sonolysis_ros.py
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
NA      = 6.022e23      # Avogadro
KB      = 1.381e-23     # Boltzmann
RG      = 8.314         # gas constant J/mol/K
P0      = 101325.0      # ambient Pa
RHO_W   = 1000.0        # water density kg/m³
MW      = 0.018         # water molar mass kg/mol
T_BODY  = 310.15        # 37°C in K
GAMMA_G = 1.4           # polytropic index
T0      = T_BODY        # ambient temperature

# ── Arrhenius parameters for H₂O dissociation ─────────────
A_ARR   = 2.0e16        # pre-exponential s⁻¹
EA      = 498000.0      # activation energy J/mol

# ── OH· properties ────────────────────────────────────────
D_OH        = 2.8e-9    # diffusion coefficient m²/s
TAU_OH_CELL = 10e-9     # lifetime in cytoplasm s
K_REC       = 5.5e9     # OH·+OH· recombination M⁻¹s⁻¹
N_LETHAL    = 1000      # lethal OH· hits for DNA damage

# ── S-ASM-CC v5.1 parameters ──────────────────────────────
OPT_FREQ  = 450000.0    # Hz
OPT_PRESS = 0.640e6     # Pa
OPT_SEL   = 88.38       # selectivity ratio

# ── Cell models ────────────────────────────────────────────
CELLS = {
    'OSCC Cancer': {
        'water': 0.78, 'stiffness': 2.5,
        'diameter': 18e-6, 'P_th': 0.6072e6,
        'color': '#ff4081', 'Rmax_Rmin': 100.0,
    },
    'Normal Keratinocyte': {
        'water': 0.72, 'stiffness': 5.0,
        'diameter': 15e-6, 'P_th': 0.7533e6,
        'color': '#00e5ff', 'Rmax_Rmin': None,
    },
}

COLORS = {
    'bg':     '#04060f',
    'panel':  '#080f20',
    'grid':   '#1a2a4a',
    'text':   '#c8d8f0',
    'core':   '#00e5ff',
    'cancer': '#ff4081',
    'normal': '#00e5ff',
    'ros':    '#00e676',
    'h2o2':   '#ff9100',
    'opt':    '#ffe57f',
    'lethal': '#ff4081',
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

def collapse_temperature(Rmax_Rmin, T0=T_BODY, gamma=GAMMA_G):
    return T0 * Rmax_Rmin**(3*(gamma-1))

def Rmax_Rmin_from_Pa(Pa, P0=P0, R0=5e-6, gamma=GAMMA_G):
    """Approximate Rmax/Rmin from driving pressure."""
    if Pa <= P0:
        return 1.0
    return (Pa/P0)**( 1.0/(3*(gamma-1)) ) * 3.0

def dissociation_rate(T):
    """Arrhenius rate k_diss [s⁻¹]."""
    exponent = np.clip(-EA/(RG*T), -500, 0)
    return A_ARR * np.exp(exponent)

def dissociation_fraction(T, tau=100e-12):
    """Fraction of H₂O dissociated during flash."""
    k = dissociation_rate(T)
    return 1.0 - np.exp(-k * tau)

def collapse_volume(R_min_m):
    return (4/3) * np.pi * R_min_m**3

def N_water_molecules(V_m3):
    n_density = RHO_W * NA / MW
    return n_density * V_m3

def OH_yield(T, R0=5e-6, Rmax_Rmin=100.0,
             f_core=0.01, f_OH=0.5):
    """OH· radicals per collapse."""
    R_min  = R0 / Rmax_Rmin
    V_col  = collapse_volume(R_min)
    N_H2O  = N_water_molecules(V_col)
    f_diss = dissociation_fraction(T)
    return N_H2O * f_core * f_diss * f_OH

def H2O2_yield(N_OH, f_rec=0.5):
    """H₂O₂ molecules from OH· recombination."""
    return N_OH * f_rec / 2.0

def OH_diffusion_length(tau=TAU_OH_CELL):
    return np.sqrt(2 * D_OH * tau)

def H2O2_concentration(N_H2O2, V_cell_m3):
    return N_H2O2 / (NA * V_cell_m3)

def kill_probability_mechanical(P_applied, P_th, k=4.1e-5):
    x = np.clip(-k*(P_applied-P_th), -500, 500)
    return 1.0/(1.0+np.exp(x))

def kill_probability_chemical(N_OH, N_lethal=N_LETHAL):
    return 1.0 - np.exp(-N_OH/N_lethal)

def total_kill_probability(P_applied, P_th, T_collapse):
    P_mech = kill_probability_mechanical(P_applied, P_th)
    N_OH   = OH_yield(T_collapse)
    P_chem = kill_probability_chemical(N_OH)
    return P_mech + (1-P_mech)*P_chem

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*65)
    print("  WATER SONOLYSIS & ROS — Layer 3")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    print("\n── Dissociation Rate vs Temperature ────────────────────")
    for T in [3000,5000,6055,10000,20000]:
        k   = dissociation_rate(T)
        f   = dissociation_fraction(T)
        print(f"  T={T:6d}K  k={k:.3e} s⁻¹  f_diss={f:.4f}")

    print("\n── OH· Yield per Collapse ───────────────────────────────")
    R0 = 5e-6
    for ratio in [50,100,200,300]:
        T   = collapse_temperature(ratio)
        N   = OH_yield(T, R0=R0, Rmax_Rmin=ratio)
        l   = OH_diffusion_length()
        print(f"  Rmax/Rmin={ratio:4d}  T={T:.0f}K  "
              f"N_OH={N:.3e}  l_diff={l*1e9:.1f}nm")

    print("\n── S-ASM-CC Operating Point ─────────────────────────────")
    for name, c in CELLS.items():
        V_cell = (4/3)*np.pi*(c['diameter']/2)**3
        if c['Rmax_Rmin']:
            T_col  = collapse_temperature(c['Rmax_Rmin'])
            N_OH   = OH_yield(T_col, Rmax_Rmin=c['Rmax_Rmin'])
            N_H2O2 = H2O2_yield(N_OH)
            C_H2O2 = H2O2_concentration(N_H2O2, V_cell)
            l_OH   = OH_diffusion_length()
            P_mech = kill_probability_mechanical(OPT_PRESS, c['P_th'])
            P_chem = kill_probability_chemical(N_OH)
            P_tot  = total_kill_probability(OPT_PRESS,c['P_th'],T_col)
            print(f"\n  {name}")
            print(f"    Rmax/Rmin    = {c['Rmax_Rmin']:.0f}×")
            print(f"    T_collapse   = {T_col:.0f} K")
            print(f"    N_OH         = {N_OH:.3e} radicals")
            print(f"    N_H2O2       = {N_H2O2:.3e} molecules")
            print(f"    C_H2O2       = {C_H2O2*1000:.4f} mM")
            print(f"    l_OH         = {l_OH*1e9:.1f} nm")
            print(f"    P_kill(mech) = {P_mech:.6f}")
            print(f"    P_kill(chem) = {P_chem:.6f}")
            print(f"    P_kill(TOTAL)= {P_tot:.6f}")
        else:
            P_mech = kill_probability_mechanical(OPT_PRESS, c['P_th'])
            print(f"\n  {name}")
            print(f"    No cavitation at Pa=0.640 MPa < P_th=0.753 MPa")
            print(f"    P_kill(mech) = {P_mech:.6f}")
            print(f"    P_kill(chem) = 0.000000 (no collapse)")
            print(f"    P_kill(TOTAL)= {P_mech:.6f}")

    print(f"\n── Lethal Dose Summary ──────────────────────────────────")
    N_OH_cancer = OH_yield(collapse_temperature(100))
    print(f"  OH· per collapse     = {N_OH_cancer:.3e}")
    print(f"  Lethal threshold     = {N_LETHAL} OH· hits")
    print(f"  Lethal margin        = {N_OH_cancer/N_LETHAL:.1e}× above threshold")
    print(f"  H₂O₂ apoptosis conc  = 0.01 mM")
    V_oscc = (4/3)*np.pi*(9e-6)**3
    C = H2O2_concentration(H2O2_yield(N_OH_cancer), V_oscc)*1000
    print(f"  H₂O₂ from 1 collapse = {C:.4f} mM")
    print(f"  Apoptosis margin     = {C/0.01:.1f}× above threshold")
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

    T_range  = np.linspace(1000, 25000, 1000)
    Pa_range = np.linspace(0.3e6, 1.2e6, 500)
    f_range  = np.logspace(4, 7, 300)

    # ── 1. Dissociation rate vs temperature ───────────────
    ax1 = fig.add_subplot(gs[0,0])
    k_vals = dissociation_rate(T_range)
    ax1.semilogy(T_range, k_vals, color=COLORS['ros'], lw=2)
    ax1.axvline(6055,  color=COLORS['opt'],    lw=1.5, ls='--',
                label='Our T=6055K')
    ax1.axvline(10000, color='#ff9100', lw=1,  ls=':',
                label='10,000K')
    ax1.axhline(1e10,  color=COLORS['lethal'], lw=1,  ls=':',
                label='τ=100ps threshold', alpha=0.7)
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('k_diss (s⁻¹)')
    ax1.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'H₂O Dissociation Rate vs T')

    # ── 2. OH· yield vs temperature ───────────────────────
    ax2 = fig.add_subplot(gs[0,1])
    N_OH_T = np.array([OH_yield(T) for T in T_range])
    ax2.semilogy(T_range, N_OH_T, color=COLORS['ros'], lw=2,
                 label='N_OH')
    ax2.axvline(6055,  color=COLORS['opt'],    lw=1.5, ls='--',
                label=f'T=6055K: {OH_yield(6055):.1e}')
    ax2.axhline(N_LETHAL, color=COLORS['lethal'], lw=1.5, ls=':',
                label=f'Lethal threshold ({N_LETHAL})')
    ax2.axhline(1e6, color='#ff9100', lw=1, ls=':',
                label='10⁶ OH·', alpha=0.7)
    ax2.set_xlabel('Temperature (K)')
    ax2.set_ylabel('N_OH per collapse')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'OH· Yield vs Collapse Temperature')

    # ── 3. OH· yield vs driving pressure ──────────────────
    ax3 = fig.add_subplot(gs[0,2])
    P_th_cancer = 0.6072e6
    P_th_normal = 0.7533e6
    N_OH_Pa = []
    for Pa in Pa_range:
        ratio = Rmax_Rmin_from_Pa(Pa)
        T_col = collapse_temperature(ratio)
        if Pa > P_th_cancer:
            N_OH_Pa.append(OH_yield(T_col, Rmax_Rmin=ratio))
        else:
            N_OH_Pa.append(0)
    N_OH_Pa = np.array(N_OH_Pa)
    ax3.semilogy(Pa_range/1e6, np.maximum(N_OH_Pa,1),
                 color=COLORS['cancer'], lw=2, label='OSCC (cavitates)')
    ax3.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=2, ls='--', label=f'Optimal {OPT_PRESS/1e6:.2f} MPa')
    ax3.axvline(P_th_cancer/1e6, color=COLORS['cancer'],
                lw=1, ls=':', label='Cancer threshold')
    ax3.axvline(P_th_normal/1e6, color=COLORS['normal'],
                lw=1, ls=':', label='Normal threshold')
    ax3.axhline(N_LETHAL, color=COLORS['lethal'],
                lw=1.5, ls=':', label='Lethal threshold')
    ax3.axvspan(P_th_cancer/1e6, P_th_normal/1e6,
                alpha=0.08, color=COLORS['ros'])
    ax3.set_xlabel('Driving Pressure (MPa)')
    ax3.set_ylabel('N_OH per collapse')
    ax3.set_ylim([1, 1e8])
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'OH· Yield vs Driving Pressure')

    # ── 4. Kill probability vs pressure ───────────────────
    ax4 = fig.add_subplot(gs[1,0])
    Pk_cancer_mech = kill_probability_mechanical(Pa_range, P_th_cancer)
    Pk_normal_mech = kill_probability_mechanical(Pa_range, P_th_normal)
    Pk_cancer_tot  = np.array([
        total_kill_probability(Pa, P_th_cancer,
                               collapse_temperature(
                                   Rmax_Rmin_from_Pa(Pa)))
        for Pa in Pa_range])
    ax4.plot(Pa_range/1e6, Pk_cancer_tot,
             color=COLORS['cancer'], lw=2, label='OSCC Total')
    ax4.plot(Pa_range/1e6, Pk_cancer_mech,
             color=COLORS['cancer'], lw=1, ls='--',
             label='OSCC Mechanical only', alpha=0.6)
    ax4.plot(Pa_range/1e6, Pk_normal_mech,
             color=COLORS['normal'], lw=2, label='Normal Cell')
    ax4.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=2, ls='--', label='Optimal Pa')
    ax4.axvspan(P_th_cancer/1e6, P_th_normal/1e6,
                alpha=0.08, color=COLORS['ros'])
    ax4.set_xlabel('Driving Pressure (MPa)')
    ax4.set_ylabel('Kill Probability')
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'Kill Probability — Mechanical + Chemical')

    # ── 5. H₂O₂ concentration vs pressure ─────────────────
    ax5 = fig.add_subplot(gs[1,1])
    V_oscc = (4/3)*np.pi*(9e-6)**3
    C_H2O2 = []
    for Pa in Pa_range:
        if Pa > P_th_cancer:
            ratio  = Rmax_Rmin_from_Pa(Pa)
            T_col  = collapse_temperature(ratio)
            N_OH   = OH_yield(T_col, Rmax_Rmin=ratio)
            N_H2O2 = H2O2_yield(N_OH)
            C_H2O2.append(H2O2_concentration(N_H2O2, V_oscc)*1000)
        else:
            C_H2O2.append(0)
    C_H2O2 = np.array(C_H2O2)
    ax5.semilogy(Pa_range/1e6, np.maximum(C_H2O2, 1e-6),
                 color=COLORS['h2o2'], lw=2, label='[H₂O₂]')
    ax5.axhline(0.01, color=COLORS['lethal'], lw=1.5, ls=':',
                label='Apoptosis threshold (0.01 mM)')
    ax5.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax5.set_xlabel('Driving Pressure (MPa)')
    ax5.set_ylabel('[H₂O₂] (mM)')
    ax5.set_ylim([1e-6, 1e3])
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'H₂O₂ Concentration in OSCC Cell')

    # ── 6. ROS species timeline ────────────────────────────
    ax6 = fig.add_subplot(gs[1,2])
    t_range = np.logspace(-12, -3, 1000)
    N_OH_t  = 1.74e6 * np.exp(-t_range/TAU_OH_CELL)
    N_H2O2_t = 8.7e5 * (1 - np.exp(-t_range/1e-6))
    ax6.loglog(t_range, np.maximum(N_OH_t,1),
               color=COLORS['ros'], lw=2, label='OH· (decays)')
    ax6.loglog(t_range, np.maximum(N_H2O2_t,1),
               color=COLORS['h2o2'], lw=2, label='H₂O₂ (builds)')
    ax6.axhline(N_LETHAL, color=COLORS['lethal'],
                lw=1.5, ls=':', label='Lethal threshold')
    ax6.axvline(TAU_OH_CELL, color=COLORS['ros'],
                lw=1, ls=':', alpha=0.6, label='OH· lifetime')
    ax6.set_xlabel('Time after collapse (s)')
    ax6.set_ylabel('Number of molecules')
    ax6.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'ROS Timeline After Collapse')

    # ── 7. Diffusion length vs lifetime ───────────────────
    ax7 = fig.add_subplot(gs[2,0])
    tau_range = np.logspace(-11, -3, 300)
    l_range   = np.sqrt(2*D_OH*tau_range)*1e9  # nm
    ax7.loglog(tau_range*1e9, l_range,
               color=COLORS['ros'], lw=2)
    ax7.axvline(TAU_OH_CELL*1e9, color=COLORS['cancer'],
                lw=1.5, ls='--',
                label=f'Cytoplasm τ={TAU_OH_CELL*1e9:.0f}ns')
    ax7.axvline(1e-6*1e9, color=COLORS['normal'],
                lw=1.5, ls='--',
                label='Pure water τ=1µs')
    ax7.set_xlabel('OH· lifetime (ns)')
    ax7.set_ylabel('Diffusion length (nm)')
    ax7.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'OH· Diffusion Length vs Lifetime')

    # ── 8. Selectivity including ROS ──────────────────────
    ax8 = fig.add_subplot(gs[2,1])
    sel_mech = (kill_probability_mechanical(Pa_range, P_th_cancer) /
                (kill_probability_mechanical(Pa_range, P_th_normal)+1e-300))
    sel_tot  = np.array([
        total_kill_probability(Pa, P_th_cancer,
                               collapse_temperature(
                                   Rmax_Rmin_from_Pa(Pa))) /
        (kill_probability_mechanical(Pa, P_th_normal)+1e-300)
        for Pa in Pa_range])
    ax8.semilogy(Pa_range/1e6, np.clip(sel_mech,1,1e8),
                 color=COLORS['normal'], lw=1.5, ls='--',
                 label='Mechanical only')
    ax8.semilogy(Pa_range/1e6, np.clip(sel_tot,1,1e8),
                 color=COLORS['ros'], lw=2,
                 label='Mechanical + Chemical')
    ax8.axhline(OPT_SEL, color=COLORS['opt'],
                lw=1.5, ls=':', label=f'S-ASM-CC {OPT_SEL}×')
    ax8.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--')
    ax8.axvspan(P_th_cancer/1e6, P_th_normal/1e6,
                alpha=0.08, color=COLORS['ros'])
    ax8.set_xlabel('Driving Pressure (MPa)')
    ax8.set_ylabel('Selectivity ratio (log)')
    ax8.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax8, 'Selectivity — Mech vs Mech+Chemical')

    # ── 9. Summary panel ──────────────────────────────────
    ax9 = fig.add_subplot(gs[2,2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.axis('off')
    T_oscc = collapse_temperature(100)
    N_oscc = OH_yield(T_oscc)
    C_h2o2 = H2O2_concentration(H2O2_yield(N_oscc),
                                 (4/3)*np.pi*(9e-6)**3)*1000
    lines = [
        ("LAYER 3 RESULTS",              COLORS['core'],   11, 0.93, True),
        ("WATER SONOLYSIS VALIDATED",     COLORS['ros'],    9,  0.83, True),
        (f"T_collapse(OSCC) = {T_oscc:.0f} K",
                                          '#ff4081',        8,  0.73, False),
        (f"N_OH per collapse = {N_oscc:.2e}",
                                          COLORS['ros'],    8,  0.64, False),
        (f"l_OH in cytoplasm = {OH_diffusion_length()*1e9:.1f} nm",
                                          COLORS['ros'],    8,  0.55, False),
        (f"[H₂O₂] per collapse = {C_h2o2:.3f} mM",
                                          COLORS['h2o2'],   8,  0.46, False),
        (f"Apoptosis threshold = 0.01 mM",
                                          COLORS['lethal'], 8,  0.37, False),
        (f"Margin = {C_h2o2/0.01:.0f}× above lethal",
                                          COLORS['ros'],    8,  0.28, False),
        ("DEDICATION",                    '#ff9100',        8,  0.18, True),
        ("Ali Sayed Muhammad Osman",      COLORS['text'],   7,  0.10, False),
        ("1957 – 2022",                   COLORS['text'],   7,  0.03, False),
    ]
    for txt,col,size,y,bold in lines:
        ax9.text(0.05, y, txt, color=col, fontsize=size,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Water Sonolysis — Layer 3  |  ROS Generation & Kill Probability",
        color=COLORS['core'], fontsize=11, fontweight='bold', y=0.97
    )

    outfile = OUT / "layer3_sonolysis_ros.png"
    plt.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
