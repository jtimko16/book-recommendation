import streamlit as st
import pandas as pd

from fun_model import recommend_books, not_recommended_books, rank_books

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv('data/model_data_assoc_rules.csv')

## Book titles
df = load_data()
book_titles = df['Book-Title'].unique()

## Prepare user-boom matrix
user_book_matrix = df.pivot(index='User-ID', columns='ISBN', values='Recommend').fillna(0)

# --- Streamlit UI ---
st.title("📚 Book Recommendation App")
st.write("Select a book title to get recommendations!")

# --- Book Input (Dropdown with Search) ---
selected_book = st.selectbox("Choose a book:", book_titles)

## Find similar books
recommendations = recommend_books(selected_book, df)
not_reccomendations = not_recommended_books(selected_book, df)
merge_reccomendations = recommendations.merge(not_reccomendations, how='left', left_on='Book-Title', right_on='Book-Title').fillna(0)
merge_reccomendations['Recommendation_Percentage'] =100* merge_reccomendations['Count_recommend'] / (merge_reccomendations['Count_recommend'] + merge_reccomendations['Count_not_recommend'])

## Top books
top_books = rank_books(merge_reccomendations, count_col="Count_recommend", percent_col="Recommendation_Percentage", top_n=10, w1=0.8, w2=0.2)


# --- Display Selected Book ---
if selected_book:
    st.write(f"✅ You selected: **{selected_book}**")


# --- Display Recommendations ---
st.write(f"📚 **Top Recommendations for {selected_book}**:"
            f"")  
st.table(recommendations)

