# Plan d'intégration — Formation sociale et économique (FSE), CESS Professionnel

Document de planification (même rôle que `docs/content_plan_informatique_francais.md`
pour Informatique/Français), pas une documentation technique permanente — voir
`docs/ARCHITECTURE.md` pour ce qui est réellement implémenté. Produit dans le cadre du
ticket GitHub #96-#102. Traçabilité du contenu : voir `docs/content_workflow.md`,
section « Contenu rédigé à partir d'un cahier des charges » — le cahier des charges
pédagogique complet est fourni directement dans les tickets #96-#101 (pas de fichier
`docs/sources_cours/` séparé pour le contenu des leçons), le périmètre officiel provenant
des documents utilisateur cités au § 2.

---

# 1. État — tickets #96-#102 (2026-10-02) — PROGRAMME COMPLET

Matière créée (`Subject` « Formation sociale et économique », `Module` code `FSE`).
**FSE01-FSE17 livrés complets** (théorie, 14 questions de banque chacun pour FSE01-16,
practice avec choix de difficulté réellement effectif, examen avec choix de difficulté ET
de sévérité de cotation distincts, correction hybride, résultats, historique) :
- Ticket #96 : FSE01 — voir `app/v1/fse_plan.py`, `app/v1/fse01_course.py`,
  `app/v1/fse01_content.py`.
- Ticket #97 : FSE02, FSE03, FSE04 — `app/v1/fse0[2-4]_course.py`/`fse0[2-4]_content.py`.
- Ticket #98 : FSE05, FSE06, FSE07, FSE08 — `app/v1/fse0[5-8]_course.py`/
  `fse0[5-8]_content.py`.
- Ticket #99 : FSE09, FSE10, FSE11, FSE12 — `app/v1/fse0[9]_course.py`/`fse1[0-2]_course.py`.
- Ticket #100 : FSE13, FSE14, FSE15, FSE16 — `app/v1/fse1[3-6]_course.py`.
- Ticket #101 : FSE17 (révision transversale, sans banque propre) —
  `app/v1/fse17_course.py` + `app.v1.session_service._start_fse_transversal_session` pour
  les trois examens blancs progressifs (facile/moyen/difficile = sélecteur de difficulté
  existant appliqué au pool transversal FSE01-16).
- Ticket #102 : contrôle de couverture — matrice exhaustive, absence de contenu hors
  périmètre, audit anti-doublon global (5 paires trouvées et corrigées, dont 1 croisée
  entre deux cours), aucune question orpheline.

FSE06/FSE08/FSE09/FSE10/FSE11/FSE14 mobilisent des affirmations juridiques et
institutionnelles réelles, vérifiées auprès de sources belges officielles et référencées
dans chaque cours (§ « Sources officielles vérifiées ») et dans
`docs/claude-reports/2026-10-01_ticket-96-fse.md` § 14 et § 15.

Tous ces cours partagent `app/v1/fse_bank.py` (banque unique, import idempotent par
cours) ; FSE17 n'y a volontairement aucune entrée.

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
| **FSE02** | **Les médias et leurs financements** (livré, ticket #97) | Médias | p. 43, 45 |
| **FSE03** | **Identités, traces numériques et appartenance** (livré, ticket #97) | Médias | p. 44-45 |
| **FSE04** | **Normes, valeurs et influence sociale** (livré, ticket #97) | Médias | p. 44-46 |
| **FSE05** | **Image, vie privée et données personnelles** (livré, ticket #98) | Médias | p. 45 |
| **FSE06** | **Droits et comportements illicites en ligne** (livré, ticket #98) | Médias | p. 45 |
| **FSE07** | **Analyser un dossier médiatique** (livré, ticket #98) | Médias | p. 41-47 |
| **FSE08** | **La Belgique : État et niveaux de pouvoir** (livré, ticket #98) | Citoyen | p. 56-57, 61 |
| **FSE09** | **Qui décide de quoi ?** (livré, ticket #99) | Citoyen | p. 61-62 |
| **FSE10** | **Élections et participation citoyenne** (livré, ticket #99) | Citoyen | p. 61-62 |
| **FSE11** | **Partis politiques et choix argumenté** (livré, ticket #99) | Citoyen | p. 61-62 |
| **FSE12** | **Le budget de l'État** (livré, ticket #99) | Citoyen | p. 61 |
| **FSE13** | **La sécurité sociale : rôle et financement** (livré, ticket #100) | Citoyen | p. 61 |
| **FSE14** | **La sécurité sociale : organismes et enjeux** (livré, ticket #100) | Citoyen | p. 61-62 |
| **FSE15** | **Le circuit économique et les interventions de l'État** (livré, ticket #100) | Citoyen | p. 43, 61-63 |
| **FSE16** | **Analyser une décision publique** (livré, ticket #100) | Citoyen | p. 57-58, 62-64 |
| **FSE17** | **Révision générale et examens blancs** (livré, ticket #101) | Synthèse | — |

FSE01-07 couvrent l'UAA « Interactions médiatiques » ; FSE08-16 couvrent l'UAA « Le citoyen
et l'État » ; FSE17 est une révision transversale (même principe que MC38 pour AMPCR — voir
`app/v1/mc38_transversal.py` — mais strictement banque, sans aucune génération IA : voir
`app.v1.session_service._start_fse_transversal_session`).

Note p. 61 du programme : le volet législation reste hors évaluation sommative (acceptation
du ticket #96) — respecté explicitement dans FSE15 (ticket #100, vérifié par
`tests/test_ticket102_coverage.py::test_fse15_respects_legislation_exclusion`).

---

# 4. Programme officiel complet livré (2026-10-02)

Les 17 mini-cours officiels FSE01-FSE17 sont désormais tous rédigés, banqués (sauf FSE17)
et installés. Prochaine étape éventuelle : un ticket futur pourrait enrichir une UAA
existante (jamais en ajouter une 18e hors du programme officiel) selon le retour de
l'utilisateur sur l'ensemble du parcours. Voir
`docs/claude-reports/2026-10-01_ticket-96-fse.md` § 1-15 pour le détail complet de
l'implémentation et les chemins de code à réutiliser pour toute évolution future.
