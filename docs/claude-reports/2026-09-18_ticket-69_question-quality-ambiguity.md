# Ticket #69 — Qualité questions AMPCR : éliminer les diagnostics/classifications/ordering/QCM trop faciles ou ambigus

**Date** : 2026-09-18
**Branche** : `feature/69-question-quality-ambiguity`

---

## 1. Contexte

#68 (validation métier IPv4/subnetting) est mergé et protège la cohérence technique
réseau. Les tests utilisateurs montrent encore des défauts de **qualité/clarté** de
question, indépendants de toute erreur technique : ordering déjà trié (exercice trivial),
énoncés qui donnent une partie de la réponse, distracteurs caricaturaux, classifications
fondées sur une formulation molle, diagnostics sans contexte concret. Ce ticket ne touche
ni au modèle de données, ni aux sessions, ni au scoring (#70), ni aux limites de réponse
longue (#73), ni au Français, ni à l'UX navigation (#67) — uniquement la qualité et la
clarté des questions.

---

## 2. § 2 — Ordering : correctif mécanique (Q4)

**Bug réel** : les éléments d'une question `ordering` générée étaient parfois affichés
directement dans le bon ordre (« Montage PC → Installer OS → RJ45 → IP → Test second PC →
Partage ») — l'utilisateur n'avait qu'à choisir 1, 2, 3, 4, 5, 6.

**Correctif préventif** (principal) : `app.v1.ai_bridge.shuffle_ordering_items` (nouveau) —
mélange l'ordre d'AFFICHAGE de `items` (jamais `correct_order`, qui reste la source de
vérité privée, basée sur des `id` et non des positions). Garantit mathématiquement que la
séquence affichée ne correspond jamais à l'ordre attendu (reshuffle si le tirage retombe
dessus, filet de sécurité déterministe — rotation d'un cran — au-delà de 20 tentatives,
utile seulement pour un nombre d'éléments minuscule). Appliqué dans
`questionnaire_question_to_content` (génération IA) ET `_editorial_item_to_v1_content`
(import legacy MC01) — « Pour TOUT ordering », sans exception.

**Filet de sécurité** (défense en profondeur) : `app.v1.quality_validation` détecte et
rejette tout `ordering` dont l'affichage correspondrait malgré tout exactement à l'ordre
attendu — ne devrait normalement jamais se déclencher vu le correctif préventif, mais
protège contre un contournement (contenu injecté autrement que via le pont IA).

---

## 3. `app/v1/quality_validation.py` (nouveau) — complémentaire au validateur #68

Même architecture de registre extensible que `app.v1.domain_validation` (§ 4 du ticket) :

```python
QUALITY_VALIDATORS = [validate_question_quality_rules]

def validate_question_quality(module, uaa, question_type, content_json) -> list[str]:
    ...
```

Quatre règles mécaniques, bornées, sans NLP (§ 9) :

1. **Ordering déjà trié** (filet de sécurité, § 2 ci-dessus).
2. **Formulation molle déterminant seule une classification** (§ 8, cas UTP/STP) :
   « souvent choisi », « généralement utilisé » et variantes proches — rejeté quel que soit
   le contexte, car une classification doit reposer sur une propriété technique
   observable.
3. **Diagnostic sans contexte concret exploitable** (§ 6/7, cas Q6 APIPA/DHCP) : une
   question `diagnostic` doit contenir au moins un marqueur concret — un chiffre (adresse/
   valeur mesurée), un token entre backticks (commande/sortie), ou un mot-clé de résultat
   explicitement observé (« échoue », « répond », « affiche »...). Sans aucun de ces
   marqueurs, la question est rejetée comme trop vague/auto-insuffisante.
4. **CIDR trop guidé** (§ 3/10, cas Q10) : un `ordering`/`classification` portant sur des
   préfixes CIDR nus (`/24`..`/30`) ne doit pas répéter un de ces préfixes littéralement
   dans le texte de l'énoncé — sinon l'énoncé donne déjà une partie de la réponse.

**Explicitement NON implémenté côté serveur** (§ 9, demandé explicitement) : « QCM dont
plusieurs distracteurs sont manifestement hors domaine » — jugement sémantique hors de
portée d'un contrôle syntaxique fiable ; couvert uniquement par le prompt de génération
(§ 4 ci-dessous) et des tests ciblés sur le CONTENU DU PROMPT, jamais un raisonnement IA
supplémentaire côté serveur. Même choix pour Q3 (richesse des catégories de
classification) et Q11/Q17 (plausibilité des distracteurs) : amélioration du prompt +
tests sur le prompt, pas de règle server-side (la plausibilité d'un distracteur est un
jugement de contenu, pas une propriété syntaxique).

---

## 4. Intégration `persist_generated_questions` — pipeline à trois niveaux

Ordre exact par question du lot, inchangé dans son principe depuis #68 : structure (#40)
→ métier (#68, `app.v1.domain_validation`) → **qualité (#69, `app.v1.quality_validation`,
nouveau)** → déduplication (#64, inchangée). Un rejet qualité est journalisé
(`QUALITY_VALIDATION_REJECTED uaa=... question_type=... reasons=[...]`), jamais persisté,
jamais servi — même paramètre `domain_rejections` que #68 (les rejets QUALITÉ y sont
ajoutés eux aussi) pour que `app.v1.session_service._generate_with_domain_retry` (#68 § 15,
inchangé) déclenche la même régénération ciblée bornée en cas de rejet qualité — pas
seulement un rejet métier IPv4. Aucune modification de `_generate_with_domain_retry`
lui-même : il ne connaît que « manque dû à un rejet légitime, oui/non », peu importe le
validateur qui a rejeté.

---

## 5. Prompt de génération (§ 10)

`app.ai.prompts.GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT` gagne une nouvelle section « QUALITÉ
(ticket #69) » : distracteurs plausibles (exemples exacts Q11 Wi-Fi et Q17 sécurité, bons
ET mauvais, repris du ticket) ; ordering jamais déjà trié ; classification avec catégories
distractrices plausibles + critère technique observable (jamais « souvent choisi ») ;
CIDR/subnetting sans révéler les bornes dans l'énoncé ; diagnostic avec symptôme/résultat/
état et exactement une démarche suivante raisonnable.

---

## 6. `app/ai/fake_provider.py` — ajustement de test infrastructure

`FakeAIProvider`'s contenu factice `diagnostic` (`"Question factice de type diagnostic."`)
ne contenait aucun marqueur concret et se faisait légitimement rejeter par la nouvelle
règle d'autosuffisance — cassant l'invariant « un seul appel IA » de plusieurs tests #55/
#58 existants. Corrigé en donnant au contenu factice `diagnostic` une adresse IP factice
(`192.0.2.1`, plage de documentation RFC 5737) et une vraie question de suivi — un
ajustement d'infrastructure de test légitime (rendre le contenu factice un peu plus
réaliste), pas un affaiblissement du validateur réel.

---

## 7. Tests

Nouveau fichier **`tests/test_ticket69_question_quality_ambiguity.py`** (36 tests) :

1. `shuffle_ordering_items`/pont IA : jamais l'ordre attendu (300 essais à 2 éléments, cas
   le plus difficile ; 100 essais à 6 éléments), id/label toujours préservés, `correct_
   order` jamais modifié, 1 seul élément géré sans erreur, intégration bout en bout via
   `questionnaire_question_to_content` sur le cas réel Q4 exact (50 essais).
2. `app.v1.quality_validation` : ordering trié rejeté/mélangé accepté ; CIDR trop guidé
   rejeté (ordering ET classification) / non guidé accepté ; Q6 vague rejeté / APIPA+DHCP
   accepté ; exemples génériques § 6 du ticket (vague rejeté, contextualisé accepté) ;
   UTP/STP « souvent choisi » rejeté / 3 formulations à critère technique acceptées ;
   « généralement utilisé » aussi détecté ; question hors périmètre jamais touchée ;
   `long_answer` jamais soumis à la règle diagnostic (portée bornée volontaire).
3. `persist_generated_questions` : question qualité-invalide non persistée (journalisée),
   absente de la banque, question valide persistée normalement, lot mixte (1 invalide + 1
   valide) ne rejette que l'invalide et alimente `domain_rejections`.
4. `app.ai.prompts` : présence des instructions et des exemples exacts du ticket
   (distracteurs Wi-Fi/sécurité bons et mauvais, ordering jamais trié, classification
   catégories/critère objectif, CIDR sans fuite, diagnostic une seule démarche).
5. Non-régression : « aucun double choix correct involontaire » déjà garanti
   structurellement par le registre #40 (`MultipleChoiceContent` lève `ValidationError` si
   `correct_option_ids` a 2 éléments pour un choix unique — documenté, pas une nouvelle
   règle) ; le validateur métier IPv4 (#68) continue de fonctionner dans le même pipeline ;
   garde-fou explicite : aucun appel/import d'`app.ai.openai_provider`.

`pytest -q` (suite complète, exécutions séquentielles — deux `pytest` concurrents sur le
même fichier SQLite de test provoquent de faux `OperationalError: database is locked`,
observé puis écarté en cours de développement, non représentatif d'une régression) :
**1026 passed** (990 baseline ticket #68 + 36 nouveaux), `0 failed`. Ruff : **36 erreurs, 0
nouvelle** (baseline identique aux tickets #62/#64/#67/#68). `git diff --check` : propre.
Aucun appel OpenAI réel.

---

## 8. Limites assumées

- **Plausibilité sémantique des distracteurs** (Q11/Q17) et **richesse des catégories de
  classification** (Q3) : couvertes uniquement par le prompt de génération + tests sur son
  contenu, jamais par une règle server-side — demandé explicitement (§ 9 : « ne tente pas
  un raisonnement IA supplémentaire côté serveur si inutile »). La qualité réelle du
  contenu généré reste à valider manuellement sur staging avec un vrai fournisseur, comme
  pour le reste du moteur IA (limite déjà documentée aux tickets #64/#68).
- **Portée de la règle diagnostic** volontairement restreinte au type `diagnostic` (pas
  `long_answer`/`short_answer`) — évite de sur-bloquer des types qui n'appellent pas la
  même exigence de mise en situation concrète.
- **Contenu déjà en banque avant ce ticket** : les correctifs protègent les FUTURES
  générations (et les futurs imports legacy) ; aucune réécriture rétroactive du contenu
  déjà persisté (aucune opération destructive sur la banque existante).
- **Seuils lexicaux** (formulations molles, mots-clés de résultat) calibrés sur les
  exemples exacts du ticket — un réglage fin resterait possible si de nouveaux faux
  positifs/négatifs étaient observés en usage réel.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 1026
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.** Modèle de données, sessions, scoring (#70), limites de réponse longue
(#73), Français et UX navigation (#67) non touchés.
