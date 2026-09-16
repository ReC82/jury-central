"""Moteur générique de génération d'exercices et de correction par IA (ticket #10,
complément « exercices générés + correction IA »).

Package volontairement indépendant du reste de l'application (comme `generators/`) :
- `schemas.py` — structures de données échangées (jamais de texte libre non structuré) ;
- `context.py` — registre des contextes pédagogiques bornés, un par cours ;
- `prompts.py` — construction des messages/schémas JSON envoyés au fournisseur ;
- `provider.py` — interface générique (`Protocol`) + exceptions ;
- `openai_provider.py` — implémentation réelle (API OpenAI, HTTP côté serveur uniquement) ;
- `fake_provider.py` — implémentation factice, déterministe, pour les tests ;
- `factory.py` — point d'entrée unique utilisé par le reste de l'application ;
- `integrity.py` — signature HMAC des exercices générés (anti-falsification côté client).
"""
