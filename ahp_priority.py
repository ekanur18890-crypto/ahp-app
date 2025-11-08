import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

# ---------- Helper Functions ----------
def ahp_weights(matrix):
    n = matrix.shape[0]
    col_sum = np.sum(matrix, axis=0)
    norm_matrix = matrix / col_sum
    weights = np.mean(norm_matrix, axis=1)
    weights = weights / np.sum(weights)
    Aw = np.dot(matrix, weights)
    lambda_max = np.mean(Aw / weights)
    CI = (lambda_max - n) / (n - 1)
    RI_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
    RI = RI_dict.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0
    return weights, CR


# ---------- Streamlit Interface ----------
st.title("⚖️ AHP Decision Support Tool with Excel Export")
st.write("Perform **AHP-based multi-criteria decision analysis** and download results as Excel.")

# Step 1: Define Criteria and Alternatives
st.header("Step 1: Define Inputs")
criteria = st.text_input("Enter criteria (comma-separated):", "Cost, Reliability, Sustainability").split(",")
criteria = [c.strip() for c in criteria if c.strip()]

alternatives = st.text_input("Enter alternatives (comma-separated):", "Solar PV, Microhydro, Biomass").split(",")
alternatives = [a.strip() for a in alternatives if a.strip()]

if len(criteria) < 2 or len(alternatives) < 2:
    st.warning("Please enter at least 2 criteria and 2 alternatives.")
    st.stop()

# Step 2: Criteria Pairwise Comparison
st.header("Step 2: Criteria Pairwise Comparison")
criteria_matrix = np.ones((len(criteria), len(criteria)))

for i in range(len(criteria)):
    for j in range(i + 1, len(criteria)):
        val = st.number_input(
            f"How much more important is {criteria[i]} compared to {criteria[j]}? (1–9 scale)",
            min_value=0.111, max_value=9.0, step=0.111, value=1.0, key=f"crit_{i}_{j}"
        )
        criteria_matrix[i, j] = val
        criteria_matrix[j, i] = 1 / val

criteria_weights, CR_criteria = ahp_weights(criteria_matrix)

st.subheader("Criteria Weights:")
criteria_df = pd.DataFrame({"Criterion": criteria, "Weight": np.round(criteria_weights, 4)})
st.table(criteria_df)
st.info(f"Criteria Consistency Ratio (CR): {CR_criteria:.3f}")
if CR_criteria > 0.1:
    st.warning("⚠️ Your criteria judgments may be inconsistent (CR > 0.1). Try adjusting the comparisons.")

# Step 3: Alternatives Pairwise Comparison per Criterion
st.header("Step 3: Alternatives Comparison for Each Criterion")
alt_weights = []
CR_alternatives = []

for c_idx, crit in enumerate(criteria):
    st.subheader(f"Criterion: {crit}")
    alt_matrix = np.ones((len(alternatives), len(alternatives)))
    for i in range(len(alternatives)):
        for j in range(i + 1, len(alternatives)):
            val = st.number_input(
                f"For {crit}, how much more preferable is {alternatives[i]} compared to {alternatives[j]}?",
                min_value=0.111, max_value=9.0, step=0.111, value=1.0, key=f"alt_{c_idx}_{i}_{j}"
            )
            alt_matrix[i, j] = val
            alt_matrix[j, i] = 1 / val

    w, cr = ahp_weights(alt_matrix)
    alt_weights.append(w)
    CR_alternatives.append(cr)

# Step 4: Final Calculation
st.header("Step 4: Final Results")
alt_weights = np.array(alt_weights)  # shape = (n_criteria, n_alternatives)
global_scores = np.dot(criteria_weights, alt_weights)

final_df = pd.DataFrame({
    "Alternative": alternatives,
    "Final Score": np.round(global_scores, 4)
}).sort_values(by="Final Score", ascending=False)

st.subheader("Final Ranking:")
st.table(final_df.reset_index(drop=True))

# Consistency summary
avg_cr = np.mean(CR_alternatives)
st.info(f"Average Consistency Ratio for alternatives: {avg_cr:.3f}")
if avg_cr > 0.1:
    st.warning("⚠️ Some alternative comparisons may be inconsistent.")


# ---------- Step 5: Export to Excel ----------
st.header("📤 Step 5: Download Results")
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    criteria_df.to_excel(writer, sheet_name="Criteria Weights", index=False)
    pd.DataFrame(alt_weights, index=criteria, columns=alternatives).to_excel(writer, sheet_name="Alt_Weights")
    final_df.to_excel(writer, sheet_name="Final Ranking", index=False)

st.download_button(
    label="⬇️ Download AHP Results as Excel",
    data=output.getvalue(),
    file_name="AHP_Results.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
