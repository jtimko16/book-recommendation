import pandas as pd


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
