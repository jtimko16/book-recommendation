import pandas as pd
import numpy as np


def recommend_books(selected_ISBN: str, df: pd.DataFrame) -> pd.DataFrame:
    """Finds books liked by users who also liked the selected ISBN."""

    # Step 1: Find users who liked the selected book
    users_who_liked = df[(df["ISBN"] == selected_ISBN) & (df["Recommend"])]
    users_list = users_who_liked["User-ID"].unique()

    # Step 2: Find other books these users also liked
    other_books = df[
        (df["User-ID"].isin(users_list))
        & (df["Recommend"])
        & (df["ISBN"] != selected_ISBN)
    ]

    # Step 3: Count occurrences of each recommended book
    book_counts = other_books["ISBN"].value_counts().reset_index()
    book_counts.columns = ["ISBN", "Count_recommend"]

    ## Look up book nammes
    book_counts = book_counts.merge(
        df[["ISBN", "Book-Title"]].drop_duplicates(),
        how="left",
        left_on="ISBN",
        right_on="ISBN",
    )

    # *Step 5: Aggregate by book title** (summing counts for books with different ISBNs but the same title)
    book_counts = book_counts.groupby("Book-Title", as_index=False).agg(
        {"Count_recommend": "sum"}
    )

    # Step 6: Sort by recommendation count
    book_counts = book_counts.sort_values(by="Count_recommend", ascending=False)

    return book_counts


def not_recommended_books(selected_ISBN: str, df: pd.DataFrame) -> pd.DataFrame:
    """Finds books not liked by users who also did not like the selected ISBN, aggregating by book title."""

    # Step 1: Find users who did not recommend the selected book
    users_who_disliked = df[(df["ISBN"] == selected_ISBN) & (df["Not_Recommend"])]
    users_list = users_who_disliked["User-ID"].unique()

    # Step 2: Find other books these users also did not like
    other_books = df[
        (df["User-ID"].isin(users_list))
        & (df["Not_Recommend"])
        & (df["ISBN"] != selected_ISBN)
    ]

    # Step 3: Count occurrences of each not recommended book (by ISBN)
    book_counts = other_books["ISBN"].value_counts().reset_index()
    book_counts.columns = ["ISBN", "Count_not_recommend"]

    # Step 4: Merge to get book titles
    book_counts = book_counts.merge(
        df[["ISBN", "Book-Title"]].drop_duplicates(), how="left", on="ISBN"
    )

    # Step 5: Aggregate by book title (summing counts for books with different ISBNs but the same title)
    book_counts = book_counts.groupby("Book-Title", as_index=False).agg(
        {"Count_not_recommend": "sum"}
    )

    # Step 6: Sort by not recommendation count
    book_counts = book_counts.sort_values(by="Count_not_recommend", ascending=False)

    return book_counts


def prepare_data_assoc_rules(
    df: pd.DataFrame,
    threshold_recomm: int = 7,
    n_books: int = 1000,
    min_rating_per_user: int = 25,
    verbose: int = 0,
) -> pd.DataFrame:
    ### Create a new binary category for rating (everything above 8 is 1, otherwise 0)
    df["Recommend"] = np.where(df["Book-Rating"] >= threshold_recomm, 1, 0)
    df["Not_Recommend"] = np.where(
        (df["Book-Rating"] < threshold_recomm) & (df["Book-Rating"] > 0), 1, 0
    )

    top_n_books = (
        df.groupby("ISBN").size().sort_values(ascending=False).head(n_books).index
    )

    # Filter the DataFrame to include only the top N books
    subset_df_books = df[df["ISBN"].isin(top_n_books)].copy()

    # Filter the DataFrame to include only users with at least N ratings
    user_counts = df.groupby("User-ID").size()
    users_with_at_least_n_ratings = user_counts[
        user_counts >= min_rating_per_user
    ].index
    subset_df_book_users = subset_df_books[
        subset_df_books["User-ID"].isin(users_with_at_least_n_ratings)
    ]

    if verbose == 1:
        print(f"Unique User-IDs: {len(subset_df_book_users['User-ID'].unique())}")
        print(f"Unique ISBNs: {len(subset_df_book_users['ISBN'].unique())}")

    return subset_df_book_users


def rank_books(
    df,
    count_col="Count_Recommend",
    percent_col="Percent_Recommend",
    top_n=10,
    w1=0.5,
    w2=0.5,
) -> pd.DataFrame:
    """Ranks books based on Count_Recommend and % Recommendation."""

    # Normalize values between 0 and 1
    df[count_col + "_norm"] = (df[count_col] - df[count_col].min()) / (
        df[count_col].max() - df[count_col].min()
    )
    df[percent_col + "_norm"] = (df[percent_col] - df[percent_col].min()) / (
        df[percent_col].max() - df[percent_col].min()
    )

    # Compute score
    df["Score"] = w1 * df[count_col + "_norm"] + w2 * df[percent_col + "_norm"]

    # Select top books
    top_books = df.sort_values(by="Score", ascending=False).head(top_n)

    return top_books[["Book-Title", "Score", count_col, percent_col]]
