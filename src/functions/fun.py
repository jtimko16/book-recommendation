import requests

def fetch_genre(isbn):
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