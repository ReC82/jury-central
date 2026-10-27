# Ticket #201 — [AMPCR pratique EX05] Examen blanc global standard — épreuve pratique écrite

- Ticket : https://github.com/ReC82/jury-central/issues/201
- **État réel : Installé — à tester**
- SHA installé : `0bc00239ba329e6a7d4d2ce64bf2865a2970f33b` (fusion de la PR #321 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

L'**examen blanc global standard EX05** du parcours **Informatique AMPCR → Pratique écrite** est
publié, après PR30 (fin de parcours, révisions transversales, comme demandé le 26/10). L'emplacement
EX05 du plan installé (`_EXERCISE_ROWS`, numérotation définitive #236 : « EX05, ticket 201 ») porte
bien le sujet du ticket : aucun écart, aucun autre cours ni examen touché. Module `AMPCR-PRATIQUE`
uniquement : Théorie (MC) et Pratique restent séparées (banques, sessions, progression).

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex05`, onglets « Sujet » et « Examen blanc »), version
  candidat **sans aucun corrigé**, 9 séquences :
  1. présentation : ce qui est évalué, les **deux variantes**, organisation et notation /100 avec
     **répartition annoncée** (matériel 20, systèmes 20, câblage 20, réseau 30, méthode 10), barème
     analytique, corrigé seulement après remise, **durée conseillée 3 h donnée comme repère et non
     comme durée officielle**, calculatrice, comment passer l'examen, version papier A4, barème
     global (situation, domaine, points, exigences, cours à revoir), exigences évaluées et
     **exigences non évaluées listées explicitement** (manques) ;
  2. à 4. **variante 1** (Fiduciaire Leclercq, Namur, réseau 192.168.1.0/24) : dossier commun
     (fiche du client, **schéma du réseau local**, **inventaire du matériel**, **journal des
     pannes**), puis questions 1–5 et 6–10 avec leurs documents propres ;
  5. à 7. **variante 2** (Bureau de géomètres Hautem, Wavre, réseau 172.16.40.0/23) : idem ;
  8. méthode ; 9. sources et supports fictifs.
  À l'impression (A4) : 12 lignes de réponse par question, chaque variante sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex05/exam`) : 10 questions, une par écran, **dans l'ordre
  du sujet**, avec contexte (repère « Variante n »), documents, consignes numérotées et points ;
  sauvegarde automatique et reprise ; barème et corrigé invisibles avant la remise ; note /100 (et
  repère /20), corrigé détaillé, bouton « Imprimer / PDF ». `/practice` redirige vers l'examen.
- **Variantes** : chaque session sert **une variante entière** (jamais un mélange) : la variante 1
  la première fois, puis la 2, puis celle que le candidat a le moins faite.

### Les 10 situations (10 points chacune, 4 critères, corrigé détaillé)

| N° | Situation | Domaine | Exigences | Variante 1 | Variante 2 |
|---|---|---|---|---|---|
| 1 | Poste lent : composants et évolution | Matériel | AP-01, AP-16 | RAM 94 % + HDD 100 % → 1 × 8 Go DDR4 DIMM (16 Go) + SSD | RAM 96 %, SSD 35 % → 1 × 8 Go DDR5 SO-DIMM, stockage inutile à changer |
| 2 | Disque défaillant : SMART et données | Matériel | AP-15, AP-01 | PC-02 à remplacer (24 en attente), PC-04 sain | PC-03 à remplacer (8 en attente, 0 réalloué : piège), disque du NAS à surveiller |
| 3 | Installation de Windows 11 | Systèmes | AP-10, AP-15 | TPM désactivé → activer | Legacy/CSM, Secure Boot, RST → UEFI, activé, AHCI |
| 4 | Installation de Linux (Ubuntu 24.04) | Systèmes | AP-10 | sha256 OK ; swap 8 Go ; /home ≈ 197 Go | sha256 FAILED → retélécharger ; swap 4 Go ; /home ≈ 457 Go |
| 5 | Cordon RJ45 et liaison cuivre | Câblage | AP-34, AP-36 | paire 1-2 inversée ; canal 90 m conforme | broche 7 ouverte ; canal 103 m trop long |
| 6 | Segment coaxial et câble BNC | Câblage | AP-35, AP-36 | 50 Ω mesurés : terminateur manquant | 30 Ω : terminateur 75 Ω + tronçon RG-59 |
| 7 | Plan d'adressage IPv4, MAC et IP | Réseau | AP-30 | /24 ; imprimante fixe dans l'étendue, PC en /16 | /23 (510 hôtes) ; PC en /24 (passerelle hors réseau), doublon avec le NAS visible dans l'ARP |
| 8 | Partages, droits et imprimante | Réseau | AP-25 | le partage limite Marc | NTFS limite Sarah |
| 9 | Portable sans Internet | Réseau | AP-37, AP-30 | DNS erroné (IP OK, nom KO) | passerelle absente (« Défaillance générale ») |
| 10 | Rapport d'intervention et vocabulaire | Méthode | AP-C01, AP-16 | durée 3 h 25 | durée 4 h 05 |

Les 11 exigences prévues pour EX05 dans le plan (AP-01, 10, 15, 16, 25, 30, 34, 35, 36, 37, C01)
sont toutes évaluées ; aucune n'est déclarée « validée » (matrice inchangée). Les exigences
officielles non évaluées par EX05 sont listées sur la page (évaluées par EX01–EX04 et les cours).

### Fichiers

- `app/v1/ampcr_pratique_ex05_figures.py` — dataclass `Variant` et les 2 variantes ; chaque valeur
  et verdict calculé par les règles **des cours** : SMART (règle EX01/PR06), `firmware_changes` et
  `activation_result` (PR08), `checksum_verdict`, `swap_advice` (PR09), `copper_verdict` (PR14),
  T568B et relevés de testeur (PR15), `bus_errors`, `ohmmeter_reading` (PR16), `AddressPlan`,
  `plan_errors`, `subnet_facts`, `ipconfig_all_lines` (PR20), `ping_outcome`, `ping_lines` (PR21),
  `weakest` (PR23), `win_ping_lines`, `nslookup_lines` (PR24) ; schéma du réseau (SVG) et table ARP.
- `app/v1/ampcr_pratique_ex05_bank.py` — documents numérotés par variante, 10 situations × 2
  variantes, validation.
- `app/v1/ampcr_pratique_ex05_course.py` — 9 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex05-v1-plan-reseau.svg`, `ex05-v2-plan-reseau.svg`.
- `app/v1/ampcr_pratique_bank.py` — EX05 déclaré avec contexte de correction propre ;
  `PracticalCourse.variants`, `has_exam_variants`, `question_item_key`, `select_exam_variant`.
- `app/v1/session_service.py` — `start_session` : pour un examen à variantes, sert une variante
  entière (`parameters_json["exam_variant"]`) ; `available_session_lengths` : 10 seulement.
- `app/v1/prompt_layout.py` — repère « Variante n » reconnu comme « Partie n » / « Dossier X ».
- `app/seed.py` — `_seed_uaa(…, "EX05", …, position 30)` (additif).
- `tests/test_ticket201_ampcr_pratique_ex05.py` (33 tests) ; comptages dans
  `tests/test_admin_content_hierarchy.py` ; motif « 4 examens blancs » assoupli dans
  `tests/test_ticket233_ampcr_pratique_ex04.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Sujet (public) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex05
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex05/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Schémas : https://jury-central.lodylands.com/static/img/ampcr-pratique/ex05-v1-plan-reseau.svg,
  https://jury-central.lodylands.com/static/img/ampcr-pratique/ex05-v2-plan-reseau.svg

Procédure courte : ouvrir le sujet, parcourir les 9 séquences ; aperçu avant impression
(Ctrl + P) ; lancer l'examen blanc (variante 1), répondre à quelques questions, quitter et
reprendre, remettre, vérifier la note /100, le barème et le corrigé ; relancer un examen blanc :
la variante 2 doit être servie.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket201_ampcr_pratique_ex05.py` : **33 passed** — réseaux recalculés
  avec `ipaddress` (dont /23 : diffusion 172.16.41.255, 510 hôtes) ; erreurs de plan attendues
  (2 et 3) et passerelle hors réseau recontrôlée ; ARP qui révèle le doublon (variante 2 seulement) ;
  mémoire (16 Go, 94 % / 96 %) ; verdicts SMART ; réglages du micrologiciel et activation ; image
  OK/FAILED, swap 8/4 Go et tailles de /home ; T568B, défauts du testeur, canal 90/103 m ;
  ohmmètre 50 Ω / 30 Ω (formule en dur) ; matrices d'accès écrites en dur et couche qui bloque ;
  relevés du portable ; durées 205/245 min ; captures ≤ 56 caractères ; schémas valides, accessibles,
  sans verdict, fichiers statiques identiques ; 20 questions, 100 points par variante, même
  structure et données différentes ; documents cités fournis avec chaque question ; réponses
  absentes des énoncés ; sujet sans corrigé (20 zones de réponse, 2 dossiers) ; seed idempotent,
  EX05 juste après PR30 ; réserve `exam` seule ; contexte de correction propre ; accueil « 5
  examens blancs sur 6 » ; **sessions : 1ʳᵉ = variante 1 dans l'ordre du sujet, corrigé masqué
  avant remise, note /100 ; 2ᵉ = variante 2**.
- Tests liés (EX04, #299, #151, #236, #192, PR30, hiérarchie admin) : 190 passed.
- **Suite complète** : **3301 passed** (une exécution, 28 min ; moteur de sessions, seed et banque partagée touchés).
- `ruff check` : fichiers créés et modifiés sans erreur.
- Contrôle visuel (navigateur sans interface) : les 2 schémas à 400 px, lisibles.
- Installation : arbre propre sur `develop`, sauvegarde (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket201-20261027-223026.db`), fast-forward `edcc5c9 → 0bc0023`, `pyproject.toml` inchangé, seed idempotent (1 UAA créée ; 61 blocs « créés » = 9 blocs EX05 + le remplacement habituel des 52 blocs FSE pilotés par le code), redémarrage des deux services (actifs), `/health` local et public OK ; sujet, accueil, matrice, PR30, EX04 et les 2 SVG en HTTP 200 (examen : 303 vers la connexion sans session, normal) ; sujet servi avec 20 questions et aucun « Corrigé de référence » ; accueil « 5 examens blancs sur 6 » ; capture de la page publiée à 1 280 px contrôlée. Compteurs utilisateurs/sessions/réponses inchangés (18 / 84 / 668).

Non effectué : validation pédagogique humaine (au propriétaire) ; correction réelle par l'IA
(tests avec `FakeAIProvider`) ; contrôle de l'impression PDF page par page.

## 4. Choix techniques faits seul

- **Variantes servies entières** : le ticket exige « au moins 2 variantes de données » et un
  dossier cohérent ; tirer 10 questions au hasard dans 20 aurait mélangé deux entreprises. Ajout
  minimal et additif au moteur (`PracticalCourse.variants`, `select_exam_variant`) actif seulement
  pour EX05 ; les autres parcours sont inchangés (suite complète).
- **Ordre fixe des questions** pour EX05 : les numéros de la session correspondent à ceux du sujet
  (suggestion notée par EX04, appliquée ici seulement).
- **10 situations de 10 points** (le ticket demande 10 à 14) : même format que EX01–EX04.
- **Durée conseillée 3 h** (repère personnel, pas la durée officielle).
- **BNC** : présenté comme un ancien segment 10BASE2 conservé hors du switch (matière PR16),
  seul usage réaliste dans un bureau de 6 postes.
- **Pas d'image générée** : schémas et valeurs exacts mieux servis par un dessin construit sur des
  données testées. Adresses publiques des plages de documentation (RFC 5737).
- **Les deux sujets sur la page** : chacun peut s'entraîner sur papier à la variante de son choix.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle).
- Suite de la file : EX06 (#234), puis audit final (#235).
- Suggestion (hors périmètre) : appliquer l'ordre fixe des questions (ou les variantes) aux autres
  examens blancs EX01–EX04 si le propriétaire le souhaite.

## Notification

L'email de livraison est envoyé par le superviseur jcorch à la fin de la session, avec ce rapport
en pièce jointe (copie dans `~/.local/state/jury-central-orch/reports/`).
