# Phase 7 — Audit qualité des questions Informatique réellement générées

**Branche :** `docs/phase7-quality-audit-informatique`
**Base :** `develop` @ `486f35c4bcabc172e6f172c0250e073b6e03223b` (merge #81)
**Type de livraison :** audit + rapport, aucun changement de code (voir « Conclusion »).

## Méthode

Les questions Informatique (AMPCR, MC01–MC38) sont **entièrement générées par IA**
à l'exécution (`app.ai.questionnaire` / `app.ai.prompts` → `app.v1.ai_bridge` →
`app.v1.bank`) — contrairement au Français, il n'existe pas de banque statique
éditoriale à auditer manuellement. L'audit porte donc sur :

1. les **instructions de génération** (`app/ai/prompts.py`) — la première ligne
   de défense ;
2. les **validateurs serveur** (`app/v1/quality_validation.py`,
   `app/v1/domain_validation.py`) — le filet de sécurité déterministe,
   indépendant de ce que produit réellement le modèle ;
3. la **vérification que ce filet est bien câblé en rejet dur** dans le chemin
   de persistance réel des questions, pas seulement défini mais jamais appelé ;
4. la **suite de tests existante** couvrant ces règles.

Aucun appel réel à l'API OpenAI n'a été effectué (cohérent avec la règle « no
real OpenAI calls in pytest » de la mission, et parce qu'un tel appel a un coût
et n'a pas été explicitement autorisé pour cet audit).

## Constat : chaque critère du ticket est déjà couvert

| Critère (ticket) | Mécanisme | Statut |
|---|---|---|
| Pas de distracteurs absurdes | Prompt `app/ai/prompts.py` §QUALITÉ (ticket #69) — contient **verbatim** les 3 exemples cités par la mission (« placer le matériel près d'un radiateur pour mieux voir », « remplacer le BSSID par une adresse IP », « pulvériser un liquide sur les composants ») comme contre-exemples explicites, chacun avec un bon exemple alternatif | Couvert (prompt), testé (`test_prompt_wifi_bad_and_good_distractor_examples_present`, `test_prompt_security_bad_and_good_distractor_examples_present`) |
| Pas de réponses évidentes | `_check_weak_classification_phrasing` + `_check_cidr_overguided` (serveur) + garde anti-fuite classification (#80, ce cycle) | Couvert (serveur, rejet dur) |
| Pas d'ordre pré-trié | `_check_ordering_not_shuffled` (filet) + `shuffle_ordering_items` (préventif, #69) | Couvert (serveur, rejet dur) |
| Pas de réponse donnée dans l'énoncé | `_check_cidr_overguided` (CIDR) + `_check_classification_reveals_answer_label` (#80, ce cycle) | Couvert (serveur, rejet dur) |
| Pas de diagnostics vagues | `_check_diagnostic_self_sufficiency` | Couvert (serveur, rejet dur) |
| Pas de classifications molles | `_check_weak_classification_phrasing` | Couvert (serveur, rejet dur) |
| Pas de doublons intra-session | `deduplicate_intra_session` (#82, ce cycle) | Couvert (serveur, garde finale) |
| Pas de bonne réponse systématiquement en position 1 | `shuffle_multiple_choice_options` (#80, ce cycle) | Couvert (serveur, à la création du contenu) |

## Vérification du câblage réel (pas seulement défini)

`app/v1/bank.py:392` appelle `validate_question_quality(...)` pour **chaque**
question générée avant persistance ; en cas d'erreur, la question est
**rejetée (skip, jamais persistée)**, avec un log `QUALITY_VALIDATION_REJECTED`
— ce n'est pas un avertissement silencieux. Ce chemin est partagé par toute
génération AMPCR (pratique, examen, MC38 transversal).

## Tests exécutés

```
pytest -q tests/test_ticket69_question_quality_ambiguity.py   → 36 passed
pytest -q tests/test_ticket64_ampcr_question_quality.py       → 32 passed
```

(Exécutés en isolation : la combinaison de plusieurs fichiers de tests dans la
même invocation pytest déclenche un artefact préexistant d'ordonnancement de
fixtures inter-fichiers — `no such table` / `UNIQUE constraint failed` — sans
rapport avec la qualité des questions ; chaque test repasse individuellement.
Ce même artefact a été observé et documenté pendant la validation de #65.)

## Limite documentée (décision produit, non bloquante)

Le ticket #69 (déjà mergé) documente explicitement, dans son propre code
(`app/v1/quality_validation.py`, lignes 24-29), que la **plausibilité
sémantique complète** d'un distracteur (« ce distracteur précis semblerait-il
crédible à un vrai débutant ? ») est **volontairement hors de portée** d'un
contrôle serveur déterministe/syntaxique, et reste confiée (a) aux
instructions du prompt et (b) à des tests ciblés sur des cas concrets déjà
rencontrés — jamais à un raisonnement IA supplémentaire côté serveur, pour
éviter d'ajouter une dépendance IA non déterministe à un filet de sécurité qui
doit rester fiable même si le modèle dérive.

Cette même limite s'applique nécessairement à l'audit de Phase 7 : vérifier de
façon fiable qu'un lot de questions **réellement générées en production**
respecte pleinement ce critère nécessiterait soit un appel réel à l'API
OpenAI (hors périmètre ici — coût, quota, non autorisé explicitement pour cet
audit), soit une relecture humaine d'échantillons réels en staging par le
pilote pédagogique (ChatGPT / l'utilisateur). C'est la suite recommandée pour
ce sous-critère précis ; elle ne bloque aucune autre phase.

## Conclusion

**Aucun changement de code n'a été nécessaire pour la Phase 7** : chaque règle
vérifiable de façon déterministe listée par le ticket est déjà implémentée et
appliquée en rejet dur, soit par le ticket #69 (déjà mergé avant cette
mission), soit par les tickets #82/#80 de ce même cycle. Cet audit constitue
la vérification et la documentation demandées par la Phase 7, avec une seule
réserve explicitement bornée (plausibilité sémantique fine, nécessitant une
relecture humaine ou un appel IA réel non exécuté ici).

## Fichiers

- `docs/claude-reports/2026-09-19_phase7_audit-qualite-questions-informatique.md` (ce rapport, seul fichier de ce commit)
