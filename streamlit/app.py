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

# --- Streamlit UI ---
st.title("📚 Book Recommendation App")
st.write("Select a book title to get recommendations!")

# --- Book Input (Dropdown with Search) ---
selected_book = st.selectbox("Choose a book:", book_titles)


# --- Display Selected Book ---
if selected_book:
    st.write(f"✅ You selected: **{selected_book}**")

# --- Slidebar ---
## Number of recommendations
n_recommendations = st.slider("Number of books:", 1, 20, 10)

## Weights for count and percentage
w1 = st.slider("Weight (w1) - number of other users who reccomended", 0.0, 1.0, 0.8)
w2 = 1 - w1

## Print w2
st.write(f"Weight (w2) - percentage of other users who reccomended: {w2:.2f}")

## Find ISBN of selected book
selected_ISBN = df[df['Book-Title'] == selected_book]['ISBN'].values[0]


## Find similar books
recommendations = recommend_books(selected_ISBN, df)
not_reccomendations = not_recommended_books(selected_ISBN, df)
merge_reccomendations = recommendations.merge(not_reccomendations, how='left', left_on='Book-Title', right_on='Book-Title').fillna(0)
merge_reccomendations['Recomm_%'] =100* merge_reccomendations['Count_recommend'] / (merge_reccomendations['Count_recommend'] + merge_reccomendations['Count_not_recommend'])

## Top books
top_books = rank_books(merge_reccomendations, count_col="Count_recommend", percent_col="Recomm_%", top_n=n_recommendations, w1=w1, w2=w2)

# --- Display Recommendations ---
st.write(f"📚 **Top Recommendations for {selected_book}**:"
            f"")  
st.dataframe(top_books.reset_index(drop=True))


