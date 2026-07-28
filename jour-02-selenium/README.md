# TP2 - Selenium : Doctolib & Les Échos

## 1. Objectif du TP

Ce TP a permis d’explorer l’utilité de Selenium pour scraper des sites dont le contenu est chargé dynamiquement par JavaScript.

Nous avons mis en place deux scripts Python :

- Un scraper pour **Doctolib**, qui récupère les fiches de médecins à partir d’une spécialité et d’une ville.
- Un scraper pour **Les Échos**, qui récupère les articles de la page d’accueil.

Les objectifs principaux sont :

- Identifier quand Selenium est indispensable face à `requests + BeautifulSoup`.
- Gérer une bannière de consentement cookies.
- Utiliser `WebDriverWait` et `ExpectedConditions` au lieu de `time.sleep()`.
- Charger du contenu dynamique grâce au scroll.
- Comparer les performances entre le mode normal et le mode headless.
- Capturer automatiquement un screenshot en cas d’échec.

---

# 2. Installation

Installation des bibliothèques nécessaires :

```bash
pip install selenium requests beautifulsoup4 lxml