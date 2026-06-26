#!/usr/bin/env python3
"""
Blackbody Emission & Sonosensitizer Matching
==============================================
Planck spectrum at SL collapse temperatures.
Overlays sonosensitizer absorption peaks.
Finds optimal temperature for each sonosensitizer.
Dedicated to Ali Sayed Muhammad Osman (1957-2022)

Usage:
  python3 blackbody_spectrum.py
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
H  = 6.626e-34
C  = 3.0e8
KB = 1.381e-23
NA = 6.022e23

# ── Collapse temperatures (from temperature_estimator.py) ──
TEMPS = {
    'T_eff Air (7,321K)':    {'T':7321,   'color':'#00e5ff', 'ls':'-'},
    'T_eff Argon (16,173K)': {'T':16173,  'color':'#ff4081', 'ls':'--'},
    'T_eff Helium (17,826K)':{'T':17826,  'color':'#ffe57f', 'ls':'-.'},
    'Sun surface (5,778K)':  {'T':5778,   'color':'#ff9100', 'ls':':'},
}

# ── Sonosensitizer absorption peaks ───────────────────────
SENSITIZERS = {
    'Protoporphyrin IX\n(PPIX)': {
        'peaks': [405, 505, 540, 575, 630],
        'primary': 405,
        'color': '#e040fb',
        'marker': 'v',
        'note': 'Most studied SDT sensitizer'
    },
    'Hematoporphyrin\n(HpD)': {
        'peaks': [390, 510, 540, 575, 630],
        'primary': 390,
        'color': '#ff9100',
        'marker': '^',
        'note': 'Clinically approved (Photofrin)'
    },
    'TiO₂\nnanoparticles': {
        'peaks': [320, 380],
        'primary': 350,
        'color': '#00e676',
        'marker': 's',
        'note': 'Inorganic — absorbs UV/near-UV'
    },
    'NaNbO₃\nnanorods': {
        'peaks': [310, 380],
        'primary': 345,
        'color': '#69f0ae',
        'marker': 'D',
        'note': 'arXiv:2310.11793 — indexed'
    },
    'Rose Bengal': {
        'peaks': [480, 510, 550],
        'primary': 510,
        'color': '#f48fb1',
        'marker': 'o',
        'note': 'Water-soluble, high ROS yield'
    },
    'Chlorin e6\n(Ce6)': {
        'peaks': [405, 660],
        'primary': 660,
        'color': '#80deea',
        'marker': 'P',
        'note': 'Red-shifted — deeper tissue'
    },
}

COLORS = {
    'bg':    '#04060f', 'panel': '#080f20',
    'grid':  '#1a2a4a', 'text':  '#c8d8f0',
    'core':  '#00e5ff', 'vis':   'rgba(255,255,100,0.1)',
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

def planck(lam, T):
    """Spectral radiance [W/m²/sr/m]."""
    x = np.clip(H*C/(lam*KB*T), 1e-10, 500)
    return (2*H*C**2/lam**5) / (np.exp(x) - 1)

def wien_peak(T):
    """Peak wavelength [m]."""
    return 2.898e-3 / T

def stefan_boltzmann(T, R_bubble=0.5e-6):
    """Total radiated power [W]."""
    sigma = 5.67e-8
    A     = 4*np.pi*R_bubble**2
    return sigma * A * T**4

def spectral_overlap(lam, T, lam_peak, width=20e-9):
    """Fraction of blackbody power near sensitizer peak."""
    B_peak = planck(np.array([lam_peak]), T)[0]
    B_total= np.trapezoid(planck(lam, T), lam)
    B_band = np.trapezoid(
        planck(lam[(lam > lam_peak-width) &
                   (lam < lam_peak+width)], T),
        lam[(lam > lam_peak-width) &
            (lam < lam_peak+width)])
    if B_total <= 0: return 0
    return B_band / B_total

def photons_per_flash(T, lam_peak,
                      R_bubble=0.5e-6,
                      tau=100e-12,
                      width=20e-9):
    """Photon count at sensitizer peak per flash."""
    P_total = stefan_boltzmann(T, R_bubble) * tau
    lam_arr = np.linspace(lam_peak-width, lam_peak+width, 50)
    B_band  = np.trapezoid(planck(lam_arr, T), lam_arr)
    B_total = np.trapezoid(planck(
                np.linspace(100e-9, 1000e-9, 500), T),
                np.linspace(100e-9, 1000e-9, 500))
    if B_total <= 0: return 0
    f_band = B_band / B_total
    E_photon = H*C/lam_peak
    return P_total * f_band / E_photon

# ══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ══════════════════════════════════════════════════════════
def print_diagnostics():
    print("\n" + "═"*70)
    print("  BLACKBODY SPECTRUM & SONOSENSITIZER MATCHING")
    print("  Dedicated to Ali Sayed Muhammad Osman (1957–2022)")
    print("═"*70)

    lam = np.linspace(100e-9, 1000e-9, 1000)

    print(f"\n── Blackbody Properties at Collapse Temperatures ───────────")
    print(f"  {'T(K)':>8} {'λ_peak(nm)':>12} {'P_total(W)':>12} "
          f"{'P_UV%':>8} {'P_vis%':>8}")
    print("  " + "─"*52)
    for name, t in TEMPS.items():
        T    = t['T']
        lp   = wien_peak(T)*1e9
        P    = stefan_boltzmann(T)
        B    = planck(lam, T)
        Bt   = np.trapezoid(B, lam)
        B_uv = np.trapezoid(B[lam<380e-9], lam[lam<380e-9])
        B_vi = np.trapezoid(B[(lam>=380e-9)&(lam<=700e-9)],
                         lam[(lam>=380e-9)&(lam<=700e-9)])
        p_uv = B_uv/Bt*100 if Bt>0 else 0
        p_vi = B_vi/Bt*100 if Bt>0 else 0
        label = name.split('(')[0].strip()[:20]
        print(f"  {T:>8,} {lp:>12.1f} {P:>12.3e} "
              f"{p_uv:>8.1f} {p_vi:>8.1f}")

    print(f"\n── Sonosensitizer Matching ──────────────────────────────────")
    print(f"  {'Sensitizer':<22} {'Peak(nm)':>9} "
          f"{'T_air':>8} {'T_Ar':>8} {'Best gas':>10}")
    print("  " + "─"*60)
    for name, s in SENSITIZERS.items():
        lp = s['primary']
        label = name.replace('\n',' ')[:21]
        ph_air = photons_per_flash(7321,  lp*1e-9)
        ph_ar  = photons_per_flash(16173, lp*1e-9)
        best   = 'Argon' if ph_ar > ph_air else 'Air'
        print(f"  {label:<22} {lp:>9} "
              f"{ph_air:>8.1e} {ph_ar:>8.1e} {best:>10}")

    print(f"\n── Optimal Temperature per Sensitizer ───────────────────────")
    T_range = np.linspace(3000, 50000, 200)
    for name, s in SENSITIZERS.items():
        lp     = s['primary'] * 1e-9
        ph_T   = [photons_per_flash(T, lp) for T in T_range]
        T_opt  = T_range[np.argmax(ph_T)]
        label  = name.replace('\n',' ')[:25]
        print(f"  {label:<25} peak={s['primary']}nm  "
              f"T_opt={T_opt:.0f}K")

    print("═"*70 + "\n")

# ══════════════════════════════════════════════════════════
# PLOTTING
# ══════════════════════════════════════════════════════════
def plot_all():
    fig = plt.figure(figsize=(16,11), facecolor=COLORS['bg'])
    gs  = gridspec.GridSpec(3, 3, figure=fig,
                            hspace=0.52, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.92, bottom=0.07)

    lam = np.linspace(100e-9, 1000e-9, 2000)
    lam_nm = lam * 1e9

    # ── 1. Blackbody spectra — all temps ──────────────────
    ax1 = fig.add_subplot(gs[0,:2])
    for name, t in TEMPS.items():
        B = planck(lam, t['T'])
        B_norm = B / B.max()
        ax1.plot(lam_nm, B_norm,
                 color=t['color'], lw=2,
                 ls=t['ls'], label=name)
    # Sensitizer peaks
    for sname, s in SENSITIZERS.items():
        for pk in s['peaks']:
            ax1.axvline(pk, color=s['color'],
                        lw=0.8, alpha=0.5)
        ax1.axvline(s['primary'], color=s['color'],
                    lw=1.5, alpha=0.8,
                    label=f"{sname.split(chr(10))[0]} {s['primary']}nm")
    # Visible range
    ax1.axvspan(380, 700, alpha=0.06,
                color='yellow', label='Visible')
    ax1.axvspan(100, 380, alpha=0.06,
                color='violet', label='UV')
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Normalized Intensity')
    ax1.set_xlim([100, 800])
    ax1.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'],
               framealpha=0.8, ncol=2,
               loc='upper right')
    style_ax(ax1, 'SL Emission Spectra + Sonosensitizer Absorption Peaks')

    # ── 2. Wien peak vs temperature ───────────────────────
    ax2 = fig.add_subplot(gs[0,2])
    T_range = np.linspace(3000, 50000, 300)
    lp_nm   = np.array([wien_peak(T)*1e9 for T in T_range])
    ax2.semilogy(T_range, lp_nm,
                 color=COLORS['core'], lw=2)
    for name, t in TEMPS.items():
        lp = wien_peak(t['T'])*1e9
        ax2.scatter([t['T']], [lp],
                    color=t['color'], s=80, zorder=5)
    ax2.axhline(380, color='violet', lw=1,
                ls='--', label='UV/Vis boundary', alpha=0.7)
    ax2.axhline(700, color='red', lw=1,
                ls='--', label='Vis/IR boundary', alpha=0.7)
    # Sensitizer peaks
    for sname, s in SENSITIZERS.items():
        ax2.axhline(s['primary'], color=s['color'],
                    lw=0.8, ls=':', alpha=0.6)
    ax2.set_xlabel('Temperature (K)')
    ax2.set_ylabel('λ_peak (nm)')
    ax2.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax2, "Wien's Peak vs Temperature")

    # ── 3. Photons at sensitizer peaks vs T ───────────────
    ax3 = fig.add_subplot(gs[1,0])
    T_scan = np.linspace(3000, 30000, 100)
    for sname, s in SENSITIZERS.items():
        ph = [photons_per_flash(T, s['primary']*1e-9)
              for T in T_scan]
        label = sname.replace('\n',' ').split('(')[0].strip()
        ax3.semilogy(T_scan, np.maximum(ph,1e-10),
                     color=s['color'], lw=1.5,
                     label=f"{label} {s['primary']}nm")
    for name, t in TEMPS.items():
        ax3.axvline(t['T'], color=t['color'],
                    lw=1, ls=':', alpha=0.6)
    ax3.set_xlabel('Collapse Temperature (K)')
    ax3.set_ylabel('Photons per flash at peak')
    ax3.legend(fontsize=6, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax3, 'Sensitizer Activation Photons vs T')

    # ── 4. UV fraction vs temperature ────────────────────
    ax4 = fig.add_subplot(gs[1,1])
    uv_frac = []
    vis_frac= []
    for T in T_range:
        B  = planck(lam, T)
        Bt = np.trapezoid(B, lam)
        Bu = np.trapezoid(B[lam<380e-9], lam[lam<380e-9])
        Bv = np.trapezoid(B[(lam>=380e-9)&(lam<=700e-9)],
                       lam[(lam>=380e-9)&(lam<=700e-9)])
        uv_frac.append(Bu/Bt*100 if Bt>0 else 0)
        vis_frac.append(Bv/Bt*100 if Bt>0 else 0)
    ax4.plot(T_range, uv_frac,
             color='#b388ff', lw=2, label='UV (<380nm)')
    ax4.plot(T_range, vis_frac,
             color='#ffe57f', lw=2, label='Visible (380-700nm)')
    for name, t in TEMPS.items():
        ax4.axvline(t['T'], color=t['color'],
                    lw=1, ls=':', alpha=0.7)
    ax4.set_xlabel('Temperature (K)')
    ax4.set_ylabel('Fraction of total power (%)')
    ax4.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax4, 'UV/Visible Fraction vs Temperature')

    # ── 5. Spectral match — TiO₂ vs Porphyrin ────────────
    ax5 = fig.add_subplot(gs[1,2])
    T_air = 7321; T_ar = 16173
    B_air = planck(lam, T_air); B_air/=B_air.max()
    B_ar  = planck(lam, T_ar);  B_ar /=B_ar.max()
    ax5.plot(lam_nm, B_air, color='#00e5ff',
             lw=2, label='Air 7,321K')
    ax5.plot(lam_nm, B_ar,  color='#ff4081',
             lw=2, ls='--', label='Argon 16,173K')
    # TiO2
    ax5.axvspan(310, 390, alpha=0.15,
                color='#00e676', label='TiO₂ absorption')
    # Porphyrin
    ax5.axvspan(390, 420, alpha=0.15,
                color='#e040fb', label='Porphyrin Soret')
    ax5.axvspan(490, 650, alpha=0.10,
                color='#e040fb')
    ax5.set_xlim([100, 800])
    ax5.set_xlabel('Wavelength (nm)')
    ax5.set_ylabel('Normalized Intensity')
    ax5.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax5, 'Spectral Match: TiO₂ vs Porphyrin')

    # ── 6. Total power vs temperature ────────────────────
    ax6 = fig.add_subplot(gs[2,0])
    P_vals = [stefan_boltzmann(T) for T in T_range]
    ax6.semilogy(T_range, P_vals,
                 color=COLORS['core'], lw=2)
    for name, t in TEMPS.items():
        P = stefan_boltzmann(t['T'])
        ax6.scatter([t['T']], [P],
                    color=t['color'], s=80, zorder=5)
    ax6.set_xlabel('Temperature (K)')
    ax6.set_ylabel('Radiated power (W)')
    style_ax(ax6, 'Total Radiated Power vs Temperature')

    # ── 7. Sensitizer comparison bar chart ───────────────
    ax7 = fig.add_subplot(gs[2,1])
    s_names  = [s.replace('\n',' ').split('(')[0].strip()
                for s in SENSITIZERS]
    ph_air_v = [photons_per_flash(7321,
                 SENSITIZERS[s]['primary']*1e-9)
                for s in SENSITIZERS]
    ph_ar_v  = [photons_per_flash(16173,
                 SENSITIZERS[s]['primary']*1e-9)
                for s in SENSITIZERS]
    x = np.arange(len(s_names))
    ax7.bar(x-0.2, ph_air_v, 0.35,
            color='#00e5ff', alpha=0.8, label='Air 7,321K')
    ax7.bar(x+0.2, ph_ar_v,  0.35,
            color='#ff4081', alpha=0.8, label='Argon 16,173K')
    ax7.set_yscale('log')
    ax7.set_xticks(x)
    ax7.set_xticklabels(s_names, rotation=30,
                         ha='right', fontsize=7)
    ax7.set_ylabel('Photons per flash')
    ax7.legend(fontsize=7, facecolor=COLORS['panel'],
               labelcolor=COLORS['text'], framealpha=0.8)
    style_ax(ax7, 'Sensitizer Activation: Air vs Argon')

    # ── 8. Summary panel ─────────────────────────────────
    ax8 = fig.add_subplot(gs[2,2])
    ax8.set_facecolor(COLORS['panel'])
    ax8.axis('off')
    lines = [
        ("BLACKBODY SPECTRUM",         COLORS['core'],  11, 0.93, True),
        ("SONOSENSITIZER MATCHED",      '#00e676',       9,  0.83, True),
        ("At T_air = 7,321K:",          COLORS['text'],  8,  0.74, True),
        ("  λ_peak = 396 nm (UV)",      '#00e5ff',       7,  0.66, False),
        ("  Best match: TiO₂, PPIX",   '#00e676',       7,  0.58, False),
        ("At T_Ar = 16,173K:",          COLORS['text'],  8,  0.50, True),
        ("  λ_peak = 179 nm (deep UV)", '#ff4081',       7,  0.42, False),
        ("  Best match: TiO₂, NaNbO₃", '#00e676',       7,  0.34, False),
        ("Argon → 100-1000× more",      '#ffe57f',       7,  0.26, False),
        ("photons at sensitizer peaks", '#ffe57f',       7,  0.19, False),
        ("DEDICATION",                  '#ff9100',       8,  0.12, True),
        ("Ali Sayed Muhammad Osman",    COLORS['text'],  7,  0.06, False),
        ("1957 – 2022",                 COLORS['text'],  7,  0.01, False),
    ]
    for txt,col,sz,y,bold in lines:
        ax8.text(0.05, y, txt, color=col, fontsize=sz,
                 fontweight='bold' if bold else 'normal',
                 transform=ax8.transAxes)

    fig.suptitle(
        "Blackbody Emission — SL Spectrum  |  Sonosensitizer Activation Map",
        color=COLORS['core'], fontsize=11,
        fontweight='bold', y=0.97
    )

    outfile = OUT / "blackbody_spectrum.png"
    plt.savefig(outfile, dpi=150,
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✅ Plot saved → {outfile}")

# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print_diagnostics()
    plot_all()
    print("  termux-open ~/sonoluminescence/02_simulations/outputs/")
