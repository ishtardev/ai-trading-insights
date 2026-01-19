# Aperçus du Trading IA

Obtenez une analyse boursière en temps réel avec des aperçus de trading alimentés par l'IA. Gratuit, rapide et simple.

## Projet : 

**Module:** Deep Learning et Intelligence Artificielle Générative
**Étudiants:** Fatima Ezzahraa Abbari, Mariem Tahramt  
**Professeur:** OUTMAN Haddani  
**Programme de Master:** Finance, Actuariat et Data Science


---

## Objectif

Récupère les prix des actions et génère automatiquement des aperçus de trading :

```
GOOGL: Clôture $319,95, Changement -1,08%
→ TENDANCE HAUSSIÈRE (MA 10j au-dessus de MA 30j) | Attention au recul

TSLA: Clôture $426,58, Changement +1,71%
→ TENDANCE BAISSIÈRE (MA 10j en-dessous de MA 30j) | Inversion possible en cours
```

## Comment cela fonctionne

1. **Obtenir les données boursières** → Récupère 30 jours d'historique des prix de Polygon.io (désormais Massive)
2. **Calculer les indicateurs** → Calcule les moyennes mobiles de 10 et 30 jours
3. **Générer l'aperçu** → Analyse la tendance et crée une recommandation de trading
4. **Stockage optionnel** → Enregistre les résultats sur S3 pour le suivi (optionnel)

## Configuration 

### 1. Obtenir les clés API

**Polygon.io / Massive** (prix des actions)
- Allez à : https://polygon.io/
- S'inscrire (niveau gratuit)
- Copier votre clé API
- Remarque : Polygon fait la transition vers la plateforme Massive

**Hugging Face** (amélioration IA optionnelle)
- Allez à : https://huggingface.co/
- S'inscrire → Paramètres → Jetons → Créer un nouveau jeton
- Choisir la permission "Lire"
- Copier le jeton

### 2. Installer et configurer

```bash
# Installer les packages
pip install -r requirements.txt

# Créer le fichier .env à partir du modèle
cp .env.example .env

# Éditer .env et coller vos clés :
# POLYGON_API_KEY=your_key_here
# HF_API_TOKEN=your_token_here
```

### 3. Exécuter

```bash
# Action unique
python stock_analyzer.py AAPL

# Plusieurs actions (délai de 13 secondes entre les requêtes)
python stock_analyzer.py GOOGL TSLA MSFT

# Enregistrer sur S3 (si configuré)
python stock_analyzer.py AAPL --save-s3
```

**Résultat:**
```
============================================================
Analyse : GOOGL
============================================================

Données boursières:
  Dernière clôture: $319,95
  Changement quotidien: -1,08%
  SMA(10j):     $296,82
  SMA(30j):     $289,65
  Volume moyen (10j): 59 250 020

Aperçu IA:
  GOOGL est en TENDANCE HAUSSIÈRE (MA 10j au-dessus de MA 30j) | Attention au recul

============================================================
```

## Comment cela fonctionne

1. **Données boursières** → L'API Polygon.io récupère les 30 derniers jours d'agrégats quotidiens
2. **Indicateurs** → Le script calcule SMA-10, SMA-30, changement quotidien %, volume moyen
3. **Invite** → Les données sont formatées dans une invite textuelle concise
4. **Analyse IA** → Invite envoyée à l'API Hugging Face Inference (modèle flan-t5-small)
5. **Aperçu** → Le modèle génère une recommandation de trading claire
6. **Stockage S3 optionnel** → Les résultats sont persistés dans un bucket compatible S3 (Massive) pour le suivi historique

## Intégration S3 (Optionnel)

Pour enregistrer les résultats d'analyse sur S3 pour le suivi historique :

1. Ajoutez les identifiants S3 à `.env`:
   ```
   S3_ACCESS_KEY=your_access_key
   S3_SECRET_KEY=your_secret_key
   S3_ENDPOINT=https://files.massive.com
   S3_BUCKET=your_bucket_name
   ```

2. Exécutez avec l'indicateur `--save-s3`:
   ```bash
   python stock_analyzer.py AAPL --save-s3
   ```

3. Les résultats sont stockés à : `s3://bucket/analyses/TICKER/YYYY-MM-DDTHH-MM-SS.json`

## Fichiers

- `stock_analyzer.py` — Script d'analyse principal
- `requirements.txt` — Dépendances Python
- `.env.example` — Modèle de clé API
- `.env` — Vos clés API réelles (créez ceci, ne commitez pas)

## Limitations du niveau gratuit et limites de débit

| Service | Limite de débit | Comment le script le gère |
|---------|-----------|-------|
| Polygon.io (Massive) | 5 appels/min | Attend 13 secondes entre les requêtes |
| Hugging Face | ~1 req/sec | Optionnel ; bascule vers l'analyse technique si indisponible |

## Que sont Polygon.io / Massive et Hugging Face ?

**Polygon.io / Massive**
- API de données financières pour actions, crypto, devises
- Niveau gratuit : prix en temps réel et historiques
- 5 appels API/min (le script attend automatiquement 13 secondes entre les tickers)
- Transition de Polygon.io vers la plateforme Massive

**Hugging Face**
- Hébergement gratuit de modèles IA et API d'inférence
- Fournit des appels API gratuits pour l'apprentissage/test
- Le script l'essaie pour des aperçus plus intelligents, bascule vers l'analyse technique si indisponible
- Aucun GPU nécessaire—s'exécute sur leurs serveurs

## Comprendre les aperçus

```
GOOGL est en TENDANCE HAUSSIÈRE (MA 10j au-dessus de MA 30j) | Attention au recul
↑                                          ↑
Signal de tendance                         Action des prix

TSLA est en TENDANCE BAISSIÈRE (MA 10j en-dessous de MA 30j) | Inversion possible en cours
↑                                           ↑
Tendance baissière                         Signal de récupération
```

## Testé et fonctionnel

 Données boursières réelles de Polygon.io
 Limitation de débit (délai de 13 secondes)
 Aperçus d'analyse technique (moyennes mobiles, détection de tendance)
 Plusieurs actions en une seule exécution
 Stockage S3 optionnel (bucket Massive)

## Prochaines étapes

- Exécutez avec vos actions: `python stock_analyzer.py MSFT AMZN NVDA`
- Vérifiez les aperçus quotidiennement pour les signaux de trading
- Configurez le stockage S3 pour suivre les tendances historiques
- Étendez avec d'autres indicateurs (RSI, MACD, Bandes de Bollinger) si nécessaire

## Résultats d'apprentissage du cours

Ce projet démontre :

- **Intégration API** → Connexion à plusieurs API gratuites (Polygon.io, Hugging Face)
- **Traitement des données** → Récupération, analyse et analyse des données financières
- **Implémentation IA** → Utilisation des modèles Hugging Face pour les aperçus IA
- **Stockage en cloud** → S3/Massive pour la persistance des données
- **Limitation de débit et gestion d'erreurs** → Gestion gracieuse des contraintes API
- **Meilleures pratiques Python** → Code propre, conception modulaire, variables d'environnement

## Structure du projet

```
ai-trading-insights/
├── stock_analyzer.py      # Script principal (270+ lignes)
├── requirements.txt       # Dépendances (requests, boto3, python-dotenv)
├── .env.example          # Modèle de clé API
├── .env                  # Vos clés réelles (non commises)
└── README.md             # Ce fichier
```

## Technologies clés

| Technologie | Objectif | Pourquoi utilisé |
|-----------|---------|-------------|
| Python | Langage principal | Simplicité, traitement des données |
| Polygon.io/Massive | API de données boursières | Gratuit, fiable, en temps réel |
| Hugging Face | Aperçus IA | Inférence gratuite, aucun GPU nécessaire |
| boto3 | Stockage S3 | Persistance des données, intégration cloud |
| python-dotenv | Gestion de la configuration | Gestion sécurisée des clés API |

## Licence

Gratuit pour un usage personnel 

