# Ticket #221 — [AMPCR pratique PR21] Connexion directe de deux PC et mini-réseau

- Ticket : https://github.com/ReC82/jury-central/issues/221
- **État réel : Installé — à tester**
- SHA installé : `acb2ddaeccea73522818e00a0752ac622d4ab1f9` (fusion de la PR #289 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR21 « Connexion directe de deux PC et mini-réseau »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC15 et MC16). Il occupe la
position 21 de l'ordre pédagogique : après PR20, avant PR24.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR21 porte bien le sujet du ticket (« PR21, ticket 221, Connexion directe de
deux PC et mini-réseau », exigences officielles AP-28 « Connexion de deux machines en direct » et
AP-38 « Création d'un mini réseau entre plusieurs machines », p. 6). Aucun autre cours n'a été touché
ni renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Carte réseau, câble droit ou croisé (historique) et Auto MDI-X** : MDI / MDI-X, brochage
   du croisé (1↔3, 2↔6), un seul port Auto MDI-X suffit, paires utilisées en 10/100 et 1 Gb/s.
2. **Voyants de lien** et vérification physique (« Média déconnecté », NO-CARRIER, vitesse).
3. **Adresses statiques** 192.168.10.1/24 et 192.168.10.2/24, masque, **pas de passerelle ni de
   DNS** en réseau isolé (fenêtre IPv4, `netsh`, `nmcli`).
4. **Tester** : ping, table ARP, lecture des quatre messages du ping (dont le piège
   « Impossible de joindre l'hôte » compté comme reçu), **pare-feu** (réseau non identifié →
   profil Public → profil Privé et règle d'écho, sans couper le pare-feu).
5. **Partage de fichiers et permissions** (partage + NTFS, la plus restrictive gagne, compte avec
   mot de passe, `net share`, `net use`, `smbclient`).
6. **Extension à 3–6 PC avec un switch** (étoile, câbles droits, adresses suivantes du plan).
7. **DHCP ou statique, routeur / box, passerelle, DNS, plan d'adressage** (carte des adresses,
   adresses fixes hors de l'étendue DHCP).
8. **Erreurs** : liaison, DHCP (169.254), IP dupliquée (« (Dupliqué) »), masque ; arbre de
   diagnostic.
9. **Mise en service et recette** (tableau de recette, procès-verbal).

**3 procédures illustrées** : connexion directe (7 étapes), extension (6), recette (9).

**5 cas résolus** : copier les dossiers d'un PC vers un portable ; deux vieux PC sans Auto MDI-X ;
ping bloqué par le pare-feu ; de deux à six appareils puis Internet ; doublon et masque après
l'extension.

**20 exercices corrigés** (le ticket en demande au moins 18), avec contexte, consignes, barème et
corrigé : 3 remises en ordre ; 5 classements auto-corrigés (câble, fixe ou DHCP, deux séries de
pistes de diagnostic, lecture du ping) ; **4 schémas à compléter** (connexion directe, câbles,
mini-réseau avec box, carte des adresses), affichés en SVG dans le cours et dans les sessions ;
**5 exercices sur relevés de commandes** (ipconfig, ping, arp -a : masque erroné, pare-feu,
doublon, 169.254, Internet sans passerelle) ; plan d'adressage à vérifier ; partage d'un dossier ;
tableau de recette.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours).

**12 figures SVG + 4 schémas à compléter**, produits depuis des données testées ; texte
alternatif, légende, mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr21_figures.py` — données et calculs (`cable_needed`, `link_up`,
  `ping_outcome`, `ping_lines`, `direct_errors`, plans isolé et avec box contrôlés par
  `plan_errors` de PR20, `range_of`, `CHECKS`/`validation_diagnosis`/`checks_from`), figures.
- `app/v1/ampcr_pratique_pr21_bank.py` — 20 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr21_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR21 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR21", …, position 21)`, ajout seul.
- `app/static/img/ampcr-pratique/pr21-*.svg` (4 fichiers).
- `tests/test_ticket221_ampcr_pratique_pr21.py` (32 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket220_ampcr_pratique_pr19.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr21
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr21/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr21/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres, cas résolus, exercices avec les 4 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (schémas et relevés affichés dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket221_ampcr_pratique_pr21.py` : **32 passed** — règles de
  câble recontrôlées sur toutes les paires d'appareils et le brochage T568A/T568B ; adressage de
  la connexion directe ; résultat du ping dans chaque situation (réponse, délai dépassé, hôte
  injoignable, défaillance générale) ; statistiques et largeur (≤ 56 caractères) de toutes les
  captures ; plans isolé et avec box (adresses fixes hors étendue, carte des adresses sans trou) ;
  ordre du diagnostic ; figures (validité, accessibilité, données dessinées) ; schémas à compléter
  sans leurs réponses et fichiers statiques identiques au SVG généré ; exercices (format du socle,
  auto-correction, nombres des corrigés) ; cours (matière du ticket, 5 cas, 3 procédures, examen
  absent, liens, pas de lien vers PR22/23/25 non publiés, types de cartes) ; seed idempotent et
  position ; réserves séparées ; contexte de correction ; pages ; sessions d'entraînement et
  d'examen /20 sans génération IA.
- **Suite complète** (une exécution, `seed.py` partagé) : **2 948 passed**, aucun échec.
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 16 schémas ; corrigés pendant la session :
  débordement de texte dans le schéma du mini-réseau, position du libellé du câble, et schéma à
  compléter du mini-réseau qui laissait deviner la passerelle (valeurs des autres postes masquées).
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket221-20261027-121835.db` ;
  avance rapide `bc6e45b → acb2dda` ; seed : 1 UAA et 68 blocs créés (16 de PR21 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR21, PR20,
  PR19, accueil, matrice et schéma statique en HTTP 200 ; entraînement en 303 vers la connexion
  (normal sans session) ; 20 cartes d'exercice servies ; « 22 cours publiés sur 30 » ; compteurs
  utilisateurs / sessions / réponses inchangés (18 / 84 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Périmètre** : brochage détaillé du croisé laissé à PR15, calculs de masques à PR20, câblage
  physique à PR18, dépannage complet à PR24 (liens) ; comptes/groupes (PR22) et permissions
  détaillées (PR23) cités sans lien (non publiés) — le partage est enseigné au niveau demandé par
  le ticket (partage + NTFS, la plus restrictive, compte avec mot de passe).
- **Convention du cours** : box en 192.168.10.254 pour garder .1 et .2 de la connexion directe ;
  plages .1–.19 postes fixes, .20–.49 imprimantes/équipements, .100–.199 DHCP. Signalée comme
  convention ; une autre organisation cohérente est acceptée par les barèmes.
- **Modèle du ping** limité à un réseau local sans routage entre sous-réseaux (le code refuse les
  cas hors modèle) ; message « Impossible de joindre l'hôte » compté comme reçu, comme Windows.
- **Pare-feu** : réseau sans passerelle = « réseau non identifié », profil Public ; correction par
  profil Privé et règle d'écho ICMPv4, jamais par désactivation du pare-feu.
- Ports de box classés MDI-X (switch intégré), port routé d'un ancien routeur MDI.
- Adresses MAC, postes et entreprises **fictifs** ; adresses publiques dans les blocs RFC 5737.
- Schémas à compléter servis en fichiers statiques, comme PR18/PR19.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestion (hors périmètre, non faite) : les cours PR15 et PR18 mentionnent « PR21 » sans lien ;
  un lien vers `/uaa/ampcr-pratique-pr21` pourrait y être ajouté lors d'une prochaine retouche.
