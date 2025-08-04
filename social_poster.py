# social_poster.py
import requests
import openai
from bs4 import BeautifulSoup

# Zaimportuj swoją nową konfigurację
from social_config import SITES, COMMON_KEYS

# Inicjalizacja klienta OpenAI
# Upewnij się, że klucz jest dostępny jako sekret, gdy uruchamiasz w chmurze
if COMMON_KEYS["OPENAI_API_KEY"]:
    openai.api_key = COMMON_KEYS["OPENAI_API_KEY"]
else:
    # Możesz dodać obsługę błędu, jeśli klucz nie jest dostępny
    print("BŁĄD: Brak klucza OPENAI_API_KEY.")


def get_latest_wp_posts(site_key, count=10):
    """Pobiera listę ostatnich artykułów z WP, włącznie z URL-em obrazka wyróżniającego."""
    site_config = SITES.get(site_key)
    if not site_config:
        print(f"Błąd: Nie znaleziono konfiguracji dla klucza '{site_key}'")
        return []

    url = f"{site_config['wp_api_url_base']}/posts"
    # DODAJEMY '_embed' ABY POBRAĆ DODATKOWE DANE, W TYM OBRAZEK
    params = {'per_page': count, 'orderby': 'date', 'order': 'desc', '_embed': ''}

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        posts = response.json()
        
        results = []
        for post in posts:
            image_url = None
            # Ta skomplikowana struktura jest potrzebna, by bezpiecznie dostać się do URL-a obrazka
            try:
                image_url = post['_embedded']['wp:featuredmedia'][0]['source_url']
            except (KeyError, IndexError):
                print(f"Post ID {post['id']} nie ma obrazka wyróżniającego.")

            results.append({
                "id": post["id"], 
                "title": post["title"]["rendered"], 
                "link": post["link"],
                "featured_image_url": image_url # <-- NOWE POLE
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania postów z {site_key}: {e}")
        return []

def choose_article_for_socials(articles):
    """Używa AI do wyboru najlepszego artykułu na post w social mediach."""
    if not articles:
        return None
    
    # Tworzymy listę tytułów dla AI
    titles_list = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles)])

    prompt = f"""
    Przeanalizuj poniższą listę tytułów artykułów. Twoim zadaniem jest wybrać JEDEN, który ma największy potencjał, aby stać się angażującym postem na Facebooku. Weź pod uwagę takie czynniki jak: ciekawość, kontrowersja, użyteczność lub potencjał do wywołania dyskusji.

    Oto lista tytułów:
    {titles_list}

    Zwróć tylko i wyłącznie numer wybranego artykułu (np. "4").
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        choice = response.choices[0].message.content.strip()
        chosen_index = int(choice) - 1
        
        # Zwracamy cały obiekt wybranego artykułu
        if 0 <= chosen_index < len(articles):
            return articles[chosen_index]
        else: # Jeśli AI poda zły numer, weź pierwszy
            return articles[0]
    except Exception as e:
        print(f"Błąd podczas wyboru artykułu przez AI: {e}")
        # W razie błędu, po prostu wybierz pierwszy z listy
        return articles[0]

def get_full_article_content(site_key, post_id):
    """Pobiera pełną treść artykułu i czyści ją z tagów HTML."""
    site_config = SITES.get(site_key)
    url = f"{site_config['wp_api_url_base']}/posts/{post_id}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content_html = response.json()["content"]["rendered"]
        
        # Czyszczenie HTML do czystego tekstu
        soup = BeautifulSoup(content_html, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"Błąd podczas pobierania pełnej treści artykułu: {e}")
        return ""

def create_facebook_post_from_article(article_title, article_content, article_link):
    """Generuje treść posta na Facebooka na podstawie artykułu, dodając link źródłowy."""
    prompt = f"""
    Jesteś ekspertem od social media. Twoim zadaniem jest stworzenie angażującego posta na Facebooka na podstawie poniższego artykułu.

    Tytuł artykułu: "{article_title}"
    Treść artykułu (fragment): "{article_content[:3000]}"
    Link do artykułu: {article_link}

    Zasady tworzenia posta:
    1.  Zacznij od jednego, pasującego do tematu emoji.
    2.  Napisz 2-4 zdania, które streszczają najważniejszy lub najciekawszy wątek artykułu w przyjazny i intrygujący sposób.
    3.  Zakończ post otwartym pytaniem do czytelników, które zachęci ich do dyskusji.
    4.  Na końcu dodaj 3-5 trafnych hasztagów.
    5.  Na samym końcu posta, w nowej linii, dodaj link do artykułu w formacie: "Więcej -> {article_link}"
    
    Zwróć tylko i wyłącznie gotową treść posta.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Błąd podczas generowania posta przez AI: {e}")
        return "Niestety, nie udało się wygenerować posta. Spróbuj ponownie."

def post_to_facebook_page(site_key, message, image_bytes=None):
    """Publikuje post (tekst lub tekst ze zdjęciem) na stronie na Facebooku."""
    fb_config = SITES.get(site_key, {}).get("facebook_page")
    if not fb_config:
        return {"error": "Brak konfiguracji Facebooka dla tego portalu."}

    page_id = fb_config['page_id']
    token = fb_config['page_access_token']
    
    if not token:
        return {"error": "Brak tokenu dostępu do Facebooka w konfiguracji."}
    
    if image_bytes:
        # Publikacja postu ze zdjęciem
        url = f"https://graph.facebook.com/{page_id}/photos"
        files = {'source': image_bytes}
        params = {'caption': message, 'access_token': token}
        response = requests.post(url, files=files, params=params, timeout=60)
    else:
        # Publikacja postu z samym tekstem
        url = f"https://graph.facebook.com/{page_id}/feed"
        params = {'message': message, 'access_token': token}
        response = requests.post(url, params=params, timeout=30)
        
    if response.status_code == 200:
        print("Post opublikowany pomyślnie!")
        return response.json()
    else:
        print(f"Błąd publikacji na Facebooku: {response.text}")
        return {"error": response.json()}
