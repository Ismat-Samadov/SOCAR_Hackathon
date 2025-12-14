"""
Generate LLM Benchmark Charts
Creates high-quality visualization charts from benchmark data
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = '#0f172a'
plt.rcParams['axes.facecolor'] = '#1e293b'
plt.rcParams['text.color'] = '#f1f5f9'
plt.rcParams['axes.labelcolor'] = '#94a3b8'
plt.rcParams['xtick.color'] = '#94a3b8'
plt.rcParams['ytick.color'] = '#94a3b8'
plt.rcParams['grid.color'] = '#334155'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# Data
models = ['GPT-4.1', 'Llama-4-Maverick', 'DeepSeek-R1']
quality_scores = [52.00, 52.00, 32.27]
citation_scores = [80.00, 80.00, 33.33]
completeness = [100.0, 100.0, 91.6]
response_times = [6.38, 4.00, 10.98]
similarity = [0.00, 0.00, 1.54]

# Model colors
colors = {
    'GPT-4.1': '#10b981',
    'Llama-4-Maverick': '#8b5cf6',
    'DeepSeek-R1': '#f59e0b'
}
model_colors = [colors[m] for m in models]

# Create charts directory
charts_dir = Path(__file__).parent.parent / "charts"
charts_dir.mkdir(exist_ok=True)

print(f"📊 Generating LLM benchmark charts...")
print(f"📂 Output directory: {charts_dir}\n")

# Chart 1: Quality Score Comparison
print("1️⃣  Generating Quality Score Comparison...")
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(models, quality_scores, color=model_colors, edgecolor='none', alpha=0.9, width=0.6)

# Add value labels on bars
for bar, score in zip(bars, quality_scores):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
            f'{score:.2f}',
            ha='center', va='bottom', color='#f1f5f9', fontweight='bold', fontsize=13)

ax.set_ylabel('Quality Score', fontsize=13, fontweight='600', color='#e2e8f0')
ax.set_title('LLM Quality Score Comparison', fontsize=16, fontweight='bold',
             color='#f1f5f9', pad=20)
ax.set_ylim(0, 65)
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(charts_dir / "llm_quality_comparison.png", dpi=300, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("   ✅ Saved: llm_quality_comparison.png")

# Chart 2: Full Metrics Breakdown (Grouped Bar Chart)
print("2️⃣  Generating Full Metrics Breakdown...")
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(models))
width = 0.25

bars1 = ax.bar(x - width, quality_scores, width, label='Quality',
               color='#3b82f6', alpha=0.9, edgecolor='none')
bars2 = ax.bar(x, citation_scores, width, label='Citation',
               color='#10b981', alpha=0.9, edgecolor='none')
bars3 = ax.bar(x + width, completeness, width, label='Completeness',
               color='#8b5cf6', alpha=0.9, edgecolor='none')

ax.set_ylabel('Score', fontsize=13, fontweight='600', color='#e2e8f0')
ax.set_title('LLM Metrics Breakdown: Quality, Citation & Completeness',
             fontsize=16, fontweight='bold', color='#f1f5f9', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=12, fontweight='500')
ax.legend(loc='upper right', framealpha=0.9, facecolor='#1e293b',
          edgecolor='#475569', fontsize=11)
ax.set_ylim(0, 115)
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(charts_dir / "llm_metrics_breakdown.png", dpi=300, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("   ✅ Saved: llm_metrics_breakdown.png")

# Chart 3: Radar Chart (Model Capability Profile)
print("3️⃣  Generating Model Capability Profile (Radar)...")
categories = ['Quality', 'Citation', 'Completeness', 'Speed']
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# Normalize speed (inverse - lower is better, so we flip it)
# Max speed: 12s, so speed_normalized = (12 - actual_time) / 12 * 100
speed_scores = [(12 - t) / 12 * 100 for t in response_times]

# Data for each model
data = {
    'GPT-4.1': [52, 80, 100, speed_scores[0]],  # ~40
    'Llama-4-Maverick': [52, 80, 100, speed_scores[1]],  # ~65
    'DeepSeek-R1': [32.27, 33.33, 91.6, speed_scores[2]]  # ~10
}

# Number of variables
num_vars = len(categories)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Complete the circle

# Plot each model
for model, values in data.items():
    values += values[:1]  # Complete the circle
    ax.plot(angles, values, 'o-', linewidth=2.5, label=model,
            color=colors[model], markersize=6)
    ax.fill(angles, values, alpha=0.15, color=colors[model])

# Fix axis
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12, fontweight='600', color='#f1f5f9')
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='#94a3b8')
ax.grid(color='#475569', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_facecolor('#1e293b')

# Title and legend
ax.set_title('LLM Multi-Dimensional Performance Profile',
             fontsize=16, fontweight='bold', color='#f1f5f9', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.9,
          facecolor='#1e293b', edgecolor='#475569', fontsize=11)

plt.tight_layout()
plt.savefig(charts_dir / "llm_radar_profile.png", dpi=300, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("   ✅ Saved: llm_radar_profile.png")

# Chart 4: Response Time Analysis (Horizontal Bar)
print("4️⃣  Generating Response Time Analysis...")
fig, ax = plt.subplots(figsize=(10, 6))

y_pos = np.arange(len(models))
bars = ax.barh(y_pos, response_times, color=model_colors, edgecolor='none', alpha=0.9)

# Add value labels
for i, (bar, time) in enumerate(zip(bars, response_times)):
    ax.text(time + 0.3, bar.get_y() + bar.get_height()/2.,
            f'{time:.2f}s',
            ha='left', va='center', color='#f1f5f9', fontweight='bold', fontsize=12)

ax.set_yticks(y_pos)
ax.set_yticklabels(models, fontsize=12, fontweight='600')
ax.set_xlabel('Response Time (seconds)', fontsize=13, fontweight='600', color='#e2e8f0')
ax.set_title('LLM Response Time Comparison (Lower is Better)',
             fontsize=16, fontweight='bold', color='#f1f5f9', pad=20)
ax.set_xlim(0, 13)
ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
ax.set_axisbelow(True)

# Invert y-axis so fastest is on top
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(charts_dir / "llm_response_time.png", dpi=300, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("   ✅ Saved: llm_response_time.png")

# Chart 5: Combined Overview Dashboard
print("5️⃣  Generating Combined Overview Dashboard...")
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#0f172a')

# Create grid
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# Top-left: Quality scores
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#1e293b')
bars = ax1.bar(models, quality_scores, color=model_colors, alpha=0.9, edgecolor='none')
for bar, score in zip(bars, quality_scores):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1.5,
             f'{score:.1f}', ha='center', va='bottom', color='#f1f5f9',
             fontweight='bold', fontsize=11)
ax1.set_title('Quality Score', fontsize=14, fontweight='bold', color='#f1f5f9', pad=12)
ax1.set_ylabel('Score', fontsize=11, color='#e2e8f0')
ax1.set_ylim(0, 65)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

# Top-right: Citation scores
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#1e293b')
bars = ax2.bar(models, citation_scores, color=model_colors, alpha=0.9, edgecolor='none')
for bar, score in zip(bars, citation_scores):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{score:.1f}', ha='center', va='bottom', color='#f1f5f9',
             fontweight='bold', fontsize=11)
ax2.set_title('Citation Score', fontsize=14, fontweight='bold', color='#f1f5f9', pad=12)
ax2.set_ylabel('Score', fontsize=11, color='#e2e8f0')
ax2.set_ylim(0, 95)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_axisbelow(True)

# Bottom-left: Completeness
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#1e293b')
bars = ax3.bar(models, completeness, color=model_colors, alpha=0.9, edgecolor='none')
for bar, score in zip(bars, completeness):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{score:.1f}%', ha='center', va='bottom', color='#f1f5f9',
             fontweight='bold', fontsize=11)
ax3.set_title('Completeness', fontsize=14, fontweight='bold', color='#f1f5f9', pad=12)
ax3.set_ylabel('Percentage', fontsize=11, color='#e2e8f0')
ax3.set_ylim(0, 110)
ax3.grid(axis='y', alpha=0.3, linestyle='--')
ax3.set_axisbelow(True)

# Bottom-right: Response time
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#1e293b')
y_pos = np.arange(len(models))
bars = ax4.barh(y_pos, response_times, color=model_colors, alpha=0.9, edgecolor='none')
for i, (bar, time) in enumerate(zip(bars, response_times)):
    ax4.text(time + 0.2, bar.get_y() + bar.get_height()/2.,
             f'{time:.2f}s', ha='left', va='center', color='#f1f5f9',
             fontweight='bold', fontsize=11)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(models, fontsize=11, fontweight='500')
ax4.set_title('Response Time (Lower = Better)', fontsize=14, fontweight='bold',
              color='#f1f5f9', pad=12)
ax4.set_xlabel('Seconds', fontsize=11, color='#e2e8f0')
ax4.set_xlim(0, 13)
ax4.grid(axis='x', alpha=0.3, linestyle='--')
ax4.set_axisbelow(True)
ax4.invert_yaxis()

# Main title
fig.suptitle('LLM Benchmark Results: Complete Overview',
             fontsize=18, fontweight='bold', color='#f1f5f9', y=0.98)

plt.savefig(charts_dir / "llm_overview_dashboard.png", dpi=300, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("   ✅ Saved: llm_overview_dashboard.png")

print(f"\n🎉 All charts generated successfully!")
print(f"📁 Location: {charts_dir}")
print(f"\nGenerated files:")
print(f"   • llm_quality_comparison.png")
print(f"   • llm_metrics_breakdown.png")
print(f"   • llm_radar_profile.png")
print(f"   • llm_response_time.png")
print(f"   • llm_overview_dashboard.png")
