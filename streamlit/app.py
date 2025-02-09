import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv('../data/model_data_assoc_rules.csv')

## Book titles
df = load_data()
book_titles = df['Book-Title'].unique()

# --- Streamlit UI ---
st.title("📚 Book Recommendation App")
st.write("Select a book title to get recommendations!")

# --- Book Input (Dropdown with Search) ---
selected_book = st.selectbox("Choose a book:", book_titles)

# --- Display Selected Book ---
if selected_book:
    st.write(f"✅ You selected: **{selected_book}**")
