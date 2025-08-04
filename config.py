# social_config.py
# Konfiguracja dla aplikacji do publikowania postów w social mediach.
# UWAGA: Ta wersja zawiera klucze API na stałe w kodzie i jest przeznaczona TYLKO DO TESTÓW.
# W wersji produkcyjnej, klucze powinny być wczytywane ze zmiennych środowiskowych (os.getenv).

import os

# Wspólne klucze API, które mogą być potrzebne
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
            "page_access_token": "EAASnnb5An6ABPHjDRtoJ9JcQew8Ir697wyPz2E3f7HIRO6bPGFvDYrBHbc6lztm5fM2hcH5iRsh7q118NZAsgst7FQvJf5YdHGLUzW6TkeKnauvf2c0Nk3pj10mGAUwFqaplDBY69ck2gKTyJP7owanR2ZClZA7WkRZAUuikm7NUJa8XqK7fiZBk8uBsCSM2U5MwftM6z4kW9Y77KHWKOzFyjHwJZAPUgybXftlRhDdgC4xZC72r2e4JycZD"
        }
    },
    "krakowskiryneknieruchomosci": {
        "friendly_name": "Krakowski Rynek Nieruchomości",
        "wp_api_url_base": "https://krakowskiryneknieruchomosci.pl/wp-json/wp/v2",
        "wp_username": os.getenv("KRN_USER"),
        "wp_password": os.getenv("KRN_PASS"),
        "auth_method": "basic",
        "facebook_page": None # Brak dopasowania na liście, do uzupełnienia
    },
    "radiopin": {
        "friendly_name": "RadioPIN.pl",
        "wp_api_url_base": "https://radiopin.pl/wp-json/wp/v2",
        "wp_bearer_token": os.getenv("RADIOPIN_BEARER_TOKEN"),
        "auth_method": "bearer",
        "facebook_page": {
            "page_id": "657887917402967",
            "page_access_token": "EAASnnb5An6ABPDDumvYHkmvwHuaisG7Vdi0ZCZBY5kcx4KD1DFi8DW8jasZAnC1aGcQTvhazYC8uTOd7tQuLZADScfQPJfYY8AFPUTByprEcz7BSbCp2EHyO1qvWEaJ8z8iHjcdIwFw3TZA9Q6LiwZA745qhkftpJbHKDZAo0CGFjyFdchTZBO1wa1G3ZCiLHPJgtXYZC7eXIaj9FjAr7J5KQsoZAEDhDF0OK5ZBIJFb6ZC8EAkqtpZBQNd0escNUZD"
        }
    },
    "echopolski": {
        "friendly_name": "EchoPolski.pl",
        "wp_api_url_base": "https://echopolski.pl/wp-json/wp/v2",
        "wp_username": os.getenv("ECHOPOLSKI_USER"),
        "wp_password": os.getenv("ECHOPOLSKI_PASS"),
        "auth_method": "basic",
        "facebook_page": None # Brak dopasowania na liście, do uzupełnienia
    },
    "infodlapolaka": {
        "friendly_name": "InfoDlaPolaka.pl",
        "wp_api_url_base": "https://infodlapolaka.pl/wp-json/wp/v2",
        "wp_username": os.getenv("INFODLAPOLAKA_USER"),
        "wp_password": os.getenv("INFODLAPOLAKA_PASS"),
        "auth_method": "basic",
        "facebook_page": {
            "page_id": "113621453424309",
            "page_access_token": "EAASnnb5An6ABPHfAr0oZCHNRdsBzayZC7r6vbFqIeFeB1cQOsxqFTebfYjh9TpkT8jZAkUIudRfWdEYBWwJx3uzJGNovERQLxaZBw2alwfZBFNr6ZCLmLwJ91UiiW2loZAKDt36Xxpb6I0bHQA0AgMhi5qoicQLiz2ZBBgEZCFw7VqwpKz1ses5hZAHF6nucg0yU1BLaxcBB5xzhsIBemoeCe0Lhmp99RIxXIBBpxaNw9bygeQewE0mjQxrwZDZD"
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
            "page_access_token": "EAASnnb5An6ABPG1pXZAFVDzJS4hpLbQZCRhsiZAPRHJZAwAvttrHkAUZCcZA24QzO49WCoI9nydSMx3iDXanxdcFvRRxnnQiBlbYUSbWEx5TtoIkuZA8gj3PCgd7kSa8wEkN3qObXZAJBfyXigu8Gxn5dslVTDhMZCidgOZBH1ZB3QUUZB5Eut64usnaXfov4MUx2BPhcYUZA5HeNGcm7gbvQgdvdZC1bcJcRVdlzfF3djRiSbiwzQBhHHKBUqQQZDZD"
        }
    },
    "superkredyty": {
        "friendly_name": "SuperKredyty.com",
        "wp_api_url_base": "https://superkredyty.com/wp-json/wp/v2",
        "wp_username": os.getenv("KREDYTY_USER"),
        "wp_password": os.getenv("KREDYTY_PASS"),
        "auth_method": "basic",
        # Nazwa 'SuperKredyty.com' nie pasuje idealnie do 'Konta bankowe od zaraz',
        # ale zakładam, że to o tę stronę chodziło. Możesz to zweryfikować.
        "facebook_page": {
            "page_id": "343411575533119",
            "page_access_token": "EAASnnb5An6ABPHE3E8UOxr3wUqecsB2AblhOoWwtjUy7XfONKdTiiN28uY0i7Tlk03MMOeed2hnYOJFdALZCvig2nVM58TxaefcZAKonX9ZCspYZBKNM37iB8Weg6Q22N5akeXZBWhihXr8ul5MK2WypR685wl3Jl4AFIQarKksZB7JwnWOa4vxdtSmGFMmjghR64e9de7xZAfoHA5ngWm4hLwRoMHevDcmgSZCcbDyWTjnC9nSGfM71Fg8ZD"
        }
    }
    # Możesz dodać tutaj resztę portali w ten sam sposób
}
