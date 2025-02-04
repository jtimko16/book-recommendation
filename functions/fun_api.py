import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # For progress bar
import pandas as pd

def fetch_genre(isbn: str) -> dict:
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        book_key = f"ISBN:{isbn}"
        
        if book_key in data:
            book_info = data[book_key]
            title = book_info.get("title", "Unknown Title")
            genres = [sub["name"] for sub in book_info.get("subjects", [])] or ["Unknown Genre"]
            return {"ISBN": isbn, "Title": title, "Genres": ", ".join(genres)}
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ISBN {isbn}: {e}")
        return {"ISBN": isbn, "Title": "Error", "Genres": "Error"}
    
    return {"ISBN": isbn, "Title": "Not Found", "Genres": "Not Found"}


# Process ISBNs in parallel
def fetch_all_genres(isbn_list:list[str], max_workers=10) -> pd.DataFrame:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_genre, isbn): isbn for isbn in isbn_list}
        for future in tqdm(as_completed(futures), total=len(isbn_list), desc="Fetching Genres"):
            results.append(future.result())

    results = pd.DataFrame(results)
    return results