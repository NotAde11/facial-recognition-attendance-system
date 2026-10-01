import matplotlib.pyplot as plt
import numpy as np

# =====================================================================
# 1. ENTER YOUR COLECTED DATA HERE
# =====================================================================
# Real-Time Latencies (in milliseconds)
raw_latencies = {
    "Preprocessing": 0.66,
    "Face Detection": 51.84,
    "LBPH Prediction": 33.04,
    "Database Write": 4.35
}

# Environmental Category Accuracies (in percentages)
raw_accuracies = {
    "General Batch": 91.79,
    "Lighting Stress": 78.16,
    "Pose Variation": 68.85,
    "Occlusion Stress": 62.5
}

# Confusion Matrix Counts per Category
# Structure: [True Positives, True Negatives, False Positives, False Negatives]
matrix_data = {
    "General": [190, 67, 5, 18],
    "Lighting": [68, 0, 4, 15],
    "Pose": [42, 0, 3, 16],
    "Occlusion": [30, 0, 2, 16]
}

# =====================================================================
# 2. CHART GENERATION LOGIC
# =====================================================================

# --- Chart 1: Component Execution Latency (Sorted Bar Chart) ---
sorted_latencies = dict(sorted(raw_latencies.items(), key=lambda item: item[1]))

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(sorted_latencies.keys(), sorted_latencies.values(), color='#2b5c8f', width=0.6)
ax.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold')
ax.set_title('System Latency Breakdown by Operational Stage', fontsize=12, fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f} ms',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('chart_component_latency.png', dpi=300)
plt.close()
print("[SUCCESS] Generated: chart_component_latency.png")


# --- Chart 2: Environmental Robustness Accuracy (Sorted Bar Chart) ---
sorted_accuracies = dict(sorted(raw_accuracies.items(), key=lambda item: item[1], reverse=True))

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(sorted_accuracies.keys(), sorted_accuracies.values(), color='#d95f02', width=0.6)
ax.set_ylabel('Accuracy Score (%)', fontsize=11, fontweight='bold')
ax.set_ylim(0, 105)
ax.set_title('System Accuracy Under Environmental Stress Conditions', fontsize=12, fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('chart_environmental_accuracy.png', dpi=300)
plt.close()
print("[SUCCESS] Generated: chart_environmental_accuracy.png")


# --- Chart 3: Confusion Matrix Grouped Breakdown ---
categories = list(matrix_data.keys())
tp_vals = [matrix_data[cat][0] for cat in categories]
tn_vals = [matrix_data[cat][1] for cat in categories]
fp_vals = [matrix_data[cat][2] for cat in categories]
fn_vals = [matrix_data[cat][3] for cat in categories]

x = np.arange(len(categories))
width = 0.18

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - 1.5*width, tp_vals, width, label='True Positives (TP)', color='#2ca02c')
ax.bar(x - 0.5*width, tn_vals, width, label='True Negatives (TN)', color='#1f77b4')
ax.bar(x + 0.5*width, fp_vals, width, label='False Positives (FP)', color='#ff7f0e')
ax.bar(x + 1.5*width, fn_vals, width, label='False Negatives (FN)', color='#d62728')

ax.set_ylabel('Total Image Count', fontsize=11, fontweight='bold')
ax.set_title('Confusion Matrix Signal Distribution Across Test Subsets', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
ax.legend(frameon=True, facecolor='white', edgecolor='none')
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('chart_confusion_matrix_breakdown.png', dpi=300)
plt.close()
print("[SUCCESS] Generated: chart_confusion_matrix_breakdown.png")