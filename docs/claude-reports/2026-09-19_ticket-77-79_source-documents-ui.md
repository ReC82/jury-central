# Ticket #77 + #79 — Français : SourceDocument visible, accessible pendant la question ET la correction

**Branche** : `fix/77-79-french-source-documents`, réutilise l'intégralité du travail de
`fix/77-french-hidden-source-document` (branché directement dessus, sans duplication) puis
l'étend. Base `develop` (a6739ed, PR #61 mergée). Aucun merge, aucun déploiement effectué.

---

# 1. Contrat SourceDocument — état final

| Type | `SourceDocumentRequirement` | Cas réels dans la banque Français |
|---|---|---|
| `document_analysis` | `REQUIRED` (inchangé) | 4 — absent = question **rejetée** à la validation |
| `source_comparison` | `MULTIPLE` (inchangé) | 4 — 2 documents, étiquetés A/B dans l'ordre authored |
| `long_answer` | `OPTIONAL` (#77) | 3 (1 fixé par #77 + 2 par l'audit #79) |
| `short_answer` | `OPTIONAL` (**#79**) | 20 |
| `vocabulary` | `OPTIONAL` (**#79**) | 5 |
| `classification` | `OPTIONAL` (**#79**) | 2 |
| `diagnostic` / `procedure` / `troubleshooting` | `NONE` (inchangé) | 0 — jamais généralisés, aucun cas réel trouvé |

`document_analysis`/`source_comparison` étaient déjà corrects. `long_answer` avait été
étendu par #77 pour UN cas réel (question id=170). L'audit systématique de #79 (§ 4) a
révélé que le même problème touchait en réalité **29 questions supplémentaires**, de 3
types différents (`short_answer`, `vocabulary`, `classification`) qui disaient
« D'après le texte »/« Selon le texte »/etc. sans aucun rattachement structuré — le texte
n'était jamais montré à l'élève. Ces 3 types ont donc reçu le même traitement que
`long_answer` (#77) : un champ `source_document_version_id` optionnel, jamais requis.

`diagnostic`/`procedure`/`troubleshooting` (types Informatique) : 0 cas réel trouvé dans
toute la base — **pas généralisés**, conformément à la consigne du ticket.

---

# 2. Source unique de vérité — élève et IA voient toujours le même document

Le principe posé par #77 (`_referenced_document_ids`, dérivé du PAYLOAD PUBLIC, jamais du
`content_json` brut) est réutilisé tel quel — aucune nouvelle divergence possible entre ce
que voit l'élève (`build_question_display`) et ce que reçoit le correcteur IA
(`_document_contexts_for`).

**Nouveau pour #79** : l'ORDRE des documents est désormais aussi une invariant garanti.
`resolve_documents_in_order` (session_service.py) résout les identifiants dans l'ordre où
la question les référence (ex. `[main, second]`), jamais par un tri par id — sinon
l'étiquetage « Document A »/« Document B » d'une `source_comparison` pourrait s'inverser
si le second document cité dans le prompt a un id numériquement plus petit que le premier.
`document_label(question_type, index)` (nouvelle fonction partagée) produit cet
étiquetage une seule fois, réutilisé par la page de question ET les résultats/export.

Vérifié par test (session exam réelle, tous types mélangés) :
`AI_SOURCE_IDS == STUDENT_SOURCE_IDS`, systématiquement.

---

# 3. Audit de la banque Français (§ 4) — 40 questions, 38 avec un rattachement structuré

Recherche systématique (script isolé, `DATABASE_URL` temporaire, jamais la base réelle)
des formulations listées au ticket dans les 40 prompts du corpus :
« D'après le texte », « Selon le texte », « En t'appuyant sur le texte »,
« Identifie un passage », « Compare le texte », « texte principal », « second texte »,
« document ».

**Avant #79** : 9/40 questions avec un rattachement structuré (4 document_analysis + 4
source_comparison + 1 long_answer, ce dernier fixé par #77).

**29 questions supplémentaires corrigées** directement dans `francais_bank.py` (jamais par
une inférence runtime par regex — corrigé à la source, comme demandé) :
- 7 dans la section « smartphone » (document `main`)
- 9 dans la section « numérique au quotidien » (document `digital_life`)
- 8 dans la section « formation professionnelle » (document `training`)
- 5 dans la section « débat programmation » (document `coding_debate`)

**Total : 38/40 questions avec un document.** Les 2 questions restantes sont des questions
d'opinion qui citent l'affirmation à juger **en entier** dans leur propre prompt (ex.
« Es-tu d'accord avec l'affirmation que le smartphone est « ni un ennemi ni un allié
absolu » ? ») — auto-suffisantes par construction, aucun document n'est nécessaire pour y
répondre. Décision documentée dans le code (commentaire à côté de chaque question laissée
sans document).

Vérifié par un test qui aurait échoué avant le fix (`test_no_francais_question_with_a_
text_reference_phrase_lacks_a_source_document`) et qui continuera à détecter toute
régression future dans `francais_bank.py`.

---

# 4. UI pendant la question (§ 5-6)

Chaque document référencé affiche désormais :

```
📄 Document de référence : <titre>        [ Voir le document ]  [ Ouvrir dans un nouvel onglet ]
```

(ou « Document A »/« Document B » pour `source_comparison`, jamais mélangés). Le bouton
« Voir le document » déplie un panneau intégré sur la même page (texte complet, hauteur
bornée `max-height: 50vh`, défilement vertical, mobile-friendly — repris du panneau #47,
scindé par document plutôt qu'en accordéon Bootstrap partagé pour permettre plusieurs
panneaux ouverts indépendamment). « Ouvrir dans un nouvel onglet » pointe vers la nouvelle
route `/documents/{id}` avec `target="_blank" rel="noopener"`.

---

# 5. Route de lecture seule `/documents/{version_id}` (§ 7)

Nouvelle route (`app/v1/routes_sessions.py::view_source_document`), gabarit dédié
(`v1_document_view.html`) :
- Titre + texte complet uniquement.
- Aucun feedback, aucune solution, aucune information sur quelle(s) question(s) le
  référencent.
- Authentification requise (mêmes règles que le reste du parcours V1) — un document est un
  contenu pédagogique partagé, pas une donnée propre à une session, donc pas de
  vérification de propriété au-delà de « être connecté ».
- 404 explicite si l'identifiant n'existe pas.
- Bouton « Retour à l'accueil », aucune logique `window.close()` fragile.

---

# 6. Résultats / correction (§ 8-9)

L'écran de résultats et l'export Markdown affichent désormais, pour chaque question
documentée :

```
Document(s) de référence :
📄 Document de référence : <titre>    [ Voir le document ]  [ Ouvrir dans un nouvel onglet ]
```

avec le même panneau intégré (texte complet, borné, défilable) que pendant la question —
l'élève peut relire le texte tout en examinant sa réponse, l'attendu, les erreurs et le
feedback, sans changer d'onglet ni perdre son contexte. Pour `source_comparison`, les deux
documents restent étiquetés A/B et ouvrables indépendamment, jamais mélangés (même
`document_label`/`resolve_documents_in_order` que côté question).

`_build_results_rows` (factorisée entre l'écran HTML et l'export, ticket #62) résout
désormais les documents une seule fois par session (pas de requête N+1 par question) et
expose `{id, label, title, content_text}` par référence.

---

# 7. Export Markdown (§ 11)

```
Document(s) de référence :

- Document de référence : <titre>
```

(ou `Document A`/`Document B` pour une comparaison). Titres/références uniquement, jamais
le texte intégral redupliqué sous chaque question — décision MVP explicitement permise par
le ticket (« Sinon les titres/références suffisent »).

---

# 8. Print / PDF (§ 12)

La ligne de référence (« 📄 Document de référence : titre ») reste visible à l'impression
(hors `d-print-none`) ; seuls les boutons interactifs (« Voir le document », « Ouvrir dans
un nouvel onglet ») sont masqués à l'impression — inutiles sur papier. Le texte complet du
panneau reste replié par défaut à l'impression (pas de duplication de 1000 mots sous
chaque question), conformément à l'instruction du ticket.

---

# 9. Rattachement au cours (§ 13) — données seulement, aucun bouton

`_build_results_rows` expose désormais `course_title`/`course_slug` par ligne de résultat
(dérivés de `SessionQuestion.question_version.question.uaa`). **Aucun bouton « Relire le
cours » n'a été ajouté** — cette UI appartient explicitement à un futur ticket (#74).
Vérifié par test que la donnée est bien présente et qu'aucun bouton n'apparaît dans le
HTML actuel.

---

# 10. Tests

Trois fichiers, aucun appel OpenAI réel (`FakeAIProvider` partout) :

- `tests/test_ticket77_hidden_source_document.py` (14 tests, hérités de #77, mis à jour
  pour la nouvelle UI — classes CSS, structure de l'export).
- `tests/test_ticket79_source_document_ui.py` (**15 nouveaux tests**) : contrat par type,
  rejet `document_analysis` sans document, audit systématique de la banque, étiquetage
  A/B de `source_comparison`, route `/documents/{id}` (contenu, auth, 404), liens nouvel
  onglet (question ET résultats), scénario complet § 15 (texte visible avant réponse puis
  encore accessible aux résultats), rattachement au cours sans bouton.
- `tests/test_ticket47_francais_v1.py` : 2 assertions obsolètes mises à jour (nombre de
  questions référençant un document : 9 → 38 ; classes CSS de l'ancien accordéon).

Suite complète du dépôt : **1094 passed**. Ruff : **0 nouvelle erreur** (36 pré-existantes
sur `develop`, dans des fichiers jamais touchés par ce ticket, confirmé par comparaison
directe).

---

# 11. Fichiers modifiés

- `app/v1/question_types.py` — `ShortAnswerContent`/`VocabularyContent`/
  `ClassificationContent` gagnent un `source_document_version_id` optionnel + `OPTIONAL`.
- `app/v1/session_service.py` — `resolve_documents_in_order`, `document_label`,
  `QuestionDisplay.source_document_labels`.
- `app/v1/routes_sessions.py` — route `/documents/{version_id}`, `_build_results_rows`
  enrichie (documents complets + `course_title`/`course_slug`), export Markdown mis à
  jour.
- `app/v1/francais_bank.py` — 29 questions corrigées (rattachement document manquant).
- `app/templates/v1_session_question.html` — panneau document avec boutons.
- `app/templates/v1_session_results.html` — même traitement pour les résultats.
- `app/templates/v1_document_view.html` — nouveau, route de lecture seule.
- `tests/test_ticket79_source_document_ui.py` — nouveau, 15 tests.
