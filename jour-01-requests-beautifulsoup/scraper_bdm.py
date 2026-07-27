#!/usr/bin/env python3


import argparse
import csv
import sqlite3
import time

import requests
from bs4 import BeautifulSoup

BASE_HOME = "https://www.blogdumoderateur.com/articles/"
BASE_URL = "https://www.blogdumoderateur.com/articles/page/{n}/"

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

CHAMPS = ["titre", "url", "date", "categorie", "chapeau"]

DDL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    categorie TEXT,
    chapeau TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""



# Partie 2/3 — Récupération et parsing d'une page

def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    """GET une page avec retry exponentiel sur erreurs temporaires (5xx, 429, timeout)."""
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"429 Too Many Requests - attente {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")
        except requests.Timeout:
            print(f"Timeout tentative {attempt + 1}/{tries} sur {url}")
            time.sleep(2 ** attempt)
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status and status < 500:
                # 4xx : erreur définitive (ex: page inexistante), on ne retente pas
                raise
            print(f"Erreur {status} tentative {attempt + 1}/{tries} sur {url}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Echec apres {tries} tentatives : {url}")


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    """Extrait les 5 champs cibles pour chaque <article class="post"> de la page,
    via une list-comprehension (refactor demandé en 5.2).

    Sélecteurs vérifiés le 27/07/2026 sur blogdumoderateur.com (le thème du site
    a changé depuis la rédaction du sujet, d'où l'écart avec les sélecteurs
    d'origine h2.post-title / .cat-links / .entry-summary) :
      - carte    : article.post
      - titre    : h3.entry-title
      - url      : cf. _extraire_url (le lien est parfois sur un <a> parent,
                    parfois dans le titre selon la page)
      - date     : time.entry-date[datetime]
      - categorie: span.favtag
      - chapeau  : div.entry-excerpt (repli sur .entry-summary puis <p>)
    """
    return [
        {
            "titre": card.select_one("h3.entry-title").get_text(strip=True),
            "url": _extraire_url(card),
            "date": (card.select_one("time.entry-date") or {}).get("datetime", "")[:10],
            "categorie": (
                card.select_one("span.favtag").get_text(strip=True)
                if card.select_one("span.favtag")
                else ""
            ),
            "chapeau": _extraire_chapeau(card),
        }
        for card in soup.select("article.post")
        if card.select_one("h3.entry-title")
    ]


def _url_absolue(href: str) -> str:
    """Complète une URL relative en URL absolue."""
    if href.startswith("/"):
        return f"https://www.blogdumoderateur.com{href}"
    return href


def _extraire_url(card: BeautifulSoup) -> str:
    """Trouve l'URL de l'article : essaie le lien parent (design page d'accueil),
    puis un lien dans le titre, puis n'importe quel lien interne de la carte
    (designs différents selon page d'accueil / page d'archive)."""
    parent_a = card.find_parent("a", href=True)
    if parent_a:
        return _url_absolue(parent_a["href"])

    titre_a = card.select_one("h3.entry-title a[href]") or card.select_one("h2 a[href]")
    if titre_a:
        return _url_absolue(titre_a["href"])

    lien = card.select_one("a[href]")
    if lien:
        return _url_absolue(lien["href"])

    return ""


def _extraire_chapeau(card: BeautifulSoup) -> str:
    """Récupère le chapeau : .entry-excerpt (nom réel sur ce thème), puis
    .entry-summary (autre nom possible selon les pages), puis en dernier
    recours le premier <p> visible de la carte."""
    for sel in (".entry-excerpt", ".entry-summary"):
        el = card.select_one(sel)
        if el:
            return el.get_text(strip=True)[:300]
    p = card.find("p")
    if p:
        return p.get_text(strip=True)[:300]
    return ""


# Partie 3 — Pagination

def scrape_all(max_articles: int = 200, delay: float = 1.5) -> list[dict]:
    """Parcourt /page/N/ jusqu'à atteindre max_articles ou tomber sur une page vide.
    Déduplique par URL (au cas où deux pages renverraient un même article)."""
    tous: list[dict] = []
    urls_vues: set[str] = set()
    page = 1
    while len(tous) < max_articles:
        url = BASE_HOME if page == 1 else BASE_URL.format(n=page)
        try:
            soup = get_page(url)
        except requests.HTTPError as e:
            print(f"Page {page} indisponible ({e}), arrêt.")
            break

        nouveaux = parse_articles(soup)
        if not nouveaux:
            print(f"Plus d'articles a la page {page}, arret.")
            break

        inedits = [a for a in nouveaux if a["url"] not in urls_vues]
        if not inedits:
            print(f"Page {page} ne contient que des doublons deja vus, arret.")
            break

        for a in inedits:
            urls_vues.add(a["url"])
        tous.extend(inedits)
        print(f"Page {page} => {len(inedits)} articles inedits | total={len(tous)}")
        page += 1
        time.sleep(delay)  # throttling : au moins 1 s entre requêtes

    return tous[:max_articles]


# Partie 4 — Persistance CSV + SQLite

def sauver_csv(articles: list[dict], chemin: str = "articles.csv") -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, extrasaction="ignore")
        w.writeheader()
        w.writerows(articles)
    print(f"CSV : {len(articles)} lignes -> {chemin}")


def sauver_sqlite(articles: list[dict], chemin: str = "articles.db") -> None:
    with sqlite3.connect(chemin) as cx:
        cx.execute(DDL)
        inserted = 0
        for a in articles:
            try:
                cx.execute(
                    "INSERT OR IGNORE INTO articles (titre,url,date,categorie,chapeau) "
                    "VALUES (:titre,:url,:date,:categorie,:chapeau)",
                    a,
                )
                inserted += cx.execute("SELECT changes()").fetchone()[0]
            except sqlite3.Error as e:
                print(f"Erreur SQLite : {e}")
        cx.commit()
    print(f"SQLite : {inserted} nouvelles lignes inserees dans {chemin}")


# Partie 5 — Main / CLI

def main():
    p = argparse.ArgumentParser(description="Scraper Blog du Moderateur")
    p.add_argument("--max", type=int, default=200, help="Nb max d'articles")
    p.add_argument("--csv", default="articles.csv")
    p.add_argument("--db", default="articles.db")
    p.add_argument("--delay", type=float, default=1.5, help="Delai entre pages (s)")
    args = p.parse_args()

    print(f"Demarrage - cible : {args.max} articles")
    articles = scrape_all(args.max, delay=args.delay)
    sauver_csv(articles, args.csv)
    sauver_sqlite(articles, args.db)
    print(f"Termine : {len(articles)} articles")


if __name__ == "__main__":
    main()
