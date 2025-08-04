# social_config.py
# Konfiguracja dla aplikacji do publikowania postów w social mediach.
# UWAGA: Ta wersja zawiera klucze API na stałe w kodzie i jest przeznaczona TYLKO DO TESTÓW.
# W wersji produkcyjnej, klucze powinny być wczytywane ze zmiennych środowiskowych (os.getenv).

import os

# Wspólne klucze API, które mogą być potrzebne
COMMON_KEYS = {
    "OPENAI_API_KEY": "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",
    "PERPLEXITY_API_KEY": "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"
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
            # ZAKTUALIZOWANY TOKEN
            "page_access_token": "EAASnnb5An6ABPAtwLEPqmHsxZA2ggvR7u9W752oKsUnvNtkKOqbirRbToH1KGus8s0a1yBnuHCtvWBQsX8UJy6WqYm71MTmDqUkEfT9qtPSeNzyT04ve9NyAqRuwlCszqq5aVZA77wS9uq2idKwVZB1VhkpdYwUVqk3cFwFzs9QzE4nuKxYnaVMEKs5i7WFJJlMZAQ4j5CZA0tK0NXn6gbVlp6s3ZAs5SBTSJWQhktMydi2IWwkr78o6ZArRUYZD"
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
            # ZAKTUALIZOWANY TOKEN
            "page_access_token": "EAASnnb5An6ABPLXwAVE36Du1726vwpPjoDRSjATWjsaRhZBHshTlOXtDShGSAdxJLvpqeFh2w2ktXLZC4GQddbNYjhf7rQhnPCqEkg8aI4mwvYamFCsQZCagY6cHScvmw1nzQa8VcZAZCELCVxxf3Y62tlLAlWhadjc27hSzdLxQKgqYiqxuZCsWe1hZAEnD75NzgxdNRA4Q2xXfkWGOZAevcZBSKpKMKZCve1yLUPSwythxtrhhw9v5ZCZALTgXZAjoZD"
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
            # ZAKTUALIZOWANY TOKEN
            "page_access_token": "EAASnnb5An6ABPLNJ0lVinqtoDXU0ZA907Kx9Vw2FdcBABaaiIBXo0EL6DWQv6dUOhbC9YBbb6LcZCACtjURcH0PE0oq8ZALTpr9hbm3b5hW4xgQB3r4uEZCLDld4JHTZBsMr9pPKgUba3OWyLxVzRZAHFVHPAZB4MEkj8b61DlDuDCEwEZCzbFZAZCNX61DCs9ZBkuIMFefY4MHzq7gUFZC8TwncxZAzvXtAfziJGcimIOlPFA68iLrfa5ltS3sfsIQZDZD"
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
            # ZAKTUALIZOWANY TOKEN
            "page_access_token": "EAASnnb5An6ABPJd0pHvHmJj51jDU28koz2x5k3ZBZApcqLNQhE7yUB5jX8VZA6QdhwMVJN9IcyfSC8srAx0Tt8fqnP2xBq8vX2NVClZBu2630sd607trZAIxIshEGqRbaBoyurIZCEXzbmwfMZCq12KZB4RaZBHLZB9OwFOgORfZCmQVaC92b67bDcEhxXejL5ZBKrqZCJ1k3NPIgdhmMVW3Om4G02XqlP8MJXIi4yymWN7VvyATyKXpGYnZC8D2jPaAZDZD"
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
            # ZAKTUALIZOWANY TOKEN
            "page_access_token": "EAASnnb5An6ABPBOn8rjB7lzUPDHaFYtgZAcPzApvIsk2cSwDkz5jAnjvwZCd0kMJnnUcNJ63dLibbHuWJtWAOs1hmBpjWHTiA636kpy55L5lVcCyMbJeQ3UZAMZCHjQHUxNOJNFxG74WPDum6Mgd7WXi9jHZCQoBkgkvf4LmPN0eZCWh0IQ31yaKxiZCWlmBPtIKAF0DFJ8SJgQIv7Pi6nPFglzZBZBd4RbfYp8HblcLYCvYJTxZAT3TNEjJKOLqIZD"
        }
    }
}