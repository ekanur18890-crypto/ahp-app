import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

# ---------- Menampilkan judul aplikasi dan deskripsi singkat ----------
st.title("AHP Priority")
st.write("Aplikasi pengambilan keputusan berbasis Analytical Hierarchy Process")

st.markdown(
    "<h2 style='text-decoration: underline;'>Perhitungan Bobot Kriteria</h2>",
    unsafe_allow_html=True
)

# Step 1: Menentukan Kriteria
st.subheader("Langkah 1: Menentukan Input Kriteria")
criteria = st.text_input("Masukkan kriteria (gunakan koma sebagai pemisah):", "Kriteria 1, Kriteria 2, Kriteria 3").split(",")
criteria = [c.strip() for c in criteria if c.strip()]

if len(criteria) < 2:
    st.warning("Masukkan minimal 2 kriteria.")
    st.stop()
    

# Step 2: Perbandingan Berpasangan
st.subheader("Langkah 2: Perbandingan Berpasangan Antar Kriteria")

st.write("Gunakan template excel untuk perbandingan berpasangan")
with open("pairwise_criteria.xlsx", "rb") as file:
    file_data = file.read()
    
st.download_button(
    label = "📥 Download template",
    data = file_data,
    file_name = "perbandingan_kriteria.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

criteria_matrix = np.ones((len(criteria), len(criteria)))
criteria_df = pd.DataFrame(criteria_matrix, columns=criteria, index=criteria)

# Step 3: Membuat tabel untuk input matriks
st.markdown("Masukkan data perbandingan berpasangan pada tabel berikut:")

edited_df = st.data_editor(criteria_df, key="criteria_table", num_rows="fixed")

# Step 4: Update reciprocals secara otomatis
for i in range(len(criteria)):
    for j in range(len(criteria)):
        if i == j:
            edited_df.iloc[i, j] = 1.0
        elif edited_df.iloc[i, j] != 0:
            edited_df.iloc[j, i] = round(1 / edited_df.iloc[i, j], 3)

# Step 5: Perhitungan Bobot
matrix = edited_df.to_numpy().astype(float)

# Normalisasi Matriks
col_sum = matrix.sum(axis=0)
normalized_matrix = matrix / col_sum

# Compute average across rows (priority vector)
weights = normalized_matrix.mean(axis=1)
weights = weights / weights.sum()  # ensure they sum to 1

# Step 6: Membuat DataFrame untuk menampilkan hasil Bobot
weights_df = pd.DataFrame({
    "Kriteria": criteria,
    "Bobot": np.round(weights, 4)
})

# Step 7: Perhitungan Consistency Ratio
weighted_sum = np.dot(matrix, weights)
consistency_vector = weighted_sum / weights
lambda_max = np.mean(consistency_vector)
n = len(criteria)
CI = (lambda_max - n) / (n - 1)

# Random Index (RI) values
RI_dict = {1:0.00, 2:0.00, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
RI = RI_dict.get(n, 1.49)  # default max for n > 10
CR = CI / RI if RI != 0 else 0

# Step 8: Menampilkan tabel hasil perhitungan final
st.write("#### Matriks Perbandingan Berpasangan")
st.dataframe(pd.DataFrame(matrix, index=criteria, columns=criteria).style.format("{:.3f}"))

st.subheader("Langkah 3: Normalisasi Matriks")
#st.subheader("Matriks Normalisasi")
st.dataframe(pd.DataFrame(normalized_matrix, index=criteria, columns=criteria).style.format("{:.3f}"))

st.subheader("Langkah 4: Menentukan Bobot Kriteria")
st.table(weights_df.style.hide(axis='index'))

# Step 9: Menampilkan hasil Consistency Ratio
st.subheader("Langkah 5: Consistency Check")
st.write(f"λ_max = {lambda_max:.4f}")
st.write(f"CI = {CI:.4f}")
st.write(f"CR = {CR:.4f}")

if CR < 0.10:
    st.success("✅ Matriks Perbandingan Berpasangan Konsisten (CR < 0.1)")
else:
    st.error("⚠️ Matriks tidak Konsisten (CR ≥ 0.1)")
    
# Step 10: Membuat file excel (downloadable) untuk menampilkan hasil
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:

    pd.DataFrame(matrix, index=criteria, columns=criteria).to_excel(writer, sheet_name='Matriks Perbandingan')
    pd.DataFrame(normalized_matrix, index=criteria, columns=criteria).to_excel(writer, sheet_name='Matriks Normalisasi')
    weights_df.to_excel(writer, sheet_name='Bobot', index=False)
    summary_df = pd.DataFrame({
        'Lambda Max': [lambda_max],
        'CI': [CI],
        'CR': [CR]
    })
    summary_df.to_excel(writer, sheet_name='Consistency', index=False)
    writer.close()

# Step 11: Membuat tombol download
st.write("Download Hasil Perhitungan dalam Excel")
st.download_button(
    label="📥 Download Hasil",
    data=output.getvalue(),
    file_name="Hasil Perhitungan AHP.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# ========================================== MODIFICATION START HERE ===========================================

st.markdown(
    "<h2 style='text-decoration: underline;'>Perhitungan Ranking Alternatif</h2>",
    unsafe_allow_html=True
)

# Step 1: Menentukan Alternative
st.subheader("Langkah 1: Menentukan Alternative")
alternatives = st.text_input("Masukkan alternative (gunakan koma sebagai pemisah):", "Alternative 1, Alternative 2, Alternative 3").split(",")
alternatives = [a.strip() for a in alternatives if a.strip()]

if len(alternatives) < 2:
    st.warning("Masukkan minimal 2 alternative.")
    st.stop()

# Step 2. Perbandingan Berpasangan tiap Kriteria
# ---------------------------
st.subheader("Langkah 2: Perbandingan Berpasangan Setiap Kriteria")

alt_weights_dict = {}  # store local weights per criterion

for c in criteria:
    st.markdown(f"#### Kriteria: {c}")
    alt_matrix = np.ones((len(alternatives), len(alternatives)))
    alt_df = pd.DataFrame(alt_matrix, columns=alternatives, index=alternatives)
    alt_edit = st.data_editor(alt_df, key=f"alt_editor_{c}", num_rows="fixed")

    # Memastikan reciprocal symmetry
    for i in range(len(alternatives)):
        for j in range(len(alternatives)):
            if i == j:
                alt_edit.iloc[i, j] = 1.0
            elif alt_edit.iloc[i, j] != 0:
                alt_edit.iloc[j, i] = round(1 / alt_edit.iloc[i, j], 3)

    # Menghitung Bobot untuk setiap Kriteria
    mat_alt = alt_edit.to_numpy().astype(float)
    norm_alt = mat_alt / mat_alt.sum(axis=0)
    local_weights = norm_alt.mean(axis=1)
    local_weights = local_weights / local_weights.sum()
    alt_weights_dict[c] = local_weights

    # Menampilkan Bobot setiap Kriteria
    st.write(f"Bobot untuk Kriteria: {c}")
    st.table(pd.DataFrame({"Alternative": alternatives, f"Weight ({c})": np.round(local_weights, 4)}).style.hide(axis='index'))

# ---------------------------
# Step 3. Menghitung Bobot Final
# ---------------------------
st.subheader("Langkah 3: Menentukan Bobot Final")

# Membuat DataFrame untuk semua Bobot tiap Kriteria
alt_weights_df = pd.DataFrame(alt_weights_dict, index=alternatives)

# Mengalikan tiap kolom dengan Bobot kriterianya
weighted_matrix = alt_weights_df * weights_df["Bobot"].values

# Menghitung hasil final
final_scores = weighted_matrix.sum(axis=1)
ranking_df = pd.DataFrame({
    "Alternative": alternatives,
    "Final Score": np.round(final_scores, 4)
}).sort_values(by="Final Score", ascending=False)

st.write("#### Bobot Alternative tiap Kriteria")
st.dataframe(weighted_matrix.style.format("{:.4f}"))

st.subheader("Langkah 4: Menentukan Final Ranking")
st.write("#### Final Ranking")
st.table(ranking_df.style.hide(axis='index'))

best_alt = ranking_df.iloc[0]["Alternative"]
st.success(f"🏆 Alternatif terbaik berdasarkan AHP: **{best_alt}**")

# Step 4. Menghitung Consistency Ratio


# ============================================================================================================
st.write("Aplikasi ini juga tersedia dalam template excel untuk digunakan secara offline.")
with open("ahp_full_template.xlsx", "rb") as file:
    file_full = file.read()
    
st.download_button(
    label = "📥 Download full template",
    data = file_full,
    file_name = "ahp_full_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ========================================== MODIFICATION END HERE ===========================================

st.markdown(
    """
    <div style='text-align: center; color: rgba(0, 0, 0, 0.5); font-size: 15px; margin-top: 50px;'>
        Kelompok Riset Microgrid<br>2025
    </div>
    
    <div style='text-align: center; color: rgba(0, 0, 0, 0.3); font-size: 18px; margin-top: 50px;'>
        PUSAT RISET TEKNOLOGI KELISTRIKAN<br>BADAN RISET DAN INOVASI NASIONAL
    </div>
    """,
    unsafe_allow_html=True
)