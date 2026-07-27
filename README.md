# Web Scraping — IPSSI Mastère Dev, Data & IA

Ce repo regroupe les TP réalisés pendant la semaine "Web Scraping" du Mastère.

## Sommaire

| Jour | Dossier | Sujet |
|---|---|---|
| Jour 1 | [`jour-01-requests-beautifulsoup/`](jour-01-requests-beautifulsoup/) | Veille technologique automatisée — scraper le Blog du Modérateur avec `requests` + `BeautifulSoup4`, export CSV + SQLite |

*(les dossiers des jours suivants seront ajoutés au fur et à mesure de la semaine)*

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
