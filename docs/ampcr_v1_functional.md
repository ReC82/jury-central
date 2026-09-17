# Jury Central — AMPCR V1 : état fonctionnel MC01→MC38 (ticket #55)

Livraison verticale urgente (examens Informatique 23/09/2026 et Français 25/09/2026) :
condense #41 (banque)/#42 (sessions)/#43 (génération batch)/#44 (correction globale)/#24
(UX entraînement)/#25 (UX évaluation) en un parcours réellement utilisable pour les 38
mini-cours du programme AMPCR, avant de commencer le Français.

---

# 1. Ce qui a changé pour l'utilisateur

`/uaa/{slug}/practice` et `/uaa/{slug}/exam`, pour toute UAA du programme AMPCR (MC01 à
MC38), affichent désormais :

1. une page de démarrage (choix de difficulté Facile/Moyen/Difficile — Adaptatif affiché
   désactivé, en attente de #45) et, si une session est déjà en cours, une proposition
   claire de reprise ;
2. un questionnaire de 10 questions (20 pour l'examen blanc global AMPCR), une question à
   la fois, avec compteur de progression, navigation Précédent/Suivant et enregistrement
   automatique de chaque réponse ;
3. **aucune correction visible avant la fin** (ni bouton Corriger par question, ni
   feedback immédiat) ;
4. un bouton unique — « Terminer et corriger » (S'entraîner) ou « Terminer l'évaluation »
   (S'évaluer, avec confirmation explicite) ;
5. après soumission, une correction complète question par question (ta réponse, attendu/
   critères, points, points forts, erreurs, éléments manquants, explication) et un score
   global ; la session devient alors immuable.

Le rendu legacy (12 exercices empilés avec bouton Corriger individuel, bloc « Génère ton
propre exercice IA ») n'est plus utilisé par aucune UAA AMPCR, mais son code
(`app.editorial_exercise`, templates `uaa_practice.html`/`uaa_exam.html`) reste
disponible et continue de servir toute UAA non migrée (Mathématiques, futur Français).

Deux nouveaux parcours globaux :

- `/modules/ampcr/practice` — S'entraîner sur l'ensemble du programme AMPCR (10 questions
  tirées dans tous les mini-cours déjà alimentés).
- `/modules/ampcr/exam` — examen blanc complet (20 questions).

---

# 2. Contexte pédagogique — autorité et limite assumée

**MC01/MC02/MC03** : contenu réellement rédigé (cahiers des charges ChatGPT, tickets
#10/#12/#14) — contexte pédagogique riche (`app.ai.context.PEDAGOGICAL_CONTEXTS`),
inchangé.

**MC04 à MC38** : ChatGPT a fourni code, titre et catégorie dans le ticket #55 — **aucun
contenu pédagogique détaillé n'existe encore** dans ce dépôt pour ces 35 mini-cours
(confirmé par `docs/content_plan_informatique_francais.md`). Leur contexte pédagogique
(`app.v1.ampcr_plan._minimal_context`) ne contient donc QUE ce titre, avec pour seule
consigne de rester strictement dans son sujet — **aucune notion technique détaillée n'a
été inventée par ce ticket** (règle du projet : Claude ne redéfinit jamais le contenu
pédagogique). Ces contextes minimaux bornent l'IA (empêchent une dérive hors programme)
mais restent volontairement pauvres : ils attendent un enrichissement éditorial (objectifs
détaillés, notions autorisées/hors scope, vocabulaire) dans un prochain ticket.

**Conséquence directe sur la banque** : voir § 4.

---

# 3. Tableau MC01 → MC38

| Code | Titre | Catégorie | Contexte | Types recommandés | Banque initiale | Practice | Exam |
|---|---|---|---|---|---|---|---|
| MC01 | Architecture générale d'un PC | hardware | riche (#10) | multiple_choice, classification, vocabulary | 12 questions importées (`editorial_exercise`) | ✅ | ✅ |
| MC02 | Carte mère, formats, bus et connectiques | hardware | riche (#12) | multiple_choice, classification, vocabulary | 0 pré-chargée (génération à la demande) | ✅ | ✅ |
| MC03 | Processeur et mémoire RAM | hardware | riche (#14) | multiple_choice, classification, vocabulary | 0 pré-chargée (génération à la demande) | ✅ | ✅ |
| MC04 | Stockage : HDD, SSD SATA et NVMe | hardware | minimal | multiple_choice, classification, vocabulary | génération à la demande | ✅ | ✅ |
| MC05 | Alimentation, refroidissement, ESD et sécurité électrique | hardware | minimal | multiple_choice, classification, vocabulary | génération à la demande | ✅ | ✅ |
| MC06 | Montage, démontage et reconditionnement d'un PC | hardware | minimal | multiple_choice, classification, vocabulary | génération à la demande | ✅ | ✅ |
| MC07 | BIOS, UEFI, POST et démarrage | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC08 | Partitionnement, GPT/MBR et formatage | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC09 | Installer Windows proprement | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC10 | Windows : administration et commandes essentielles | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC11 | Linux : bases utiles au technicien PC-réseaux | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC12 | Pilotes, périphériques et logiciels | systems | minimal | multiple_choice, ordering, short_answer | génération à la demande | ✅ | ✅ |
| MC13 | Fondamentaux réseau : LAN, WAN, OSI et TCP/IP | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC14 | Équipements réseau : switch, routeur, point d'accès, modem | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC15 | Câblage Ethernet et RJ45 : T568A/T568B | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC16 | IPv4 : adresses, masque, passerelle et plages privées | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC17 | Subnetting 1 : masques et CIDR | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC18 | Subnetting 2 : réseau, broadcast et exercices avancés | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC19 | DHCP : attribution automatique des paramètres IP | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC20 | DNS, ARP et ICMP | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC21 | TCP, UDP et ports réseau | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC22 | Internet, NAT/PAT et routage de base | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC23 | Switching, topologies et segmentation | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC24 | VLAN, trunk et réseau invité | networks | minimal | numeric, calculation, multiple_choice | génération à la demande | ✅ | ✅ |
| MC25 | Wi-Fi : normes, bandes, canaux et couverture | wifi | minimal | multiple_choice, true_false, vocabulary | génération à la demande | ✅ | ✅ |
| MC26 | Sécurité Wi-Fi : WPA2, WPA3, PSK, Enterprise | wifi | minimal | multiple_choice, true_false, vocabulary | génération à la demande | ✅ | ✅ |
| MC27 | Sécurité réseau traditionnelle | security | minimal | multiple_choice, true_false, diagnostic | génération à la demande | ✅ | ✅ |
| MC28 | Menaces informatiques et protection des postes | security | minimal | multiple_choice, true_false, diagnostic | génération à la demande | ✅ | ✅ |
| MC29 | Dépannage matériel : méthode et pannes courantes | troubleshooting | minimal | diagnostic, troubleshooting, ordering | génération à la demande | ✅ | ✅ |
| MC30 | Dépannage Windows et Linux | troubleshooting | minimal | diagnostic, troubleshooting, ordering | génération à la demande | ✅ | ✅ |
| MC31 | Dépannage réseau méthodique | troubleshooting | minimal | diagnostic, troubleshooting, ordering | génération à la demande | ✅ | ✅ |
| MC32 | Maintenance préventive et entretien | troubleshooting | minimal | diagnostic, troubleshooting, ordering | génération à la demande | ✅ | ✅ |
| MC33 | Partage de ressources, comptes, droits et permissions | professional | minimal | short_answer, multiple_choice, true_false | génération à la demande | ✅ | ✅ |
| MC34 | Inventaire matériel et gestion simple des ressources | professional | minimal | short_answer, multiple_choice, true_false | génération à la demande | ✅ | ✅ |
| MC35 | Ergonomie, sécurité, environnement et confidentialité | professional | minimal | short_answer, multiple_choice, true_false | génération à la demande | ✅ | ✅ |
| MC36 | Communication client et rapport technique | professional | minimal | short_answer, multiple_choice, true_false | génération à la demande | ✅ | ✅ |
| MC37 | Laboratoire intégrateur PC + réseau | final | minimal | multiple_choice, classification, ordering | génération à la demande | ✅ | ✅ |
| MC38 | Révision finale et examen blanc AMPCR | final | minimal | multiple_choice, classification, ordering | génération à la demande | ✅ | ✅ |

« Practice »/« Exam » = ✅ signifie : la route existe, exige un compte, protège la
correction jusqu'à la soumission, autosave, reprise, et peut produire un questionnaire
complet — soit depuis la banque (MC01), soit par génération batch à la première
utilisation (tous les autres, dans la limite de la disponibilité du fournisseur IA
configuré en production ; testé en pytest exclusivement avec `FakeAIProvider`, jamais un
appel réseau réel).

---

# 4. Banque : ce qui est réellement pré-chargé vs généré à la demande

Seul **MC01** dispose d'une banque pré-chargée (12 questions, importées automatiquement
au premier accès à `/uaa/ampcr-mc01/practice` ou `/exam` depuis les 12 exercices déjà
rédigés du ticket #29 — `app.v1.bank.import_mc01_legacy_to_bank`, idempotent).

**MC02 à MC38 partent d'une banque vide.** Choix assumé (voir § 2) : produire 5 questions
« de référence » pour chacun des 37 mini-cours restants aurait exigé soit un contenu
pédagogique détaillé qui n'existe pas encore dans ce dépôt (risque d'inventer des faits
techniques erronés sur des sujets sensibles — sous-réseaux, sécurité Wi-Fi...), soit des
dizaines d'appels OpenAI réels non maîtrisés avant l'échéance. Le mécanisme de génération
batch (§ 5) est identique pour ces 37 mini-cours et pour MC01 : à la première session
créée pour un mini-cours, s'il manque des questions, UN appel IA les génère et les
persiste dans la banque (`generation_source=AI_GENERATED`) — la banque grandit donc
organiquement à l'usage, toujours validée par le registre #40, sans jamais exposer de
solution au navigateur.

---

# 5. Génération et correction (rappel du mécanisme, détail dans le rapport de ticket)

- **Génération** : au plus UN appel `generate_questionnaire` par session créée, uniquement
  si la banque ne fournit pas assez de questions non vues ; les types demandés excluent
  automatiquement les types sémantiques longs si le plafond de 3 est déjà atteint par la
  sélection de banque.
- **Correction** : au plus UN appel `correct_semantic_batch` par soumission de session
  (via `app.ai.questionnaire.correct_questionnaire`, ticket #23, réutilisé tel quel) ; les
  types déterministes sont toujours corrigés localement, sans appel réseau.
- **Repli sans IA** : si la génération échoue, la session se construit quand même avec ce
  que la banque peut fournir (y compris répétitions en dernier recours) ; si la correction
  échoue, les questions locales sont corrigées normalement et les questions sémantiques
  reçoivent un message explicite (« correction indisponible ») plutôt qu'un score inventé
  ou une erreur serveur.

---

# 6. Ce qui reste hors périmètre de ce ticket

- Contenu pédagogique détaillé pour MC04-MC38 (objectifs, notions précises) : à rédiger
  par ChatGPT/l'équipe pédagogique dans un ticket dédié.
- Français (aucune UAA, aucun contexte, explicitement reporté).
- #45 (rating), #46 (admin complet), #48 (visuels avancés), paiement, quotas réels,
  analytics avancées.
- Composition équilibrée précise par catégorie pour le parcours global (§ 16 du ticket) :
  la sélection actuelle tire aléatoirement parmi toutes les questions déjà taguées
  `uaa_id`, sans pondération stricte par catégorie hardware/systems/réseaux/... — une
  répartition fine est reportée à un ticket ultérieur, plusieurs sessions successives
  restant nécessaires pour couvrir tout le programme (accepté explicitement par le
  ticket : « ne pas garantir 1 question sur chaque MC dans 10 questions »).
