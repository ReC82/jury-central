# Audit UX/technique — MC01 et transformation en expérience interactive générique

**Date** : 2026-09-16
**Demandé par** : ChatGPT (chef de projet), suite à la validation visuelle du mini-cours 01 (MC01).
**Type** : audit, aucune modification de code.
**Portée** : `/srv/jury-central`, branche `develop` (état post-merge tickets #10, #12, #14).

Aucune modification effectuée pour cet audit (lecture seule) : `app/models.py`, `app/quiz.py`,
`app/exercise_blocks.py`, `app/ai_exercise_blocks.py`, `app/ai/*`, `app/practice.py`,
`app/templates/uaa_detail.html`, `app/templates/_cards.html`,
`app/static/js/{design_system,exercise,quiz,value_table,rich_content,progress,ai_exercise}.js`,
`app/static/css/design-system.css`, `docs/{UI_GUIDELINES,EXERCISE_TYPES,ai_exercise_engine}.md`,
`docs/components/{ExerciseCard,ExamCard}.md`.

---

## Contexte de la demande

La validation visuelle du MC01 montre que le contenu pédagogique est globalement correct, mais
que l'expérience utilisateur ressemble trop à un document de cours statique. L'objectif de Jury
Central est une plateforme d'apprentissage interactive. Il a été demandé de déterminer
précisément comment transformer MC01 en expérience interactive réutilisable pour tous les futurs
cours, sans coder quoi que ce soit à ce stade.

Expérience cible demandée (résumé) :
1. Théorie lisible avec interactions légères (sections repliables, schémas, encadrés, navigation
   rapide, progression).
2. Exercices éditoriaux transformés en vraies activités (réponse courte, réponse rédigée,
   classement, remise en ordre, association, choix multiple/vrai-faux si pertinent).
3. Correction en deux niveaux : locale déterministe quand pertinent, IA pour les réponses libres.
4. Génération IA affichée comme une vraie interface (difficulté → génération → réponse →
   correction → nouvel exercice), sans rechargement complet si possible.
5. Examen final réellement remplissable, correction jamais visible avant validation finale,
   score /20 puis détail par question.
6. Progression utilisateur générique (Théorie ✓, Exercices X/Y, Examen Z/20).
7. UX mobile soignée (gros contrôles, pas de débordement horizontal, cartes lisibles).
8. Mode impression essentiellement statique, mode web interactif.
9. Architecture générique (pas de gabarit par cours type `mc01_exercise_form.html`).

---

## A. Pourquoi MC01 est actuellement statique

Trois familles de contenu, trois niveaux d'interactivité réels très différents :

| Élément | Implémentation actuelle | Interactif ? |
|---|---|---|
| Cours (théorie) | Bloc `MARKDOWN`, rendu Jinja + MathJax | Lecture seule, avec barre de progression de lecture (`design_system.js::initLessonProgress`) |
| Exercices générés (déterministes) | Bloc `GENERATED_EXERCISE` → générateur Python | **Déjà pleinement interactif** (`exercise.js`, AJAX, sans rechargement) |
| Exercice IA (génération/correction) | Bloc `AI_EXERCISE` (#10) | **Déjà pleinement interactif** (`ai_exercise.js`, AJAX, sans rechargement) |
| Quiz groupé | Bloc `QUIZ` avec `group` | **Déjà pleinement interactif** (`quiz.js::quiz-run`, parcours paginé, score) |
| **Exercices éditoriaux** (les 12 par cours) | Bloc `MARKDOWN`, prose `## Exercice N — ...` + `**Correction :**` | **Statique** : `splitExerciseCorrections()` (`design_system.js`) masque/affiche un bloc de HTML déjà rendu — aucune saisie, aucune vérification serveur, aucun score |
| **Examen final** | Bloc `MARKDOWN`, questions seules ; corrigé dans un second bloc `is_published=False` | **Statique** : aucune zone de réponse, aucune interaction ; la non-visibilité du corrigé est obtenue en ne l'envoyant simplement jamais au navigateur, pas par un flux de correction différée |

**Cause précise** : les exercices éditoriaux et l'examen ne sont pas un type de donnée structuré
— ce sont du texte Markdown dans lequel un heuristique JS repère des motifs (`## Exercice`,
`**Correction :**`) pour cacher/révéler du HTML déjà généré côté serveur. Il n'existe ni saisie,
ni endpoint de vérification, ni score pour ces deux familles.

**Ce n'est pas un oubli isolé** : le projet l'avait déjà anticipé et documenté comme dette
volontaire :
- `docs/UI_GUIDELINES.md` § Mini-tests décrit déjà la cible demandée ici (*« une question à la
  fois, navigation Précédent/Suivant/Terminer »*), jamais implémentée.
- `docs/components/ExamCard.md` § Limite connue : *« Le mini-test reste un seul bloc à
  correction masquée globalement, pas un parcours paginé... évolution volontairement
  reportée »*.
- `docs/components/ExerciseCard.md` § Limite connue : *« pas de vérification serveur...
  nécessiterait une réponse structurée par exercice... explicitement hors périmètre »*.

Autrement dit : l'architecture pour rendre ça interactif existe déjà et fonctionne (preuve :
exercices générés, IA, quiz), elle n'a simplement pas encore été appliquée aux exercices
éditoriaux et à l'examen.

---

## B. Ce qui existe déjà et est directement réutilisable

1. **Pattern « bloc → config JSON → route de vérification → widget JS sans rechargement »**,
   déjà implémenté 3 fois à l'identique (value_table, quiz, ai_exercise) : `*BlockConfig`
   (dataclass, `to_json`/`from_json`), route `POST /practice/api/...`, réponse jamais porteuse
   de la réponse correcte avant validation.
2. **`quiz-run`** (`quiz.js`) : parcours paginé, une question à la fois, score cumulé, bouton
   recommencer — **exactement** le patron demandé au point 5 (examen), à un détail près (voir C).
3. **`renderRichContent()`** (`rich_content.js`) : point d'entrée unique pour injecter du HTML
   déjà rendu serveur (tableaux, MathJax) sans dupliquer de logique — déjà utilisé partout,
   réutilisable tel quel pour tout nouveau widget.
4. **Moteur IA générique** (`app/ai/`) : provider abstrait, contexte pédagogique borné par cours,
   sortie JSON stricte, signature HMAC anti-triche. Déjà branché et fonctionnel pour la
   génération/correction d'exercices IA (#10). **Le widget de génération demandé au point 4 du
   ticket est déjà quasiment celui qui existe** (difficulté → génération → réponse → correction
   → nouvel exercice, tout en AJAX, sans rechargement) — écart réel très réduit, voir C.
5. **`design_system.js::enhanceRichContent`** : tableaux responsives automatiques
   (`.table-responsive`), déjà conforme au point 7 (mobile, pas de débordement horizontal).
6. **Impression** : convention `.d-print-none` (Bootstrap) déjà utilisée systématiquement sur
   tous les contrôles interactifs existants — le point 8 du ticket est déjà une convention
   établie, à répliquer sur les nouveaux composants, pas à inventer.
7. **`progress.js`** : mécanisme de progression **local** (localStorage), déjà générique par UAA
   (todo/in_progress/done), déjà agrégeable (`aggregateStatus`). Base réutilisable pour le
   point 6, mais aujourd'hui **uniquement au niveau UAA entière** — aucun détail par
   exercice/question.
8. **Sécurité déjà acquise** : `app/answer_checking.py` (comparaison serveur sans `eval()`),
   signature HMAC des exercices IA (`app/ai/integrity.py`), contexte pédagogique borné
   (`app/ai/context.py`) — tout ceci se transpose directement aux nouveaux types d'exercices
   sans rien réinventer.

---

## C. Ce qui manque réellement pour l'expérience décrite

| Besoin du ticket | Manque précis |
|---|---|
| Exercices éditoriaux interactifs | Aucune structure de données ; aucun type d'activité (réponse courte, classement, ordre, association...) ; aucune route de vérification ; aucun stockage de réponse candidate |
| Correction locale déterministe | N'existe que pour `value_table` (cellules) et `quiz` (choix/numérique) — rien pour classement/ordre/association |
| Correction IA d'exercice éditorial (réponse libre fixe) | Le provider IA actuel corrige un exercice **généré par lui-même** (statement signé au moment de la génération) ; il ne sait pas encore corriger un énoncé **fixe, éditorial, stocké en base** — flux légèrement différent (voir E/F) |
| Génération IA « vraie interface » | **Déjà fait à ~90 %** (`ai_exercise.js`) : difficulté, bouton générer, affichage in-page, réponse, correction, tout sans rechargement. Écart réel : aucun bouton « Nouvel exercice » distinct aujourd'hui (il faut re-choisir la difficulté et re-cliquer « Générer », ce qui revient au même en pratique) — ajustement mineur, pas une refonte |
| Examen interactif /20 | Aucune zone de réponse, aucun flux de soumission groupée, aucune correction différée jusqu'à validation finale — à construire entièrement, mais sur le patron `quiz-run` adapté (voir G) |
| Progression fine (Exercices 8/12, Examen 14/20) | `progress.js` ne connaît que le statut de l'UAA entière — aucune notion d'exercice individuel ni de score d'examen |
| Sections repliables / navigation rapide | Bootstrap (déjà chargé) fournit le composant *Collapse* clé en main ; aucune utilisation actuelle dans les templates de cours |
| Modèle générique (point 9) | Chaque famille d'exercice a son propre `*BlockConfig` (`ExerciseBlockConfig`, `AIExerciseBlockConfig`) mais rien qui couvre les exercices éditoriaux structurés |

---

## D. Modèle générique proposé pour les exercices interactifs

Respecte exactement la convention déjà en place (`app/exercise_blocks.py::ExerciseBlockConfig`,
`app/ai_exercise_blocks.py::AIExerciseBlockConfig` : dataclass → `to_json`/`from_json`,
représentation publique sans réponse, mêmes conventions de nommage `app/<domaine>_blocks.py`).

Proposition : **un seul type de bloc générique**, par exemple `BlockType.EDITORIAL_EXERCISE`,
dont le contenu JSON est une **liste** d'items (un bloc = plusieurs exercices, comme
aujourd'hui) :

```
EditorialExerciseBlockConfig
  mode: "practice" | "exam"        # practice = correction immédiate par item ; exam = correction différée à la soumission finale
  items: [ EditorialExerciseItem ]

EditorialExerciseItem
  exercise_id: str                  # stable, pour la progression et la correction
  type: "short_answer" | "long_answer" | "single_choice" | "true_false"
        | "classification" | "ordering" | "matching"
  prompt: str                       # markdown, rendu serveur comme partout ailleurs
  points: float                     # 1 par défaut pour un exercice, barème libre pour l'examen
  # Selon le type — jamais envoyé au client avant correction :
  expected_answer: str | None       # réponse rédigée attendue / barème (short_answer, long_answer)
  choices: list[str] | None         # single_choice / true_false
  correct_choice: int | None
  categories: list[str] | None      # classification
  items_to_sort: list[str] | None   # ordering / classification / matching (le contenu, pas la solution)
  correct_solution: ... | None      # forme selon le type, jamais publique
  ai_context_key: str | None        # obligatoire pour short_answer/long_answer si correction IA voulue
```

C'est très exactement la forme `{type, prompt, expected_answer/rubric, points, ai_context}`
esquissée par ChatGPT, adaptée aux conventions existantes (suffixe `BlockConfig`, séparation
représentation publique/complète déjà systématique dans le projet).

**Un exercice éditorial = `mode: "practice"` (correction immédiate, par item). L'examen = le
même modèle avec `mode: "exam"`** (correction différée, agrégée). Un seul moteur, une seule UI
de rendu par type d'activité, deux comportements de timing de correction pilotés par un simple
flag — c'est ce qui évite d'avoir un second modèle de données pour l'examen (donc aucun
`mc0X_exam.html`, conforme au point 9 de la demande).

---

## E. Fonctionnement proposé — correction locale déterministe

Pour `single_choice`, `true_false`, `classification`, `ordering`, `matching` : mêmes principes
que `value_table`/`quiz` déjà en place.

- Nouveau `app/editorial_exercise.py` (nom à valider), miroir de `app/value_table.py` : une
  fonction `check_editorial_answer(item_config, submitted_answer) -> CorrectionResult` par
  famille de type, comparaison normalisée (pas d'`eval()`, réutilise au besoin
  `app/answer_checking.py` pour la normalisation texte).
- Route `POST /practice/api/editorial/{block_id}/verify` — payload `{exercise_id, answer}` (la
  forme d'`answer` dépend du type : index pour choix, liste réordonnée pour ordering, mapping
  pour matching). Le serveur recharge toujours la configuration complète depuis
  `LessonBlock.content` (jamais confiée au client), exactement comme
  `/api/quiz/{block_id}/verify` aujourd'hui.
- Réponse : `{correct, correct_answer, explanation, explanation_html}` — jamais envoyée avant cet
  appel.
- Widgets JS : un fichier par famille d'interaction (`ordering.js`, `matching.js`...) **ou** un
  seul `editorial_exercise.js` avec une fonction de construction par `type` — cohérent avec le
  principe « un composant générique par type d'activité », pas un template par cours.

---

## F. Fonctionnement proposé — correction IA

Pour `short_answer`/`long_answer` : réutilise **le même provider**, **la même interface
`AIProvider`**, **le même schéma JSON strict** qu'aujourd'hui (`app/ai/provider.py`,
`app/ai/prompts.py`) — aucun second moteur.

Différence clé avec le flux existant (`/api/ai/correct`, pensé pour un exercice **généré** par
l'IA elle-même) : ici l'énoncé et le barème sont **fixes, éditoriaux, déjà stockés côté
serveur**. Pas besoin de jeton HMAC client — le serveur charge lui-même
`prompt`/`expected_answer` depuis `LessonBlock.content` à partir de `(block_id, exercise_id)`,
ce qui est **plus simple et plus sûr** que le cas génération (rien à faire confirmer par le
client).

- Nouvelle route `POST /practice/api/editorial/{block_id}/correct` — payload
  `{exercise_id, answer}` uniquement.
- Extension mineure et rétrocompatible de `app/ai/provider.py::correct_answer` /
  `app/ai/prompts.py::build_correct_messages` : accepter un `rubric: str | None` optionnel (le
  `expected_answer` éditorial), en plus du contexte pédagogique déjà borné par cours — même
  appel réseau, même schéma de sortie (`AICorrectionResult`), aucun nouveau type d'appel
  OpenAI.
- Réponse candidate toujours traitée comme donnée délimitée (déjà acquis,
  `app/ai/prompts.py`).

---

## G. Fonctionnement proposé — examen interactif /20

Adaptation directe de `quiz-run`, avec la différence essentielle demandée : **aucune correction
avant la validation finale**.

1. Rendu : les 10 questions (mode `exam`) s'affichent **toutes**, chacune avec sa zone de
   réponse (texte, ou contrôle du type approprié) — pas de pagination stricte nécessaire ici
   puisque rien n'est corrigé en cours de route (contrairement à `quiz-run` où paginer sert à
   cacher les questions suivantes ; ici on peut choisir pagination **ou** défilement continu, à
   trancher avec ChatGPT).
2. Les réponses restent en mémoire côté client (état JS du widget), **jamais transmises avant
   la fin**.
3. Bouton unique **« Terminer et corriger l'examen »** → un seul appel
   `POST /practice/api/exam/{block_id}/submit` avec `{answers: [{question_id, answer}, ...]}`.
4. Le serveur charge le bloc examen **et** le bloc corrigé (`is_published=False`, déjà en base,
   jamais exposé ailleurs), corrige chaque question (déterministe si le type s'y prête, sinon
   IA via le mécanisme de F — un appel IA par question dans une première version, simple et
   déjà éprouvé ; regroupement en un seul appel IA multi-questions envisageable en optimisation
   ultérieure), et renvoie `{score, max_score, results: [{question_id, points,
   submitted_answer, correct_answer, explanation}, ...]}` en une seule réponse.
5. Le front affiche alors le score puis le détail par question — jamais avant cet appel unique.
   C'est structurellement impossible de fuiter une correction en cours de route puisque le
   serveur ne renvoie rien avant la soumission complète.

---

## H. Gestion proposée de la progression

Le modèle actuel (`progress.js`, localStorage, clé par slug d'UAA, 3 états) permet déjà
l'affichage demandé **si on enrichit la structure stockée**, sans rien casser :

```
{
  "ampcr-mc01": {
    "status": "in_progress",              // existant, inchangé
    "theory_read": true,                   // nouveau, dérivé de la barre de lecture existante
    "exercises_done": ["ex1","ex3","ex7"], // nouveau, rempli par les widgets à chaque correction réussie/tentée
    "exam": { "score": 14, "max": 20, "completedAt": "..." }  // nouveau
  }
}
```

- Chaque widget interactif (exercice éditorial, exercice IA, examen) appelle une petite API
  commune ajoutée à `progress.js` (ex. `recordExerciseAttempt(uaaSlug, exerciseId)`,
  `recordExamResult(uaaSlug, score, max)`) après une correction — cohérent avec le principe « un
  seul endroit qui gère la progression », pas une logique dupliquée par composant.
- Affichage : un petit résumé générique en tête d'UAA (Théorie / Exercices X sur Y / Examen
  Z/20), calculé à partir de `uaa.lesson_blocks` (le total d'exercices/points est connu côté
  serveur au rendu de la page, transmis en attribut `data-*`, comme le fait déjà `quiz-run` avec
  `data-questions`).
- **Reste volontairement client-side (localStorage)** : cohérent avec l'absence actuelle de
  comptes utilisateurs (`docs/admin.md`, « Évolutions prévues »). Persistance serveur
  multi-appareil = évolution future distincte, à ne pas mélanger à ce chantier.

---

## I. UX mobile

Le socle est déjà largement conforme (Bootstrap 5 + `design-system.css` existants) :
- Boutons : classes Bootstrap déjà utilisées (`btn`, `btn-sm`) — à vérifier au cas par cas que
  les nouveaux contrôles n'utilisent pas `btn-sm` pour les actions principales (préférer taille
  standard sur mobile).
- Zones de saisie : `form-control`/`textarea` déjà pleine largeur par défaut ; les `max-width`
  inline existants (ex. `style="max-width: 320px"`) sont des **plafonds**, pas des largeurs
  fixes — sans risque de débordement.
- Tableaux : déjà systématiquement enveloppés (`.table-responsive`, `enhanceRichContent`) —
  nouveaux composants (classement/association) à concevoir nativement en cartes/listes
  empilables plutôt qu'en tableau large, pour éviter d'avoir à les envelopper après coup.
- Aucun nouveau composant ne doit introduire de contrôle `<10px` ni de survol obligatoire
  (glisser-déposer souris uniquement) — pour `ordering`/`matching`, prévoir une interaction
  tactile simple (boutons ↑/↓ ou sélection-puis-association plutôt qu'un drag-and-drop pur),
  plus robuste sur mobile que le drag-and-drop.

---

## J. Découpage en tickets recommandé

Ordre proposé (dépendances explicites) :

1. **Modèle générique + moteur de correction locale** — `EditorialExerciseBlockConfig`,
   `BlockType.EDITORIAL_EXERCISE`, types `single_choice`/`true_false`/`short_answer` (les plus
   simples), route `/verify`, widgets JS de base, migration **d'un seul cours pilote** (MC01)
   vers ce format. *(Dépendance : aucune.)*
2. **Types d'interaction avancés** — `classification`, `ordering`, `matching` (UI + correction
   locale). *(Dépend de 1.)*
3. **Correction IA des exercices éditoriaux** — extension `rubric` du provider existant, route
   `/correct`, types `long_answer`. *(Dépend de 1, réutilise le moteur IA de #10 sans le
   modifier structurellement.)*
4. **Examen interactif** — modèle `mode: "exam"`, route `/exam/{block_id}/submit`, correction
   différée agrégée. *(Dépend de 1 et 3.)*
5. **Progression enrichie** — extension `progress.js`, résumé Théorie/Exercices/Examen.
   *(Dépend de 1 et 4 pour les événements à enregistrer.)*
6. **Polish théorie** — sections repliables (Bootstrap Collapse), navigation rapide générée
   depuis les titres de blocs. *(Indépendant, peut être fait en parallèle.)*
7. **Migration de contenu** — reformuler les exercices/examens **déjà écrits** de MC01 à MC04
   dans le nouveau format structuré (travail éditorial, coordonné avec ChatGPT ; ne redéfinit
   aucune règle pédagogique, seulement la structuration technique). *(Dépend de 1–4 ;
   probablement un ticket par cours ou groupé.)*
8. **Admin** — formulaire dédié pour créer/éditer un bloc `EDITORIAL_EXERCISE` (aujourd'hui tout
   est écrit dans `app/seed.py`) — non bloquant pour les tickets 1–7, à faire quand plusieurs
   cours en dépendent.

---

## Statut

Audit terminé. Aucun fichier de code modifié, aucun commit. En attente d'arbitrage de ChatGPT
sur le découpage ci-dessus (notamment : pagination vs défilement continu pour l'examen au point
G, et séquencement exact des tickets 1 à 8).
