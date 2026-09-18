"""Validation MÉTIER des questions générées (ticket #68).

Pourquoi un niveau de validation en plus du registre #40
----------------------------------------------------------
`app.v1.question_engine.validate_content` (#40) garantit qu'un `content_json` est
STRUCTURELLEMENT valide pour son type (bons champs, bons types Python) — il ne garantit
RIEN sur la VÉRITÉ TECHNIQUE du contenu. Un JSON peut être parfaitement valide au sens du
schéma tout en étant faux en subnetting IPv4. Cas réel détecté en staging (MC17,
question `diagnostic` générée) :

    « Un poste possède l'adresse 192.168.50.130/26. Le technicien compare quatre
    adresses possibles pour un autre poste : 192.168.50.129, 192.168.50.150,
    192.168.50.191, 192.168.50.192. Laquelle est dans un autre sous-réseau ?
    Justifie avec l'incrément. »

Pour /26, 192.168.50.191 est l'adresse de BROADCAST et 192.168.50.192 est l'adresse
RÉSEAU du sous-réseau suivant — ni l'une ni l'autre ne peut être « une adresse possible
pour un poste ». Le JSON de cette question était structurellement irréprochable ; il était
techniquement faux. Ce module ajoute ce second niveau de validation, appliqué APRÈS le
registre #40 et AVANT toute persistance/service à un utilisateur (voir
`app.v1.bank.persist_generated_questions`).

Architecture — registre extensible
-----------------------------------
`DOMAIN_VALIDATORS` est une liste de fonctions `(module, uaa, question_type, content_json)
-> list[str]` (liste d'erreurs, vide = OK). `validate_domain_question(...)` les exécute
toutes et agrège les erreurs — chaque validateur décide lui-même s'il est concerné par la
question (retourne `[]` sinon) et ne bloque jamais une question hors de son périmètre.
Aujourd'hui, un seul domaine : IPv4/subnetting (`validate_ipv4_subnet_question`). Un futur
domaine (RJ45, ports/protocoles, commandes OS, compatibilité matériel...) s'ajoute en
écrivant un nouveau validateur de même signature et en l'ajoutant à `DOMAIN_VALIDATORS` —
jamais en touchant `app.v1.bank` ni `app.v1.session_service`. Voir
`docs/domain_question_validation.md` pour le détail.

Portée volontairement bornée (§ 13 du ticket) : ce module extrait des adresses IPv4/CIDR
par PATRON SYNTAXIQUE (regex simples, jamais de tentative de compréhension sémantique d'un
paragraphe libre) et ne compare que des valeurs STRUCTURÉES et déterministes (la réponse
réellement marquée correcte — `accepted_answers`, l'option pointée par
`correct_option_ids` — jamais un distracteur volontairement faux, jamais une lecture floue
de tout le texte)."""

import ipaddress
import re
from typing import Any, Protocol

from app.answer_checking import normalize_text

# --- Faits de référence IPv4 (périmètre AMPCR actuel : /24 à /30, § 3 du ticket) -----------

MIN_SCOPED_PREFIX = 24
MAX_SCOPED_PREFIX = 30

EXPECTED_MASK_BY_PREFIX: dict[int, str] = {
    24: "255.255.255.0",
    25: "255.255.255.128",
    26: "255.255.255.192",
    27: "255.255.255.224",
    28: "255.255.255.240",
    29: "255.255.255.248",
    30: "255.255.255.252",
}

EXPECTED_INCREMENT_BY_PREFIX: dict[int, int] = {24: 256, 25: 128, 26: 64, 27: 32, 28: 16, 29: 8, 30: 4}


def usable_host_count(prefix: int) -> int:
    """Nombre d'hôtes utilisables pour `prefix` (§ 10 : `num_addresses - 2`, jamais
    généralisé à /31 — hors périmètre du programme actuel)."""
    return ipaddress.ip_network(f"0.0.0.0/{prefix}").num_addresses - 2


# --- Extraction syntaxique (regex bornées, jamais de NLP de paragraphe libre) --------------

_CIDR_RE = re.compile(r"\b((?:\d{1,3}\.){3}\d{1,3})\s*/\s*(\d{1,2})\b")
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_MASK_RE = re.compile(r"\b255(?:\.\d{1,3}){3}\b")
_INT_RE = re.compile(r"\b\d{1,3}\b")
_BARE_PREFIX_TOKEN_RE = re.compile(r"^/?\s*(\d{1,2})\s*$")
# CIDR nu (« /28 »), sans adresse IP associée — ex. « Quel masque pour un préfixe /28 ? ».
# Borné à 24-30 (périmètre du programme, § 3) pour ne jamais confondre avec une date ou
# une fraction sans rapport.
_BARE_CIDR_SUFFIX_RE = re.compile(r"/(2[4-9]|30)\b")

# Mots indiquant qu'une adresse est présentée comme destinée à UN POSTE/UNE MACHINE
# (§ 6 du ticket) — seul contexte où « jamais network/broadcast » s'applique. Une question
# qui demande explicitement d'identifier l'adresse réseau ou de broadcast (ex. un exercice
# de classification réseau/hôte/broadcast) n'est jamais concernée par cette règle.
_HOST_CONTEXT_KEYWORDS = ("poste", "machine", "hote", "ordinateur", "interface reseau", "interface")

_OTHER_SUBNET_KEYWORDS = ("autre sous-reseau", "autre sous reseau", "autre subnet")

# Signal qu'une question relève du domaine IPv4/subnetting (§ 5) : soit une UAA scopée
# (MC16/17/18), soit une adresse IPv4 littérale dans le texte (signal fort, quasi jamais un
# faux positif dans ce programme), soit un mot-clé réellement spécifique au sous-adressage
# — jamais le seul mot « réseau », trop générique (câblage/matériel réseau notamment).
_SCOPED_UAA_CODES = frozenset({"MC16", "MC17", "MC18"})
_SUBNETTING_KEYWORDS = (
    "cidr", "broadcast", "sous-reseau", "sous reseau", "subnetting", "masque",
    "increment", "adresse ip", "hotes utilisables", "nombre d'hotes", "nombre d hotes",
)


def _extract_ipv4_literals(text: str) -> list[str]:
    return _IPV4_RE.findall(text or "")


def _first_reference_cidr(text: str) -> tuple[str, int] | None:
    match = _CIDR_RE.search(text or "")
    if match is None:
        return None
    ip_str, prefix_str = match.groups()
    prefix = int(prefix_str)
    if not (MIN_SCOPED_PREFIX <= prefix <= MAX_SCOPED_PREFIX):
        return None
    try:
        ipaddress.ip_address(ip_str)
    except ValueError:
        return None
    return ip_str, prefix


def _first_prefix_in_text(text: str) -> int | None:
    """Préfixe CIDR mentionné dans `text`, avec OU sans adresse IP associée (§ 8/9/10 :
    « quel masque pour un /28 ? » n'a pas besoin d'une adresse concrète pour être
    validable). `None` si aucun préfixe dans le périmètre /24-/30 n'est trouvé."""
    cidr = _first_reference_cidr(text)
    if cidr is not None:
        return cidr[1]
    match = _BARE_CIDR_SUFFIX_RE.search(text or "")
    return int(match.group(1)) if match is not None else None


def _reference_network(text: str) -> ipaddress.IPv4Network | None:
    found = _first_reference_cidr(text)
    if found is None:
        return None
    ip_str, prefix = found
    try:
        return ipaddress.ip_interface(f"{ip_str}/{prefix}").network
    except ValueError:
        return None


def _looks_like_ipv4_subnetting_question(uaa_code: str | None, full_text: str) -> bool:
    if uaa_code in _SCOPED_UAA_CODES:
        return True
    if _IPV4_RE.search(full_text or ""):
        return True
    normalized = normalize_text(full_text)
    return any(keyword in normalized for keyword in _SUBNETTING_KEYWORDS)


def _host_context_present(text: str) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in _HOST_CONTEXT_KEYWORDS)


def _asks_for_other_subnet(text: str) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in _OTHER_SUBNET_KEYWORDS)


def _extract_option_texts(question_type: str, content: dict[str, Any]) -> list[str]:
    if question_type == "multiple_choice":
        return [str(o.get("label", "")) for o in content.get("options") or []]
    if question_type == "classification":
        return [str(e) for e in content.get("elements") or []]
    if question_type == "ordering":
        items = content.get("items") or []
        return [str(i.get("label", "")) if isinstance(i, dict) else str(i) for i in items]
    return []


def _correct_answer_texts(question_type: str, content: dict[str, Any]) -> list[str]:
    """Texte(s) de la/les réponse(s) réellement marquée(s) correcte(s) — jamais un
    distracteur volontairement faux (§ 13 : ne valider que ce qui est déterministe)."""
    if question_type == "multiple_choice":
        options = {o.get("option_id"): str(o.get("label", "")) for o in content.get("options") or []}
        return [options[oid] for oid in content.get("correct_option_ids") or [] if oid in options]
    if question_type in ("short_answer", "vocabulary"):
        return [str(a) for a in content.get("accepted_answers") or []]
    return []


def _expects_single_answer(question_type: str, content: dict[str, Any]) -> bool:
    if question_type == "multiple_choice":
        return int(content.get("max_selections", 1) or 1) == 1
    return question_type in ("short_answer", "vocabulary", "diagnostic", "long_answer")


# --- Règle § 6/7 : adresse « pour un poste » jamais réseau/broadcast, unicité ---------------


def _check_host_addresses(prompt: str, question_type: str, content: dict[str, Any]) -> list[str]:
    reference_network = _reference_network(prompt)
    if reference_network is None:
        return []
    full_text_parts = [prompt, *_extract_option_texts(question_type, content)]
    full_text = " ".join(full_text_parts)
    if not _host_context_present(full_text):
        return []

    option_texts = _extract_option_texts(question_type, content)
    if option_texts:
        candidates = _extract_ipv4_literals(" ".join(option_texts))
    else:
        # Types texte libre (diagnostic/long_answer/short_answer/vocabulary) : les
        # adresses candidates vivent directement dans l'énoncé (cas réel du ticket) — la
        # toute première adresse qualifiée d'un préfixe est la RÉFÉRENCE (le poste déjà
        # existant, un fait donné, jamais une proposition à évaluer séparément).
        reference_cidr = _first_reference_cidr(prompt)
        reference_host = reference_cidr[0] if reference_cidr else None
        candidates = [a for a in _extract_ipv4_literals(prompt) if a != reference_host]

    if not candidates:
        return []

    prefixlen = reference_network.prefixlen
    invalid_as_host: list[str] = []
    own_subnet_hosts: list[str] = []
    other_subnet_hosts: list[str] = []
    for addr in candidates:
        try:
            ip = ipaddress.ip_address(addr)
            own_block = ipaddress.ip_network(f"{addr}/{prefixlen}", strict=False)
        except ValueError:
            continue
        if ip == own_block.network_address or ip == own_block.broadcast_address:
            invalid_as_host.append(addr)
        elif own_block == reference_network:
            own_subnet_hosts.append(addr)
        else:
            other_subnet_hosts.append(addr)

    errors: list[str] = []
    if invalid_as_host:
        errors.append(
            "Adresse(s) présentée(s) comme possible(s) pour un poste alors qu'il "
            f"s'agit de l'adresse réseau ou de broadcast d'un sous-réseau /{prefixlen} : "
            f"{', '.join(sorted(set(invalid_as_host)))}."
        )

    if _asks_for_other_subnet(full_text) and _expects_single_answer(question_type, content):
        if len(other_subnet_hosts) == 0:
            errors.append(
                "Aucune adresse hôte valide dans un autre sous-réseau parmi les "
                "propositions (question attend une réponse unique)."
            )
        elif len(other_subnet_hosts) > 1:
            errors.append(
                "Plusieurs adresses hôtes valides dans un autre sous-réseau "
                f"({', '.join(sorted(set(other_subnet_hosts)))}) alors que la question "
                "attend une réponse unique."
            )
        elif question_type == "multiple_choice":
            correct_texts = " ".join(_correct_answer_texts(question_type, content))
            if other_subnet_hosts[0] not in correct_texts:
                errors.append(
                    "La réponse marquée correcte ne correspond pas à l'adresse hôte "
                    f"réellement dans un autre sous-réseau ({other_subnet_hosts[0]})."
                )

    return errors


# --- Règle § 8 : cohérence masque/CIDR ------------------------------------------------------


def _check_mask_cidr_consistency(prompt: str, question_type: str, content: dict[str, Any]) -> list[str]:
    prefix = _first_prefix_in_text(prompt)
    if prefix is None:
        return []
    if "masque" not in normalize_text(prompt):
        return []
    expected = EXPECTED_MASK_BY_PREFIX[prefix]
    errors: list[str] = []
    for text in _correct_answer_texts(question_type, content):
        for mask in _MASK_RE.findall(text):
            if mask != expected:
                errors.append(
                    f"Masque annoncé comme correct incohérent avec /{prefix} : {mask} "
                    f"(attendu {expected})."
                )
    return errors


def _check_classification_prefix_mask_pairs(content: dict[str, Any]) -> list[str]:
    """Classification prefixe CIDR → masque décimal (ex. « associe chaque préfixe à son
    masque ») — motif structurel étroit : ne déclenche que si les éléments RESSEMBLENT
    littéralement à des préfixes nus (« /26 », « 26 ») et les catégories à des masques."""
    elements = content.get("elements") or []
    categories = content.get("categories") or []
    correct = content.get("correct_categories") or []
    errors: list[str] = []
    for element, cat_index in zip(elements, correct, strict=False):
        match = _BARE_PREFIX_TOKEN_RE.match(str(element).strip())
        if match is None:
            continue
        prefix = int(match.group(1))
        if prefix not in EXPECTED_MASK_BY_PREFIX:
            continue
        if not isinstance(cat_index, int) or not (0 <= cat_index < len(categories)):
            continue
        mask_match = _MASK_RE.search(str(categories[cat_index]))
        if mask_match and mask_match.group(0) != EXPECTED_MASK_BY_PREFIX[prefix]:
            errors.append(
                f"Classification incohérente : /{prefix} associé à {mask_match.group(0)} "
                f"(attendu {EXPECTED_MASK_BY_PREFIX[prefix]})."
            )
    return errors


# --- Règle § 9 : cohérence de l'incrément ---------------------------------------------------


def _check_increment_consistency(prompt: str, question_type: str, content: dict[str, Any]) -> list[str]:
    prefix = _first_prefix_in_text(prompt)
    if prefix is None:
        return []
    if "increment" not in normalize_text(prompt):
        return []
    expected = EXPECTED_INCREMENT_BY_PREFIX[prefix]
    plausible_increments = set(EXPECTED_INCREMENT_BY_PREFIX.values())
    errors: list[str] = []
    for text in _correct_answer_texts(question_type, content):
        for raw in _INT_RE.findall(text):
            value = int(raw)
            if value != expected and value in plausible_increments:
                errors.append(
                    f"Incrément annoncé comme correct incohérent avec /{prefix} : {value} "
                    f"(attendu {expected})."
                )
    return errors


# --- Règle § 10 : nombre d'hôtes utilisables ------------------------------------------------


def _check_host_count_consistency(prompt: str, question_type: str, content: dict[str, Any]) -> list[str]:
    prefix = _first_prefix_in_text(prompt)
    if prefix is None:
        return []
    normalized = normalize_text(prompt)
    if "hote" not in normalized or not ("combien" in normalized or "nombre" in normalized):
        return []
    expected = usable_host_count(prefix)
    errors: list[str] = []
    for text in _correct_answer_texts(question_type, content):
        for raw in _INT_RE.findall(text):
            value = int(raw)
            if value != expected and 0 < value <= 254:
                errors.append(
                    f"Nombre d'hôtes utilisables annoncé comme correct incohérent avec "
                    f"/{prefix} : {value} (attendu {expected})."
                )
    return errors


# --- Règle § 11 : réseau / broadcast / premier / dernier hôte explicites -------------------

_EXPLICIT_VALUE_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("adresse reseau", "adresse de reseau"), "network"),
    (("adresse de broadcast", "adresse broadcast"), "broadcast"),
    (("premier hote", "premiere adresse hote", "premiere adresse utilisable"), "first_host"),
    (("dernier hote", "derniere adresse hote", "derniere adresse utilisable"), "last_host"),
)


def _expected_explicit_value(network: ipaddress.IPv4Network, kind: str) -> str:
    if kind == "network":
        return str(network.network_address)
    if kind == "broadcast":
        return str(network.broadcast_address)
    if kind == "first_host":
        return str(network[1])
    return str(network[-2])  # "last_host"


def _check_network_broadcast_range_claims(prompt: str, question_type: str, content: dict[str, Any]) -> list[str]:
    reference_network = _reference_network(prompt)
    if reference_network is None:
        return []
    normalized = normalize_text(prompt)
    errors: list[str] = []
    for keywords, kind in _EXPLICIT_VALUE_PATTERNS:
        if not any(keyword in normalized for keyword in keywords):
            continue
        expected = _expected_explicit_value(reference_network, kind)
        for text in _correct_answer_texts(question_type, content):
            for addr in _extract_ipv4_literals(text):
                if addr != expected:
                    errors.append(
                        f"Valeur annoncée comme correcte incohérente ({kind}) : {addr} "
                        f"(attendu {expected})."
                    )
    return errors


# --- Point d'entrée du domaine IPv4/subnetting ----------------------------------------------

_SUPPORTED_TYPES = frozenset(
    {"multiple_choice", "classification", "ordering", "short_answer", "vocabulary", "diagnostic", "long_answer"}
)


def validate_ipv4_subnet_question(
    module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
) -> list[str]:
    """Validateur métier IPv4/subnetting (§ 4-11 du ticket #68). Retourne une liste
    d'erreurs explicites (vide = question acceptée). Ne bloque QUE les questions qui
    relèvent effectivement de ce domaine (§ 5) — toute autre question ressort avec une
    liste vide, quel que soit son contenu."""
    if question_type not in _SUPPORTED_TYPES or not isinstance(content_json, dict):
        return []

    prompt = str(content_json.get("prompt", ""))
    option_texts = _extract_option_texts(question_type, content_json)
    rubric = str(content_json.get("rubric", "") or "")
    full_text = " ".join([prompt, *option_texts, rubric])

    uaa_code = getattr(uaa, "code", None)
    if not _looks_like_ipv4_subnetting_question(uaa_code, full_text):
        return []

    errors: list[str] = []
    errors.extend(_check_host_addresses(prompt, question_type, content_json))
    errors.extend(_check_mask_cidr_consistency(prompt, question_type, content_json))
    errors.extend(_check_classification_prefix_mask_pairs(content_json))
    errors.extend(_check_increment_consistency(prompt, question_type, content_json))
    errors.extend(_check_host_count_consistency(prompt, question_type, content_json))
    errors.extend(_check_network_broadcast_range_claims(prompt, question_type, content_json))
    return errors


class DomainValidator(Protocol):
    def __call__(
        self, module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
    ) -> list[str]: ...


# Registre extensible (§ 4 du ticket) : un futur domaine (RJ45, ports/protocoles, commandes
# OS, compatibilité matériel...) s'ajoute ici, jamais en modifiant `app.v1.bank`.
DOMAIN_VALIDATORS: list[DomainValidator] = [validate_ipv4_subnet_question]


def validate_domain_question(
    module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
) -> list[str]:
    """Exécute tous les validateurs métier enregistrés et agrège leurs erreurs. Liste
    vide = question acceptée par tous les domaines concernés."""
    errors: list[str] = []
    for validator in DOMAIN_VALIDATORS:
        errors.extend(validator(module, uaa, question_type, content_json))
    return errors
