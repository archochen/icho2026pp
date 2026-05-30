"""Job's plot for the Fe(III)/SBH system (IChO 2026 prep, P3.32, Q4).

Generates parts/part3/images/q32_jobs_plot.png.

Layout principles for a tent-shaped Job's plot:
- The "tent" leaves an empty upper-left triangle (above the rising wing)
  and an empty upper-right triangle (above the falling wing). Use these.
- Place the legend in the upper-right triangle, the wing-intersection
  annotation in the upper-left triangle, and keep the `x_Fe = 1/3`
  guide-line label down near the x-axis. This guarantees no overlap with
  the title or with each other regardless of font scaling.
"""
import numpy as np
import matplotlib.pyplot as plt

# --- Data from the problem statement ---
x = np.array([0.000, 0.125, 0.250, 0.375, 0.500, 0.583, 0.667,
              0.750, 0.833, 0.917, 1.000])
A = np.array([0.031, 0.091, 0.152, 0.183, 0.150, 0.128, 0.105,
              0.084, 0.061, 0.039, 0.017])
A_L = A[0]
A_M = A[-1]

# Linear-baseline-corrected absorbance
dA = A - (A_L * (1 - x) + A_M * x)

# Rising-wing through-origin fit: use x = 0.125, 0.250
x_rise = x[1:3]
y_rise = dA[1:3]
m_rise = float(np.sum(x_rise * y_rise) / np.sum(x_rise**2))
b_rise = 0.0

# Falling-wing fit: use x >= 0.500
mask_fall = x >= 0.500
m_fall, b_fall = np.polyfit(x[mask_fall], dA[mask_fall], 1)
m_fall, b_fall = float(m_fall), float(b_fall)

# Wing intersection
x_star = (b_fall - b_rise) / (m_rise - m_fall)
y_star = m_rise * x_star + b_rise

print(f"Rising wing:  slope = {m_rise:+.4f}, intercept = {b_rise:+.4f}")
print(f"Falling wing: slope = {m_fall:+.4f}, intercept = {b_fall:+.4f}")
print(f"Intersection: x* = {x_star:.4f}, dA* = {y_star:.4f}")
print(f"Expected for 1:2 complex: 1/3 = {1/3:.4f}")
print(f"Deviation: {(x_star - 1/3) / (1/3) * 100:+.2f} %")

# --- Plot ---
fig, ax = plt.subplots(figsize=(7.8, 5.0), dpi=170)

# Data
ax.plot(x, A, marker='o', mfc='white', mec='#888', mew=1.4, ls='', ms=7,
        label=r'Raw absorbance $A$', zorder=3)
ax.plot(x, dA, marker='o', mfc='#2a2b80', mec='#2a2b80', ls='', ms=7,
        label=r'Baseline-corrected $\Delta A$', zorder=4)

# Extrapolated wings
xx_rise = np.linspace(0.0, 0.50, 50)
xx_fall = np.linspace(0.20, 1.0, 50)
ax.plot(xx_rise, m_rise * xx_rise + b_rise, ls='--', color='#c0392b', lw=1.4,
        label=fr'Rising wing fit:  $\Delta A = {m_rise:.3f}\,x_{{\rm Fe}}$',
        zorder=2)
ax.plot(xx_fall, m_fall * xx_fall + b_fall, ls='--', color='#117a3d', lw=1.4,
        label=fr'Falling wing fit:  $\Delta A = {b_fall:.3f} {m_fall:+.3f}\,x_{{\rm Fe}}$',
        zorder=2)

# Vertical guides at x = 1/3 (theory) and x* (experiment)
ax.axvline(1/3, ls=':', color='black', lw=1.0, alpha=0.6, zorder=1)
ax.axvline(x_star, ls=':', color='#c0392b', lw=1.0, alpha=0.4, zorder=1)

# Star at the intersection
ax.plot([x_star], [y_star], marker='*', color='#c0392b', ms=20,
        mec='black', mew=0.7, zorder=6)

# --- Annotation in the upper-LEFT empty triangle, well below the title ---
annotation_text = (
    fr'$x_{{\rm Fe}}^{{\,*}} = {x_star:.3f} \approx \dfrac{{1}}{{3}}$'
    '\n'
    r'$\Rightarrow$  Fe : SBH = 1 : 2'
)
ax.annotate(
    annotation_text,
    xy=(x_star, y_star),
    xytext=(0.06, 0.205),
    fontsize=11,
    ha='left', va='center',
    bbox=dict(boxstyle='round,pad=0.45', fc='#fff8dc',
              ec='#888', lw=0.7, alpha=0.95),
    arrowprops=dict(arrowstyle='->', color='black', lw=1.0,
                    connectionstyle='arc3,rad=-0.18'),
    zorder=7,
)

# --- Legend in the upper-RIGHT empty triangle ---
ax.legend(
    loc='upper right',
    bbox_to_anchor=(0.99, 0.99),
    fontsize=9, frameon=True, fancybox=True,
    facecolor='white', edgecolor='#bbb', framealpha=0.9,
    handlelength=2.5, borderpad=0.5,
)

# --- x_Fe = 1/3 label down near the x-axis (out of title/annotation space) ---
ax.text(1/3 + 0.008, 0.012, r'$x_{\rm Fe} = 1/3$',
        fontsize=10, va='bottom', color='#222')

# Axis dressing
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.012, 0.255)
ax.set_xticks(np.linspace(0.0, 1.0, 11))
ax.set_xticklabels([f'{v:.2f}' for v in np.linspace(0.0, 1.0, 11)], fontsize=9.5)
ax.set_yticks(np.linspace(0.00, 0.25, 6))
ax.set_yticklabels([f'{v:.2f}' for v in np.linspace(0.00, 0.25, 6)], fontsize=9.5)
ax.set_xlabel(r'Mole fraction of Fe(III),  $x_{\rm Fe} = V_{\rm Fe}/(V_{\rm Fe}+V_{\rm SBH})$',
              fontsize=11)
ax.set_ylabel(r'Absorbance', fontsize=11)
ax.set_title("Job's plot — Fe(III)/SBH (1 mM each, methanol)",
             fontsize=12, pad=14)
ax.grid(True, ls=':', alpha=0.4)

fig.tight_layout()
out = "/Users/qchen/code/icho2026-solutions/parts/part3/images/q32_jobs_plot.png"
fig.savefig(out, dpi=170, bbox_inches='tight', facecolor='white')
print("Saved:", out)
