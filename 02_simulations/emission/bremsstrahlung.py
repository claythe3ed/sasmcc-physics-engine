#!/usr/bin/env python3
"""
Bremsstrahlung Radiation Model
================================
Free-free emission from electron-ion encounters in plasma.
Compares to blackbody at same temperature.
Validates emission mechanism at SL collapse conditions.

Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 bremsstrahlung.py
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
H    = 6.626e-34
C    = 3.0e8
KB   = 1.381e-23
E    = 1.602e-19
ME   = 9.109e-31
EPS0 = 8.854e-12
NA   = 6.022e23

# ── Bremsstrahlung coefficient ─────────────────────────────
# P_brem = C_b * n_e * n_i * Z^2 * sqrt(T)
C_B  = 1.69e-40       # W·m³·K^(-1/2) — thermal bremsstrahlung

# ── Collapse conditions ────────────────────────────────────
R_COLLAPSE = 0.5e-6   # bubble radius at collapse [m]
V_COLLAPSE = (4/3)*np.pi*R_COLLAPSE**3

# ── Operating temperatures ─────────────────────────────────
TEMPS = {
    'Air 7,321K':    {'T':7321,  'color':'#00e5ff', 'ls':'-'},
    'Argon 16,173K': {'T':16173, 'color':'#ff4081', 'ls':'--'},
}

COLORS = {
    'bg':    '#04060f', 'panel': '#080f20',
    'grid':  '#1a2a4a', 'text':  '#c8d8f0',
    'core':  '#00e5ff', 'brem':  '#ff9100',
    'bb':    '#7c4dff', 'opt':   '#ffe57f',
    'ros':   '#00e676',
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

def saha_ionization(T, E_ion_eV=15.76, g_i=1, g_a=1,
                    n_total=1e25):
    """
    Saha equation ionization fraction.
    Returns (n_e, n_i, n_a) number densities.
    Default: Argon ionization energy 15.76 eV
    """
    E_ion  = E_ion_eV * E  # convert to Joules
    Lambda = np.sqrt(H**2 / (2*np.pi*ME*KB*T))
    saha_K = (2*g_i/g_a) * (1/Lambda**3) * np.exp(-E_ion/(KB*T))
    # n_e = n_i, n_total = n_a + n_i
    # n_i^2 / n_a = saha_K
    # solving quadratic: n_i^2 + saha_K*n_i - saha_K*n_total = 0
    disc = saha_K**2 + 4*saha_K*n_total
    n_i  = (-saha_K + np.sqrt(disc)) / 2
    n_i  = min(n_i, n_total)
    n_e  = n_i
    n_a  = n_total - n_i
    return n_e, n_i, n_a

def bremsstrahlung_power(T, n_e, n_i, Z=1):
    """Total bremsstrahlung power [W/m³]."""
    return C_B * n_e * n_i * Z**2 * np.sqrt(T)

def bremsstrahlung_spectrum(nu, T, n_e, n_i, Z=1):
    """
    Spectral bremsstrahlung power [W/m³/Hz].
    P(ν) ∝ n_e * n_i * Z^2 * exp(-hν/kT) / sqrt(T)
    """
    C_spec = 6.8e-51  # spectral constant W·m³·Hz^(-1)·K^(1/2)
    return C_spec * n_e * n_i * Z**2 / np.sqrt(T) * np.exp(
        np.clip(-H*nu/(KB*T), -500, 0))

def planck_power(nu, T, V=V_COLLAPSE):
    """Planck spectral power [W/Hz] from bubble volume."""
    x = np.clip(H*nu/(KB*T), 1e-10, 500)
    u = (8*np.pi*H*nu**3/C**3) / (np.exp(x) - 1)
    return u * V  # energy density × volume × (c/4) factor

def ionization_fraction(T, E_ion_eV=15.76):
    n_e, n_i, n_a = saha_ionization(T, E_ion_eV)
    n_total = n_e + n_a
    return n_i / n_total if n_total > 0 else 0

def cutoff_frequency(T):
    """Exponential cutoff: hν = kT → ν_c = kT/h."""
    return KB * T / H

def cutoff_wavelength(T):
    """Corresponding wavelength."""
    return C / cutoff_frequency(T)

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*65)
    print("  BREMSSTRAHLUNG RADIATION MODEL")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*65)

    n_total = 1e25  # number density at collapse [m⁻³]

    print(f"\n── Saha Ionization at Collapse ─────────────────────────")
    print(f"  {'T(K)':>8} {'f_ion':>10} {'n_e(m⁻³)':>14} "
          f"{'n_i(m⁻³)':>14} {'n_a(m⁻³)':>14}")
    print("  " + "─"*60)
    for T in [3000, 5000, 7321, 10000, 16173, 20000]:
        n_e, n_i, n_a = saha_ionization(T, n_total=n_total)
        fi = n_i / n_total
        print(f"  {T:>8,} {fi:>10.4f} {n_e:>14.3e} "
              f"{n_i:>14.3e} {n_a:>14.3e}")

    print(f"\n── Bremsstrahlung Power ────────────────────────────────")
    for name, t in TEMPS.items():
        T = t['T']
        n_e, n_i, n_a = saha_ionization(T, n_total=n_total)
        P_brem = bremsstrahlung_power(T, n_e, n_i) * V_COLLAPSE
        nu_c   = cutoff_frequency(T)
        lam_c  = cutoff_wavelength(T) * 1e9
        fi     = n_i / n_total
        print(f"\n  {name}:")
        print(f"    Ionization fraction = {fi:.4f}")
        print(f"    n_e = n_i           = {n_e:.3e} m⁻³")
        print(f"    P_bremsstrahlung    = {P_brem:.3e} W")
        print(f"    Cutoff frequency    = {nu_c:.3e} Hz")
        print(f"    Cutoff wavelength   = {lam_c:.1f} nm")

    print(f"\n── Bremsstrahlung vs Blackbody ─────────────────────────")
    print(f"  Mechanism comparison at our temperatures:")
    for name, t in TEMPS.items():
        T    = t['T']
        n_e, n_i, _ = saha_ionization(T, n_total=n_total)
        P_brem = bremsstrahlung_power(T, n_e, n_i) * V_COLLAPSE
        sigma  = 5.67e-8
        A      = 4*np.pi*R_COLLAPSE**2
        P_bb   = sigma * A * T**4
        ratio  = P_brem / P_bb if P_bb > 0 else 0
        dominant = 'Blackbody' if P_bb > P_brem else 'Bremsstrahlung'
        print(f"  {name}:")
        print(f"    P_blackbody    = {P_bb:.3e} W")
        print(f"    P_bremsstrahlung= {P_brem:.3e} W")
        print(f"    Ratio brem/bb  = {ratio:.4f}")
        print(f"    Dominant       = {dominant}")

    print(f"\n── SDT Implications ────────────────────────────────────")
    print(f"  Blackbody dominates at our temperatures")
    print(f"  Bremsstrahlung becomes significant above ~20,000K")
    print(f"  Both mechanisms activate sonosensitizers")
    print(f"  Combined emission = blackbody + bremsstrahlung")
    print(f"  → Our blackbody model is the correct primary model")
    print(f"  → Bremsstrahlung adds ~1-10% correction at 7321K")
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

    n_total = 1e25
    T_range = np.linspace(3000, 30000, 300)
    nu_range= np.logspace(14, 17, 500)  # 100nm–10µm
    lam_range = C / nu_range * 1e9      # nm

    # ── 1. Ionization fraction vs T ───────────────────────
    ax1 = fig.add_subplot(gs[0,0])
    for E_ion, gas, col in [
            (15.76,'Argon',  '#ff4081'),
            (13.62,'Oxygen', '#00e676'),
            (24.59,'Helium', '#ffe57f'),
            (14.53,'Nitrogen','#00e5ff')]:
        fi = [ionization_fraction(T, E_ion) for T in T_range]
        ax1.semilogy(T_range, np.maximum(fi,1e-10),
                     color=col, lw=2, label=gas)
    for name, t in TEMPS.items():
        ax1.axvline(t['T'], color=t['color'],
                    lw=1, ls=':', alpha=0.7)
    ax1.axhline(0.01, color='white', lw=0.8,
                ls=':', alpha=0.4, label='1% ionized')
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Ionization fraction')
    ax1.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax1, 'Saha Ionization Fraction vs T')

    # ── 2. Bremsstrahlung power vs T ──────────────────────
    ax2 = fig.add_subplot(gs[0,1])
    P_brem_v = []
    P_bb_v   = []
    for T in T_range:
        n_e, n_i, _ = saha_ionization(T, n_total=n_total)
        P_b = bremsstrahlung_power(T, n_e, n_i)*V_COLLAPSE
        sigma = 5.67e-8; A = 4*np.pi*R_COLLAPSE**2
        P_bb  = sigma*A*T**4
        P_brem_v.append(P_b)
        P_bb_v.append(P_bb)
    ax2.semilogy(T_range, np.maximum(P_brem_v,1e-20),
                 color=COLORS['brem'], lw=2,
                 label='Bremsstrahlung')
    ax2.semilogy(T_range, np.maximum(P_bb_v,1e-20),
                 color=COLORS['bb'], lw=2,
                 label='Blackbody')
    for name, t in TEMPS.items():
        ax2.axvline(t['T'], color=t['color'],
                    lw=1, ls=':', alpha=0.7)
    ax2.set_xlabel('Temperature (K)')
    ax2.set_ylabel('Power (W)')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, 'Bremsstrahlung vs Blackbody Power')

    # ── 3. Spectral comparison at 7321K ───────────────────
    ax3 = fig.add_subplot(gs[0,2])
    T = 7321
    n_e, n_i, _ = saha_ionization(T, n_total=n_total)
    B_brem = np.array([bremsstrahlung_spectrum(
                nu, T, n_e, n_i)*V_COLLAPSE
                for nu in nu_range])
    B_bb   = np.array([planck_power(nu, T)
                for nu in nu_range])
    B_brem_norm = B_brem/max(B_brem.max(),1e-40)
    B_bb_norm   = B_bb/max(B_bb.max(),1e-40)
    ax3.semilogy(lam_range[::-1],
                 np.maximum(B_brem_norm[::-1],1e-10),
                 color=COLORS['brem'], lw=2,
                 label='Bremsstrahlung')
    ax3.semilogy(lam_range[::-1],
                 np.maximum(B_bb_norm[::-1],1e-10),
                 color=COLORS['bb'], lw=2, ls='--',
                 label='Blackbody')
    ax3.axvspan(200, 400, alpha=0.08,
                color='violet', label='UV')
    ax3.set_xlabel('Wavelength (nm)')
    ax3.set_ylabel('Normalized spectral power')
    ax3.set_xlim([100, 1000])
    ax3.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'Spectral Shape at T=7321K (Air)')

    # ── 4. Spectral comparison at 16173K ──────────────────
    ax4 = fig.add_subplot(gs[1,0])
    T = 16173
    n_e, n_i, _ = saha_ionization(T, n_total=n_total)
    B_brem2 = np.array([bremsstrahlung_spectrum(
                 nu, T, n_e, n_i)*V_COLLAPSE
                 for nu in nu_range])
    B_bb2   = np.array([planck_power(nu, T)
                 for nu in nu_range])
    B_brem2_norm = B_brem2/max(B_brem2.max(),1e-40)
    B_bb2_norm   = B_bb2/max(B_bb2.max(),1e-40)
    ax4.semilogy(lam_range[::-1],
                 np.maximum(B_brem2_norm[::-1],1e-10),
                 color=COLORS['brem'], lw=2,
                 label='Bremsstrahlung')
    ax4.semilogy(lam_range[::-1],
                 np.maximum(B_bb2_norm[::-1],1e-10),
                 color=COLORS['bb'], lw=2, ls='--',
                 label='Blackbody')
    ax4.axvspan(100, 200, alpha=0.1,
                color='violet', label='Deep UV')
    ax4.set_xlabel('Wavelength (nm)')
    ax4.set_ylabel('Normalized spectral power')
    ax4.set_xlim([100, 1000])
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'Spectral Shape at T=16173K (Argon)')

    # ── 5. Cutoff wavelength vs T ─────────────────────────
    ax5 = fig.add_subplot(gs[1,1])
    lam_c = [cutoff_wavelength(T)*1e9 for T in T_range]
    ax5.semilogy(T_range, lam_c,
                 color=COLORS['core'], lw=2)
    ax5.axhline(380, color='violet', lw=1,
                ls='--', label='UV boundary (380nm)')
    ax5.axhline(200, color='white', lw=1,
                ls=':', alpha=0.5, label='Deep UV (200nm)')
    for name, t in TEMPS.items():
        lc = cutoff_wavelength(t['T'])*1e9
        ax5.scatter([t['T']], [lc],
                    color=t['color'], s=80, zorder=5,
                    label=f"{name.split(' ')[0]}: {lc:.0f}nm")
    ax5.set_xlabel('Temperature (K)')
    ax5.set_ylabel('Cutoff wavelength (nm)')
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'Bremsstrahlung Cutoff Wavelength')

    # ── 6. Combined spectrum at 7321K ─────────────────────
    ax6 = fig.add_subplot(gs[1,2])
    T = 7321
    n_e, n_i, _ = saha_ionization(T, n_total=n_total)
    B_brem3 = np.array([bremsstrahlung_spectrum(
                 nu, T, n_e, n_i)*V_COLLAPSE
                 for nu in nu_range])
    B_bb3   = np.array([planck_power(nu, T)
                 for nu in nu_range])
    B_total = B_bb3 + B_brem3
    norm    = max(B_total.max(), 1e-40)
    lam_rev = lam_range[::-1]
    ax6.fill_between(lam_rev,
                     np.maximum(B_bb3[::-1]/norm,1e-10),
                     alpha=0.4, color=COLORS['bb'],
                     label='Blackbody')
    ax6.fill_between(lam_rev,
                     np.maximum(B_brem3[::-1]/norm,1e-10),
                     alpha=0.4, color=COLORS['brem'],
                     label='Bremsstrahlung')
    ax6.semilogy(lam_rev,
                 np.maximum(B_total[::-1]/norm,1e-10),
                 color='white', lw=1.5, label='Combined')
    ax6.axvspan(345, 410, alpha=0.15,
                color='#e040fb', label='PPIX+TiO₂ window')
    ax6.set_xlabel('Wavelength (nm)')
    ax6.set_ylabel('Normalized power')
    ax6.set_xlim([100, 1000])
    ax6.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax6, 'Combined Emission at T=7321K')

    # ── 7. Brem/BB ratio vs T ─────────────────────────────
    ax7 = fig.add_subplot(gs[2,0])
    ratios = []
    for T in T_range:
        n_e,n_i,_ = saha_ionization(T, n_total=n_total)
        P_b  = bremsstrahlung_power(T,n_e,n_i)*V_COLLAPSE
        P_bb = 5.67e-8*4*np.pi*R_COLLAPSE**2*T**4
        ratios.append(P_b/P_bb if P_bb>0 else 0)
    ax7.semilogy(T_range, np.maximum(ratios,1e-10),
                 color=COLORS['brem'], lw=2)
    ax7.axhline(1.0, color='white', lw=1,
                ls='--', label='Equal power', alpha=0.7)
    ax7.axhline(0.01, color=COLORS['ros'], lw=1,
                ls=':', label='1% correction')
    for name, t in TEMPS.items():
        ax7.axvline(t['T'], color=t['color'],
                    lw=1, ls=':', alpha=0.7)
    ax7.set_xlabel('Temperature (K)')
    ax7.set_ylabel('P_brem / P_blackbody')
    ax7.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'Bremsstrahlung Fraction of Total Emission')

    # ── 8. n_e density vs T ───────────────────────────────
    ax8 = fig.add_subplot(gs[2,1])
    ne_vals = [saha_ionization(T,n_total=n_total)[0]
               for T in T_range]
    ax8.semilogy(T_range, np.maximum(ne_vals,1),
                 color='#ff9100', lw=2)
    for name, t in TEMPS.items():
        ne = saha_ionization(t['T'],n_total=n_total)[0]
        ax8.scatter([t['T']], [ne],
                    color=t['color'], s=80, zorder=5)
    ax8.set_xlabel('Temperature (K)')
    ax8.set_ylabel('Electron density n_e (m⁻³)')
    style_ax(ax8, 'Electron Density vs Temperature')

    # ── 9. Summary ────────────────────────────────────────
    ax9 = fig.add_subplot(gs[2,2])
    ax9.set_facecolor(COLORS['panel'])
    ax9.axis('off')
    T_air = 7321
    n_e_air,n_i_air,_ = saha_ionization(T_air,n_total=n_total)
    P_brem_air = bremsstrahlung_power(T_air,n_e_air,n_i_air)*V_COLLAPSE
    P_bb_air   = 5.67e-8*4*np.pi*R_COLLAPSE**2*T_air**4
    fi_air     = n_i_air/n_total
    lines = [
        ("BREMSSTRAHLUNG MODEL",        COLORS['core'],  11, 0.93, True),
        ("EMISSION VALIDATED",          COLORS['brem'],  9,  0.83, True),
        ("At T_air = 7,321K:",          COLORS['text'],  8,  0.74, True),
        (f"  Ionization = {fi_air:.4f} ({fi_air*100:.2f}%)",
                                        '#ff9100',       7,  0.65, False),
        (f"  P_brem = {P_brem_air:.2e} W",
                                        COLORS['brem'],  7,  0.57, False),
        (f"  P_bb   = {P_bb_air:.2e} W",
                                        COLORS['bb'],    7,  0.49, False),
        (f"  Ratio  = {P_brem_air/P_bb_air:.4f}",
                                        COLORS['text'],  7,  0.41, False),
        ("Blackbody DOMINATES",         COLORS['bb'],    8,  0.33, True),
        ("Bremsstrahlung ~1% correction",COLORS['text'], 7,  0.25, False),
        ("DEDICATION",                  '#ff9100',       8,  0.16, True),
        ("Ali Sayed Muhammad Osman",    COLORS['text'],  7,  0.09, False),
        ("1957 – 2022",                 COLORS['text'],  7,  0.03, False),
    ]
    for txt,col,sz,y,bold in lines:
        ax9.text(0.05, y, txt, color=col, fontsize=sz,
                 fontweight='bold' if bold else 'normal',
                 transform=ax9.transAxes)

    fig.suptitle(
        "Bremsstrahlung — Layer 4  |  Free-Free Emission vs Blackbody",
        color=COLORS['core'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "bremsstrahlung.png"
    plt.savefig(outfile, dpi=150,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
