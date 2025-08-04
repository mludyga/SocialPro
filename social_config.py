# social_config.py
# OSTATECZNA WERSJA - W PEŁNI BEZPIECZNA
# Ten plik wczytuje WSZYSTKIE wrażliwe dane z sekretów Streamlit / zmiennych środowiskowych.

import os

# Wspólne klucze API wczytywane z sekretów
COMMON_KEYS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
}

# Konfiguracja poszczególnych portali i powiązanych z nimi stron na Facebooku
SITES = {
    "autozakup": {
        "friendly_name": "Autozakup.com.pl",
        "wp_api_url_base": "https://autozakup.com.pl/wp-json/wp/v2",
        "wp_username": os.getenv("AUTOZAKUP_USER"),
        "wp_password": os.getenv("AUTOZAKUP_PASS"),
        "auth_method": "basic",
        "facebook_page": {
            "page_id": "652774754577577",
            "page_access_token": os.getenv("FB_AUTOZAKUP_TOKEN")
        }
    },
    "krakowskiryneknieruchomosci": {
        "friendly_name": "Krakowski Rynek Nieruchomości",
        "wp_api_url_base": "https://krakowskiryneknieruchomosci.pl/wp-json/wp/v2",
        "wp_username": os.getenv("KRN_USER"),
        "wp_password": os.getenv("KRN_PASS"),
        "auth_method": "basic",
        "facebook_page": None
    },
    "radiopin": {
        "friendly_name": "RadioPIN.pl",
        "wp_api_url_base": "https://radiopin.pl/wp-json/wp/v2",
        "wp_bearer_token": os.getenv("RADIOPIN_BEARER_TOKEN"),
        "auth_method": "bearer",
        "facebook_page": {
            "page_id": "657887917402967",
            "page_access_token": os.getenv("FB_RADIOPIN_TOKEN")
        }
    },
    "echopolski": {
        "friendly_name": "EchoPolski.pl",
        "wp_api_url_base": "https://echopolski.pl/wp-json/wp/v2",
        "wp_username": os.getenv("ECHOPOLSKI_USER"),
        "wp_password": os.getenv("ECHOPOLSKI_PASS"),
        "auth_method": "basic",
        "facebook_page": None
    },
    "infodlapolaka": {
        "friendly_name": "InfoDlaPolaka.pl",
        "wp_api_url_base": "https://infodlapolaka.pl/wp-json/wp/v2",
        "wp_username": os.getenv("INFODLAPOLAKA_USER"),
        "wp_password": os.getenv("INFODLAPOLAKA_PASS"),
        "auth_method": "basic",
        "facebook_page": {
            "page_id": "113621453424309",
            "page_access_token": os.getenv("FB_INFODLAPOLAKA_TOKEN")
        }
    },
    "tylkoslask": {
        "friendly_name": "TylkoSlask.pl",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "facebook_page": {
            "page_id": "105250655039704",
            "page_access_token": os.getenv("FB_TYLKOSLASK_TOKEN")
        }
    },
    "superkredyty": {
        "friendly_name": "SuperKredyty.com",
        "wp_api_url_base": "https://superkredyty.com/wp-json/wp/v2",
        "wp_username": os.getenv("KREDYTY_USER"),
        "wp_password": os.getenv("KREDYTY_PASS"),
        "auth_method": "basic",
        "facebook_page": {
            "page_id": "343411575533119",
            "page_access_token": os.getenv("FB_SUPERKREDYTY_TOKEN")
        }
    }
}
