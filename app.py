import streamlit as st
import pandas as pd
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# Configuration de Selenium
def setup_selenium():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service('./chromedriver-win64/chromedriver.exe')  # Remplacez par le chemin vers votre chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def fetch_html_selenium(url):
    driver = setup_selenium()
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def process_data(url):
    html = fetch_html_selenium(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Extraire le texte
    texts = [p.get_text() for p in soup.find_all('p')]  # Exemple pour extraire le texte des balises <p>

    # Extraire les liens
    links = [a['href'] for a in soup.find_all('a', href=True)]

    # Extraire les images
    images = [img['src'] for img in soup.find_all('img', src=True)]

    # Aligner les données dans un format compatible pour DataFrame
    max_length = max(len(texts), len(links), len(images))

    # Compléter les listes avec None pour égaliser la longueur
    texts += [None] * (max_length - len(texts))
    links += [None] * (max_length - len(links))
    images += [None] * (max_length - len(images))

    data = [{'text': texts[i], 'link': links[i], 'image': images[i]} for i in range(max_length)]

    return data


# Titre de l'application
st.title("Web Scraper avec Téléchargement")

# Champ pour l'URL
url = st.text_input("Entrez l'URL à scraper")

if st.button("Scraper"):
    if url:
        data = process_data(url)

        # Convertir les données en DataFrame
        df = pd.DataFrame(data)

        # Afficher les données
        st.subheader("Données Scrappées")
        st.write(df)

        # Options pour le téléchargement
        st.subheader("Télécharger les Données")
        file_format = st.selectbox("Choisissez le format de fichier", ["JSON", "CSV", "TXT"])

        if file_format == "JSON":
            json_data = df.to_json(orient='records', lines=True)
            st.download_button(
                label="Télécharger JSON",
                data=json_data,
                file_name='data.json',
                mime='application/json'
            )

        elif file_format == "CSV":
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv_data,
                file_name='data.csv',
                mime='text/csv'
            )

        elif file_format == "TXT":
            txt_data = '\n'.join(
                df.apply(lambda x: f"Text: {x['text']}, Link: {x['link']}, Image: {x['image']}", axis=1))
            st.download_button(
                label="Télécharger TXT",
                data=txt_data,
                file_name='data.txt',
                mime='text/plain'
            )
    else:
        st.warning("Veuillez entrer une URL valide.")
