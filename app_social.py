# app_social.py
import streamlit as st
import requests # <-- DODAJ TĘ LINIĘ
from social_config import SITES

# Importujemy wszystkie nasze funkcje z logiki backendu
from social_poster import (
    get_latest_wp_posts,
    choose_article_for_socials,
    get_full_article_content,
    create_facebook_post_from_article,
    post_to_facebook_page
)

# --- Konfiguracja strony ---
st.set_page_config(page_title="Social Media Poster AI", layout="centered")
st.title("🤖 Social Media Poster AI")
st.write("Narzędzie do tworzenia i publikacji postów na Facebooku na podstawie artykułów.")

# --- Inicjalizacja Pamięci Sesji (bardzo ważne!) ---
# Przechowujemy tu dane, aby nie znikały po każdym kliknięciu
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""
if 'featured_image_bytes' not in st.session_state:
    st.session_state.featured_image_bytes = None

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal źródłowy")

# Tworzymy listę przyjaznych nazw portali, które mają konfigurację FB
friendly_names = {
    key: SITES[key]['friendly_name']
    for key in SITES if SITES[key].get("facebook_page")
}
# Odwracamy słownik, aby łatwo znaleźć klucz po przyjaznej nazwie
friendly_names_reversed = {v: k for k, v in friendly_names.items()}

chosen_friendly_name = st.selectbox(
    "Portal, z którego pobierzemy artykuły:",
    options=list(friendly_names.values())
)
# Znajdujemy klucz systemowy (np. "autozakup") na podstawie wybranej nazwy
site_key = friendly_names_reversed[chosen_friendly_name]


# --- KROK 2: Wybór trybu pracy (Automatyczny vs Ręczny) ---
st.header("Krok 2: Wybierz tryb pracy")

auto_tab, manual_tab = st.tabs(["🚀 Tryb Automatyczny", "✍️ Tryb Ręczny"])


# OSTATECZNA WERSJA - cała sekcja dla Trybu Automatycznego
with auto_tab:
    st.info("W tym trybie AI wybierze najlepszy artykuł, napisze do niego posta, a Ty go tylko zatwierdzisz.")

    if st.button("Pobierz artykuły i wygeneruj posta AI"):
        # Resetujemy poprzednie dane
        st.session_state.generated_post = ""
        st.session_state.featured_image_bytes = None

        with st.spinner("Krok 1/5: Pobieranie najnowszych artykułów..."):
            articles = get_latest_wp_posts(site_key, count=10)

        if not articles:
            st.error("Nie udało się pobrać żadnych artykułów z tego portalu.")
        else:
            with st.spinner("Krok 2/5: AI analizuje, który artykuł jest najciekawszy..."):
                chosen_article = choose_article_for_socials(articles)
                st.write(f"Wybrano artykuł: **{chosen_article['title']}**")

            with st.spinner("Krok 3/5: Pobieranie pełnej treści artykułu..."):
                full_content = get_full_article_content(site_key, chosen_article['id'])

            with st.spinner("Krok 4/5: Pobieranie i weryfikacja obrazka wyróżniającego..."):
                image_url = chosen_article.get("featured_image_url")
                if image_url:
                    try:
                        # --- OSTATECZNA POPRAWKA: Dodajemy nagłówek User-Agent ---
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        image_response = requests.get(image_url, headers=headers, timeout=15)
                        # ---------------------------------------------------------

                        if image_response.status_code == 200:
                            content_type = image_response.headers.get('content-type', '')
                            if 'image' in content_type:
                                st.session_state.featured_image_bytes = image_response.content
                            else:
                                st.warning(f"Link prowadzi do treści, która nie jest obrazem ({content_type}). Pomijam pobieranie.")
                        else:
                            st.warning(f"Nie udało się pobrać obrazka. Serwer odpowiedział kodem: {image_response.status_code}")
                    except Exception as e:
                        st.warning(f"Wystąpił błąd podczas pobierania obrazka: {e}")
                else:
                    st.info("Wybrany artykuł nie ma obrazka wyróżniającego.")

            with st.spinner("Krok 5/5: AI pisze angażującego posta na Facebooka..."):
                generated_post = create_facebook_post_from_article(chosen_article['title'], full_content, chosen_article['link'])
                st.session_state.generated_post = generated_post
                st.rerun() # Odświeżamy, aby pokazać wyniki

    # Jeżeli post został wygenerowany, wyświetlamy go w edytowalnym polu
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


# --- Logika dla Trybu Ręcznego ---
with manual_tab:
    st.info("W tym trybie samodzielnie piszesz treść posta i wybierasz, gdzie go opublikować.")

    manual_message = st.text_area("Wpisz treść posta:", height=200, key="manual_message")
    manual_image = st.file_uploader("Dodaj zdjęcie (opcjonalnie):", type=['jpg', 'jpeg', 'png'], key="manual_image")

    if st.button("Opublikuj ręcznie na Facebooku"):
        if not manual_message:
            st.warning("Treść posta nie może być pusta!")
        else:
            with st.spinner("Publikowanie..."):
                image_bytes = manual_image.getvalue() if manual_image else None
                # Używamy klucza portalu wybranego na samej górze
                result = post_to_facebook_page(site_key, manual_message, image_bytes)

                if "error" in result:
                    st.error(f"Błąd publikacji: {result['error']}")
                else:
                    post_id = result.get('id', 'Brak ID')
                    st.success(f"Post został opublikowany! ID posta: {post_id}")
                    st.balloons()

