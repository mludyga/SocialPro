# social_poster.py - WERSJA Z POPRAWIONYM PUBLIKOWANIEM ZDJĘĆ
import requests
import openai
import base64
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


# --- Funkcja do logowania w WordPress ---
def get_auth_header(site_config):
    auth_method = site_config.get('auth_method', 'basic')
    if auth_method == 'bearer':
        token = site_config.get("wp_bearer_token")
        if not token: return {}
        return {'Authorization': f"Bearer {token}"}
    
    username = site_config.get("wp_username")
    password = site_config.get("wp_password")
    if not username or not password: return {}
    
    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f"Basic {token}"}


def get_latest_wp_posts(site_key, count=10):
    site_config = SITES.get(site_key)
    if not site_config:
        return []
    url = f"{site_config['wp_api_url_base']}/posts"
    params = {'per_page': count, 'orderby': 'date', 'order': 'desc', '_embed': ''}
    try:
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
                "id": post["id"], "title": post["title"]["rendered"], 
                "link": post["link"], "featured_image_url": image_url
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania postów z {site_key}: {e}")
        return []

def get_full_article_content(site_key, post_id):
    site_config = SITES.get(site_key)
    if not site_config: return ""
    url = f"{site_config['wp_api_url_base']}/posts/{post_id}"
    try:
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
    pexels_api_key = COMMON_KEYS.get("PEXELS_API_KEY")
    if not pexels_api_key: return []
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
    if not client: return "BŁĄD: Klient OpenAI nie jest skonfigurowany."
    prompt = f"Jesteś ekspertem od social media... Stwórz post... Tytuł: \"{article_title}\"... Link: {article_link}..."
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! BŁĄD w funkcji create_facebook_post_from_article: {e} !!!")
        return "Niestety, nie udało się wygenerować posta."

# --- OSTATECZNA, POPRAWIONA FUNKCJA PUBLIKACJI ---
def post_to_facebook_page(site_key, message, image_bytes=None):
    """Publikuje post na stronie na Facebooku."""
    fb_config = SITES.get(site_key, {}).get("facebook_page")
    if not fb_config: return {"error": "Brak konfiguracji Facebooka dla tego portalu."}
    
    page_id = fb_config['page_id']
    token = fb_config['page_access_token']
    if not token: return {"error": "Brak tokenu dostępu do Facebooka."}
    
    try:
        if image_bytes:
            # Krok 1: Wgraj zdjęcie jako nieopublikowane, aby uzyskać jego ID
            upload_url = f"https://graph.facebook.com/{page_id}/photos"
            files = {'source': image_bytes}
            upload_params = {'access_token': token, 'published': 'false'}
            
            print("LOG: Krok 1/2 - Wysyłanie zdjęcia na serwer Facebooka...")
            upload_response = requests.post(upload_url, files=files, params=upload_params, timeout=60)
            upload_response.raise_for_status()
            photo_id = upload_response.json().get('id')
            
            if not photo_id:
                print(f"!!! BŁĄD: Nie udało się uzyskać ID wgranego zdjęcia. Odpowiedź: {upload_response.text}")
                return {"error": "Nie udało się uzyskać ID wgranego zdjęcia."}

            # Krok 2: Opublikuj post na osi czasu, dołączając wgrane zdjęcie za pomocą jego ID
            post_url = f"https://graph.facebook.com/{page_id}/feed"
            post_params = {
                'access_token': token,
                'message': message,
                'attached_media[0]': f'{{"media_fbid": "{photo_id}"}}'
            }
            
            print(f"LOG: Krok 2/2 - Publikowanie posta z dołączonym zdjęciem (ID: {photo_id})...")
            response = requests.post(post_url, params=post_params, timeout=30)
            response.raise_for_status()
            
        else:
            # Publikacja postu z samym tekstem (bez zmian)
            post_url = f"https://graph.facebook.com/{page_id}/feed"
            post_params = {'message': message, 'access_token': token}
            response = requests.post(post_url, params=post_params, timeout=30)
            response.raise_for_status()
        
        return response.json()

    except requests.exceptions.RequestException as e:
        error_text = e.response.text if e.response else str(e)
        print(f"Błąd publikacji na Facebooku: {error_text}")
        return {"error": e.response.json() if e.response else {"message": str(e)}}
