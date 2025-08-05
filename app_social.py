# app_social.py - OSTATECZNA WERSJA Z INTEGRACJĄ PEXELS
import streamlit as st
import requests
from social_config import SITES

# Importujemy wszystkie nasze funkcje z logiki backendu, w tym nową funkcję Pexels
from social_poster import (
    get_latest_wp_posts,
    choose_article_for_socials,
    get_full_article_content,
    create_facebook_post_from_article,
    post_to_facebook_page,
    find_pexels_images_list # <-- NOWY IMPORT
)

# --- Konfiguracja strony ---
st.set_page_config(page_title="Social Media Poster AI", layout="centered")
st.title("🤖 Social Media Poster AI")
st.write("Narzędzie do tworzenia i publikacji postów na Facebooku na podstawie artykułów.")

# --- Inicjalizacja Pamięci Sesji (dodajemy nowe zmienne dla Pexels) ---
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""
if 'featured_image_bytes' not in st.session_state:
    st.session_state.featured_image_bytes = None
if 'featured_image_url' not in st.session_state:
    st.session_state.featured_image_url = None
if 'pexels_results' not in st.session_state: # <-- NOWA ZMIENNA
    st.session_state.pexels_results = []
if 'selected_pexels_url' not in st.session_state: # <-- NOWA ZMIENNA
    st.session_state.selected_pexels_url = None

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal źródłowy")

friendly_names = {key: SITES[key]['friendly_name'] for key in SITES if SITES[key].get("facebook_page")}
friendly_names_reversed = {v: k for k, v in friendly_names.items()}
chosen_friendly_name = st.selectbox("Portal, z którego pobierzemy artykuły:", options=list(friendly_names.values()))
site_key = friendly_names_reversed[chosen_friendly_name]

# --- KROK 2: Wybór trybu pracy ---
st.header("Krok 2: Wybierz tryb pracy")
auto_tab, manual_tab = st.tabs(["🚀 Tryb Automatyczny", "✍️ Tryb Ręczny"])

# --- Logika dla Trybu Automatycznego ---
with auto_tab:
    st.info("W tym trybie AI wybierze najlepszy artykuł, napisze do niego posta, a Ty go tylko zatwierdzisz.")

    if st.button("Pobierz artykuły i wygeneruj posta AI"):
        # Resetujemy wszystkie poprzednie dane
        st.session_state.generated_post = ""
        st.session_state.featured_image_bytes = None
        st.session_state.featured_image_url = None
        st.session_state.pexels_results = []
        st.session_state.selected_pexels_url = None

        with st.spinner("Krok 1/5: Pobieranie najnowszych artykułów..."):
            articles = get_latest_wp_posts(site_key, count=10)

        if not articles:
            st.error("Nie udało się pobrać żadnych artykułów z tego portalu.")
        else:
            with st.spinner("Krok 2/5: AI analizuje, który artykuł jest najciekawszy..."):
                chosen_article = choose_article_for_socials(articles)
                st.session_state.article_title_for_pexels = chosen_article['title'] # Zapisujemy tytuł dla Pexels
                st.write(f"Wybrano artykuł: **{chosen_article['title']}**")

            with st.spinner("Krok 3/5: Pobieranie pełnej treści artykułu..."):
                full_content = get_full_article_content(site_key, chosen_article['id'])

            with st.spinner("Krok 4/5: Pobieranie obrazka wyróżniającego..."):
                image_url = chosen_article.get("featured_image_url")
                if image_url:
                    st.session_state.featured_image_url = image_url
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        image_response = requests.get(image_url, headers=headers, timeout=15)
                        if image_response.status_code == 200 and 'image' in image_response.headers.get('content-type', ''):
                            st.session_state.featured_image_bytes = image_response.content
                    except Exception:
                        st.warning("Nie udało się pobrać obrazka z artykułu.")

            with st.spinner("Krok 5/5: AI pisze angażującego posta na Facebooka..."):
                generated_post = create_facebook_post_from_article(chosen_article['title'], full_content, chosen_article['link'])
                st.session_state.generated_post = generated_post
                st.rerun()

    # Jeżeli post został wygenerowany, wyświetlamy go w edytowalnym polu
    if st.session_state.generated_post:
        st.subheader("Wygenerowany post (możesz go edytować):")
        edited_post = st.text_area("Treść posta:", value=st.session_state.generated_post, height=250)
        
        # --- NOWA SEKCJA WYBORU OBRAZKA Z ZAKŁADKAMI ---
        st.subheader("Wybierz zdjęcie do posta:")
        img_tab1, img_tab2, img_tab3 = st.tabs(["🖼️ Z artykułu", "⬆️ Wgraj ręcznie", "🎨 Szukaj w Pexels"])

        with img_tab1:
            if st.session_state.featured_image_bytes:
                st.image(st.session_state.featured_image_bytes, caption="Sugerowane zdjęcie z artykułu.")
                st.markdown(f"**Źródło:** [{st.session_state.featured_image_url}]({st.session_state.featured_image_url})")
            else:
                st.info("Brak obrazka wyróżniającego w artykule lub nie udało się go pobrać.")

        with img_tab2:
            uploaded_image = st.file_uploader("Wybierz plik z dysku", type=['jpg', 'jpeg', 'png'])

        with img_tab3:
            search_query = st.text_input("Wpisz, co chcesz znaleźć:", value=st.session_state.get('article_title_for_pexels', ''))
            if st.button("Szukaj zdjęć w Pexels"):
                with st.spinner("Szukanie..."):
                    st.session_state.pexels_results = find_pexels_images_list(search_query)

            if st.session_state.pexels_results:
                cols = st.columns(3)
                for i, photo in enumerate(st.session_state.pexels_results):
                    with cols[i % 3]:
                        st.image(photo['preview_url'], caption=f"Autor: {photo['photographer']}")
                        if st.button("✅ Wybierz", key=f"pexels_{photo['id']}"):
                            st.session_state.selected_pexels_url = photo['original_url']
                            st.session_state.pexels_results = [] # Czyścimy wyniki po wyborze
                            st.rerun()
            
            if st.session_state.selected_pexels_url:
                st.success("Wybrano zdjęcie z Pexels!")
                st.image(st.session_state.selected_pexels_url)

        st.divider()

        # --- ZAKTUALIZOWANA LOGIKA PUBLIKACJI ---
        if st.button("✅ Opublikuj na Facebooku"):
            image_to_publish = None
            source_info = "Publikowanie posta "

            # Priorytet 1: Obrazek wgrany ręcznie
            if uploaded_image:
                source_info += "z ręcznie wgranym obrazkiem..."
                image_to_publish = uploaded_image.getvalue()
            # Priorytet 2: Obrazek wybrany z Pexels
            elif st.session_state.selected_pexels_url:
                source_info += "z obrazkiem z Pexels..."
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(st.session_state.selected_pexels_url, headers=headers, timeout=15)
                    image_to_publish = response.content
                except Exception as e:
                    st.error(f"Nie udało się pobrać obrazka z Pexels: {e}")
            # Priorytet 3: Obrazek z artykułu
            elif st.session_state.featured_image_bytes:
                source_info += "z obrazkiem z artykułu..."
                image_to_publish = st.session_state.featured_image_bytes
            else:
                source_info += "bez obrazka..."

            with st.spinner(source_info):
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



