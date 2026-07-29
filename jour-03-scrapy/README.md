\# Jour 3 — Scrapy



\## Résumé



| Projet | Cible | Statut | Résultat |

|---|---|---|---|

| allocine | allocine.fr/film/meilleurs | ❌ Bloqué (Cloudflare Turnstile) | Voir section "AlloCine" ci-dessous |

| boursorama | boursorama.com palmarès CAC 40 | ✅ Réussi | bourse.db, 30 actions, UNIQUE(isin) validé |

| niceagenda | jds.fr/nice/agenda (Défi 1) | ✅ Réussi | events.csv, 25 événements |



\## AlloCine — Blocage Cloudflare



Le site allocine.fr est protégé par Cloudflare Turnstile (challenge "Vérifiez que vous êtes humain"), qui bloque Scrapy même avec scrapy-playwright et un navigateur Chromium visible (headless=False), avec 8s d'attente pour laisser le JS s'exécuter. Résultat : 403 systématique, y compris sur robots.txt.



Le projet `allocine/` contient le code conforme au sujet (items, pipeline, spider, settings), mais n'a pas pu être exécuté avec succès pour cette raison. Remplacé par le Défi 1 (voir `niceagenda/`).



\## Boursorama



Sélecteurs validés dans scrapy shell — corrections apportées par rapport au sujet original : les valeurs (cours, variation, volume) sont dans des `<span class="c-instrument--...">` et non du texte brut de `<td>` positionnel. Contrainte UNIQUE(isin) vérifiée par double crawl (30 → 32 lignes, pas 60).



\## Défi 1 — niceagenda (remplace AlloCine)



Voir `niceagenda/README.md` pour le détail et la comparaison avec AlloCine.

