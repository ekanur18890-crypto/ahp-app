import streamlit as st
import numpy as np
import pandas as pd

# ----- AHP CALCULATION FUNCTION -----
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

# ----- STREAMLIT UI -----
st.title("⚖️ AHP Calculation Tool")
st.write("Use this app to calculate priorities using the Analytic Hierarchy Process (AHP).")

# Step 1: Define Criteria
st.header("Step 1: Define Criteria")
criteria = st.text_input("Enter criteria (comma-separated):", "Cost, Reliability, Sustainability").split(",")
criteria = [c.strip() for c in criteria if c.strip()]

if len(criteria) < 2:
    st.warning("Please enter at least 2 criteria.")
    st.stop()

# Step 2: Pairwise Comparison Matrix
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

criteria_weights, CR = ahp_weights(criteria_matrix)

st.subheader("Results:")
st.table(pd.DataFrame({"Criterion": criteria, "Weight": np.round(criteria_weights, 4)}))
st.info(f"Consistency Ratio (CR): {CR:.3f}")
if CR > 0.1:
    st.warning("⚠️ Your judgments may be inconsistent (CR > 0.1). Try adjusting the comparisons.")
