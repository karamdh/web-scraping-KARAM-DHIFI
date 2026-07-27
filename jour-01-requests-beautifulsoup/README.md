# TP - Veille technologique automatisée — Blog du Moderateur

## 1. robots.txt — le scraping de `/feed/` est-il autorisé ?

Non. Le fichier `https://www.blogdumoderateur.com/robots.txt` contient explicitement,
pour `User-agent: *` :

```
Disallow: /feed/
Disallow: /*/feed/
```

Le flux RSS/`/feed/` est donc interdit au scraping pour tout robot générique.
En revanche, les pages d'archives que nous ciblons (`/` et `/page/N/`) ne figurent
dans aucune règle `Disallow` pour `User-agent: *` : leur exploration est donc
autorisée pour ce user-agent générique. Le script `scraper_bdm.py` ne scrape
jamais `/feed/` — il utilise uniquement `/` et `/page/N/`.

## 2. Est-ce personnel ?

Non. Les données extraites (titre, URL, date, catégorie, chapeau) sont des
métadonnées éditoriales publiques, publiées par le média dans un but de
diffusion. Aucune donnée personnelle (identité, contact, comportement d'un
individu) n'est collectée.

## 3. Suis-je discret ?

Oui :
- **User-Agent identifiable** : `IPSSI-scraper (+contact@ipssi.fr)`, qui permet
  à l'éditeur de nous contacter en cas de problème, contrairement à un
  User-Agent usurpé.
- **Throttling** : `time.sleep(1.5)` entre chaque page (configurable via
  `--delay`), soit un débit largement inférieur à 1 requête/seconde.
- **Retry raisonné** : backoff exponentiel sur erreurs 5xx/429, avec respect
  du header `Retry-After` s'il est présent, pour ne pas insister en cas de
  surcharge du serveur.

## Cadre légal

Conformément à la jurisprudence de la CJUE (arrêt *Ryanair* de 2015 et
décisions ultérieures), le scraping de données publiques à des fins non
commerciales/éducatives est licite dès lors que le site n'impose pas de
restriction technique ou contractuelle contraire et que l'accès reste
respectueux (débit, identification). Ce TP respecte ces trois conditions.

## Livrables

| Fichier | Description |
|---|---|
| `scraper_bdm.py` | Script exécutable : `python scraper_bdm.py --max 200` |
| `articles.csv` | Export CSV UTF-8 (colonnes : titre, url, date, categorie, chapeau) |
| `articles.db` | Base SQLite, table `articles`, contrainte `UNIQUE(url)` |
| `README.md` | Ce fichier |

## Utilisation

```bash
python -m venv .venv && source .venv/bin/activate
pip install requests beautifulsoup4 lxml
python scraper_bdm.py --max 200 --csv articles.csv --db articles.db
```

Options :
- `--max` : nombre d'articles cible (défaut 200)
- `--delay` : délai entre requêtes en secondes (défaut 1.5)
- `--csv` / `--db` : chemins de sortie

## Remarque d'exécution

⚠️ Ce script n'a pas pu être testé en conditions réelles dans l'environnement de
génération : le bac à sable réseau de cette session Claude n'autorise que
quelques domaines techniques (pypi, github, npm...) et bloque
`blogdumoderateur.com` (réponse HTTP 403 côté proxy). Le code a d'abord été
écrit selon les sélecteurs et l'URL de pagination indiqués dans le sujet du
TP, puis **corrigé et validé en conditions réelles avec l'aide de l'étudiant**
qui a exécuté le script sur sa machine — le site a changé de thème depuis la
rédaction du sujet, d'où plusieurs écarts :

| Élément | Sujet du TP (obsolète) | Réel (vérifié le 27/07/2026) |
|---|---|---|
| Pagination | `/page/N/` | `/articles/page/N/` (`/page/N/` renvoie la page d'accueil, pas une archive) |
| Carte article | `article.post` | `article.post` — inchangé |
| Titre | `h2.post-title a` | `h3.entry-title` |
| URL | `h2.post-title a['href']` | lien absent du titre : recherche du `<a>` parent, puis repli sur d'autres liens de la carte (`_extraire_url`) |
| Date | `time[datetime]` | `time.entry-date[datetime]` |
| Catégorie | `.cat-links a` | `span.favtag` |
| Chapeau | `.entry-summary` | `div.entry-excerpt` (repli sur `.entry-summary` puis `<p>`) |

Ce travail de correction correspond exactement à l'exercice demandé en partie
1.2 du sujet (identifier les sélecteurs avec DevTools) : le HTML change, la
méthode pour le vérifier reste la même.
