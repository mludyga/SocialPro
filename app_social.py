# app_social.py
import streamlit as st
import requests
from social_config import SITES

# --- LOGOWANIE STARTU APLIKACJI ---
print("\n--- APLIKACJA app_social.py URUCHOMIONA ---")

from social_poster import (
    get_latest_wp_posts,
    choose_article_for_socials,
    get_full_article_content,
    create_facebook_post_from_article,
    post_to_facebook_page
)

st.set_page_config(page_title="Social Media Poster AI", layout="centered")
st.title("🤖 Social Media Poster AI")
st.write("Narzędzie do tworzenia i publikacji postów na Facebooku na podstawie artykułów.")

if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""
if 'featured_image_bytes' not in st.session_state:
    st.session_state.featured_image_bytes = None

st.header("Krok 1: Wybierz portal źródłowy")
friendly_names = {key: SITES[key]['friendly_name'] for key in SITES if SITES[key].get("facebook_page")}
friendly_names_reversed = {v: k for k, v in friendly_names.items()}
chosen_friendly_name = st.selectbox(
    "Portal, z którego pobierzemy artykuły:",
    options=list(friendly_names.values())
)
site_key = friendly_names_reversed[chosen_friendly_name]

st.header("Krok 2: Wybierz tryb pracy")
auto_tab, manual_tab = st.tabs(["🚀 Tryb Automatyczny", "✍️ Tryb Ręczny"])

with auto_tab:
    st.info("W tym trybie AI wybierze najlepszy artykuł, napisze do niego posta, a Ty go tylko zatwierdzisz.")

    if st.button("Pobierz artykuły i wygeneruj posta AI"):
        st.session_state.generated_post = ""
        st.session_state.featured_image_bytes = None
        
        # --- LOGOWANIE KROKÓW ---
        print("LOG: KROK 1/5 - Rozpoczynam pobieranie artykułów z WordPress.")
        articles = get_latest_wp_posts(site_key, count=10)
        
        if not articles:
            st.error("Nie udało się pobrać żadnych artykułów z tego portalu.")
            print("!!! BŁĄD: get_latest_wp_posts zwróciło pustą listę.")
        else:
            print(f"LOG: KROK 2/5 - POBRANO {len(articles)} artykułów. Rozpoczynam wybór przez AI.")
            chosen_article = choose_article_for_socials(articles)
            st.write(f"Wybrano artykuł: **{chosen_article['title']}**")
            
            print(f"LOG: KROK 3/5 - WYBRANO ARTYKUŁ: '{chosen_article['title']}'. Pobieram pełną treść.")
            full_content = get_full_article_content(site_key, chosen_article['id'])
            
            print("LOG: KROK 4/5 - POBRANO TREŚĆ. Pobieram obrazek wyróżniający.")
            image_url = chosen_article.get("featured_image_url")
            if image_url:
                try:
                    image_response = requests.get(image_url, timeout=15)
                    if image_response.status_code == 200:
                        content_type = image_response.headers.get('content-type', '')
                        if 'image' in content_type:
                            st.session_state.featured_image_bytes = image_response.content
                            print("LOG: Obrazek pobrany pomyślnie.")
                        else:
                            st.warning(f"Link prowadzi do treści, która nie jest obrazem ({content_type}).")
                            print(f"LOG: Link do obrazka nie jest obrazem: {content_type}")
                    else:
                        st.warning(f"Nie udało się pobrać obrazka. Kod: {image_response.status_code}")
                        print(f"LOG: Błąd pobierania obrazka, kod: {image_response.status_code}")
                except Exception as e:
                    st.warning(f"Wystąpił błąd podczas pobierania obrazka: {e}")
                    print(f"LOG: Wyjątek podczas pobierania obrazka: {e}")
            else:
                st.info("Wybrany artykuł nie ma obrazka wyróżniającego.")
                print("LOG: Brak obrazka wyróżniającego dla artykułu.")

            print("LOG: KROK 5/5 - Rozpoczynam generowanie posta przez AI.")
            generated_post = create_facebook_post_from_article(chosen_article['title'], full_content, chosen_article['link'])
            st.session_state.generated_post = generated_post
            print("LOG: Zakończono proces generowania.")
            st.rerun() # Odświeżamy aplikację, aby pokazać wyniki

    if st.session_state.generated_post:
        st.subheader("Wygenerowany post (możesz go edytować):")
        edited_post = st.text_area("Treść posta:", value=st.session_state.generated_post, height=250)
        
        if st.session_state.featured_image_bytes:
            st.subheader("Sugerowane zdjęcie (możesz je zmienić poniżej):")
            st.image(st.session_state.featured_image_bytes)
        
        uploaded_image = st.file_uploader("Opcjonalnie: zmień lub dodaj zdjęcie do posta", type=['jpg', 'jpeg', 'png'])
        if st.button("✅ Opublikuj na Facebooku"):
            image_to_publish = None
            if uploaded_image:
                image_to_publish = uploaded_image.getvalue()
            elif st.session_state.featured_image_bytes:
                image_to_publish = st.session_state.featured_image_bytes
            with st.spinner("Publikowanie..."):
                result = post_to_facebook_page(site_key, edited_post, image_to_publish)
                if "error" in result:
                    st.error(f"Błąd publikacji: {result['error']}")
                else:
                    post_id = result.get('id', 'Brak ID')
                    st.success(f"Post został opublikowany! ID posta: {post_id}")
                    st.balloons()
with manual_tab:
    # Sekcja manualna pozostaje bez zmian
    st.info("W tym trybie samodzielnie piszesz treść posta i wybierasz, gdzie go opublikować.")
    manual_message = st.text_area("Wpisz treść posta:", height=200, key="manual_message")
    manual_image = st.file_uploader("Dodaj zdjęcie (opcjonalnie):", type=['jpg', 'jpeg', 'png'], key="manual_image")
    if st.button("Opublikuj ręcznie na Facebooku"):
        if not manual_message:
            st.warning("Treść posta nie może być pusta!")
        else:
            with st.spinner("Publikowanie..."):
                image_bytes = manual_image.getvalue() if manual_image else None
                result = post_to_facebook_page(site_key, manual_message, image_bytes)
                if "error" in result:
                    st.error(f"Błąd publikacji: {result['error']}")
                else:
                    post_id = result.get('id', 'Brak ID')
                    st.success(f"Post został opublikowany! ID posta: {post_id}")
                    st.balloons()
