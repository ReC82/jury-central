# Jury Central — Validation métier des questions générées (ticket #68)

Ce document décrit le deuxième niveau de validation appliqué à toute question générée par
IA avant qu'elle n'entre dans la banque ou ne soit servie à un utilisateur, introduit par
le ticket #68 suite à un bug réel détecté en staging.

---

## 1. Pourquoi une validation MÉTIER en plus de la validation SCHEMA (#40)

Le registre #40 (`app.v1.question_engine.validate_content`) garantit qu'un `content_json`
est **structurellement** valide pour son type : les bons champs sont présents, avec les
bons types Python (une liste d'options, un entier pour `correct_option_ids`, etc.). Il ne
garantit **rien** sur la **vérité technique** du contenu.

Cas réel détecté en staging (MC17, question `diagnostic` générée) :

> « Un poste possède l'adresse 192.168.50.130/26. Le technicien compare quatre adresses
> possibles pour un autre poste : 192.168.50.129, 192.168.50.150, 192.168.50.191,
> 192.168.50.192. Laquelle est dans un autre sous-réseau ? Justifie avec l'incrément. »

Pour `/26`, le sous-réseau de 192.168.50.130 est 192.168.50.128/26 :

| Élément | Valeur |
|---|---|
| Adresse réseau | 192.168.50.128 |
| Premier hôte | 192.168.50.129 |
| Dernier hôte | 192.168.50.190 |
| Broadcast | **192.168.50.191** |
| Sous-réseau suivant | 192.168.50.192/26 (adresse **réseau**) |

192.168.50.191 est l'adresse de **broadcast** du sous-réseau de référence ; 192.168.50.192
est l'adresse **réseau** du sous-réseau suivant. Ni l'une ni l'autre ne peut être décrite
comme « une adresse possible pour un poste ». Le JSON de cette question était
structurellement irréprochable (schéma #40 respecté) ; il était **techniquement faux**.
Aucune vérification serveur n'existait entre « JSON structurellement valide » et
« persisté/servi ». Ce ticket comble cet écart.

---

## 2. Registre de validateurs extensible

`app/v1/domain_validation.py` expose :

```python
DOMAIN_VALIDATORS: list[DomainValidator] = [validate_ipv4_subnet_question]

def validate_domain_question(module, uaa, question_type, content_json) -> list[str]:
    ...
```

Chaque validateur a la signature `(module, uaa, question_type, content_json) -> list[str]`
(liste d'erreurs explicites, vide = accepté). `validate_domain_question` les exécute tous
et agrège les erreurs. Chaque validateur décide **lui-même** s'il est concerné par la
question — il retourne `[]` s'il ne l'est pas, ne bloque **jamais** une question hors de
son périmètre.

Aujourd'hui, un seul domaine : **IPv4/subnetting**. Une future extension (RJ45, ports/
protocoles, commandes OS, compatibilité matériel...) s'ajoute en écrivant un nouveau
validateur de même signature et en l'ajoutant à `DOMAIN_VALIDATORS` — **jamais** en
modifiant `app.v1.bank` ou `app.v1.session_service`, qui n'appellent que le point d'entrée
générique.

---

## 3. Le validateur IPv4/subnetting

### 3.1 Détection du périmètre (`_looks_like_ipv4_subnetting_question`)

Une question entre dans le périmètre du validateur si :

- son UAA est **MC16, MC17 ou MC18** (toujours scopées), OU
- son texte contient une **adresse IPv4 littérale** (`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`,
  signal fort, quasi jamais un faux positif dans ce programme), OU
- son texte contient un mot-clé réellement spécifique au sous-adressage (`cidr`,
  `broadcast`, `sous-réseau`, `subnetting`, `masque`, `incrément`, `adresse ip`, `hôtes
  utilisables`...).

Le seul mot « réseau » **n'est jamais** un déclencheur à lui seul (trop générique — présent
aussi en câblage/matériel réseau, hors périmètre IPv4).

### 3.2 Utilisation de `ipaddress` (stdlib)

Tous les calculs réseau utilisent le module standard `ipaddress` — jamais d'arithmétique
maison sur des octets. `ipaddress.ip_network("192.168.50.130/26", strict=False)` donne
directement `.network_address`, `.broadcast_address`, `.netmask`, `.prefixlen`,
`.num_addresses` ; `network[1]`/`network[-2]` donnent le premier/dernier hôte utilisable
(indexation native du module, inclut network/broadcast dans le décompte).

### 3.3 Règle host/network/broadcast (§ 6/7 du ticket)

Si le texte de la question indique qu'une adresse est destinée à un **poste/machine/
hôte/ordinateur/interface** (mots-clés explicites), une adresse proposée ne peut **jamais**
être l'adresse réseau ni l'adresse de broadcast de son propre sous-réseau (même longueur de
préfixe que la référence). Calculé via `ipaddress.ip_network(f"{adresse}/{prefixlen}",
strict=False)` pour chaque adresse candidate, comparé à `.network_address`/
`.broadcast_address`.

Une question qui demande explicitement d'**identifier** l'adresse réseau ou de broadcast
(ex. un exercice de classification « réseau / broadcast / hôte ») n'est jamais concernée
par cette règle — elle ne s'applique qu'au contexte « adresse **pour** un poste ».

Pour les questions « quelle adresse est dans un **autre** sous-réseau ? » (détection du
segment « autre sous-réseau »), le validateur classe chaque adresse candidate (même
sous-réseau que la référence / autre sous-réseau / invalide car réseau-broadcast) et
vérifie qu'**exactement une** réponse valide existe si la question attend une réponse
unique — zéro ou deux+ réponses valides est un rejet (§ 7 : « Si deux réponses sont
possibles : QUESTION INVALID. Si aucune réponse n'est possible : QUESTION INVALID. »).

### 3.4 Masque/CIDR, incrément, nombre d'hôtes (§ 8/9/10)

Ces trois règles comparent une valeur **structurée et déterministe** — jamais un
distracteur volontairement faux :

- `multiple_choice` : le texte de l'option pointée par `correct_option_ids` (jamais les
  autres options, qui peuvent légitimement contenir des valeurs fausses comme
  distracteurs) ;
- `short_answer`/`vocabulary` : `accepted_answers` ;
- `classification` (masque ↔ préfixe uniquement) : chaque paire `(élément, catégorie)`
  réellement marquée correcte par `correct_categories`.

Tables de référence (périmètre AMPCR actuel, /24 à /30 — jamais généralisé à /31, hors
programme) :

| Préfixe | Masque | Incrément | Hôtes utilisables |
|---|---|---|---|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |

### 3.5 Réseau/broadcast/premier/dernier hôte explicites (§ 11)

Si la question demande explicitement « l'adresse réseau », « l'adresse de broadcast », « la
première adresse hôte » ou « la dernière adresse hôte » pour une référence `IP/préfixe`
donnée, la valeur marquée correcte est comparée à la valeur réellement calculée par
`ipaddress` pour cette référence.

### 3.6 Portée volontairement bornée (§ 13)

Le module extrait des adresses IPv4/CIDR par **motif syntaxique** (regex simples,
`\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?`) — jamais de tentative de compréhension sémantique d'un
paragraphe libre. Pour les types texte libre (`diagnostic`/`long_answer`, sans champ
structuré de réponse attendue), seule la règle host/network/broadcast (§ 3.3, adresses
extraites directement de l'énoncé) s'applique ; les règles masque/incrément/nombre
d'hôtes/valeurs explicites (§ 3.4/3.5) ne s'appliquent qu'aux types dotés d'un champ
déterministe (`accepted_answers`, `correct_option_ids`).

---

## 4. Comportement reject / regenerate

### 4.1 Rejet avant persistance

`app.v1.bank.persist_generated_questions` appelle `validate_domain_question` **après** la
validation structurelle (#40) et **avant** `create_question(...)` : une question rejetée
n'est **jamais** persistée, jamais visible en banque, jamais servie. Le rejet est
journalisé (`logging`, niveau `WARNING`) :

```
DOMAIN_VALIDATION_REJECTED uaa=MC17 question_type=diagnostic reasons=[...]
```

Aucun secret journalisé (pas de session, pas de mot de passe, pas de clé API) — seulement
l'UAA, le type de question et les raisons métier (déjà des messages non sensibles).

### 4.2 Régénération bornée (§ 15)

Si une partie du lot généré est rejetée par la validation métier, `app.v1.session_service`
retente un appel **ciblé** (uniquement pour le manque restant) via
`_generate_with_domain_retry`, borné à `MAX_DOMAIN_REGENERATION_ATTEMPTS = 2` tentatives de
complément (3 appels au total au maximum). « Priorité qualité > économie de tokens » (§ 15
du ticket) : ce n'est plus un souci d'optimiser le nombre d'appels IA avant les examens.

**Important — ne casse pas l'invariant du ticket #55** (« un seul appel IA par session ») :
un second appel n'est déclenché **que** si le manque est réellement imputable à la
validation métier. Un manque dû à autre chose (dédoublonnage #64, contenu structurellement
invalide) ne déclenche **jamais** de second appel — `persist_generated_questions` accepte
un paramètre optionnel `domain_rejections: list[str]` que l'appelant utilise pour
distinguer les deux cas.

Si la limite de tentatives est atteinte sans combler le manque, l'appelant retombe sur le
repli banque existant (§ GÉNÉRATION du ticket #55, déjà en place) — **jamais** une question
techniquement fausse servie pour atteindre artificiellement le nombre de questions demandé.

### 4.3 Prompt IA (§ 16)

`app.ai.prompts.GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT` inclut une instruction explicite de
vérification mathématique réseau/broadcast/plage avant sortie JSON pour toute question
IPv4/subnetting. **Ce n'est pas la protection principale** — un modèle de langage peut se
tromper malgré l'instruction — le validateur serveur (`app.v1.domain_validation`) reste la
seule garantie réellement fiable, exécutée indépendamment du comportement du fournisseur.

---

## 5. Extension future

Pour ajouter un nouveau domaine métier (exemple : RJ45/sertissage, ports/protocoles,
commandes OS, compatibilité matériel) :

1. Écrire une fonction `validate_<domaine>_question(module, uaa, question_type,
   content_json) -> list[str]` dans un nouveau module (ou `app/v1/domain_validation.py` si
   la portée reste petite).
2. L'ajouter à `DOMAIN_VALIDATORS`.
3. Ne jamais toucher `app.v1.bank`/`app.v1.session_service` — ils n'appellent que
   `validate_domain_question`, agnostique du nombre/de la nature des validateurs
   enregistrés.

Domaines explicitement **non implémentés** par ce ticket (prévus, hors périmètre) : RJ45,
ports/protocoles, commandes OS, compatibilité matériel.
