import time
import streamlit as st
import requests
from urllib.parse import urlparse
import streamlit as st
import requests


def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)


def validate_url(url):
    if not url:
        return False, "Please enter a URL."

    # Parse the URL
    try:
        result = urlparse(url)

        # Check if URL has a scheme and netloc
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format. Please include http:// or https://"

        # Check if it's http or https
        if result.scheme not in ["http", "https"]:
            return False, "URL must start with http:// or https://"

        # Try to fetch the URL to verify it's accessible
        try:
            response = requests.head(url, timeout=5)
            if response.status_code >= 400:
                return (
                    False,
                    f"Unable to access the website. Status code: {response.status_code}",
                )
        except requests.RequestException as e:
            return False, f"Error accessing the website: {str(e)}"

        return True, ""

    except Exception as e:
        return False, f"URL validation error: {str(e)}"
