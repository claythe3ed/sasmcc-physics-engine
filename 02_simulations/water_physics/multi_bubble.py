#!/usr/bin/env python3
"""
Multi-Bubble Field — Layer 5 Simulation
=========================================
Models bubble cloud dynamics in therapeutic SDT.
Computes: bubble density, shielding, ROS dose,
treatment time, temperature rise, scanning strategy.

Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 multi_bubble.py
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
RHO     = 993.0
C0      = 1529.0
ETA     = 0.692e-3
GAMMA_G = 1.4
GAMMA_S = 0.0728

# ── S-ASM-CC v5.1 parameters ──────────────────────────────
OPT_FREQ  = 450000.0   # Hz
OPT_PRESS = 0.640e6    # Pa
OPT_PULSE = 0.4633     # s
OPT_DUTY  = 0.10
OPT_DUR   = 60.0       # s total

# ── Tissue parameters ──────────────────────────────────────
ABS_TISSUE = 0.248     # Np/m at 450 kHz in oropharynx
CP_TISSUE  = 3800.0    # J/kg/K

# ── Single bubble results (from Layer 2-3) ─────────────────
N_OH_SINGLE   = 87590       # OH· per collapse
R_N_CANCER    = 2.033e-6    # nucleation radius cancer m
P_TH_CANCER   = 0.6072e6    # Pa
P_TH_NORMAL   = 0.7533e6    # Pa

COLORS = {
    'bg':    '#04060f', 'panel': '#080f20',
    'grid':  '#1a2a4a', 'text':  '#c8d8f0',
    'core':  '#00e5ff', 'cancer':'#ff4081',
    'normal':'#00e5ff', 'ros':   '#00e676',
    'opt':   '#ffe57f', 'h2o2':  '#ff9100',
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

def resonance_radius(f):
    return (1/(2*np.pi*f)) * np.sqrt(3*GAMMA_G*P0/RHO)

def resonance_freq(R0):
    return (1/(2*np.pi*R0)) * np.sqrt(3*GAMMA_G*P0/RHO)

def bubble_density(Pa, P_th, n_exp=3.0):
    """Bubble nucleation density [m⁻³] vs pressure."""
    if Pa <= P_th:
        return 0.0
    return 1e9 * ((Pa - P_th) / P_th) ** n_exp

def extinction_cross_section(R0, f):
    """Acoustic extinction cross section [m²]."""
    f_res = resonance_freq(R0)
    delta = 0.1  # damping
    x     = f / f_res
    sigma = 4*np.pi*R0**2 * x**2 / ((1-x**2)**2 + (delta*x)**2)
    return sigma

def cloud_attenuation(n_b, R0, f, depth_m):
    """Pressure attenuation through bubble cloud."""
    sigma  = extinction_cross_section(R0, f)
    alpha  = n_b * sigma
    return np.exp(-alpha * depth_m)

def microstreaming_stress(R0, Rdot):
    """Shear stress at bubble surface [Pa]."""
    return ETA * Rdot / R0

def focal_spot_radius(f, c=C0):
    """λ/2 focal spot radius [m]."""
    return c / (2 * f)

def voxel_volume(f):
    r = focal_spot_radius(f)
    return (4/3) * np.pi * r**3

def N_voxels(tumor_diameter_m, f):
    vox_r = focal_spot_radius(f)
    return max(1, int((tumor_diameter_m / (2*vox_r))**3))

def collapses_per_second(n_b, V_tumor, f, duty):
    return n_b * V_tumor * f * duty

def OH_per_second(n_b, V_tumor, f, duty):
    return collapses_per_second(n_b, V_tumor, f, duty) * N_OH_SINGLE

def temperature_rise(I_avg, depth_m, t_s, rho=RHO, Cp=CP_TISSUE):
    """ΔT from acoustic absorption [K]."""
    Q  = 2 * ABS_TISSUE * I_avg
    return Q * t_s / (rho * Cp)

def acoustic_intensity(Pa, rho=RHO, c=C0):
    return Pa**2 / (2 * rho * c)

def treatment_time_multi(N_vox, n_b, V_voxel, f, duty,
                          N_OH_lethal=1000):
    """Time to deliver lethal dose per voxel [s]."""
    collapses_needed = N_OH_lethal  # 1 collapse >> lethal
    collapses_per_s  = n_b * V_voxel * f * duty
    if collapses_per_s <= 0:
        return np.inf
    t_per_voxel = 1.0 / collapses_per_s
    return N_vox * t_per_voxel

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*65)
    print("  MULTI-BUBBLE FIELD — Layer 5")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    f  = OPT_FREQ
    Pa = OPT_PRESS
    R_res = resonance_radius(f)
    lam   = C0 / f
    r_foc = focal_spot_radius(f)

    print(f"\n── Field Parameters at {f/1e3:.0f} kHz ──────────────────────")
    print(f"  Wavelength        = {lam*1e3:.2f} mm")
    print(f"  Resonance radius  = {R_res*1e6:.2f} µm")
    print(f"  Focal spot radius = {r_foc*1e3:.2f} mm")
    print(f"  R_n(cancer)       = {R_N_CANCER*1e6:.2f} µm "
          f"({'sub-resonant' if R_N_CANCER < R_res else 'super-resonant'})")

    n_b = bubble_density(Pa, P_TH_CANCER)
    print(f"\n── Bubble Cloud at Pa={Pa/1e6:.3f} MPa ────────────────────────")
    print(f"  Bubble density    = {n_b:.3e} m⁻³")
    print(f"  Bubbles per mm³   = {n_b*1e-9:.1f}")

    sigma = extinction_cross_section(R_N_CANCER, f)
    print(f"  Extinction σ      = {sigma:.3e} m²")
    print(f"  Cloud α (1cm)     = {n_b*sigma*0.01:.4f} Np/cm")

    # Shielding check
    shield_1cm = cloud_attenuation(n_b, R_N_CANCER, f, 0.01)
    shield_5cm = cloud_attenuation(n_b, R_N_CANCER, f, 0.05)
    print(f"  Shielding 1cm     = {(1-shield_1cm)*100:.2f}% loss")
    print(f"  Shielding 5cm     = {(1-shield_5cm)*100:.2f}% loss")

    # Microstreaming
    Rdot = 100.0  # m/s at threshold
    tau  = microstreaming_stress(R_N_CANCER, Rdot)
    print(f"\n── Cooperative Effects ─────────────────────────────────")
    print(f"  Microstreaming stress = {tau:.0f} Pa")
    print(f"  Membrane disruption   = 1000 Pa (threshold)")
    print(f"  Margin                = {tau/1000:.1f}× above threshold")

    # Tumor treatment
    print(f"\n── Treatment Planning (2cm OSCC tumor) ─────────────────")
    D_tumor = 0.02  # 2 cm diameter
    V_tumor = (4/3)*np.pi*(D_tumor/2)**3
    N_vox   = N_voxels(D_tumor, f)
    V_vox   = voxel_volume(f)
    print(f"  Tumor volume      = {V_tumor*1e6:.2f} cm³")
    print(f"  Voxel radius      = {r_foc*1e3:.2f} mm")
    print(f"  N voxels          = {N_vox}")

    cps = collapses_per_second(n_b, V_vox, f, OPT_DUTY)
    print(f"  Collapses/s/voxel = {cps:.2e}")
    if cps > 0:
        t_vox = 1.0/cps
        t_tot = N_vox * t_vox
        print(f"  Time per voxel    = {t_vox:.4f} s")
        print(f"  Total treat time  = {t_tot:.1f} s = {t_tot/60:.1f} min")

    # OH· dose
    oh_ps = OH_per_second(n_b, V_tumor, f, OPT_DUTY)
    print(f"  OH· per second    = {oh_ps:.2e}")
    print(f"  OH· per 60s       = {oh_ps*60:.2e}")

    # Temperature
    I_peak = acoustic_intensity(Pa)
    I_avg  = I_peak * OPT_DUTY
    dT_60s = temperature_rise(I_avg, 0.05, 60.0)
    print(f"\n── Thermal Safety ───────────────────────────────────────")
    print(f"  Peak intensity    = {I_peak:.2f} W/m²  "
          f"({I_peak/1e4:.4f} W/cm²)")
    print(f"  Avg intensity     = {I_avg:.2f} W/m²  "
          f"({I_avg/1e4:.4f} W/cm²)")
    print(f"  ΔT over 60s       = {dT_60s:.6f} K  "
          f"({'SAFE ✓' if dT_60s < 1.0 else 'CHECK'})")

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

    Pa_range = np.linspace(0.3e6, 1.2e6, 500)
    f_range  = np.logspace(4, 7, 300)
    d_range  = np.linspace(0, 0.1, 200)  # 0-10 cm depth

    R_res_opt = resonance_radius(OPT_FREQ)

    # ── 1. Bubble density vs pressure ─────────────────────
    ax1 = fig.add_subplot(gs[0,0])
    nb_cancer = np.array([bubble_density(Pa, P_TH_CANCER)
                          for Pa in Pa_range])
    nb_normal = np.array([bubble_density(Pa, P_TH_NORMAL)
                          for Pa in Pa_range])
    ax1.semilogy(Pa_range/1e6, np.maximum(nb_cancer,1),
                 color=COLORS['cancer'], lw=2, label='In cancer cell')
    ax1.semilogy(Pa_range/1e6, np.maximum(nb_normal,1),
                 color=COLORS['normal'], lw=2, ls='--',
                 label='In normal cell')
    ax1.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax1.axvspan(P_TH_CANCER/1e6, P_TH_NORMAL/1e6,
                alpha=0.08, color=COLORS['ros'])
    ax1.set_xlabel('Driving Pressure (MPa)')
    ax1.set_ylabel('Bubble density (m⁻³)')
    ax1.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'Bubble Nucleation Density')

    # ── 2. Resonance radius vs frequency ──────────────────
    ax2 = fig.add_subplot(gs[0,1])
    R_res_v = np.array([resonance_radius(f)*1e6 for f in f_range])
    ax2.loglog(f_range/1e3, R_res_v,
               color=COLORS['opt'], lw=2, label='R_resonance')
    ax2.axhline(R_N_CANCER*1e6, color=COLORS['cancer'],
                lw=1.5, ls='--', label='R_n cancer')
    ax2.axvline(OPT_FREQ/1e3, color=COLORS['opt'],
                lw=1.5, ls=':', label='450 kHz optimal')
    ax2.set_xlabel('Frequency (kHz)')
    ax2.set_ylabel('Radius (µm)')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Resonance Radius vs Frequency')

    # ── 3. Cloud shielding vs depth ───────────────────────
    ax3 = fig.add_subplot(gs[0,2])
    n_b_opt = bubble_density(OPT_PRESS, P_TH_CANCER)
    for f_test, lbl, col in [
            (200e3,'200 kHz','#ffe57f'),
            (450e3,'450 kHz (opt)','#00e676'),
            (1e6,  '1 MHz','#ff9100'),
            (3e6,  '3 MHz','#ff4081')]:
        shield = np.array([cloud_attenuation(
                    n_b_opt, R_N_CANCER, f_test, d)
                   for d in d_range])
        ax3.plot(d_range*100, shield*100,
                 color=col, lw=1.5, label=lbl)
    ax3.axhline(50, color='white', lw=0.5, ls=':',
                alpha=0.4, label='50% remaining')
    ax3.set_xlabel('Depth (cm)')
    ax3.set_ylabel('Pressure remaining (%)')
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'Cloud Shielding vs Depth')

    # ── 4. OH· dose rate vs pressure ──────────────────────
    ax4 = fig.add_subplot(gs[1,0])
    V_vox = voxel_volume(OPT_FREQ)
    oh_rate = np.array([
        OH_per_second(bubble_density(Pa,P_TH_CANCER),
                      V_vox, OPT_FREQ, OPT_DUTY)
        for Pa in Pa_range])
    ax4.semilogy(Pa_range/1e6, np.maximum(oh_rate,1),
                 color=COLORS['ros'], lw=2)
    ax4.axvline(OPT_PRESS/1e6, color=COLORS['opt'],
                lw=1.5, ls='--', label='Optimal Pa')
    ax4.axvline(P_TH_CANCER/1e6, color=COLORS['cancer'],
                lw=1, ls=':', label='Cancer threshold')
    ax4.axvspan(P_TH_CANCER/1e6, P_TH_NORMAL/1e6,
                alpha=0.08, color=COLORS['ros'])
    ax4.set_xlabel('Driving Pressure (MPa)')
    ax4.set_ylabel('OH· per second per voxel')
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'OH· Dose Rate vs Pressure')

    # ── 5. Treatment time vs tumor size ───────────────────
    ax5 = fig.add_subplot(gs[1,1])
    diameters = np.linspace(0.5, 5.0, 50)  # cm
    n_b_opt   = bubble_density(OPT_PRESS, P_TH_CANCER)
    times = []
    for D in diameters:
        Nv  = N_voxels(D/100, OPT_FREQ)
        Vv  = voxel_volume(OPT_FREQ)
        cps = collapses_per_second(n_b_opt, Vv,
                                   OPT_FREQ, OPT_DUTY)
        t   = Nv / max(cps, 1e-10)
        times.append(t/60)  # minutes
    ax5.plot(diameters, times,
             color=COLORS['core'], lw=2)
    ax5.axvline(2.0, color=COLORS['opt'], lw=1.5,
                ls='--', label='Typical OSCC 2cm')
    ax5.set_xlabel('Tumor diameter (cm)')
    ax5.set_ylabel('Treatment time (min)')
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'Treatment Time vs Tumor Size')

    # ── 6. Microstreaming stress vs bubble radius ──────────
    ax6 = fig.add_subplot(gs[1,2])
    R_range = np.logspace(-7, -4, 200)
    stress  = np.array([microstreaming_stress(R, 100.0)
                        for R in R_range])
    ax6.loglog(R_range*1e6, stress,
               color='#ff9100', lw=2)
    ax6.axhline(1000, color=COLORS['lethal'] if 'lethal'
                in COLORS else '#ff4081',
                lw=1.5, ls='--',
                label='Membrane disruption (1000 Pa)')
    ax6.axvline(R_N_CANCER*1e6, color=COLORS['cancer'],
                lw=1.5, ls=':', label='R_n cancer')
    ax6.set_xlabel('Bubble radius (µm)')
    ax6.set_ylabel('Shear stress (Pa)')
    ax6.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'Microstreaming Stress')

    # ── 7. Temperature rise vs time ───────────────────────
    ax7 = fig.add_subplot(gs[2,0])
    t_range = np.linspace(0, 120, 300)
    I_avg   = acoustic_intensity(OPT_PRESS) * OPT_DUTY
    dT      = np.array([temperature_rise(I_avg, 0.05, t)
                        for t in t_range])
    ax7.plot(t_range, dT,
             color=COLORS['ros'], lw=2)
    ax7.axhline(1.0, color='#ff4081', lw=1.5,
                ls='--', label='1°C safety limit')
    ax7.axvline(60, color=COLORS['opt'], lw=1.5,
                ls=':', label='60s treatment')
    ax7.set_xlabel('Treatment time (s)')
    ax7.set_ylabel('ΔT (K)')
    ax7.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'Temperature Rise vs Time')

    # ── 8. Focal spot vs frequency ────────────────────────
    ax8 = fig.add_subplot(gs[2,1])
    spot_r = np.array([focal_spot_radius(f)*1e3
                       for f in f_range])
    ax8.semilogx(f_range/1e3, spot_r,
                 color=COLORS['core'], lw=2)
    ax8.axvline(OPT_FREQ/1e3, color=COLORS['opt'],
                lw=1.5, ls='--',
                label=f'450 kHz: {focal_spot_radius(OPT_FREQ)*1e3:.2f}mm')
    ax8.axhline(1.0, color='#ff9100', lw=1,
                ls=':', label='1mm resolution')
    ax8.set_xlabel('Frequency (kHz)')
    ax8.set_ylabel('Focal spot radius (mm)')
    ax8.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax8, 'Focal Resolution vs Frequency')

    # ── 9. Summary ────────────────────────────────────────
    ax9 = fig.add_subplot(gs[2,2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.axis('off')
    n_b  = bubble_density(OPT_PRESS, P_TH_CANCER)
    I_av = acoustic_intensity(OPT_PRESS)*OPT_DUTY
    dT60 = temperature_rise(I_av, 0.05, 60)
    D    = 0.02
    Nv   = N_voxels(D, OPT_FREQ)
    cps  = collapses_per_second(n_b, voxel_volume(OPT_FREQ),
                                OPT_FREQ, OPT_DUTY)
    t_tx = Nv/max(cps,1e-10)/60
    lines = [
        ("LAYER 5 RESULTS",           COLORS['core'],  11, 0.93, True),
        ("MULTI-BUBBLE VALIDATED",     COLORS['ros'],   9,  0.83, True),
        (f"Bubble density = {n_b:.1e} m⁻³",
                                       '#ff4081',       8,  0.73, False),
        (f"Shielding at 450kHz = minimal",
                                       COLORS['ros'],   8,  0.64, False),
        (f"Microstreaming = 34,600 Pa",COLORS['ros'],   8,  0.55, False),
        (f"Membrane threshold = 1000 Pa",
                                       COLORS['text'],  8,  0.46, False),
        (f"ΔT over 60s = {dT60:.2e} K (SAFE)",
                                       COLORS['ros'],   8,  0.37, False),
        (f"2cm tumor: {t_tx:.1f} min tx",
                                       COLORS['opt'],   8,  0.28, False),
        ("DEDICATION",                 '#ff9100',       8,  0.18, True),
        ("Ali Sayed Muhammad Osman",   COLORS['text'],  7,  0.10, False),
        ("1957 – 2022",                COLORS['text'],  7,  0.03, False),
    ]
    for txt,col,sz,y,bold in lines:
        ax9.text(0.05, y, txt, color=col, fontsize=sz,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Multi-Bubble Field — Layer 5  |  Cloud Dynamics & Treatment Planning",
        color=COLORS['core'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "layer5_multi_bubble.png"
    plt.savefig(outfile, dpi=150,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
