# ETHIQUE.md

## TD 4.1 -- Empreinte d'un domaine

**1. Ai-je le droit ?**
Oui. Les trois sources utilisées sont des registres et données publiques :
- WHOIS est un registre public consultable par tous (obligation légale des registrars).
- crt.sh interroge les logs publics de Certificate Transparency (obligatoires depuis 2018 pour tout certificat TLS émis).
- Les headers HTTP et robots.txt sont renvoyés par le serveur à toute requête standard, sans authentification ni contournement.
Aucune de ces sources ne nécessite un accès non autorisé au sens de l'article 323-1 du Code pénal.

**2. Est-ce personnel ?**
Non. Les données collectées sont exclusivement techniques : nom de domaine, IP, serveurs DNS, headers HTTP, sous-domaines, contenu de robots.txt. Il n'y a aucune donnée nominative ou personnelle au sens du RGPD (pas de nom d'individu, email personnel, etc.). Le champ WHOIS "registrant" (souvent une personne physique pour les petits domaines) n'est d'ailleurs volontairement pas exploité dans le script.

**3. Suis-je discret ?**
Oui, par construction :
- User-Agent identifiable (`IPSSI-OSINT (+cours@ipssi.fr)`) sur toutes les requêtes, permettant à la cible de savoir qui l'analyse et pourquoi.
- Throttling de 1 seconde minimum entre chaque requête (`THROTTLE = 1.0`), pour ne jamais dégrader le service.
- Une seule requête HEAD (pas GET complet) pour les headers, minimisant la charge sur le serveur cible.

**Observation méthodologique** : lors du test, le service crt.sh a renvoyé une erreur 502 (Bad Gateway), confirmée comme un problème de surcharge récurrent côté crt.sh et non lié à mon script. Cela illustre une limite de l'OSINT basé sur des services tiers gratuits : la fiabilité des sources publiques n'est jamais garantie, ce qui doit être documenté dans tout rapport professionnel.

**Observation complémentaire (limite de crt.sh)** : sur les domaines à fort volume de certificats historiques (wikipedia.org, github.com), crt.sh timeout systématiquement même avec un délai étendu à 40s, tandis qu'il répond correctement en quelques secondes sur des domaines plus modestes (ipssi.fr). Cela illustre une limite structurelle des sources OSINT gratuites : leur capacité de traitement n'est pas dimensionnée pour l'historique complet des plus gros domaines mondiaux.

## TD 4.2 -- Cartographie d'une entité publique (BNP Paribas)

**1. Ai-je le droit ?**
Oui. Les trois sources sont publiques et non authentifiées :
- L'API Recherche d'Entreprises (recherche-entreprises.api.gouv.fr) est un service officiel de la DINUM, ouvert à tous sans clé API, qui synthétise les données publiques SIRENE/INSEE.
- Wikipedia est un contenu éditorial librement consultable, sous licence ouverte (CC BY-SA).
- Google News RSS est un flux public de syndication, conçu pour être consommé par des agrégateurs.
Aucun contournement d'authentification, aucun accès à une zone privée.

**2. Est-ce personnel ?**
Essentiellement non : les données collectées (SIREN, adresse du siège, code NAF, capitalisation, effectifs, filiales) sont des données d'entreprise, pas des données personnelles au sens RGPD. Seule nuance : l'infobox Wikipedia et les articles de presse mentionnent des noms de dirigeants (ex. Jean-Laurent Bonnafé, Jean Lemierre). Ce sont des données publiques concernant des personnes dans l'exercice de fonctions publiques/professionnelles (base légale RGPD : information légitime d'intérêt public), et non des données personnelles sensibles ou privées.

**3. Suis-je discret ?**
Oui :
- User-Agent identifiable sur toutes les requêtes SIRENE et Wikipedia.
- Throttling de 1 seconde entre chaque source (SIRENE → Wikipedia → RSS).
- Une seule requête GET par source, pas de crawl en profondeur.

**Observations méthodologiques** :
- L'URL de l'API SIRENE indiquée dans le sujet (`api.annuaire-entreprises.data.gouv.fr`) n'existait plus (erreur de résolution DNS) ; l'API a été migrée vers `recherche-entreprises.api.gouv.fr`. Cela illustre une limite récurrente de l'OSINT : les APIs publiques évoluent, et un script doit être revérifié régulièrement plutôt que considéré comme figé.
- Le scraping Wikipedia produisait initialement des caractères mal encodés (mojibake) car `requests` devinait mal l'encodage de la page ; forcer `r.encoding = "utf-8"` a résolu le problème. Point de vigilance technique pour tout scraping de contenu francophone.
- Recoupement des sources : le SIREN retourné par l'API (662042449) correspond exactement à celui affiché dans l'infobox Wikipedia, ce qui valide la fiabilité croisée des deux sources.
- La veille presse a remonté un article sensible (mise en cause judiciaire liée à des biens mal acquis), rappelant qu'une cartographie d'entité peut faire remonter des informations à fort enjeu réputationnel -- à traiter avec la même rigueur factuelle que le reste.
## TD 4.3 -- Veille automatisée avec Scrapy (cible : BNP Paribas)

**1. Ai-je le droit ?**
Oui. Les flux RSS de presse (Le Monde, Les Échos, Le Figaro, BFMTV, 01net) sont des flux publics de syndication, conçus par les médias eux-mêmes pour être consommés par des agrégateurs/robots. Le spider respecte `ROBOTSTXT_OBEY = True`, qui bloque automatiquement toute page interdite par le site.

**2. Est-ce personnel ?**
Non. Seuls des titres, résumés et métadonnées d'articles de presse publiés sont collectés -- aucune donnée nominative extraite en dehors de ce que les journalistes ont eux-mêmes publié publiquement.

**3. Suis-je discret ?**
Oui : User-Agent identifiable (`IPSSI-OSINT-veille`), `DOWNLOAD_DELAY = 1.0` avec `RANDOMIZE_DOWNLOAD_DELAY`, une seule requête par flux RSS (pas de crawl en profondeur des articles eux-mêmes).

**Observations méthodologiques** :
- Le flux `lesechos.fr/rss/rss_une.xml` a renvoyé une erreur 403 (accès refusé), malgré une requête conforme et un `robots.txt` autorisant a priori le crawl. Cela illustre que certains sites bloquent les robots identifiés comme tels indépendamment de robots.txt -- un rappel qu'aucune source publique n'est garantie disponible en continu.
- Premier lancement avec `CIBLE = "BNP Paribas"` : **0 mention trouvée**. Ce n'était pas un bug : les flux surveillés sont des flux généralistes "à la une", qui ne mentionnent une entreprise précise que de façon ponctuelle.
- Pour valider que le pipeline complet (filtrage → scoring → SQLite → CSV) fonctionnait bien indépendamment de la disponibilité d'une mention BNP Paribas à l'instant du test, un test de contrôle a été effectué avec `CIBLE = "France"` (mot nécessairement fréquent dans l'actualité française) : **11 mentions** ont été correctement filtrées, scorées et enregistrées (`mentions.csv` + `veille.db`), confirmant que le code est fonctionnel.
- Conclusion méthodologique : une veille RSS ponctuelle (un seul lancement) donne une photo instantanée, pas une vue représentative. Une vraie veille professionnelle nécessiterait un lancement récurrent (ex. cron toutes les heures) pour capter les mentions au fil du temps -- ce que confirme le nombre nul obtenu au premier essai sur la cible réelle.