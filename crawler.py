import requests
from bs4 import BeautifulSoup
import telebot
from datetime import datetime
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
import nltk

# ID
TOKEN = "(tokenaqui)"
GRUPO_ID = "(idaqui)"

LANGUAGE = "portuguese"
SENTENCES_COUNT = 3
MAX_NOTICIAS = 10 

# NLKT 
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)


def resumir_noticia(url_noticia):
    try:
        parser = HtmlParser.from_url(url_noticia, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)

        sentences = [str(s) for s in summarizer(parser.document, SENTENCES_COUNT)]
        return " ".join(sentences)
    except Exception as e:
        print(f"Erro ao resumir a notícia {url_noticia}: {e}")
        return None


# g1
def extrair_e_resumir_noticias_g1():
    print("Extraindo notícias do G1...")
    url = "https://g1.globo.com/"
    noticias = []

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            noticias_raw = soup.find_all("div", class_="feed-post-body")
            for noticia in noticias_raw[:10]:
                link_tag = noticia.find("a")
                if link_tag:
                    url_noticia = link_tag.get("href")
                    titulo = link_tag.text.strip()

                    if url_noticia and url_noticia.startswith("http"):
                        resumo = resumir_noticia(url_noticia)
                        if resumo:
                            noticias.append({"titulo": titulo, "url": url_noticia, "resumo": resumo})
    except Exception as e:
        print(f"Erro ao acessar o G1: {e}")
    return noticias



def extrair_e_resumir_noticias_folha():
    print("Extraindo notícias da Folha de SP...")
    url = "https://www.folha.uol.com.br/"
    noticias = []

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            noticias_raw = soup.find_all("a", class_="c-main-headline__url")
            for noticia in noticias_raw[:10]:
                url_noticia = noticia.get("href")
                titulo = noticia.text.strip()
                if url_noticia and titulo:
                    resumo = resumir_noticia(url_noticia)
                    if resumo:
                        noticias.append({"titulo": titulo, "url": url_noticia, "resumo": resumo})
    except Exception as e:
        print(f"Erro ao acessar a Folha: {e}")
    return noticias


def extrair_e_resumir_noticias_uol():
    print("Extraindo notícias do UOL...")
    url = "https://www.uol.com.br/"
    noticias = []

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            noticias_raw = soup.find_all("a", class_="titulo")
            for noticia in noticias_raw[:10]:
                url_noticia = noticia.get("href")
                titulo = noticia.text.strip()
                if url_noticia and titulo:
                    resumo = resumir_noticia(url_noticia)
                    if resumo:
                        noticias.append({"titulo": titulo, "url": url_noticia, "resumo": resumo})
    except Exception as e:
        print(f"Erro ao acessar o UOL: {e}")
    return noticias


# Todos os sites
noticias_g1 = extrair_e_resumir_noticias_g1()
noticias_folha = extrair_e_resumir_noticias_folha()
noticias_uol = extrair_e_resumir_noticias_uol()

# Junta todas
todas_noticias = noticias_g1 + noticias_folha + noticias_uol

noticias_filtradas = []
vistos = set()
for n in todas_noticias:
    if n["titulo"] not in vistos:
        noticias_filtradas.append(n)
        vistos.add(n["titulo"])

# Limite
noticias_finais = noticias_filtradas[:MAX_NOTICIAS]

# Log
agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_entry = f"[{agora}] - Script executado. Encontradas {len(noticias_finais)} notícias.\n"
with open("crawler_log.txt", "a", encoding="utf-8") as f:
    f.write(log_entry)
print(f"\n{log_entry}")

# Quebrar em blocos, texto que aparece
if noticias_finais:
    data_atual = datetime.now().strftime("%d/%m/%Y")
    texto_telegram = f"<b>Resumo de Notícias do Dia ({data_atual}):</b>\n\n"
    print(texto_telegram)
    for i, noticia in enumerate(noticias_finais):
        texto_telegram += f"<b>{i+1}. {noticia['titulo']}</b>\n"
        if noticia.get("resumo"):
            texto_telegram += f"{noticia['resumo']}\n"
        texto_telegram += f"<a href='{noticia['url']}'>Leia mais</a>\n\n"


    bot = telebot.TeleBot(TOKEN)

    try:
        # dividir em blocos de até 4000 caracteres
        for i in range(0, len(texto_telegram), 4000):
            bot.send_message(GRUPO_ID, texto_telegram[i:i+4000], parse_mode="HTML")

        print("Resumo enviado para o Telegram com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")
else:
    print("Nenhuma notícia encontrada para enviar.")