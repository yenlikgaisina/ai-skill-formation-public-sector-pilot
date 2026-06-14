"""
AI & Skill Formation in Public-Sector Knowledge Work — synthetic pilot.

A reproducible, methods-demonstrating pilot for the research question:
  When knowledge workers use AI assistance, what happens to immediate output
  quality, speed, and DELAYED skill (retention) — and does it differ by seniority?

The data here is SIMULATED (no real participants) to demonstrate the full
analysis pipeline end-to-end. Planted effects mirror prior findings (AI helps
speed/immediate quality but can reduce delayed skill formation, more so for
juniors). The analysis below 'discovers' them with standard methods.
"""

import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
N = 400

# --- Design: randomised AI vs control; balanced seniority ---
ai      = rng.integers(0, 2, N)                      # 1 = AI-assisted, 0 = control
senior  = rng.integers(0, 2, N)                      # 1 = senior, 0 = junior

# --- Planted ground truth (what a real study would try to recover) ---
# Immediate quality: AI helps a little; seniors a little better
quality = 70 + 4*ai + 5*senior + rng.normal(0, 9, N)

# Time on task (minutes): AI is faster
time_mins = 42 - 8*ai + 4*(1-senior) + rng.normal(0, 6, N)

# DELAYED retention (unassisted task later): AI REDUCES it, and MORE for juniors
#   junior (senior=0) AI penalty = -3 + -6 = -9 ; senior AI penalty = -3
retention = 66 + 9*senior - 3*ai - 6*ai*(1-senior) + rng.normal(0, 9, N)

df = pd.DataFrame(dict(
    participant_id=np.arange(1, N+1),
    group=np.where(ai==1, "ai", "control"),
    seniority=np.where(senior==1, "senior", "junior"),
    ai=ai, senior=senior,
    quality_score=quality.round(1),
    time_mins=time_mins.round(1),
    retention_score=retention.round(1),
))
df.to_csv("data_synthetic.csv", index=False)

print("="*64)
print("SYNTHETIC PILOT — AI vs CONTROL  (N =", N, ")")
print("="*64)
print("\nGroup means:")
print(df.groupby("group")[["quality_score","time_mins","retention_score"]].mean().round(2))

def ttest(col):
    a = df[df.ai==1][col]; c = df[df.ai==0][col]
    t,p = stats.ttest_ind(a,c)
    diff = a.mean()-c.mean()
    # 95% CI for difference in means (Welch-ish, equal-var here)
    se = np.sqrt(a.var(ddof=1)/len(a) + c.var(ddof=1)/len(c))
    lo,hi = diff-1.96*se, diff+1.96*se
    print(f"  {col:16s} AI-Control diff = {diff:+6.2f}  95% CI [{lo:+.2f}, {hi:+.2f}]  t={t:+.2f}  p={p:.4f}")

print("\nTreatment effects (AI minus control):")
for c in ["quality_score","time_mins","retention_score"]:
    ttest(c)

print("\nRegression — retention with AI x seniority interaction:")
m = smf.ols("retention_score ~ ai * senior", data=df).fit()
print(m.summary().tables[1])

print("\nInterpretation of retention model:")
b = m.params
print(f"  Junior + AI effect on retention: {b['ai']:+.2f}  (p={m.pvalues['ai']:.4f})")
print(f"  Extra AI effect for seniors:     {b['ai:senior']:+.2f}  (p={m.pvalues['ai:senior']:.4f})")
print(f"  => AI's retention penalty is concentrated among JUNIOR workers.")

# --- Figure: retention by group x seniority ---
piv = df.groupby(["seniority","group"])["retention_score"].mean().unstack()
ax = piv.plot(kind="bar", color=["#888","#005EB8"], figsize=(7,4.5), edgecolor="white")
ax.set_ylabel("Mean delayed retention score"); ax.set_xlabel("")
ax.set_title("AI assistance and delayed skill retention, by seniority\n(synthetic pilot data)")
ax.legend(title="Condition"); plt.xticks(rotation=0); plt.tight_layout()
plt.savefig("retention_by_group.png", dpi=130)

print("\nSaved figure: retention_by_group.png")
print("Saved data:   data_synthetic.csv")
