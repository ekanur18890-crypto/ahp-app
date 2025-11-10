import streamlit as st
import numpy as np
import pandas as pd

st.write("Latihan membuat Kolom isian")
data = st.text_input("Masukkan data:").split(";")

If len(data) < 2
    st.warning("Data harus lebih dari 2")