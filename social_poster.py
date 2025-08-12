# social_poster.py - WERSJA Z POPRAWIONYM PUBLIKOWANIEM ZDJĘĆ
import requests
import openai
import base64
from bs4 import BeautifulSoup
from social_config import SITES, COMMON_KEYS
import re

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
    if not articles:
        return None
    if not client:
        return articles[0]

    titles_list = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(articles)])
    prompt = (
        "Wybierz numer JEDNEGO tytułu, który ma najwyższy potencjał na post na Facebooku.\n"
        "Kryteria: wysoka ciekawość, konkretne korzyści dla czytelnika, jasna obietnica, potencjał na listę/punkty, niezbyt techniczny.\n"
        "Zwróć tylko numer (cyfrę), nic więcej.\n\n" + titles_list
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=5
        )
        choice = response.choices[0].message.content.strip()
        chosen_index = int(re.findall(r'\d+', choice)[0]) - 1
        return articles[chosen_index] if 0 <= chosen_index < len(articles) else articles[0]
    except Exception as e:
        print(f"Błąd w funkcji choose_article_for_socials: {e}")
        return articles[0]

def create_facebook_post_from_article(article_title, article_content, article_link, length="standard", max_hashtags=5):
    """
    Generuje gotowy post na Facebooka (PL), bez 'Tytuł:' i bez markdown linków.
    length: 'short' (~400 zzs), 'standard' (~900 zzs), 'long' (~1400 zzs)
    """
    if not client:
        return "BŁĄD: Klient OpenAI nie jest skonfigurowany."

    # Ustal limity długości wg preferencji
    limits = {"short": 400, "standard": 900, "long": 1400}
    char_limit = limits.get(length, 900)

    system_msg = (
        "Piszesz post na Facebooka po polsku. Bez nagłówków typu 'Tytuł:' i bez linków w formacie Markdown."
        " Używaj 1–3 emoji w kluczowych miejscach (nie na początku każdej linii)."
    )

    prompt = f"""
Zadanie: Napisz JEDEN gotowy post na Facebooka o artykule.
Zasady (KLUCZOWE):
- Nie pisz słowa 'Tytuł:' ani nie cytuj tytułu w cudzysłowie.
- NIE używaj formatu Markdown do linków. Pokaż link jako czysty URL.
- Struktura:
  • Hak otwierający (1–2 zdania, konkretnie dlaczego czytelnik ma kliknąć).
  • 3–5 krótkich punktów (myślniki lub '•') z faktami/korzyściami.
  • Zakończ wezwaniem do działania + czysty link na KOŃCU.
- 3–5 hashtagów po polsku (krótkich; bez spacji). Nie duplikuj.
- Zwięźle: maksymalnie ~{char_limit} znaków.
- Ton: informacyjny, żywy, ale bez przesady w emoji/clickbaitu.

Dane wejściowe:
Tytuł artykułu: {article_title}
Kluczowe informacje (zajawka):
{(article_content or '')[:1200]}

Link (użyj jako czysty URL): {article_link}

Wynik: Zwróć wyłącznie treść posta gotową do wklejenia na Facebooka (bez dodatkowych komentarzy).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        return sanitize_facebook_post(raw, article_link, max_hashtags=max_hashtags, char_limit=char_limit)
    except Exception as e:
        print(f"!!! BŁĄD w funkcji create_facebook_post_from_article: {e} !!!")
        # awaryjnie fallback – czysty, krótki szkielet
        fallback = f"""Poznaj najważniejsze fakty i wskazówki 👇
- Sprawdź szczegóły w artykule
- Krótko i konkretnie
- Link na końcu

Czytaj więcej:
{article_link}
#Informacje #Polecamy"""
        return fallback

def sanitize_facebook_post(text, link, max_hashtags=5, char_limit=900):
    # 1) Usuń linie zaczynające się od "Tytuł:" / "Tytul:"
    text = re.sub(r'^\s*(Tytu[łl]):\s*.*$', '', text, flags=re.IGNORECASE | re.MULTILINE)

    # 2) Zamień markdown linki [tekst](url) -> "tekst: url"
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'\1: \2', text)

    # 3) Jeśli nie ma żadnego URL-a, dołącz czysty link na końcu
    if not re.search(r'https?://', text) and link:
        text = text.rstrip() + f"\n{link}"

    # 4) Ogranicz liczbę hashtagów do max_hashtags i usuń duplikaty (z zachowaniem kolejności)
    hashtags = re.findall(r'(?:^|\s)(#[A-Za-z0-9_ĄąĆćĘęŁłŃńÓóŚśŹźŻż]+)', text)
    seen = set()
    pruned = []
    for h in hashtags:
        key = h.lower()
        if key not in seen and len(pruned) < max_hashtags:
            pruned.append(h)
            seen.add(key)

    # usuń wszystkie hashtagi z treści
    text_no_hash = re.sub(r'(?:^|\s)#[A-Za-z0-9_ĄąĆćĘęŁłŃńÓóŚśŹźŻż]+', '', text)
    text = text_no_hash.strip()

    # 5) Przytnij nadmiar pustych linii
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    # 6) Dołącz pruned hashtagi na końcu (jeśli są)
    if pruned:
        text = text + "\n" + " ".join(pruned)

    # 7) Twarde przycięcie długości (jeśli trzeba), nie urywa URL-i:
    if len(text) > char_limit:
        # Jeśli końcówka zawiera URL, nie obcinaj go – najpierw spróbuj skrócić środek
        lines = text.splitlines()
        # zachowaj ostatnią linię jeśli to link/hashtagi
        tail = []
        if lines and (re.search(r'https?://', lines[-1]) or lines[-1].strip().startswith('#')):
            tail = [lines[-1]]
            body = "\n".join(lines[:-1])
        else:
            body = text
        # przytnij body
        body = body[:max(0, char_limit - (len("\n".join(tail)) + 1))].rstrip()
        text = (body + ("\n" + "\n".join(tail) if tail else "")).strip()

    return text

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

