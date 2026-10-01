# Plan d'intégration — Formation sociale et économique (FSE), CESS Professionnel

Document de planification (même rôle que `docs/content_plan_informatique_francais.md`
pour Informatique/Français), pas une documentation technique permanente — voir
`docs/ARCHITECTURE.md` pour ce qui est réellement implémenté. Produit dans le cadre du
ticket GitHub #96/#97. Traçabilité du contenu : voir `docs/content_workflow.md`, section
« Contenu rédigé à partir d'un cahier des charges » — le cahier des charges pédagogique
complet est fourni directement dans les tickets #96/#97 (pas de fichier
`docs/sources_cours/` séparé pour le contenu des leçons), le périmètre officiel provenant
des documents utilisateur cités au § 2.

---

# 1. État — ticket #96 (2026-10-01)

Matière créée (`Subject` « Formation sociale et économique », `Module` code `FSE`) et
**FSE01 — Communiquer : le schéma de communication** livré complet (théorie, 14 questions
de banque, practice avec choix de difficulté, examen avec choix de difficulté ET de
sévérité de cotation, correction hybride, résultats, historique) — voir
`app/v1/fse_plan.py`, `app/v1/fse01_course.py`, `app/v1/fse01_content.py`,
`app/v1/fse_bank.py`.

FSE02→FSE17 ci-dessous restent au stade de PLAN (titre, thème, pages du programme) : ils
ne sont ni seedés en base ni présentés comme disponibles (même principe que Français
FR06→FR20 au moment du ticket #94 PHASE A) — chacun fera l'objet d'un ticket de rédaction
dédié, suivant le même cahier des charges de rédaction que le ticket #97 (objectifs
observables, théorie progressive, définitions, méthode, 3 exemples commentés, 2 exercices
guidés corrigés, pièges, fiche mémo, 8 exercices d'entraînement, examen /20).

---

# 2. Périmètre officiel (consignes CESS P 2026-2027/1)

Uniquement :
- **Interactions médiatiques** — programme 474/2016/240, pages imprimées 41-47 (= PDF
  75-81 dans l'exemplaire de 100 pages fourni par l'utilisateur) ;
- **Le citoyen et l'État** — pages imprimées 56-64 (= PDF 90-98), **sauf IPP**.

Exclusions explicites : budget familial, crédits, emprunts, TAEG, classification des
revenus du ménage, déclaration IPP, calcul IPP, avertissement-extrait de rôle, fiscalité
immobilière détaillée. La fiscalité/parafiscalité générale et le budget de l'État restent
inclus (seule l'IPP est exclue). L'ancien examen d'avril 2024 (document utilisateur
« Jurys — CESS P — Exemple de questionnaire ») est indicatif seulement : ni son barème
/131, ni ses 3h, ni ses questions hors périmètre ne définissent l'épreuve actuelle (2h
maximum, seuil de réussite 50 %).

---

# 3. Plan des 17 mini-cours

| Code | Titre | Thème | Pages programme |
|---|---|---|---|
| **FSE01** | **Communiquer : le schéma de communication** (livré, ticket #96) | Médias | p. 43-45 |
| FSE02 | Les médias et leurs financements | Médias | p. 43, 45 |
| FSE03 | Identités, traces numériques et appartenance | Médias | p. 44-45 |
| FSE04 | Normes, valeurs et influence sociale | Médias | p. 44-46 |
| FSE05 | Image, vie privée et données personnelles | Médias | p. 45 |
| FSE06 | Droits et comportements illicites en ligne | Médias | p. 45 |
| FSE07 | Analyser un dossier médiatique | Médias | p. 41-47 |
| FSE08 | La Belgique : État et niveaux de pouvoir | Citoyen | p. 56-57, 61 |
| FSE09 | Qui décide de quoi ? | Citoyen | p. 61-62 |
| FSE10 | Élections et participation citoyenne | Citoyen | p. 61-62 |
| FSE11 | Partis politiques et choix argumenté | Citoyen | p. 61-62 |
| FSE12 | Le budget de l'État | Citoyen | p. 61 |
| FSE13 | La sécurité sociale : rôle et financement | Citoyen | p. 61 |
| FSE14 | La sécurité sociale : organismes et enjeux | Citoyen | p. 61-62 |
| FSE15 | Le circuit économique et les interventions de l'État | Citoyen | p. 43, 61-63 |
| FSE16 | Analyser une décision publique | Citoyen | p. 57-58, 62-64 |
| FSE17 | Révision générale et examens blancs | — | — |

FSE01-07 couvrent l'UAA « Interactions médiatiques » ; FSE08-16 couvrent l'UAA « Le citoyen
et l'État » ; FSE17 est une révision transversale (rôle comparable à MC38 pour AMPCR —
voir `app/v1/mc38_transversal.py` — mais jamais implémentée comme telle avant son propre
ticket dédié).

Note p. 61 du programme : le volet législation reste hors évaluation sommative (acceptation
du ticket #96) — à respecter explicitement lors de la rédaction de FSE12-14.

---

# 4. Prochaine étape

Rédaction de FSE02-04 (cahier des charges déjà fourni par le ticket #97), en réutilisant
strictement `app/v1/fse_plan.py`/`app/v1/fse_bank.py` (mêmes conventions que FSE01, jamais
un second moteur) — voir `docs/claude-reports/2026-10-01_ticket-96-fse.md` pour le détail
de l'implémentation de FSE01 et les chemins de code à réutiliser.
