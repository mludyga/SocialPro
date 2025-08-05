# social_poster.py - WERSJA OSTATECZNA
import requests
import openai
import base64  # Ważny import dla logowania
from bs4 import BeautifulSoup
from social_config import SITES, COMMON_KEYS

# --- Prawidłowa inicjalizacja klienta OpenAI ---
client = None
api_key = COMMON_KEYS.get("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
    print("LOG: Klient OpenAI został poprawnie zainicjowany.")
else:
    print("!!! KRYTYCZNY BŁĄD: Nie znaleziono klucza OPENAI_API_KEY. !!!")


# --- NOWA FUNKCJA DO LOGOWANIA W WORDPRESS ---
def get_auth_header(site_config):
    """Tworzy nagłówek autoryzacyjny dla WordPressa na podstawie metody w configu."""
    auth_method = site_config.get('auth_method', 'basic')
    
    if auth_method == 'bearer':
        token = site_config.get("wp_bearer_token")
        if not token: return {}
        return {'Authorization': f"Bearer {token}"}
    
    # Domyślnie używamy metody 'basic'
    username = site_config.get("wp_username")
    password = site_config.get("wp_password")
    if not username or not password: return {}
    
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f"Basic {token}"}


def get_latest_wp_posts(site_key, count=5):
    """Pobiera listę ostatnich artykułów z WP, włącznie z autoryzacją."""
    site_config = SITES.get(site_key)
    if not site_config:
        print(f"Błąd: Nie znaleziono konfiguracji dla klucza '{site_key}'")
        return []

    url = f"{site_config['wp_api_url_base']}/posts"
    params = {'per_page': count, 'orderby': 'date', 'order': 'desc', '_embed': ''}
    
    try:
        # POPRAWKA: Dodajemy nagłówki z danymi logowania
        headers = get_auth_header(site_config)
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        
        posts = response.json()
        results = []
        for post in posts:
            image_url = None
            try:
                image_url = post['_embedded']['wp:featuredmedia'][0]['source_url']
            except (KeyError, IndexError):
                pass
            results.append({
                "id": post["id"],
                "title": post["title"]["rendered"],
                "link": post["link"],
                "featured_image_url": image_url
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania postów z {site_key}: {e}")
        return []

def get_full_article_content(site_key, post_id):
    """Pobiera pełną treść artykułu, włącznie z autoryzacją."""
    site_config = SITES.get(site_key)
    if not site_config: return ""
    
    url = f"{site_config['wp_api_url_base']}/posts/{post_id}"
    try:
        # POPRAWKA: Dodajemy nagłówki z danymi logowania
        headers = get_auth_header(site_config)
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content_html = response.json()["content"]["rendered"]
        soup = BeautifulSoup(content_html, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"Błąd w funkcji get_full_article_content: {e}")
        return ""

def find_pexels_images_list(query, count=6):
    """Wyszukuje w Pexels listę zdjęć i zwraca ich dane."""
    pexels_api_key = COMMON_KEYS.get("PEXELS_API_KEY")
    if not pexels_api_key:
        print("LOG: Brak klucza PEXELS_API_KEY.")
        return []

    try:
        from pexels_api import API
        api = API(pexels_api_key)
        api.search(query, page=1, results_per_page=count)
        photos = api.get_entries()

        if photos:
            return [{"id": photo.id, "photographer": photo.photographer, "preview_url": photo.medium, "original_url": photo.large, "description": photo.description} for photo in photos]
        return []
    except Exception as e:
        print(f"!!! BŁĄD w funkcji find_pexels_images_list: {e} !!!")
        return []

def choose_article_for_socials(articles):
    """Używa AI do wyboru najlepszego artykułu na post."""
    if not client: return articles[0] if articles else None
    if not articles: return None

    titles_list = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles)])
    prompt = f"Przeanalizuj listę tytułów i wybierz jeden z największym potencjałem na post na Facebooku...\n{titles_list}\nZwróć tylko numer."
    
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.5)
        choice = response.choices[0].message.content.strip()
        chosen_index = int(choice) - 1
        return articles[chosen_index] if 0 <= chosen_index < len(articles) else articles[0]
    except Exception as e:
        print(f"Błąd w funkcji choose_article_for_socials: {e}")
        return articles[0]

def create_facebook_post_from_article(article_title, article_content, article_link):
    """Generuje treść posta na Facebooka."""
    if not client: return "BŁĄD: Klient OpenAI nie jest skonfigurowany."
        
    prompt = f"""
    Jesteś ekspertem od social media. Stwórz angażujący post na Facebooka na podstawie artykułu.
    Tytuł: "{article_title}"
    Treść (fragment): "{article_content[:3000]}"
    Link: {article_link}
    Zasady:
    1. Zacznij od emoji.
    2. Napisz 2-4 zdania streszczenia.
    3. Zakończ pytaniem do czytelników.
    4. Dodaj 3-5 hasztagów.
    5. Na końcu dodaj link w formacie: "Więcej -> {article_link}"
    Zwróć tylko treść posta.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! BŁĄD w funkcji create_facebook_post_from_article: {e} !!!")
        return "Niestety, nie udało się wygenerować posta. Spróbuj ponownie."

def post_to_facebook_page(site_key, message, image_bytes=None):
    """Publikuje post na stronie na Facebooku."""
    fb_config = SITES.get(site_key, {}).get("facebook_page")
    if not fb_config: return {"error": "Brak konfiguracji Facebooka dla tego portalu."}
    
    page_id = fb_config['page_id']
    token = fb_config['page_access_token']
    if not token: return {"error": "Brak tokenu dostępu do Facebooka w konfiguracji."}
    
    if image_bytes:
        url = f"https://graph.facebook.com/{page_id}/photos"
        files = {'source': image_bytes}
        params = {'caption': message, 'access_token': token}
        response = requests.post(url, files=files, params=params, timeout=60)
    else:
        url = f"https://graph.facebook.com/{page_id}/feed"
        params = {'message': message, 'access_token': token}
        response = requests.post(url, params=params, timeout=30)
        
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Błąd publikacji na Facebooku: {response.text}")
        return {"error": response.json()}
