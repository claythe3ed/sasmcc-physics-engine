#!/usr/bin/env python3
"""
Keller-Miksis Equation Solver
================================
Compressibility-corrected bubble dynamics.
Adds acoustic radiation damping to RPE.
Critical since V_wall = 0.97c_L in our simulation.

Compares KM vs RPE to quantify compressibility effects.
Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 keller_miksis.py
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

OUT = Path.home() / "sonoluminescence/02_simulations/outputs"
OUT.mkdir(parents=True, exist_ok=True)

# ── Physical constants ─────────────────────────────────────
RHO     = 998.0
ETA     = 1.002e-3
GAMMA_S = 0.0728
P0      = 101325.0
C_L     = 1497.0
T_AMB   = 293.15
GAMMA_G = 1.4
VDW_H   = 0.0802

# ── Simulation parameters ──────────────────────────────────
R0   = 5e-6
Pa   = 1.3 * P0
FREQ = 26500.0
NCYC = 4

COLORS = {
    'bg':    '#04060f', 'panel': '#080f20',
    'grid':  '#1a2a4a', 'text':  '#c8d8f0',
    'rpe':   '#00e5ff', 'km':    '#ff4081',
    'opt':   '#ffe57f', 'vel':   '#7c4dff',
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
# ODE SYSTEMS
# ══════════════════════════════════════════════════════════

def gas_pressure(R, R0, P0_gas):
    Rv    = VDW_H * R0
    denom = R**3 - Rv**3
    if denom <= 0: return P0_gas
    return P0_gas * ((R0**3 - Rv**3) / denom)**GAMMA_G

def dgas_dt(R, Rdot, R0, P0_gas):
    """Time derivative of gas pressure for KM equation."""
    Rv    = VDW_H * R0
    denom = R**3 - Rv**3
    if denom <= 0: return 0.0
    Pg = P0_gas * ((R0**3 - Rv**3) / denom)**GAMMA_G
    return -3*GAMMA_G * Pg * R**2 * Rdot / denom

def P_drive(t):
    return Pa * np.sin(2*np.pi*FREQ*t)

def dP_drive_dt(t):
    return Pa * 2*np.pi*FREQ * np.cos(2*np.pi*FREQ*t)

# ── Rayleigh-Plesset ODE ───────────────────────────────────
def rpe_ode(t, y):
    R, Rdot = y
    Rv = VDW_H * R0
    if R <= Rv*1.001: return [0.0, 0.0]
    P0_gas = P0 + 2*GAMMA_S/R0
    Pg  = gas_pressure(R, R0, P0_gas)
    Pt  = P_drive(t)
    Rddot = ((Pg-P0-Pt)/RHO
             - 4*ETA*Rdot/(RHO*R)
             - 2*GAMMA_S/(RHO*R)
             - 1.5*Rdot**2) / R
    return [Rdot, Rddot]

# ── Keller-Miksis ODE ─────────────────────────────────────
def km_ode(t, y):
    R, Rdot = y
    Rv = VDW_H * R0
    if R <= Rv*1.001: return [0.0, 0.0]

    M   = Rdot / C_L          # Mach number
    P0_gas = P0 + 2*GAMMA_S/R0
    Pg  = gas_pressure(R, R0, P0_gas)
    dPg = dgas_dt(R, Rdot, R0, P0_gas)
    Pt  = P_drive(t)
    dPt = dP_drive_dt(t)

    # Effective pressure terms
    P_eff   = Pg - P0 - Pt
    dP_eff  = dPg - dPt

    # KM equation:
    # (1 - M)R*Rddot + (3/2)(1 - M/3)Rdot²
    # = (1+M)/ρ * P_eff + R/(ρ*C_L)*dP_eff
    # - 4η*Rdot/(ρ*R) - 2γ/(ρ*R)

    lhs_coeff  = (1 - M)
    kin_coeff  = 1.5 * (1 - M/3)

    rhs = ((1+M)/RHO * P_eff
           + R/(RHO*C_L) * dP_eff
           - 4*ETA*Rdot/(RHO*R)
           - 2*GAMMA_S/(RHO*R))

    Rddot = (rhs - kin_coeff*Rdot**2) / (lhs_coeff*R + 1e-30)
    return [Rdot, Rddot]

# ══════════════════════════════════════════════════════════
# SOLVER
# ══════════════════════════════════════════════════════════
def solve(ode_func, label):
    T      = 1.0/FREQ
    t_span = (0, NCYC*T)
    t_eval = np.linspace(0, NCYC*T, NCYC*8000)
    sol = solve_ivp(ode_func, t_span, [R0, 0.0],
                    t_eval=t_eval, method='Radau',
                    rtol=1e-10, atol=1e-12,
                    max_step=T/5000)
    if not sol.success:
        print(f"  ⚠ {label}: {sol.message}")
    return sol

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics(sol_rpe, sol_km):
    print("\n" + "═"*65)
    print("  KELLER-MIKSIS vs RPE — Compressibility Comparison")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    for label, sol in [('RPE', sol_rpe), ('KM', sol_km)]:
        R    = sol.y[0]
        Rdot = sol.y[1]
        Rmax = np.max(R)
        Rmin = np.min(R)
        Vmax = np.max(np.abs(Rdot))
        Mmax = Vmax / C_L
        T_max= T_AMB * (Rmax/Rmin)**(3*(GAMMA_G-1))

        print(f"\n  {label}:")
        print(f"    R_max        = {Rmax*1e6:.3f} µm")
        print(f"    R_min        = {Rmin*1e9:.2f} nm")
        print(f"    R_max/R_min  = {Rmax/Rmin:.1f}×")
        print(f"    V_wall_max   = {Vmax:.1f} m/s")
        print(f"    Mach_max     = {Mmax:.4f}")
        print(f"    T_max (est.) = {T_max:.0f} K")

    # Differences
    R_rpe  = sol_rpe.y[0]
    R_km   = sol_km.y[0]
    Rmax_rpe = np.max(R_rpe); Rmin_rpe = np.min(R_rpe)
    Rmax_km  = np.max(R_km);  Rmin_km  = np.min(R_km)
    Vmax_rpe = np.max(np.abs(sol_rpe.y[1]))
    Vmax_km  = np.max(np.abs(sol_km.y[1]))

    print(f"\n  DIFFERENCES (RPE vs KM):")
    print(f"    ΔR_max       = {(Rmax_rpe-Rmax_km)*1e6:.3f} µm  "
          f"({(Rmax_rpe-Rmax_km)/Rmax_rpe*100:.2f}%)")
    print(f"    ΔR_min       = {(Rmin_rpe-Rmin_km)*1e9:.2f} nm")
    print(f"    ΔV_wall      = {(Vmax_rpe-Vmax_km):.1f} m/s  "
          f"({(Vmax_rpe-Vmax_km)/Vmax_rpe*100:.2f}%)")
    print(f"    ΔR_max/Rmin  = {Rmax_rpe/Rmin_rpe - Rmax_km/Rmin_km:.1f}×")

    Mmax = Vmax_rpe/C_L
    print(f"\n  COMPRESSIBILITY ASSESSMENT:")
    print(f"    Peak Mach    = {Mmax:.4f}")
    if Mmax > 0.1:
        print(f"    → M > 0.1: KM correction IS significant")
    else:
        print(f"    → M < 0.1: KM correction marginal")
    print(f"    KM reduces V_wall by radiation damping")
    print(f"    More accurate for near-sonic collapse")
    print("═"*65 + "\n")

# ══════════════════════════════════════════════════════════
# PLOTTING
# ══════════════════════════════════════════════════════════
def plot_all(sol_rpe, sol_km):
    fig = plt.figure(figsize=(14,9), facecolor=COLORS['bg'])
    gs  = gridspec.GridSpec(3, 2, figure=fig,
                            hspace=0.48, wspace=0.32,
                            left=0.08, right=0.97,
                            top=0.92, bottom=0.07)

    t_rpe = sol_rpe.t * 1e6
    t_km  = sol_km.t  * 1e6
    R_rpe = sol_rpe.y[0] * 1e6
    R_km  = sol_km.y[0]  * 1e6
    V_rpe = sol_rpe.y[1]
    V_km  = sol_km.y[1]

    # ── 1. Radius comparison ──────────────────────────────
    ax1 = fig.add_subplot(gs[0,:])
    ax1.plot(t_rpe, R_rpe, color=COLORS['rpe'],
             lw=1.5, label='RPE', alpha=0.9)
    ax1.plot(t_km,  R_km,  color=COLORS['km'],
             lw=1.5, ls='--', label='Keller-Miksis', alpha=0.9)
    ax1.set_xlabel('Time (µs)')
    ax1.set_ylabel('Radius (µm)')
    ax1.legend(fontsize=8, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'Bubble Radius — RPE vs Keller-Miksis')

    # ── 2. Wall velocity comparison ───────────────────────
    ax2 = fig.add_subplot(gs[1,0])
    ax2.plot(t_rpe, V_rpe, color=COLORS['rpe'], lw=1.2,
             label='RPE', alpha=0.9)
    ax2.plot(t_km,  V_km,  color=COLORS['km'],
             lw=1.2, ls='--', label='KM', alpha=0.9)
    ax2.axhline(-C_L, color=COLORS['opt'], lw=1,
                ls=':', label=f'c_L={C_L:.0f} m/s')
    ax2.set_xlabel('Time (µs)')
    ax2.set_ylabel('Ṙ (m/s)')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Wall Velocity — RPE vs KM')

    # ── 3. Mach number ────────────────────────────────────
    ax3 = fig.add_subplot(gs[1,1])
    M_rpe = np.abs(V_rpe) / C_L
    M_km  = np.abs(V_km)  / C_L
    ax3.semilogy(t_rpe, M_rpe+1e-6,
                 color=COLORS['rpe'], lw=1.2, label='RPE')
    ax3.semilogy(t_km,  M_km+1e-6,
                 color=COLORS['km'],  lw=1.2, ls='--', label='KM')
    ax3.axhline(0.1, color=COLORS['opt'], lw=1,
                ls=':', label='M=0.1 (KM threshold)')
    ax3.axhline(1.0, color='white', lw=0.8,
                ls=':', alpha=0.4, label='M=1 (sonic)')
    ax3.set_xlabel('Time (µs)')
    ax3.set_ylabel('Mach number |Ṙ/c_L|')
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'Mach Number vs Time')

    # ── 4. Phase portrait comparison ──────────────────────
    ax4 = fig.add_subplot(gs[2,0])
    ax4.plot(R_rpe, V_rpe, color=COLORS['rpe'],
             lw=0.8, alpha=0.8, label='RPE')
    ax4.plot(R_km,  V_km,  color=COLORS['km'],
             lw=0.8, alpha=0.8, ls='--', label='KM')
    ax4.set_xlabel('R (µm)')
    ax4.set_ylabel('Ṙ (m/s)')
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'Phase Portrait — RPE vs KM')

    # ── 5. Radius difference ──────────────────────────────
    ax5 = fig.add_subplot(gs[2,1])
    # Interpolate to common time grid
    t_common = np.linspace(max(t_rpe[0],t_km[0]),
                           min(t_rpe[-1],t_km[-1]), 5000)
    R_rpe_i  = np.interp(t_common, t_rpe, R_rpe)
    R_km_i   = np.interp(t_common, t_km,  R_km)
    dR       = R_rpe_i - R_km_i
    ax5.plot(t_common, dR,
             color=COLORS['opt'], lw=1.2)
    ax5.axhline(0, color='white', lw=0.5, alpha=0.4)
    ax5.set_xlabel('Time (µs)')
    ax5.set_ylabel('R_RPE − R_KM (µm)')
    style_ax(ax5, 'Radius Difference RPE − KM')

    fig.suptitle(
        "Keller-Miksis vs RPE  |  Compressibility Correction at M=0.97",
        color=COLORS['rpe'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "keller_miksis_vs_rpe.png"
    plt.savefig(outfile, dpi=150,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    T = 1.0/FREQ
    print(f"\n  Solving RPE...")
    sol_rpe = solve(rpe_ode, "RPE")
    print(f"  Solving Keller-Miksis...")
    sol_km  = solve(km_ode,  "KM")
    print_diagnostics(sol_rpe, sol_km)
    plot_all(sol_rpe, sol_km)
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
