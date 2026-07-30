import json
import sys
import time
 
import requests
import feedparser  # pip install feedparser
from bs4 import BeautifulSoup  # pip install beautifulsoup4 lxml
 
HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}
TIMEOUT = 10
THROTTLE = 1.0  # secondes entre requetes -- ne jamais degrader le service cible
 
 
def chercher_sirene(nom: str) -> dict:
    """API Recherche d'Entreprises (data.gouv.fr / DINUM) -- pas besoin de cle API.
 
    Note : l'ancienne adresse api.annuaire-entreprises.data.gouv.fr n'existe plus ;
    l'API a ete migree vers recherche-entreprises.api.gouv.fr.
    """
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={nom}&limit=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            ent = data["results"][0]
            return {
                "siren": ent.get("siren"),
                "denomination": ent.get("nom_complet"),
                "adresse_siege": ent.get("siege", {}).get("adresse"),
                "code_naf": ent.get("activite_principale"),
                "date_creation": ent.get("date_creation"),
                "tranche_effectif": ent.get("tranche_effectif_salarie"),
            }
        return {"resultat": "Non trouve dans SIRENE"}
    except Exception as e:
        return {"erreur": str(e)}
 
 
def scraper_wikipedia(nom: str) -> dict:
    """Scraper l'infobox et l'intro de la page Wikipedia."""
    slug = nom.replace(" ", "_")
    url = f"https://fr.wikipedia.org/wiki/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.encoding = "utf-8"  # Wikipedia sert du contenu en UTF-8 ; requests le devine parfois mal
        soup = BeautifulSoup(r.text, "lxml")
 
        # Infobox : tableau d'informations sur la droite
        infobox = {}
        table = soup.select_one("table.infobox, table.wikitable")
        if table:
            for tr in table.select("tr"):
                th = tr.select_one("th")
                td = tr.select_one("td")
                if th and td:
                    cle = th.get_text(strip=True)
                    val = td.get_text(" ", strip=True)[:200]
                    infobox[cle] = val
 
        # Premier paragraphe = introduction
        intro = ""
        for p in soup.select("#mw-content-text p"):
            txt = p.get_text(strip=True)
            if len(txt) > 80:
                intro = txt[:500]
                break
 
        return {"infobox": infobox, "intro": intro, "url": url}
    except Exception as e:
        return {"erreur": str(e)}
 
 
def veille_presse(nom: str, nb_max: int = 10) -> list[dict]:
    """Google News RSS : articles recents mentionnant l'entite."""
    query = nom.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"
    try:
        feed = feedparser.parse(url)
        return [
            {
                "titre": e.get("title", ""),
                "source": e.get("source", {}).get("title", ""),
                "date": e.get("published", ""),
                "lien": e.get("link", ""),
            }
            for e in feed.entries[:nb_max]
        ]
    except Exception as e:
        return [{"erreur": str(e)}]
 
 
def construire_fiche(nom: str) -> dict:
    print(f"[*] Construction de la fiche pour : {nom}")
 
    fiche = {"entite": nom}
 
    print("[*] API SIRENE...")
    fiche["sirene"] = chercher_sirene(nom)
    time.sleep(THROTTLE)
 
    print("[*] Wikipedia...")
    fiche["wikipedia"] = scraper_wikipedia(nom)
    time.sleep(THROTTLE)
 
    print("[*] Veille presse (Google News RSS)...")
    fiche["presse"] = veille_presse(nom)
 
    fiche["nb_articles"] = len(fiche["presse"])
    return fiche
 
 
def main() -> None:
    nom = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "BNP Paribas"
    fiche = construire_fiche(nom)
 
    sortie = "fiche_entite.json"
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(fiche, f, indent=2, ensure_ascii=False)
 
    print(f"[+] Fiche sauvegardee : {sortie}")
    print(f"    SIREN : {fiche['sirene'].get('siren', 'n/a')}")
    print(f"    Articles: {fiche['nb_articles']}")
 
 
if __name__ == "__main__":
    main()