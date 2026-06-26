#!/usr/bin/env python3
"""
Rayleigh-Plesset Equation Solver
==================================
Simulates single bubble dynamics under acoustic driving.
Foundation of all sonoluminescence and SDT simulations.

Usage:
  python3 rp_solver.py              # default SBSL parameters
  python3 rp_solver.py --pa 1.5     # custom driving pressure (atm)
  python3 rp_solver.py --r0 4       # custom equilibrium radius (um)
  python3 rp_solver.py --freq 26500 # custom frequency (Hz)
  python3 rp_solver.py --cycles 5   # number of acoustic cycles
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')  # no display needed — saves to file
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import argparse
import os
from pathlib import Path

# ── Output directory ───────────────────────────────────────
OUT = Path.home() / "sonoluminescence/02_simulations/outputs"
OUT.mkdir(parents=True, exist_ok=True)

# ── Physical constants ─────────────────────────────────────
RHO     = 998.0      # water density          [kg/m³]
ETA     = 1.002e-3   # dynamic viscosity      [Pa·s]
GAMMA_S = 0.0728     # surface tension        [N/m]
P0      = 101325.0   # ambient pressure       [Pa]
C_L     = 1497.0     # speed of sound water   [m/s]
T_AMB   = 293.15     # ambient temperature    [K]
K_B     = 1.381e-23  # Boltzmann constant     [J/K]
GAMMA_G = 1.4        # polytropic index (air) [-]

# ── Van der Waals hard core ────────────────────────────────
# Prevents R → 0 singularity. h = R_min/R0 ≈ 0.0802 for air
VDW_H   = 0.0802

def parse_args():
    ap = argparse.ArgumentParser(description="Rayleigh-Plesset Solver")
    ap.add_argument("--pa",    type=float, default=1.3,
                    help="Acoustic driving amplitude [atm], default 1.3")
    ap.add_argument("--r0",    type=float, default=5.0,
                    help="Equilibrium bubble radius [µm], default 5.0")
    ap.add_argument("--freq",  type=float, default=26500.0,
                    help="Driving frequency [Hz], default 26500")
    ap.add_argument("--cycles",type=int,   default=4,
                    help="Number of acoustic cycles, default 4")
    return ap.parse_args()


def make_solver(R0, Pa, freq, n_cycles):
    """
    Build and run the RPE system.

    The RPE rewritten as two first-order ODEs:
      y[0] = R       (bubble radius)
      y[1] = Rdot    (wall velocity)

    Full equation:
      R·R̈ + (3/2)·Ṙ² = (1/ρ)[Pg - P0 - Pa·sin(2πft)
                         - 4η·Ṙ/R - 2γ/R]

    With Van der Waals gas pressure:
      Pg = P0·(R0³ - h³·R0³)/(R³ - h³·R0³)^γ   (adiabatic)
    """
    omega  = 2 * np.pi * freq
    R_vdw  = VDW_H * R0          # hard core radius
    P0_gas = P0 + 2*GAMMA_S/R0   # initial gas pressure (Laplace)

    def rp_ode(t, y):
        R, Rdot = y

        # Guard against collapse singularity
        R_min = R_vdw * 1.001
        if R <= R_min:
            return [0.0, 0.0]

        # Van der Waals adiabatic gas pressure
        num   = R0**3 - R_vdw**3
        denom = R**3  - R_vdw**3
        if denom <= 0:
            return [0.0, 0.0]
        Pg = P0_gas * (num / denom) ** GAMMA_G

        # Driving pressure
        Pt = Pa * np.sin(omega * t)

        # Pressure terms
        pressure  = (Pg - P0 - Pt) / RHO
        viscosity = -4.0 * ETA * Rdot / (RHO * R)
        surface   = -2.0 * GAMMA_S / (RHO * R)

        Rddot = (pressure + viscosity + surface - 1.5 * Rdot**2) / R
        return [Rdot, Rddot]

    T      = 1.0 / freq
    t_span = (0.0, n_cycles * T)
    t_eval = np.linspace(*t_span, n_cycles * 8000)
    y0     = [R0, 0.0]

    print(f"\n  Solving RPE...")
    print(f"  R0    = {R0*1e6:.1f} µm")
    print(f"  Pa    = {Pa/P0:.2f} atm")
    print(f"  freq  = {freq/1000:.2f} kHz")
    print(f"  VdW h = {VDW_H} → R_min = {R_vdw*1e6:.3f} µm")

    sol = solve_ivp(
        rp_ode, t_span, y0,
        t_eval=t_eval,
        method='Radau',      # stiff solver — essential for RPE
        rtol=1e-10,
        atol=1e-12,
        dense_output=False,
    )

    if not sol.success:
        print(f"  ⚠  Solver warning: {sol.message}")
    else:
        print(f"  ✓  Solved {len(sol.t)} points")

    return sol, T


def compute_temperature(R, R0):
    """
    Estimate internal temperature via adiabatic heating.
    T = T_amb * (V0/V)^(gamma-1) = T_amb * (R0/R)^(3*(gamma-1))
    Only meaningful near collapse (R << R0).
    """
    ratio = np.where(R > 0, R0 / R, 1.0)
    return T_AMB * ratio ** (3.0 * (GAMMA_G - 1.0))


def find_collapse_events(t, R, R0):
    """Find indices where bubble reaches local minimum (collapse points)."""
    collapses = []
    for i in range(1, len(R)-1):
        if R[i] < R[i-1] and R[i] < R[i+1]:
            if R[i] < 0.3 * R0:   # only real collapses
                collapses.append(i)
    return collapses


def plot_results(sol, T, R0, Pa, freq, n_cycles):
    t = sol.t
    R = sol.y[0]
    Rdot = sol.y[1]
    Temp = compute_temperature(R, R0)

    collapses = find_collapse_events(t, R, R0)
    R_max = np.max(R)
    R_min_collapse = np.min(R[R < 0.5*R0]) if np.any(R < 0.5*R0) else R0
    T_max = np.max(Temp[R < 0.5*R0]) if np.any(R < 0.5*R0) else T_AMB
    V_max = np.min(Rdot)   # most negative = fastest inward

    # ── Print key diagnostics ──────────────────────────────
    print(f"\n  ── Collapse Diagnostics ──────────────────────")
    print(f"  R_max          = {R_max*1e6:.2f} µm")
    print(f"  R_min          = {R_min_collapse*1e9:.2f} nm")
    print(f"  R_max/R_min    = {R_max/R_min_collapse:.1f}×")
    print(f"  T_max (est.)   = {T_max:.0f} K  ({T_max/5778:.1f}× sun surface)")
    print(f"  Peak wall vel  = {abs(V_max):.0f} m/s  ({abs(V_max)/C_L:.2f}× speed of sound)")
    print(f"  Collapse events: {len(collapses)}")
    print(f"  ─────────────────────────────────────────────")

    # ── Plot ───────────────────────────────────────────────
    fig = plt.figure(figsize=(13, 9), facecolor='#04060f')
    gs  = gridspec.GridSpec(3, 2, figure=fig,
                            hspace=0.45, wspace=0.35,
                            left=0.08, right=0.96,
                            top=0.90, bottom=0.07)

    COLORS = {
        'radius':  '#00e5ff',
        'vel':     '#7c4dff',
        'temp':    '#ff4081',
        'drive':   '#ff9100',
        'phase':   '#00e676',
        'grid':    '#1a2a4a',
        'text':    '#c8d8f0',
        'bg':      '#04060f',
        'panel':   '#080f20',
    }

    def style_ax(ax, title):
        ax.set_facecolor(COLORS['panel'])
        ax.tick_params(colors=COLORS['text'], labelsize=8)
        ax.xaxis.label.set_color(COLORS['text'])
        ax.yaxis.label.set_color(COLORS['text'])
        ax.title.set_color(COLORS['text'])
        ax.set_title(title, fontsize=9, pad=6)
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS['grid'])
        ax.grid(True, color=COLORS['grid'], linewidth=0.5, alpha=0.7)

    t_us = t * 1e6   # time in microseconds

    # 1. Radius vs time
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t_us, R*1e6, color=COLORS['radius'], lw=1.2, label='R(t)')
    for ci in collapses:
        ax1.axvline(t[ci]*1e6, color='#ff4081', alpha=0.4, lw=0.8)
    ax1.set_xlabel('Time (µs)')
    ax1.set_ylabel('Radius (µm)')
    style_ax(ax1, 'Bubble Radius  —  Rayleigh-Plesset Solution')
    ax1.legend(fontsize=8, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)

    # 2. Wall velocity
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t_us, Rdot, color=COLORS['vel'], lw=1.0)
    ax2.axhline(-C_L, color='#ff9100', lw=0.8, ls='--', alpha=0.7,
                label=f'Speed of sound ({C_L:.0f} m/s)')
    ax2.set_xlabel('Time (µs)')
    ax2.set_ylabel('Ṙ (m/s)')
    style_ax(ax2, 'Wall Velocity')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)

    # 3. Temperature estimate
    ax3 = fig.add_subplot(gs[1, 1])
    # only show near-collapse regions (R < 0.5 R0)
    mask = R < 0.5 * R0
    if np.any(mask):
        ax3.semilogy(t_us[mask], Temp[mask],
                     color=COLORS['temp'], lw=1.0, ls='none',
                     marker='.', markersize=1)
    ax3.axhline(5778,   color='#ff9100', lw=0.8, ls='--',
                label='Sun surface (5778 K)')
    ax3.axhline(10000,  color='#ffe57f', lw=0.8, ls=':',
                label='10,000 K')
    ax3.set_xlabel('Time (µs)')
    ax3.set_ylabel('T (K)  [log scale]')
    style_ax(ax3, 'Collapse Temperature (adiabatic estimate)')
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)

    # 4. Phase portrait R vs Rdot
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(R*1e6, Rdot, color=COLORS['phase'],
             lw=0.6, alpha=0.8)
    ax4.set_xlabel('R (µm)')
    ax4.set_ylabel('Ṙ (m/s)')
    style_ax(ax4, 'Phase Portrait  R vs Ṙ')

    # 5. Driving pressure
    ax5 = fig.add_subplot(gs[2, 1])
    t_one = np.linspace(0, T, 1000)
    P_drive = Pa * np.sin(2*np.pi*freq*t_one)
    ax5.plot(t_one*1e6, P_drive/P0,
             color=COLORS['drive'], lw=1.2)
    ax5.axhline(0, color=COLORS['grid'], lw=0.5)
    ax5.set_xlabel('Time (µs)')
    ax5.set_ylabel('P / P₀')
    style_ax(ax5, f'Driving Pressure  ({freq/1000:.1f} kHz)')

    # Title
    fig.suptitle(
        f"Rayleigh–Plesset  |  R₀={R0*1e6:.0f} µm  "
        f"Pa={Pa/P0:.2f} atm  f={freq/1000:.1f} kHz",
        color=COLORS['radius'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / f"rp_R{R0*1e6:.0f}um_Pa{Pa/P0:.2f}atm.png"
    plt.savefig(outfile, dpi=150, facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  ✅ Plot saved → {outfile}")
    return outfile


def main():
    args  = parse_args()
    R0    = args.r0   * 1e-6     # µm → m
    Pa    = args.pa   * P0       # atm → Pa
    freq  = args.freq
    n_cyc = args.cycles

    sol, T = make_solver(R0, Pa, freq, n_cyc)
    plot_results(sol, T, R0, Pa, freq, n_cyc)

    print(f"\n  Open plot:")
    print(f"  termux-open ~/sonoluminescence/02_simulations/outputs/")


if __name__ == "__main__":
    main()
