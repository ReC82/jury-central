# Ticket #68 — URGENT fiabilité réseau : validation métier des questions IPv4/subnetting

**Date** : 2026-09-18
**Branche** : `feature/68-ipv4-domain-validation`

---

## 1. Contexte

Bug réel détecté en staging (MC17, question `diagnostic` générée), déjà documenté dans le
ticket : une question structurellement valide (registre #40) proposait 192.168.50.191
(broadcast) et 192.168.50.192 (adresse réseau du sous-réseau suivant) comme « adresses
possibles pour un autre poste » pour le réseau 192.168.50.128/26 — techniquement
impossible. Le JSON était irréprochable au sens du schéma ; il était faux au sens du
réseau. Aucun contrôle serveur n'existait entre « structurellement valide » et
« persisté/servi ». Ce ticket comble cet écart avec un second niveau de validation, sans
toucher au moteur de génération/correction/banque/rating lui-même, et sans casser le
ticket #64 (déjà mergé).

---

## 2. Architecture — `app/v1/domain_validation.py` (nouveau)

Registre extensible, aucun `if/elif` enfoui dans `bank.py` :

```python
DOMAIN_VALIDATORS: list[DomainValidator] = [validate_ipv4_subnet_question]

def validate_domain_question(module, uaa, question_type, content_json) -> list[str]:
    ...
```

Chaque validateur `(module, uaa, question_type, content_json) -> list[str]` décide
lui-même s'il est concerné (liste vide sinon) — un futur domaine (RJ45, ports/protocoles,
commandes OS, compatibilité matériel — explicitement **non implémentés** ici) s'ajoute en
écrivant un nouveau validateur et en l'ajoutant à `DOMAIN_VALIDATORS`, jamais en touchant
`app.v1.bank`/`app.v1.session_service`. Détail complet, règles et exemples :
**`docs/domain_question_validation.md`**.

Utilise exclusivement la stdlib `ipaddress` (`ip_network`, `.network_address`,
`.broadcast_address`, `.num_addresses`, indexation `network[1]`/`network[-2]` pour premier/
dernier hôte) — aucun calcul réseau artisanal.

**Portée bornée (§ 13 du ticket)** : extraction d'adresses IPv4/CIDR par motif syntaxique
(regex simples), jamais de compréhension sémantique d'un paragraphe libre. Les comparaisons
masque/incrément/nombre d'hôtes/valeurs explicites (réseau/broadcast/premier/dernier hôte)
ne portent que sur la valeur **structurée et réellement marquée correcte**
(`accepted_answers`, l'option pointée par `correct_option_ids`) — jamais un distracteur
volontairement faux.

---

## 3. Détection du périmètre (§ 5)

MC16/MC17/MC18 toujours scopées ; sinon, une adresse IPv4 littérale dans le texte (signal
fort) ou un mot-clé spécifique (`cidr`, `broadcast`, `sous-réseau`, `subnetting`, `masque`,
`incrément`, `adresse ip`, `hôtes utilisables`). Le seul mot « réseau » (trop générique —
câblage/matériel) **ne déclenche jamais** seul la validation, conformément à « éviter de
valider arbitrairement une question qui n'a rien à voir ».

---

## 4. Règles implémentées (§ 6-11)

- **§ 6/7 — host/network/broadcast** : une adresse présentée comme destinée à un poste/
  machine/hôte/ordinateur/interface ne peut jamais être l'adresse réseau ni de broadcast de
  son propre sous-réseau. Pour les questions « quelle adresse est dans un autre
  sous-réseau ? », exactement une réponse valide est exigée si la question est singulière
  — zéro ou deux+ réponses valides = rejet.
- **§ 8 — masque/CIDR** : table complète /24→/30, y compris pour les questions
  `classification` de type « associe chaque préfixe à son masque ».
- **§ 9 — incrément** : table complète /24→/30.
- **§ 10 — nombre d'hôtes utilisables** : `num_addresses - 2`, jamais généralisé à /31.
- **§ 11 — réseau/broadcast/premier/dernier hôte explicites** : comparés à la valeur
  réellement calculée par `ipaddress` pour la référence citée.
- **§ 12 — jamais confiance à `correct_option_ids` seul** : pour les QCM « autre
  sous-réseau », la réponse marquée correcte est comparée à l'adresse hôte réellement dans
  un autre sous-réseau, pas seulement acceptée telle quelle.

---

## 5. Intégration `persist_generated_questions` (§ 14, ne casse pas #64)

`app/v1/bank.py::persist_generated_questions` appelle la validation métier **après** le
registre #40 (structurel) et **avant** `create_question(...)`. Ordre exact par question du
lot : structure (#40) → métier (#68) → déduplication (#64, inchangée). Rejet journalisé :

```
DOMAIN_VALIDATION_REJECTED uaa=MC17 question_type=diagnostic reasons=[...]
```

Aucun secret journalisé. Nouveau paramètre optionnel `domain_rejections: list[str] | None
= None` : si fourni, le type de chaque question rejetée par la validation MÉTIER (jamais
structurelle ni dédoublonnage) y est ajouté — signature 100 % rétrocompatible (paramètre
optionnel, tous les appels existants du ticket #64 continuent de fonctionner sans
modification).

---

## 6. Régénération bornée (§ 15) — sans casser l'invariant « un seul appel » du ticket #55

`app.v1.session_service._generate_with_domain_retry` (nouveau) : un second appel IA n'est
déclenché **que** si le manque après persistance est réellement imputable à la validation
métier (`domain_rejected > 0` sur le dernier lot) — **jamais** pour un manque dû au
dédoublonnage (#64) ou à un contenu structurellement invalide, qui ne justifient pas un
second appel. Borné à `MAX_DOMAIN_REGENERATION_ATTEMPTS = 2` tentatives de complément (3
appels au total au maximum) — jamais de boucle infinie. Au-delà, repli sur le mécanisme
banque déjà existant (§ GÉNÉRATION du ticket #55) : jamais une question techniquement
fausse servie pour compléter artificiellement une session.

**Point de vigilance corrigé en cours de développement** : une première version retentait
un appel pour **tout** manque, quelle qu'en soit la cause — cassait les tests existants du
ticket #55 (`test_session_practice_created_with_ten_questions`,
`test_generation_called_at_most_once_for_an_empty_bank_mc`) qui vérifient explicitement
« au plus un appel IA par session ». Corrigé en ne retentant que si le lot précédent
contenait au moins un rejet **métier** (voir § 5 ci-dessus, `domain_rejections`) — tous les
tests #55/#64 repassent sans modification (voir § Tests).

`start_session` (per-UAA et parcours global) et `_start_mc38_transversal_session`
utilisent la même fonction partagée — aucune duplication de la logique de retry.

---

## 7. Prompt IA (§ 16)

`app.ai.prompts.GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT` porte une nouvelle consigne IPv4/
subnetting (vérifier mathématiquement réseau/broadcast/plage, ne jamais proposer network/
broadcast comme adresse hôte, garantir exactement le nombre de bonnes réponses attendu,
revérifier avant JSON final) — explicitement présentée comme une aide à la qualité, pas la
protection principale : le validateur serveur reste seul garant.

---

## 8. Tests

Nouveau fichier **`tests/test_ticket68_ipv4_domain_validation.py`** (37 tests) :

1. `app.v1.domain_validation` (unitaire, pur) : cas réel exact du ticket (§ 17, REJECT) et
   cas corrigé (§ 18, VALID) ; network/broadcast rejetés comme hôte, hôte valide accepté ;
   masque/CIDR (table complète + classification préfixe↔masque) ; incrément (table
   complète) ; nombre d'hôtes (/28→14, /30→2) ; réseau/broadcast/premier/dernier hôte
   explicites ; 0 et 2+ bonnes réponses rejetés ; `correct_option_ids` jamais pris pour
   argent comptant (§ 12) ; question hors périmètre jamais touchée ; le seul mot
   « réseau » ne déclenche pas la validation hors MC16-18 ; MC16/17/18 toujours scopées ;
   préfixe hors /24-/30 non contrôlé ; un exercice qui identifie explicitement réseau/
   broadcast (pas de contexte "poste") n'est jamais bloqué.
2. `app.v1.bank.persist_generated_questions` : question invalide non persistée, rejet
   journalisé (`caplog`), absente de la banque, question valide persistée normalement, lot
   mixte (1 invalide + 1 valide) ne rejette que l'invalide.
3. `app.v1.session_service` : régénération réussie après rejet (2 appels), limite de
   tentatives respectée avec repli banque final (`1 + MAX_DOMAIN_REGENERATION_ATTEMPTS`
   appels exactement), **aucune régénération** quand le manque n'est pas d'origine métier
   (non-régression explicite de l'invariant #55/#64), garde-fou explicite : le module de
   validation n'importe/n'appelle jamais `app.ai.openai_provider`.

`pytest -q` (suite complète) : **990 passed** (953 baseline ticket #64 + 37 nouveaux),
`0 failed`. Aucun appel OpenAI réel (`FakeAIProvider`/doublures maison partout,
`OPENAI_API_KEY=""` forcé par `tests/conftest.py`, inchangé). Ruff : **36 erreurs, 0
nouvelle** (baseline identique à celle documentée aux tickets #62/#64/#67). `git diff
--check` : propre.

---

## 9. Limites assumées

- **Portée du validateur** : extraction syntaxique par regex, jamais de compréhension
  sémantique d'un paragraphe libre (§ 13, demandé explicitement) — un cas IPv4 mal détecté
  parce que formulé de façon suffisamment inhabituelle pour échapper aux motifs de
  détection resterait non contrôlé. Les deux tests obligatoires du ticket (cas réel exact
  + cas corrigé) passent, ainsi qu'un large éventail de variantes structurelles, mais ce
  n'est pas un vérificateur formel exhaustif de tout texte français possible.
- **Types texte libre** (`diagnostic`/`long_answer`) : seule la règle host/network/
  broadcast s'applique (adresses extraites directement de l'énoncé) — les règles masque/
  incrément/nombre d'hôtes nécessitent un champ structuré (`accepted_answers`) qu'ils
  n'ont pas, conformément à § 13.
- **Autres domaines métier** (RJ45, ports/protocoles, commandes OS, compatibilité
  matériel) : architecture prête (`DOMAIN_VALIDATORS`), aucun validateur écrit — demandé
  explicitement comme hors périmètre de ce ticket.
- **Contenu déjà en banque avant ce ticket** : la validation protège les FUTURES
  générations ; elle ne réécrit ni ne purge rétroactivement une question déjà persistée
  (aucune opération destructive sur la banque existante, conformément à la consigne de ne
  jamais toucher aux données déjà produites sans instruction explicite). Une purge
  éventuelle du contenu legacy potentiellement fautif serait une décision produit séparée,
  hors périmètre de ce ticket.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 990
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.** Le Français (`feature/47-francais-v1`) n'a pas été touché ;
génération/correction/banque/rating/admin/paiement non modifiés au-delà du point
d'intégration explicitement demandé (`persist_generated_questions`).
