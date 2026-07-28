"""
TP2 - IPSSI - Selenium
Scraper Les Echos : titres a la une + comparaison headless vs normal.

Usage:
    python lesechos_scraper.py
    python lesechos_scraper.py --skip-check   # sauter le test requests prealable
"""
import argparse
import json
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOTS_DIR = "screenshots"


def screenshot_echec(driver, nom: str) -> None:
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    chemin = os.path.join(SCREENSHOTS_DIR, nom)
    try:
        driver.save_screenshot(chemin)
        print(f"Screenshot d'echec sauvegarde : {chemin}")
    except Exception as e:
        print(f"Impossible de sauvegarder le screenshot : {e}")


def tester_avec_requests() -> bool:
    """Etape 1 : verifie si requests+BS4 suffiraient (contenu deja dans le HTML brut).
    Renvoie True si le contenu semble accessible sans JS (Selenium inutile)."""
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(
        "https://www.lesechos.fr",
        headers={"User-Agent": "IPSSI-scraper (+contact@ipssi.fr)"},
        timeout=10,
    )
    soup = BeautifulSoup(r.text, "lxml")
    titres = soup.select("h2, h3")
    print(f"[requests] {len(titres)} balises de titre trouvees dans le HTML brut")
    if len(titres) == 0:
        print("[requests] => Page chargee en JS, Selenium est necessaire")
        return False
    print("[requests] => Du contenu est present, mais on verifie quand meme avec Selenium")
    return True


def make_driver(headless: bool = False) -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        # Sans taille explicite, le viewport headless peut etre minuscule
        # et empecher le rendu normal (responsive) du site.
        opts.add_argument("--window-size=1920,1080")
    else:
        opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)


def _premier_texte(art, selecteurs: list[str], defaut: str = "") -> str:
    for sel in selecteurs:
        els = art.find_elements(By.CSS_SELECTOR, sel)
        if els and els[0].text.strip():
            return re.sub(r"\s+", " ", els[0].text).strip()
    return defaut


def extraire_articles(driver, limite: int = 20) -> list[dict]:
    articles = driver.find_elements(
        By.CSS_SELECTOR, "article, [class*='article-item'], [class*='card-article']"
    )
    resultats = []
    for art in articles[:limite]:
        titre = _premier_texte(art, ["h2", "h3", "[class*='title']"])
        if not titre:
            continue
        rubrique = _premier_texte(art, ["[class*='rubrique']", "[class*='section']", "[class*='category']", "[class*='tag']"])
        chapeau = _premier_texte(art, ["p", "[class*='chapo']", "[class*='intro']", "[class*='description']"])[:300]
        heure = _premier_texte(art, ["time", "[class*='date']", "[class*='time']"])
        premium = bool(art.find_elements(
            By.CSS_SELECTOR, "[class*='premium'], [class*='abonne'], svg[class*='lock'], [class*='paywall']"
        ))
        resultats.append({
            "titre": titre,
            "rubrique": rubrique,
            "chapeau": chapeau,
            "heure_publi": heure,
            "premium": premium,
        })
    return resultats


def scraper_une_fois(headless: bool) -> tuple[list[dict], float]:
    t0 = time.time()
    driver = make_driver(headless=headless)
    articles = []
    try:
        driver.get("https://www.lesechos.fr")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article, [class*='article']"))
        )
        articles = extraire_articles(driver)
    except TimeoutException as e:
        mode = "headless" if headless else "normal"
        screenshot_echec(driver, f"lesechos_erreur_{mode}.png")
        print(f"Timeout en mode {mode} : {e}")
    finally:
        driver.quit()
    duree = time.time() - t0
    return articles, duree


def main():
    p = argparse.ArgumentParser(description="Scraper Les Echos")
    p.add_argument("--skip-check", action="store_true", help="Sauter le test requests prealable")
    p.add_argument("--out", default="lesechos.json")
    p.add_argument("--compare-headless", action="store_true",
                    help="Lance aussi une passe headless pour comparer les temps")
    args = p.parse_args()

    if not args.skip_check:
        tester_avec_requests()

    print("\n--- Passe normale (navigateur visible) ---")
    articles, t_normal = scraper_une_fois(headless=False)
    print(f"Mode normal : {t_normal:.1f}s, {len(articles)} articles")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"{len(articles)} articles exportes dans {args.out}")

    if args.compare_headless:
        print("\n--- Passe headless (comparaison) ---")
        _, t_headless = scraper_une_fois(headless=True)
        print(f"Normal   : {t_normal:.1f}s")
        print(f"Headless : {t_headless:.1f}s")
        if t_headless > 0:
            print(f"Gain     : {t_normal / t_headless:.1f}x plus rapide en headless")


if __name__ == "__main__":
    main()
