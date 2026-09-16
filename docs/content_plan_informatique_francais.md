# Plan d'intégration — Informatique (AMPCR) et Français (CESS Professionnel)

Document de planification, pas une documentation technique permanente (voir
`docs/ROADMAP.md` pour les statuts de version, `docs/ARCHITECTURE.md` pour ce qui est
réellement implémenté). Produit dans le cadre du ticket GitHub #4, à partir d'un audit du
dépôt effectué le 2026-09-16. Objectif : permettre à ChatGPT de créer les tickets d'import
suivants sans refaire cet audit.

**Portée** : ce document ne contient et ne déclenche aucun import de contenu. Il cartographie
ce qui existe, ce qui manque, et propose un découpage en tickets.

---

# 0. Mise à jour — mini-cours 01 livré (ticket #10, 2026-09-16)

Le mini-cours 01 Informatique AMPCR (« Architecture générale d'un PC ») est désormais
implémenté (branche `feature/10-informatique-ampcr-mc01-architecture-pc`), avec un chemin
de traçabilité **différent** de celui anticipé au § 2 : ChatGPT a fourni le cahier des
charges pédagogique complet directement dans le corps du ticket GitHub #10 (référentiel
officiel cité : programme 345/2007/249 AMPCR), plutôt que de déposer d'abord un fichier
brouillon séparé (tickets A/C imaginés ci-dessous). Voir
`docs/content_workflow.md`, section « Contenu rédigé à partir d'un cahier des charges »,
pour la règle de traçabilité réellement appliquée (le ticket GitHub fait foi).

Ce qui reste vrai et non résolu : aucun référentiel officiel FWB/AMPCR complet (profil de
formation) n'est déposé dans le dépôt lui-même ; la structure Module=« AMPCR »,
UAA=« MC01 » (§ 4.2 ci-dessous) reste une hypothèse technique, pas une correspondance
officielle confirmée avec des codes FWB. Les tickets B/D (référentiel officiel, cartographie
détaillée) gardent leur pertinence pour fiabiliser cette correspondance au fil des 37
mini-cours suivants.

## Mise à jour — mini-cours 02 livré (ticket #12, 2026-09-16)

« Carte mère, formats et connectiques » (UAA `MC02`, sous le même module `AMPCR`) suit
exactement le même chemin de traçabilité que MC01 (cahier des charges dans le ticket
GitHub, pas de fichier `docs/sources_cours/`). Confirme la réutilisabilité de
l'architecture posée par #10 : même système de blocs, même moteur IA générique (un seul
contexte pédagogique ajouté par cours, `app/ai/context.py`), aucune duplication. Le
complément IA du ticket #10 (génération/correction) est donc validé sur un deuxième cours
sans modification de son code.

## Mise à jour — mini-cours 03 livré (ticket #14, 2026-09-16)

« CPU et mémoire RAM » (UAA `MC03`, sous le même module `AMPCR`) confirme à nouveau la
réutilisabilité de l'architecture #10 sur un troisième cours : même chemin de traçabilité
(cahier des charges du ticket GitHub), même système de blocs, même moteur IA générique —
seule une nouvelle entrée de contexte pédagogique (`PEDAGOGICAL_CONTEXTS["ampcr-mc03"]`) a
été ajoutée, aucune ligne de `app/ai/` (hors `context.py`) modifiée depuis le ticket #10.

---

# 1. Changement de priorité produit

À partir de ce ticket, l'ordre de priorité produit devient :

1. **Informatique — Assistant/Assistante de maintenance PC-réseaux (AMPCR)**
2. **Français — CESS Professionnel**
3. Reste du contenu Mathématiques (MB32 UAA3, MQ32, MQ34) et autres matières (VS007)

MB32 UAA3 (« Statistique et probabilité », prochaine étape indiquée jusqu'ici dans
`docs/current_state.md`) passe donc derrière Informatique et Français. Voir § 9 pour les
autres documents impactés par ce changement.

---

# 2. Méthodologie : distinguer source officielle et brouillon ChatGPT

Deux catégories de matériel existent pour ces deux matières, et ne doivent **jamais** être
confondues :

| Catégorie | Définition | Statut dans Jury Central |
|---|---|---|
| **Source officielle** | Référentiel/profil de formation FWB, ou cours officiel au même format que `docs/sources_cours/CESS/P/Mathématiques/` (`cours.html` + `cours.pdf` + `metadata.yaml`) | Seule base légitime pour qualifier un contenu publié d'« officiel » (voir `docs/PROJECT_RULES.md` § 4-5) |
| **Brouillon ChatGPT** | Suites de cours déjà préparées avec ChatGPT en dehors du dépôt (mini-cours Informatique, 10 cours Français) | Base de **structuration et de révision** uniquement. Ne peut pas être publié tel quel comme contenu officiel tant qu'il n'est pas rapproché d'une source officielle correspondante |

Règle de traçabilité proposée pour la suite (à valider avant le premier import réel, voir
ticket 1 § 7) :

- Les brouillons ChatGPT ne sont **jamais** déposés dans `docs/sources_cours/` (réservé aux
  sources officielles immuables, `docs/PROJECT_RULES.md` § 4). Ils vivent dans un dossier
  séparé, par exemple `docs/sources_chatgpt/<matière>/`, clairement nommé pour ne pas être
  confondu avec les sources officielles.
- `metadata.yaml` gagne un champ explicite `source_type: official` (déjà le cas implicite
  pour Mathématiques) ou `source_type: chatgpt_draft`.
- Un bloc de leçon ou une page publiée construite à partir d'un brouillon ChatGPT sans
  référentiel officiel correspondant doit rester visuellement identifiable comme
  provisoire (statut « brouillon », non « officiel ») tant que la source officielle n'a
  pas été rapprochée.
- Aucun contenu n'est affiché comme correspondant à un référentiel FWB précis sans que ce
  référentiel soit présent dans le dépôt.

---

# 3. Inventaire réel des sources présentes dans le dépôt

Vérifié par recherche exhaustive dans le dépôt (hors `.venv`/`.git`) à la date de ce ticket.

## 3.1 Mathématiques (rappel, hors périmètre de ce ticket)

`docs/sources_cours/CESS/P/Mathématiques/` : 22 UAA sources officielles (`cours.html` +
`cours.pdf` + `metadata.yaml` chacune, `manifest.yaml` au niveau matière), réparties sur
MB32 (3), MQ32 (3), MQ34 (15). Seules MB32 UAA1 et UAA2 sont importées dans l'application
(`app/seed.py`) à ce jour.

## 3.2 Informatique / AMPCR

- **Sources officielles dans le dépôt** : **aucune**. Pas de dossier
  `docs/sources_cours/.../Informatique/`, pas de référentiel FWB AMPCR, pas de
  `metadata.yaml`.
- **Brouillon ChatGPT dans le dépôt** : **aucun fichier**. Le ticket #4 mentionne un
  « mini-cours 04 — Stockage : HDD, SSD SATA et NVMe » (technologies de stockage,
  interfaces, SMART, performances, fiabilité, sauvegarde) à titre d'exemple, mais aucun
  fichier correspondant à cette suite de mini-cours n'est présent dans le dépôt. Cette
  suite existe uniquement « hors du dépôt » selon le ticket.
- **Contenu déjà importé en base** : aucun (`app/seed.py` ne définit que la matière
  Mathématiques ; aucune base `jury_central.db` n'existe dans l'environnement audité).
- **Documentation associée** : aucune mention d'AMPCR dans `docs/` en dehors de ce document
  et de la liste générique « Informatique » de `docs/ROADMAP.md` § VS007.

## 3.3 Français CESS Professionnel

- **Sources officielles dans le dépôt** : **aucune**. Pas de référentiel FWB Français CESS
  P, pas de dossier `docs/sources_cours/.../Français/`.
- **Brouillon ChatGPT dans le dépôt** : **aucun fichier**. Le ticket #4 mentionne une suite
  de 10 cours (fondations lire/écrire, justification/explicitation, recherche
  d'information, résumé, opinion écrite, opinion orale, œuvre, récit/relater, révision
  générale/méthodologie CESS), mais seuls des intitulés sont connus, pas de fichier.
  **Écart à noter** : la liste donnée dans le ticket énumère 9 intitulés pour « une suite de
  10 cours » — soit « fondations lire/écrire » recouvre en réalité deux cours distincts
  (lire, écrire), soit un dixième cours n'est pas nommé. À confirmer dès que les fichiers
  seront fournis (voir ticket 6, § 7).
- **Contenu déjà importé en base** : aucun. Les seules occurrences du mot « Français »
  dans le dépôt sont des noms de matière utilisés comme donnée de test générique dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_quiz_import.py` (CRUD/rejet de
  slug), sans rapport avec un contenu réel.
- **Documentation associée** : aucune, en dehors de la liste générique de
  `docs/ROADMAP.md` § VS007.

## 3.4 Conclusion de l'inventaire

Pour les deux matières prioritaires, le dépôt ne contient **ni source officielle, ni
brouillon ChatGPT, ni contenu déjà publié**. Tout le travail de cadrage ci-dessous part de
la seule description fournie dans le ticket #4 — elle doit être traitée comme une
**intention produit à vérifier**, pas comme un inventaire de fichiers.

---

# 4. Cartographie — Informatique AMPCR (priorité 1)

## 4.1 Ce qui est structurellement réutilisable

La hiérarchie `Subject → Module → UAA → LessonBlock` (`app/models.py`) est générique et ne
contient rien de spécifique aux mathématiques. Le workflow d'import
(`docs/IMPORT_WORKFLOW.md`), le Design System (`docs/UI_GUIDELINES.md`) et le moteur de
quiz sont directement réutilisables sans modification de code pour une matière
Informatique.

## 4.2 Structure proposée (hypothèse, à confirmer par le référentiel officiel)

| Niveau Jury Central | Proposition pour AMPCR | Statut |
|---|---|---|
| Subject | « Informatique » (nom exact à confirmer — l'intitulé officiel FWB pourrait être plus spécifique, ex. lié à l'option AMPCR) | À valider |
| Module | Code(s) de module officiel(s) FWB pour la formation AMPCR (inconnus à ce jour) | Manquant |
| UAA / chapitre | Les « mini-cours progressifs » ChatGPT (ex. mini-cours 04 « Stockage ») pourraient correspondre à des UAA ou à des sous-parties d'UAA, une fois mis en regard du référentiel | Manquant — dépend du référentiel |

Aucun code de module ni découpage en UAA ne peut être fixé sans le référentiel officiel :
poser ces codes maintenant reviendrait à inventer une structure, ce que
`docs/PROJECT_RULES.md` § 11 interdit sans décision produit explicite.

## 4.3 Ce qui est connu (uniquement via la description du ticket #4)

- Mini-cours 04 : « Stockage : HDD, SSD SATA et NVMe » — couvre technologies de stockage,
  interfaces, SMART, performances, fiabilité, sauvegarde.
- La suite est qualifiée de « progressive » — un mini-cours 01, 02, 03 (et probablement
  au-delà de 04) existe donc vraisemblablement, sans que leur contenu soit connu.

## 4.4 Manques identifiés

- Référentiel officiel FWB pour AMPCR (profil de formation / référentiel de compétences).
- Liste complète des mini-cours déjà préparés avec ChatGPT (au moins 4, probablement plus).
- Fichiers sources correspondants (texte des mini-cours), non présents dans le dépôt.
- Correspondance entre chaque mini-cours et une UE/UAA officielle.

---

# 5. Cartographie — Français CESS Professionnel (priorité 2)

## 5.1 Structure proposée (hypothèse, à confirmer par le référentiel officiel)

| Niveau Jury Central | Proposition pour Français CESS P | Statut |
|---|---|---|
| Subject | « Français » | Cohérent avec la convention Mathématiques, à confirmer |
| Module | Code(s) de module officiel(s) FWB Français CESS P (inconnus) | Manquant |
| UAA / chapitre | Les 9-10 cours ChatGPT (fondations lire/écrire, justification/explicitation, recherche d'information, résumé, opinion écrite, opinion orale, œuvre, récit/relater, révision générale/méthodologie CESS) | Manquant — dépend du référentiel |

## 5.2 Manques identifiés

- Référentiel officiel FWB Français CESS Professionnel.
- Clarification du nombre exact de cours (9 intitulés donnés pour « 10 cours », voir § 3.3).
- Fichiers sources des 10 cours ChatGPT, non présents dans le dépôt.
- Correspondance entre chaque cours et une UE/UAA officielle.

---

# 6. Écarts / sources manquantes — synthèse transversale

| Élément | Informatique AMPCR | Français CESS P |
|---|---|---|
| Référentiel officiel FWB dans le dépôt | ❌ Absent | ❌ Absent |
| Brouillon ChatGPT dans le dépôt | ❌ Absent (décrit dans le ticket, aucun fichier) | ❌ Absent (décrit dans le ticket, aucun fichier) |
| Structure Subject/Module/UAA officielle | ❌ Inconnue | ❌ Inconnue |
| Contenu déjà publié dans l'application | ❌ Aucun | ❌ Aucun |

**Rien ne peut être importé immédiatement pour ces deux matières.** Toute suite donnée à ce
ticket dépend d'abord du dépôt, par l'utilisateur, des fichiers concernés dans le dépôt.

---

# 7. Ordre recommandé d'intégration et tickets atomiques proposés

Chaque ticket ci-dessous est conçu pour être petit et vérifiable, avec ses propres critères
d'acceptation. Numérotation indicative (à reprendre par ChatGPT lors de la création réelle
des tickets GitHub) ; l'ordre reflète les dépendances.

### Ticket A — Convention de traçabilité source officielle / brouillon ChatGPT

- **Objectif** : formaliser dans `docs/content_workflow.md` (ou `docs/IMPORT_WORKFLOW.md`)
  la distinction officielle/brouillon décrite au § 2 : emplacement dédié aux brouillons
  ChatGPT, champ `source_type` dans `metadata.yaml`, règle d'affichage « brouillon » côté
  contenu tant qu'aucune source officielle n'est rattachée.
- **Justification** : prérequis transverse aux deux matières, évite de le refaire deux fois.
- **Périmètre** : documentation uniquement, aucun changement de modèle de données.
- **Critères d'acceptation** : convention documentée et validée avant le premier dépôt de
  brouillon (ticket C).
- **Dépendances** : aucune.

### Ticket B — Obtenir et déposer le référentiel officiel AMPCR

- **Objectif** : déposer le référentiel/profil de formation FWB AMPCR dans le dépôt, au
  même niveau de rigueur que les sources Mathématiques.
- **Justification** : sans lui, aucune structure Module/UAA ne peut être validée pour
  Informatique.
- **Périmètre** : dépôt de fichier(s) fourni(s) par l'utilisateur ; pas d'écriture de
  contenu pédagogique.
- **Critères d'acceptation** : document officiel présent et référencé dans le dépôt.
- **Dépendances** : fourniture du document par l'utilisateur (bloquant, hors main de Claude).

### Ticket C — Déposer les brouillons ChatGPT Informatique AMPCR

- **Objectif** : déposer la suite de mini-cours déjà préparée avec ChatGPT dans
  l'emplacement dédié (ticket A), avec un inventaire des mini-cours disponibles.
- **Justification** : rend le matériel exploitable par Claude sans le faire passer pour une
  source officielle.
- **Périmètre** : dépôt de fichiers fournis par l'utilisateur, aucune réécriture.
- **Critères d'acceptation** : mini-cours listés et déposés, distincts de
  `docs/sources_cours/`.
- **Dépendances** : ticket A ; fourniture des fichiers par l'utilisateur (bloquant).

### Ticket D — Cartographie détaillée Informatique AMPCR

- **Objectif** : remplacer la structure « hypothèse » du § 4.2 par une cartographie réelle
  (modules/UAA officiels, correspondance avec chaque mini-cours, couverture du programme,
  écarts restants).
- **Justification** : nécessaire avant tout import réel pour éviter une structure inventée.
- **Périmètre** : documentation, extension de ce document ou nouveau document dédié.
- **Critères d'acceptation** : chaque mini-cours disponible est rattaché à une UAA
  officielle ou signalé comme non couvert par le référentiel.
- **Dépendances** : tickets B et C.

### Ticket E — Tranche verticale pilote Informatique AMPCR

- **Objectif** : importer une première UAA/chapitre complet (candidat naturel : le
  mini-cours 04 « Stockage », déjà décrit) selon `docs/REFERENCE_UAA.md`.
- **Justification** : valide la cartographie sur un cas réel avant de généraliser.
- **Périmètre** : une seule tranche verticale (cours, quiz, éventuel générateur, tests,
  documentation), marquage clair officiel/brouillon selon le ticket A.
- **Critères d'acceptation** : ceux de `docs/IMPORT_WORKFLOW.md` § Critères de réussite.
- **Dépendances** : ticket D.

### Ticket F — Obtenir et déposer le référentiel officiel Français CESS P

- Symétrique au ticket B, pour Français.

### Ticket G — Déposer les 10 cours ChatGPT Français CESS P

- Symétrique au ticket C. Inclut la clarification du nombre exact de cours (§ 3.3, § 5.2).

### Ticket H — Cartographie détaillée Français CESS P

- Symétrique au ticket D. Dépend de F et G.

### Ticket I — Tranche verticale pilote Français CESS P

- Symétrique au ticket E. Dépend de H. Candidat naturel : le premier cours de la suite
  (« fondations lire/écrire »), à confirmer une fois la cartographie réelle disponible.

### Après I

Reprise du reste des mathématiques (MB32 UAA3, MQ32, MQ34 — VS004/VS005/VS006 de
`docs/ROADMAP.md`), puis matières suivantes de VS007, selon l'ordre déjà documenté.

---

# 8. Ce qui peut démarrer immédiatement vs ce qui attend l'utilisateur

| Peut démarrer sans attendre | Nécessite d'abord une action de l'utilisateur |
|---|---|
| Ticket A (convention de traçabilité, documentation) | Ticket B (référentiel officiel AMPCR) |
| — | Ticket C (brouillons ChatGPT Informatique) |
| — | Ticket F (référentiel officiel Français) |
| — | Ticket G (brouillons ChatGPT Français) |

Tous les tickets de cartographie (D, H) et d'import (E, I) dépendent en cascade des dépôts
de fichiers ci-dessus. **Aucun import de contenu réel n'est possible avant qu'au moins un
brouillon ChatGPT ou une source officielle soit effectivement présent dans le dépôt.**

---

# 9. Impact sur la documentation existante

- `docs/current_state.md` (« Priorité actuelle » / « Prochaine étape ») et
  `docs/ROADMAP.md` sont mis à jour dans ce même ticket pour refléter le nouvel ordre de
  priorité (§ 1) et renvoyer vers ce document — voir le commit associé.
- Ce document devra être complété (§ 4, § 5) dès que les tickets B/C (Informatique) puis
  F/G (Français) auront livré de la matière réelle à cartographier — mise à jour plutôt que
  nouveau document, conformément à `docs/PROJECT_RULES.md` § 9.
