# Matrice de couverture pédagogique FSE01-17 — reprise du ticket #102

Ticket #131. Installé sur `jury-central.lodylands.com`.

**SHA installé : `10b02f0`** (merge de la PR #132).

---

## 1. Avertissement méthodologique — à lire avant tout le reste

**Les documents officiels sources ne sont présents nulle part sur ce serveur.** Recherche
exhaustive effectuée (`find / -iname "*CESS*FSE*"`, `*Formation_sociale*`,
`*26-27-1-CESSP*`) : aucun résultat. Les trois PDF cités comme « sources fournies par
l'utilisateur » dans le ticket #96 (consignes CESS P 2026-2027/1, programme
474/2016/240, exemple de questionnaire avril 2024) n'ont jamais été déposés sur ce
serveur, malgré la mention de leur fourniture. Une recherche web n'a pas non plus permis
de les localiser publiquement (programme non indexé, probablement accessible uniquement
via le portail enseignement.be authentifié).

**Conséquence directe sur ce ticket** : je n'ai pas pu « relire les documents officiels »
au sens littéral, ni comparer question par question l'exemple 2024, comme demandé. Le
ticket #96 anticipait précisément ce cas et autorise explicitement la solution de repli
retenue ici : *« Si absentes du serveur, utiliser le cahier des charges original de ces
tickets, signaler l'absence et ne pas inventer le contenu des PDF »* — exception
documentée dans `docs/content_workflow.md`.

**Source faisant foi pour cette matrice** : le cahier des charges pédagogique complet
transcrit dans les issues GitHub #96 à #101 (périmètre officiel, puis pour chaque cours
une section « Matière obligatoire » et « Application attendue » détaillée, visiblement
recopiées/paraphrasées à partir des pages du programme par l'utilisateur lors de la
création de ces tickets). C'est la même source que celle utilisée pour rédiger
initialement FSE01-17 — cette matrice compare donc le contenu installé à la même
référence que celle qui a servi à l'écrire, **pas** à une relecture indépendante du PDF
original. C'est une limite réelle, explicitement assumée plutôt que dissimulée.

**Sur l'exemple de questionnaire 2024** : son contenu exact (les questions elles-mêmes)
n'a jamais été transcrit nulle part dans ce dépôt — ni dans les tickets, ni dans aucun
rapport précédent. Je ne peux donc **pas** produire la comparaison question par question
demandée. Ce que j'ai pu vérifier : qu'aucun contenu actuel ne dépend de cet examen
(aucune mention de « avril 2024 », d'un barème « /131 », d'une durée de 3h, nulle part
dans `app/v1/fse*.py` ni `app/v1/fse_bank.py` — vérifié par recherche exhaustive, § 6) et
que le périmètre actuel exclut explicitement les sujets propres à cet ancien examen
(crédits, budget familial, fiche de paie — voir § 6). C'est une vérification
**d'absence de dépendance**, pas une comparaison positive question par question.

---

## 2. Méthode suivie

Pour chacun des 17 cours : lecture intégrale de `app/v1/fseNN_course.py`,
`app/v1/fseNN_content.py` (documents support) et de la fonction
`import_fseNN_to_bank` dans `app/v1/fse_bank.py` (14 questions, énoncé + corrigé/
explication pour chacune) — jamais seulement les titres de bloc, jamais un ancien
rapport, jamais la seule réussite des tests. Chaque item de « Matière obligatoire »
(cahier des charges) a été recherché explicitement dans ce contenu réel, avec un
contrôle systématique par script (recherche textuelle de chaque notion nommée) en
complément de la lecture manuelle, pour réduire le risque d'oubli humain. Une notion
n'est comptée « complet » que si elle est expliquée (définition + nuance), pas
seulement nommée, et si une méthode/un exemple/une question permet de l'appliquer
comme demandé par « Application attendue ».

---

## 3. Résultat global

**16 cours sur 17 (FSE01-16) : couverture complète confirmée dès la première lecture,
sans correction nécessaire.** Qualité constante : 14 questions de banque par cours, 7
types de questions différents à chaque fois (jamais seulement des QCM), théorie +
définitions + méthode + 3 exemples + 2 exercices guidés + pièges + fiche mémo présents
partout, exclusions respectées (voir § 6).

**1 gap réel trouvé et corrigé** : FSE10 n'expliquait jamais la notion d'**abstention**,
alors que le cahier des charges demande explicitement « expliquer blanc/nul/procuration
**sans confondre abstention et vote blanc** ». Le mot n'apparaissait nulle part — ni
théorie, ni définitions, ni pièges, ni mémo, ni banque. Corrigé (§ 5).

**FSE17** : conforme à son propre cahier des charges (révision transversale, aucune
notion nouvelle, carte des 2 thèmes, tableau notion→savoir-faire→exemple, lexique
transversal, confusions fréquentes, 4 fiches méthode CITER/IDENTIFIER/EXPLIQUER/
JUSTIFIER, 12 exercices transversaux corrigés séparément, 3 examens blancs /100
couvrant les deux thèmes).

---

## 4. Matrice détaillée — FSE01 à FSE07 (thème « Interactions médiatiques », p. 41-47)

| Cours | Exigence officielle (cahier des charges) | Page | Section du code | Exercice | Question banque | Statut | Preuve |
|---|---|---|---|---|---|---|---|
| FSE01 | Émetteur, récepteur, message, code, canal/contact, contexte/référent | 43-45 | `_section_theory()` théorie + `.jc-definitions` | Exercice 1 (annoter l'affiche) | 6 questions dédiées (classification, vocab, MC) | ✅ Complet | `app/v1/fse01_course.py` §2-3 ; `fse_bank.py:126-341` |
| FSE01 | Distinguer canal et code (piège explicite) | 43-45 | § Comparer, blockquote piège | Exercice 1 | MC canal + classification rétroaction | ✅ Complet | `fse01_course.py:134-137` (piège dédié) |
| FSE01 | Schéma de Jakobson appliqué à mail/affiche/réseau social | 43-45 | 3 documents réalistes (EmailCard/PosterCard/SocialPostCard) | Exercices 1-3 | 3 `document_analysis`/`long_answer` sur les 3 documents | ✅ Complet | `fse01_content.py` ; `fse_bank.py:112-118` (3 `create_source_document`) |
| FSE01 | Obstacle/bruit et rétroaction pour expliquer une interaction | 43-45 | Théorie + définitions | Exercice 2 (candidature Karim) | `short_answer`/`long_answer` obstacle+rétroaction | ✅ Complet | `fse_bank.py:143-160,400-427` |
| FSE01 | App. attendue : candidature mail + interruption connexion | 43-45 | Exemple 1 (mail Karim Haddad) | Exercice 2 | `long_answer` obstacle/conséquence/rétroaction | ✅ Complet | `fse01_content.py` FSE01_MAIL_TEXT |
| FSE02 | Offre médiatique (presse/radio/TV/sites/réseaux) ; interactivité | 43, 45 | Théorie | — | MC/vocab interactivité | ✅ Complet | `fse02_course.py` §2 |
| FSE02 | Financement : vente/abonnement/publicité/fonds publics | 43, 45 | Théorie, 3 documents (Hebdo/Flash/RCW) | Exemples 1-3 | classification financement | ✅ Complet | `fse02_content.py` ; nuance financement mixte ajoutée ticket #115 |
| FSE02 | Lien financement/audience/comportements, agents/flux économiques | 43, 45 | Théorie (paragraphe audience) | — | `document_analysis` | ✅ Complet | `fse02_course.py` § audience |
| FSE02 | App. attendue : comparer média payant/gratuit-pub/public | 43, 45 | 3 documents réalistes | 2 exercices guidés | 3 docs = 3 `source_document_version_id` distincts | ✅ Complet | `fse02_content.py` |
| FSE03 | Identité personnelle/collective, identité numérique | 44-45 | « Qui suis-je ? » (bespoke, ticket #120/126) | — | classification/vocab | ✅ Complet | `fse03_course.py::_section_identity` |
| FSE03 | Trace volontaire/involontaire, réputation, groupe d'appartenance | 44-45 | « Quelles traces je laisse ? » + « Quelle image... » | — | classification traces | ✅ Complet | `fse03_course.py::_section_traces/_section_image` |
| FSE03 | Nuance : ancienne publication volontaire ≠ devenue involontaire | 44-45 | Encadré dédié (blockquote) | — | — | ✅ Complet | `fse03_course.py` § traces, ajouté ticket #120 |
| FSE03 | App. attendue : classer traces + conséquences candidature | 44-45 | 5 documents Sophie Lambert + note RH | Exercices 1-2 | `document_analysis`/`long_answer` | ✅ Complet | `fse03_content.py` (ticket #118) |
| FSE04 | Norme, valeur, besoin, comportement, frustration, influence sociale, socialisation | 44-46 | 3 cartes bespoke (ticket #126) | — | classification/vocab | ✅ Complet | `fse04_course.py` |
| FSE04 | Pression du groupe et limites (jamais toute l'UAA Normes/Société) | 44-46 | § « Peut-on agir autrement ? » | — | MC limites | ✅ Complet | `fse04_course.py::_section_can_one_act_differently` |
| FSE04 | App. attendue : vidéo humiliante, distinguer valeur/norme/comportement | 44-46 | Documents groupe + témoignage Karim | 2 exercices | `document_analysis` | ✅ Complet | `fse04_content.py` |
| FSE05 | Droit à l'image, vie privée, données personnelles, consentement | 45 | Théorie complète | — | vocab/MC | ✅ Complet | `fse05_course.py` §2-3 |
| FSE05 | Prise de vue ≠ diffusion ; sujet principal/personne accessoire | 45 | Théorie + méthode | Exercice 1 | classification | ✅ Complet | `fse05_course.py` §2,4 |
| FSE05 | Aucune règle absolue « lieu public = diffusion libre » | 45 | Piège dédié | — | — | ✅ Complet | `fse05_course.py` § pièges |
| FSE05 | App. attendue : 6 situations, répondre séparément prise de vue/diffusion | 45 | `FSE05_SITUATIONS_TEXT` | Exercices 1-2 | 14 questions sur les 6 situations | ✅ Complet | `fse05_content.py` — **6 situations vérifiées par comptage** |
| FSE06 | 9 comportements (cyberharcèlement → traitement données sans base valable) | 45 | Théorie, les 9 catégories | Exercices 1-2 | classification/vocab | ✅ Complet | `fse06_course.py` §2-3 |
| FSE06 | Vocabulaire pédagogique, jamais de qualification pénale/peine | 45 | Rappelé 4 fois (intro, méthode, piège, mémo) | — | — | ✅ Complet | `fse06_course.py` |
| FSE06 | Liberté d'expression et limites | 45 | Théorie, 1er paragraphe | Exemple 3 (critique restaurant) | MC | ✅ Complet | `fse06_course.py` |
| FSE06 | App. attendue : 10 scénarios associés aux comportements | 45 | `FSE06_SCENARIOS_TEXT` | — | 14 questions | ✅ Complet | `fse06_content.py` — **10 scénarios vérifiés par comptage** |
| FSE07 | Recueillir/traiter/analyser/synthétiser ; fait/interprétation/opinion | 41-47 | Théorie | Exercice 1 | classification | ✅ Complet | `fse07_course.py` §2 |
| FSE07 | Vérifier auteur/date/contexte/preuves | 41-47 | Méthode étape 1 | Exercice 2 | `document_analysis` | ✅ Complet | `fse07_course.py` §4 |
| FSE07 | Enjeux juridiques et sociologiques, conclusion argumentée | 41-47 | Théorie + exemples | — | `long_answer` conclusion | ✅ Complet | `fse07_course.py` §2,9 |
| FSE07 | Réutilise FSE01/04/05/06 sans les ré-enseigner (pas un cours de journalisme complet) | 41-47 | Prérequis explicites | — | — | ✅ Complet | `fse07_course.py` docstring + §1 |
| FSE07 | App. attendue : dossier 3 documents, analyse guidée + cas autonome | 41-47 | École/chat/forum (3 documents) | 2 exercices | 14 questions | ✅ Complet | `fse07_content.py` |

---

## 5. Matrice détaillée — FSE08 à FSE17 (thème « Le citoyen et l'État », p. 56-64)

| Cours | Exigence officielle | Page | Section du code | Exercice | Question banque | Statut | Preuve |
|---|---|---|---|---|---|---|---|
| FSE08 | État fédéral, monarchie constitutionnelle, démocratie parlementaire | 56-57, 61 | Théorie §1 | Corrigé 9 | MC | ✅ Complet | `fse08_course.py` §2 |
| FSE08 | 5 niveaux, 3 Régions, 3 Communautés | 56-57, 61 | Théorie + schéma SVG | Exercice 1 | classification | ✅ Complet | `fse08_course.py` (diagramme `FSE08_POWER_LEVELS_DIAGRAM_SVG`) |
| FSE08 | Loi/décret/ordonnance, exception Bruxelles | 56-57, 61 | Définitions + piège dédié | Exercice 2 | MC exception | ✅ Complet | `fse08_course.py` § pièges |
| FSE08 | Jamais un cours exhaustif de droit constitutionnel | 56-57, 61 | Piège explicite | — | — | ✅ Complet | `fse08_course.py` § pièges |
| FSE09 | Région (territoire) / Communauté (personnes-langue-culture) | 61-62 | Théorie, réutilise FSE08 | Exercices 1-2 | classification ×2 | ✅ Complet | `fse09_course.py` |
| FSE09 | Santé/sécu sociale multi-niveaux, pas de réponse unique trompeuse | 61-62 | Situation 8, dédiée | Exercice 2 | `document_analysis`+`long_answer` | ✅ Complet | `fse09_content.py` situation 8 |
| FSE09 | App. attendue : 10 situations → niveau + matière | 61-62 | `FSE09_SITUATIONS_TEXT` | — | 14 questions, les 10 situations utilisées | ✅ Complet | **10 situations vérifiées par comptage** |
| FSE10 | 5 scrutins, périodicité, scrutin proportionnel, coalition | 61-62 | Théorie + tableau daté | Exemple 1 | MC/classification | ✅ Complet | `fse10_content.py` FSE10_TABLE_TEXT |
| FSE10 | Procuration, témoin dépouillement, pétition, consultation/référendum | 61-62 | Définitions | — | 2 vocab + 1 MC + 1 short_answer | ✅ Complet | `fse10_course.py` §3 |
| FSE10 | Vote blanc/nul, **sans confondre abstention et vote blanc** | 61-62 | Théorie + définitions + piège + mémo | Exercice 2 | classification + MC | ⚠️→✅ **Corrigé ticket #131** | Absent avant ce ticket ; voir § 5bis |
| FSE10 | Conditions vérifiées par scrutin ET région, jamais universelles | 61-62 | Théorie + piège + tableau daté | Exercice 1 | classification Flandre | ✅ Complet | `fse10_content.py` (réforme 2024 référencée) |
| FSE10 | App. attendue : bulletins + tableau daté | 61-62 | 4 bulletins + tableau | 2 exercices | 14 questions | ✅ Complet | `fse10_content.py` |
| FSE11 | 5 familles (socialiste/libérale/écologiste/centriste-humaniste/radicale) | 61-62 | Théorie | Exercice 1 | classification | ✅ Complet | `fse11_course.py` §2 |
| FSE11 | Axe gauche-centre-droite = repère simplifié, jamais vérité absolue | 61-62 | Rappelé 4 fois | — | MC dédiée | ✅ Complet | `fse11_course.py` |
| FSE11 | 6 partis 2024 (PS/MR/Ecolo/Les Engagés/PTB/Vlaams Belang), sourcés/datés | 61-62 | § Sources officielles | — | classification 4/6 extraits + document_analysis extrait 6 | ✅ Complet | **6 partis vérifiés par comptage**, source Brussels Times datée |
| FSE11 | Comparer valeur/priorité/effets, **sans opinion personnelle** | 61-62 | Théorie + piège + méthode | Exercice 2 | MC dédiée « jamais juger » | ✅ Complet | `fse11_course.py` ; aucune question banque ne demande l'avis de l'élève |
| FSE12 | Recettes fiscales/parafiscales/non fiscales | 61 | Théorie | Exercice 1 | classification | ✅ Complet | `fse12_course.py` §2 |
| FSE12 | Dépenses fonctionnement/investissement/transfert | 61 | Théorie | Exercice 1 | classification | ✅ Complet | `fse12_course.py` §2 |
| FSE12 | Solde budgétaire, déficit, dette ; calculs sur données fictives | 61 | Méthode + exemple 3 | Exercice 2 | `document_analysis` calcul | ✅ Complet | `fse12_content.py` tableau fictif |
| FSE12 | IPP nommée seulement comme recette, **aucun calcul/déclaration** | 61 | Rappelé 5 fois (titre inclus) | — | MC dédiée | ✅ Complet | Vérifié par recherche exhaustive § 6 |
| FSE13 | Solidarité, mutualisation, assurance sociale, redistribution | 61 | Théorie | Exercice 2 | `long_answer` | ✅ Complet | `fse13_course.py` §2 |
| FSE13 | Financement/gestion/versement distincts | 61 | Théorie + piège | — | MC dédiée | ✅ Complet | `fse13_course.py` |
| FSE13 | App. attendue : trajet cotisation→prestation, 6 situations/risques | 61 | `FSE13_SITUATIONS_TEXT` | Exercices 1-2 | 14 questions | ✅ Complet | **6 situations vérifiées par comptage** |
| FSE14 | 7 organismes (ONSS/INAMI/ONEM/SFP/FEDRIS/ONVA/INASTI) | 61-62 | Théorie + mémo | Exercice 1 | MC/short_answer | ✅ Complet | **7 organismes vérifiés par comptage** |
| FSE14 | FAMIWAL (Wallonie) / FAMIRIS (Bruxelles), régionalisation | 61-62 | Théorie + exemple 3 | — | classification | ✅ Complet | `fse14_course.py` + sources Wallonie.be/Iriscare |
| FSE14 | Collecteur/gestionnaire/intermédiaire payeur | 61-62 | Théorie + définitions | Exercice 1 | MC | ✅ Complet | `fse14_course.py` §3 |
| FSE14 | Enjeux vieillissement/dépenses santé, **sans montants/âges précis** | 61-62 | Théorie + piège | Exercice 2 | `short_answer` | ✅ Complet | `fse14_course.py` § pièges |
| FSE15 | 4 agents, flux réels/monétaires | 43, 61-63 | Théorie + schéma SVG | Exercice 1 | classification | ✅ Complet | `fse15_course.py` |
| FSE15 | Redistribution/régulation/production biens collectifs | 43, 61-63 | Théorie | — | vocab | ✅ Complet | `fse15_course.py` §2 |
| FSE15 | Volet législation hors évaluation sommative (note 90) | 43, 61-63 | Piège + mémo explicites | — | — | ✅ Complet | Vérifié par `test_fse15_respects_legislation_exclusion` (préexistant) |
| FSE15 | App. attendue : compléter circuit + effets aide publique | 43, 61-63 | Exemple 3 (aide média) | Exercice 2 | `long_answer` propagation | ✅ Complet | `fse15_content.py` |
| FSE16 | Méthode : décision/niveau/objectifs/agents/flux/effets/limites/conséquences | 57-58, 62-64 | Théorie + méthode | Exercices 1-2 | `document_analysis`×2 | ✅ Complet | `fse16_course.py` §2,4 |
| FSE16 | Court terme / long terme, conclusion fondée sur documents | 57-58, 62-64 | Théorie + corrigé 9 | — | `long_answer` conclusion | ✅ Complet | `fse16_course.py` |
| FSE16 | App. attendue : dossier 3 documents, aide transports | 57-58, 62-64 | Proposition/note budget/réactions | 2 exercices | 14 questions | ✅ Complet | `fse16_content.py` — **3 documents vérifiés** |
| FSE17 | Carte 2 thèmes, tableau notion→savoir-faire→exemple | — | §1-2 | — | n/a (pas de banque propre) | ✅ Complet | `fse17_course.py` |
| FSE17 | Lexique transversal, confusions fréquentes | — | §3-4 | — | n/a | ✅ Complet | `fse17_course.py` |
| FSE17 | 4 fiches méthode CITER/IDENTIFIER/EXPLIQUER/JUSTIFIER | — | §5 | — | n/a | ✅ Complet | `fse17_course.py` |
| FSE17 | 12 exercices transversaux corrigés séparément | — | §7-8 | 12 exercices | n/a | ✅ Complet | **12 exercices + 12 corrigés vérifiés par comptage** |
| FSE17 | 3 examens blancs /100, couvrant les 2 thèmes, non officiels | — | §9 | — | banque transversale FSE01-16 | ✅ Complet | `app.v1.session_service._start_fse_transversal_session` (préexistant, non modifié) |

---

## 5bis. Détail du gap trouvé et corrigé (FSE10 — abstention)

**Exigence** (issue #99) : « expliquer blanc/nul/procuration sans confondre abstention et
vote blanc ».

**Avant ce ticket** : le mot « abstention » n'apparaissait dans aucun des trois fichiers
FSE10 (`fse10_course.py`, `fse10_content.py`, l'entrée `import_fse10_to_bank` de
`fse_bank.py`) — vérifié par recherche exhaustive (`grep -ni abstention`, zéro résultat).
Un élève pouvait donc confondre les deux notions sans que le cours ne l'en empêche,
exactement le risque que le cahier des charges demande d'éviter.

**Corrigé** :
- Théorie : nouveau paragraphe distinguant l'abstention (ne pas se présenter, aucun acte
  de vote) du vote blanc (se présenter et déposer un bulletin sans marque), avec la nuance
  que l'abstention reste légalement sanctionnable mais que la sanction n'est plus
  appliquée depuis 2003 (vérifié auprès d'une source citoyenne qui rapporte le texte
  légal — voir § Sources officielles vérifiées, nouvelle entrée Bruxelles-J).
- Définitions : nouvelle entrée « Abstention ».
- Méthode (étape 3) : complétée pour inclure explicitement cette distinction.
- Mauvaises réponses comparées aux bonnes : nouvelle paire dédiée.
- Pièges : nouvelle entrée dédiée.
- Fiche mémo : nouvelle puce dédiée.
- Banque : la question à choix multiple sur le vote blanc teste désormais explicitement
  la distinction (l'option « ne pas se présenter au bureau de vote » devient un
  distracteur explicite, testant directement la confusion que le cahier des charges
  demande d'éviter) — remplace une option redondante avec une autre question déjà
  existante, le nombre de questions (14) et la répartition de difficulté (7/4/3) restent
  inchangés.

Aucune autre notion retirée : tout le contenu précédent reste intact, cette correction
est strictement additive.

---

## 6. Vérification des exclusions (périmètre officiel)

Recherche exhaustive (`grep -rniE`) sur l'ensemble de `app/v1/fse*.py` pour les termes
explicitement exclus par le périmètre officiel :

| Exclusion | Résultat | Détail |
|---|---|---|
| Calcul ou déclaration d'IPP | ✅ Aucune occurrence réelle | Seules les mentions trouvées sont les rappels explicites de l'exclusion elle-même (FSE08, FSE12, `fse_plan.py`) |
| Crédit à la consommation / emprunt / TAEG | ✅ Aucune occurrence réelle | Idem |
| Budget familial / fiche de paie | ✅ Aucune occurrence réelle | Idem |
| Avertissement-extrait de rôle | ✅ Aucune occurrence | — |
| Question sur un numéro d'UAA | ✅ Aucune occurrence | — |
| Volet législation en évaluation sommative (FSE15) | ✅ Respecté | Déjà vérifié par `test_fse15_respects_legislation_exclusion` (préexistant) |

**Comparaison à l'exemple 2024** (voir avertissement § 1 : contenu non disponible) :
vérification indirecte effectuée — aucune mention de « avril 2024 », d'un barème « /131 »
ni d'une durée de « 3h » (ou « 3 heures ») nulle part dans le code source des 17 cours.
Le périmètre actuel (2h maximum, seuil 50 %, périmètre p. 41-47/56-64 sauf IPP) est
appliqué de façon autonome, sans dépendance à l'ancien examen — conforme à l'instruction
« ni son barème /131, ni ses 3h, ni ses questions hors périmètre ne définissent l'épreuve
actuelle ».

---

## 7. Ambiguïtés et limites explicitement signalées

1. **Documents officiels absents** (§ 1) — limite majeure, qui affecte la fiabilité de
   toute la matrice : je compare le contenu installé à la même source (cahier des
   charges transcrit) qui a servi à l'écrire, pas à une relecture indépendante du
   programme officiel. Si le cahier des charges transcrit par l'utilisateur en 2026-10-01
   contenait lui-même une omission par rapport au PDF réel, cette matrice ne peut pas la
   détecter.
2. **Exemple de questionnaire 2024 non comparé question par question** (§ 1) — seule une
   vérification d'absence de dépendance a pu être faite.
3. **FSE10, procuration/témoin du dépouillement/pétition/consultation populaire** :
   chacun dispose d'une définition et d'au moins une question de banque (vocabulaire ou
   QCM), mais aucun n'a d'exemple commenté dédié avec un scénario complet travaillé dans
   le corps du cours (contrairement au vote blanc/nul, qui a deux bulletins analysés en
   détail). Jugé suffisant (définition + méthode + banque couvrent l'exigence), mais
   signalé ici par souci de transparence plutôt que silencieusement classé « complet »
   sans réserve.
4. Cette matrice couvre le contenu pédagogique (théorie, exemples, exercices, banque de
   questions) — elle ne re-vérifie pas les propriétés génériques du moteur (autosave,
   export, impression, isolation des sessions), déjà couvertes par les suites de tests
   génériques existantes et non modifiées par ce ticket.

---

## 8. Contrôles effectués

| Contrôle | Résultat |
|---|---|
| `tests/test_ticket131_fse_coverage_audit.py` (nouveau, 8 cas : présence/distinction de l'abstention, nuance sanction non appliquée, question banque, 14 questions/7-4-3 inchangés, régression de rafraîchissement de contenu) | ✅ |
| `tests/test_ticket99_fse09_12.py`, `card_kind`, `admin_content_hierarchy`, `test_ticket120_fse_theory_generic.py` | ✅ (122 passants au total) |
| Recherche exhaustive des 17 cours contre le cahier des charges (script + lecture manuelle intégrale de 14/17 fichiers, connaissance directe récente des 3 autres) | ✅ |
| Recherche exhaustive des termes exclus du périmètre | ✅ (§ 6) |
| Vérification que le fait nouvellement ajouté (sanction de l'abstention) est exact | ✅ (source citoyenne citant le texte légal, § 5bis) |

**Non fait, et pourquoi** : rendu réel dans un navigateur de chacun des 17 cours — ce
ticket porte sur le contenu pédagogique (texte, questions, corrigés), pas sur la mise en
page, déjà traitée et validée par les tickets #120/#124/#126. Suite de tests complète du
dépôt (plusieurs centaines de tests) — contrôles ciblés uniquement, conformément à
l'instruction explicite de ce ticket.

**Comptes et données** : vérifiés intacts avant/après chaque étape du déploiement.

---

## 9. Installation

- Fusionné via PR #132, fast-forward sur `jury-central.lodylands.com`.
- Sauvegarde préalable : `jury_central.db.bak-pre-ticket131-<horodatage>`.
- Comptes/sessions/réponses avant et après le seed : 18 utilisateurs, 68 sessions, 546
  réponses — strictement identiques (seed purement additif, aucune suppression).
- `seed-db` : 51 blocs créés (rafraîchissement forcé des 3 blocs FSE10 modifiés +
  rafraîchissements habituels déjà en place pour les autres cours), 264 conservés
  inchangés.
- Vérifié en base de données que les 3 blocs FSE10 modifiés contiennent bien
  « abstention » après le seed.
- Vérifié sur la page réelle en production (`https://jury-central.lodylands.com/uaa/fse-fse10`)
  : présence du mot « abstention », présence de la phrase de distinction (« ne pas se
  présenter »), aucune fuite Markdown, aucune mention « provisoire ».

**Lien à vérifier** : https://jury-central.lodylands.com/uaa/fse-fse10 (section théorie,
« Comparer pour ne pas confondre » et « Fiche mémo »).
