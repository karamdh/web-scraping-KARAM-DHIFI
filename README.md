# Web Scraping — IPSSI Mastère Dev, Data & IA

Ce repo regroupe les TP réalisés pendant la semaine "Web Scraping" du Mastère.

## Sommaire

| Jour | Dossier | Sujet |
|---|---|---|
| Jour 1 | `jour-01-requests-beautifulsoup/` | Veille technologique automatisée — scraper le Blog du Modérateur avec `requests` + `BeautifulSoup4`, export CSV + SQLite |
| Jour 2 | `jour-02-selenium/` | Scraping dynamique avec Selenium — Doctolib et Les Echos |
| Jour 3 | `jour-03-scrapy/` | Framework Scrapy — Boursorama (CAC 40, SQLite), Défi 1 : agenda culturel de Nice (jds.fr). AlloCine bloqué par Cloudflare Turnstile, documenté en remplacement |

## Organisation

Chaque dossier `jour-0X-<sujet>/` contient :
- le(s) script(s) Python du TP
- un `README.md` propre à ce TP (contexte, choix techniques, justification éthique si scraping)
- les livrables attendus (CSV, DB, etc. — sauf s'ils sont exclus par `.gitignore`)

## Environnement

```bash
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate.bat
pip install -r requirements.txt
```
