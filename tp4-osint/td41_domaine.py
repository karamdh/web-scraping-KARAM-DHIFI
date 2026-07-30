import json
import socket
import sys
import time

import requests
import whois  # pip install python-whois

HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}
TIMEOUT = 10
THROTTLE = 1.0  


def premiere_date(valeur) -> str:
    """Normalise une date WHOIS (peut etre None, datetime, ou liste de dates)."""
    if isinstance(valeur, list):
        valeur = valeur[0] if valeur else None
    return str(valeur or "n/a")[:10]


def analyse_whois(domaine: str) -> dict:
    """Interroge le registre WHOIS public du domaine."""
    try:
        w = whois.whois(domaine)
        return {
            "registrar": str(w.registrar or "n/a"),
            "creation_date": premiere_date(w.creation_date),
            "expiration_date": premiere_date(w.expiration_date),
            "name_servers": sorted(set(w.name_servers or [])),
            "country": str(w.country or "n/a"),
        }
    except Exception as e:
        return {"erreur": str(e)}


def analyse_headers(domaine: str) -> dict:
    """Recupere les en-tetes HTTP exposes publiquement (HEAD request)."""
    try:
        r = requests.head(
            f"https://{domaine}",
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        h = r.headers
        return {
            "status": r.status_code,
            "server": h.get("Server", "n/a"),
            "x_powered_by": h.get("X-Powered-By", "n/a"),
            "x_frame_options": h.get("X-Frame-Options", "n/a"),
            "csp_present": "Content-Security-Policy" in h,
            "hsts_present": "Strict-Transport-Security" in h,
        }
    except Exception as e:
        return {"erreur": str(e)}


def sous_domaines_crtsh(domaine: str) -> list[str]:
    """Cherche les sous-domaines via l'API publique crt.sh (Certificate Transparency)."""
    url = f"https://crt.sh/?q=%.{domaine}&output=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=40)
        r.raise_for_status()
        data = r.json()
        subs = {
            entry["name_value"].strip()
            for entry in data
            for name in entry["name_value"].split("\n")  # certains certs multi-noms
            if "*" not in entry["name_value"] and entry["name_value"].endswith(domaine)
        }
        return sorted(subs)[:100]  # on limite a 100 pour rester raisonnable
    except Exception as e:
        return [f"ERREUR: {e}"]


def analyse_robots(domaine: str) -> str:
    """Recupere le robots.txt (juste pour information -- pas d'usage en bypass)."""
    try:
        r = requests.get(f"https://{domaine}/robots.txt", headers=HEADERS, timeout=TIMEOUT)
        return r.text[:1000] if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return str(e)


def resolution_ip(domaine: str) -> str:
    try:
        return socket.gethostbyname(domaine)
    except Exception as e:
        return f"ERREUR: {e}"


def analyser_domaine(domaine: str) -> dict:
    print(f"[*] Analyse de {domaine}...")

    rapport = {"domaine": domaine}

    rapport["ip"] = resolution_ip(domaine)

    print("[*] WHOIS...")
    rapport["whois"] = analyse_whois(domaine)
    time.sleep(THROTTLE)

    print("[*] Headers HTTP...")
    rapport["headers_http"] = analyse_headers(domaine)
    time.sleep(THROTTLE)

    print("[*] Sous-domaines (crt.sh)...")
    rapport["sous_domaines"] = sous_domaines_crtsh(domaine)
    time.sleep(THROTTLE)

    print("[*] robots.txt...")
    rapport["robots_txt"] = analyse_robots(domaine)

    rapport["nb_sous_domaines"] = len(
        [s for s in rapport["sous_domaines"] if not s.startswith("ERREUR")]
    )
    return rapport


def main() -> None:
    domaine = sys.argv[1] if len(sys.argv) > 1 else "wikipedia.org"
    rapport = analyser_domaine(domaine)

    sortie = "rapport_domaine.json"
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)

    print(f"[+] Rapport sauvegarde : {sortie}")
    print(f"    {rapport['nb_sous_domaines']} sous-domaines trouves")
    print(f"    Serveur : {rapport['headers_http'].get('server', 'n/a')}")


if __name__ == "__main__":
    main()