"""
TP2 - Selenium
Scraper Doctolib : fiches médecins pour une spécialité + ville

Usage :
python doctolib_scraper.py --specialite cardiologue --ville lyon
"""

import argparse
import json
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


SCREENSHOTS_DIR = "screenshots"


# -------------------------
# Création navigateur
# -------------------------

def make_driver(headless=False):

    options = webdriver.ChromeOptions()

    # Profil Selenium conservé
    options.add_argument(
        r"--user-data-dir=C:\Users\HP\Desktop\selenium_profile"
    )

    options.add_argument(
        "--profile-directory=Default"
    )

    options.add_argument(
        "--window-size=1920,1080"
    )

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )


    if headless:
        options.add_argument("--headless=new")


    return webdriver.Chrome(options=options)



# -------------------------
# Screenshot erreur
# -------------------------

def screenshot_echec(driver, nom):

    os.makedirs(
        SCREENSHOTS_DIR,
        exist_ok=True
    )

    chemin = os.path.join(
        SCREENSHOTS_DIR,
        nom
    )

    driver.save_screenshot(
        chemin
    )

    print(
        "Screenshot sauvegarde :",
        chemin
    )



# -------------------------
# Cookies
# -------------------------

def accepter_cookies(driver, wait):

    try:

        bouton = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains("
                    "translate(.,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'accepter')]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            bouton
        )

        print(
            "Cookies acceptes"
        )

        time.sleep(3)


    except TimeoutException:

        print(
            "Pas de bannière cookies"
        )



# -------------------------
# Vérification Cloudflare
# -------------------------

def verifier_cloudflare(driver):

    html = driver.page_source.lower()

    mots = [
        "verify you are human",
        "vérifiez que vous êtes humain",
        "cloudflare"
    ]

    return any(
        mot in html
        for mot in mots
    )



# -------------------------
# Attente résultats
# -------------------------

def attendre_resultats(driver, wait):

    try:

        wait.until(

            lambda d:
            len(
                d.find_elements(
                    By.CSS_SELECTOR,
                    "a[href*='/medecin'],"
                    "a[href*='/cardiologue'],"
                    "a[href*='/cabinet-medical']"
                )
            ) >= 5

        )


        print(
            "Resultats charges"
        )


    except TimeoutException:


        if verifier_cloudflare(driver):

            print(
                "Blocage Cloudflare detecte"
            )


        screenshot_echec(
            driver,
            "doctolib_erreur_resultats.png"
        )


        raise Exception(
            "Resultats non charges"
        )



# -------------------------
# Nettoyage texte
# -------------------------

def nettoyer(text):

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()



# -------------------------
# Extraction médecins
# -------------------------

def extraire_medecins(driver, limite=10):


    liens = driver.find_elements(

        By.CSS_SELECTOR,

        "a[href*='/medecin'],"
        "a[href*='/cardiologue'],"
        "a[href*='/cabinet-medical']"

    )


    resultats = []


    vus = set()


    for lien in liens:


        if len(resultats) >= limite:
            break


        try:


            url = lien.get_attribute(
                "href"
            )


            if not url or url in vus:
                continue


            vus.add(url)



            texte = nettoyer(
                lien.text
            )



            lignes = [
                x.strip()
                for x in texte.split("\n")
                if x.strip()
            ]



            nom = (
                lignes[0]
                if lignes
                else "n/a"
            )


            adresse = "n/a"
            consultation = []
            creneaux = []



            texte_lower = texte.lower()



            # Adresse approximative

            for ligne in lignes:

                if (
                    "lyon" in ligne.lower()
                    or "rue" in ligne.lower()
                    or "avenue" in ligne.lower()
                ):

                    adresse = ligne
                    break



            # Type consultation

            if (
                "vidéo" in texte_lower
                or
                "video" in texte_lower
            ):

                consultation.append(
                    "Consultation vidéo"
                )


            if (
                "présentiel" in texte_lower
                or
                "présence" in texte_lower
            ):

                consultation.append(
                    "Présentiel"
                )


            if not consultation:

                consultation.append(
                    "n/a"
                )



            # Créneaux

            boutons = lien.find_elements(

                By.CSS_SELECTOR,

                "button"

            )


            for bouton in boutons[:3]:

                txt = nettoyer(
                    bouton.text
                )

                if txt:
                    creneaux.append(
                        txt
                    )



            if not creneaux:

                creneaux = [
                    "n/a"
                ]



            resultats.append(

                {

                    "nom": nom,

                    "adresse": adresse,

                    "type_consultation":
                        consultation,

                    "prochains_creneaux":
                        creneaux,

                    "url_fiche":
                        url

                }

            )


        except (
            StaleElementReferenceException,
            NoSuchElementException
        ):

            continue



    return resultats



# -------------------------
# Programme principal
# -------------------------

def main():


    parser = argparse.ArgumentParser()


    parser.add_argument(
        "--specialite",
        default="cardiologue"
    )


    parser.add_argument(
        "--ville",
        default="lyon"
    )


    parser.add_argument(
        "--headless",
        action="store_true"
    )


    parser.add_argument(
        "--out",
        default="doctolib.json"
    )


    args = parser.parse_args()



    url = (
        f"https://www.doctolib.fr/"
        f"{args.specialite}/"
        f"{args.ville}"
    )


    print(
        "Cible :",
        url
    )



    driver = make_driver(
        args.headless
    )


    wait = WebDriverWait(
        driver,
        120
    )


    medecins = []



    try:


        driver.get(
            url
        )


        time.sleep(5)


        accepter_cookies(
            driver,
            wait
        )


        attendre_resultats(
            driver,
            wait
        )


        medecins = extraire_medecins(
            driver,
            10
        )



    except Exception as e:


        print(
            "Erreur :",
            e
        )


        screenshot_echec(
            driver,
            "doctolib_erreur_fatale.png"
        )



    finally:

        driver.quit()



    with open(

        args.out,

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            medecins,

            f,

            indent=2,

            ensure_ascii=False

        )



    print(

        len(medecins),

        "medecins exportes dans",

        args.out

    )



if __name__ == "__main__":

    main()