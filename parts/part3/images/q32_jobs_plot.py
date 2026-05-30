import numpy as np
import matplotlib.pyplot as plt

# Data from the IChO 2026 prep problem 32
x = np.array([0.000, 0.125, 0.250, 0.375, 0.500, 0.583, 0.667, 0.750, 0.833, 0.917, 1.000])
A = np.array([0.031, 0.091, 0.152, 0.183, 0.150, 0.128, 0.105, 0.084, 0.061, 0.039, 0.017])
A_L = A[0]      # absorbance of pure SBH stock
A_M = A[-1]     # absorbance of pure Fe stock

# Linear baseline subtraction (one absorbing complex assumption)
dA = A - (A_L * (1 - x) + A_M * x)

# Rising-wing fit: through origin using the two innermost points
x_rise = x[1:3]      # 0.125, 0.250
y_rise = dA[1:3]
m_rise = np.sum(x_rise * y_rise) / np.sum(x_rise**2)   # least-squares through origin
b_rise = 0.0

# Falling-wing fit: x >= 0.500 (SBH-limited region, far from peak)
mask_fall = x >= 0.500
x_fall = x[mask_fall]
y_fall = dA[mask_fall]
m_fall, b_fall = np.polyfit(x_fall, y_fall, 1)

# Intersection of the two extrapolated lines
x_star = (b_fall - b_rise) / (m_rise - m_fall)
y_star = m_rise * x_star + b_rise

print(f"Rising wing:  slope = {m_rise:+.4f}, intercept = {b_rise:+.4f}")
print(f"Falling wing: slope = {m_fall:+.4f}, intercept = {b_fall:+.4f}")
print(f"Intersection: x* = {x_star:.4f}, dA* = {y_star:.4f}")
print(f"Expected for 1:2 complex: 1/3 = {1/3:.4f}")
print(f"Deviation: {(x_star - 1/3) / (1/3) * 100:+.2f} %")

# Plot
fig, ax = plt.subplots(figsize=(7.0, 4.6), dpi=170)

# Raw A (open circles)
ax.plot(x, A, marker='o', mfc='white', mec='#888', mew=1.4, ls='', ms=7, label=r'Raw absorbance $A$')

# Baseline-corrected dA (solid circles)
ax.plot(x, dA, marker='o', mfc='#2a2b80', mec='#2a2b80', ls='', ms=7,
        label=r'Baseline-corrected $\Delta A$')

# Extrapolated wings (dashed)
xx_rise = np.linspace(0.0, 0.45, 50)
xx_fall = np.linspace(0.20, 1.0, 50)
ax.plot(xx_rise, m_rise * xx_rise + b_rise, ls='--', color='#c0392b', lw=1.3,
        label=fr'Rising wing fit: $\Delta A = {m_rise:.3f}\,x_{{\rm Fe}}$')
ax.plot(xx_fall, m_fall * xx_fall + b_fall, ls='--', color='#117a3d', lw=1.3,
        label=fr'Falling wing fit: $\Delta A = {b_fall:.3f} {m_fall:+.3f}\,x_{{\rm Fe}}$')

# Vertical guides
ax.axvline(1/3, ls=':', color='black', lw=1.0)
ax.axvline(x_star, ls=':', color='#c0392b', lw=1.0, alpha=0.6)

# Mark the intersection
ax.plot([x_star], [y_star], marker='*', color='#c0392b', ms=18, mec='black', mew=0.7, zorder=5)
ax.annotate(
    fr'$x_{{\rm Fe}}^{{\,*}} = {x_star:.3f}$' + '\n' + r'$\approx \dfrac{1}{3}\ \Rightarrow\ $Fe:SBH = 1:2',
    xy=(x_star, y_star), xytext=(0.50, 0.21),
    fontsize=11.5, ha='left',
    arrowprops=dict(arrowstyle='->', color='black', lw=0.9, connectionstyle='arc3,rad=-0.12'),
)

# Axis dressing
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.005, 0.225)
ax.set_xticks(np.linspace(0.0, 1.0, 11))
ax.set_xticklabels([f'{v:.2f}' for v in np.linspace(0.0, 1.0, 11)], fontsize=9)
ax.set_yticks(np.linspace(0.00, 0.20, 5))
ax.set_yticklabels([f'{v:.2f}' for v in np.linspace(0.00, 0.20, 5)], fontsize=9)
ax.set_xlabel(r'Mole fraction of Fe(III),  $x_{\rm Fe} = V_{\rm Fe}/(V_{\rm Fe}+V_{\rm SBH})$',
              fontsize=11)
ax.set_ylabel(r'Absorbance', fontsize=11)
ax.set_title("Job's plot — Fe(III)/SBH (1 mM each, methanol)", fontsize=12, pad=8)
ax.grid(True, ls=':', alpha=0.45)
ax.legend(loc='upper right', fontsize=9, frameon=False, handlelength=2.2)

# Annotate the x_Fe = 1/3 line
ax.text(1/3 + 0.005, 0.205, r'$x_{\rm Fe} = 1/3$', fontsize=10, va='top')

fig.tight_layout()
out = "/Users/qchen/code/icho2026-solutions/parts/part3/images/q32_jobs_plot.png"
fig.savefig(out, dpi=170, bbox_inches='tight', facecolor='white')
print("Saved:", out)
