# Ticket #67 — UX navigation : accueil par parcours CESS → CESS P → Informatique

- Ticket : https://github.com/ReC82/jury-central/issues/67
- **État réel : Déjà livré** (par le ticket #136, tranche 1 — PR #140/#141, fusionnée le 21/10/2026) — à vérifier par le propriétaire
- **SHA installé** sur https://jury-central.lodylands.com : `42ef0313f7ac7e107e83b38b242eb5e770ebef46`
- Aucun code modifié dans cette session (constat + rapport uniquement).

## 1. Constat (réconciliation)

Le rapport #136 (`docs/claude-reports/2026-10-21_ticket-136-parcours-ludique.md`) indique
explicitement reprendre le volet A de #67. Contrôle effectué sur le code de `develop` et sur
le site réellement servi, critère par critère :

| Critère #67 | Constat | Preuve |
|---|---|---|
| `/` n'est plus un placeholder | Accueil avec « Choisir mon parcours » / « Continuer mon parcours » + tuiles | `/` HTTP 200, texte présent sur le site |
| `S'entraîner` absent du header | Retiré ; la route `/practice/...` reste servie | `app/templates/base.html` ; test `test_home_invites_to_choose_and_header_has_no_practice_link` |
| Header simple | Accueil · Mon parcours · Matières · Quiz (#137) · Mes entraînements · compte · Déconnexion | `app/templates/base.html` |
| Déconnexion plus propre | Bouton discret `jc-logout` avec icône (formulaire POST + CSRF) | `app/templates/base.html` |
| Parcours CESS → CESS P → Informatique en quelques clics | `/parcours` (CESS) → `?diplome=cess` (CESS P ; CESS G/TQ « pas encore de contenu ») → `?diplome=cess&forme=p` (option AMPCR) → `/mon-parcours` | pages en HTTP 200 sur le site |
| Informatique mène au contenu AMPCR existant | Tuile → `/modules/ampcr` (chemin MC01→MC38, Cours / S'entraîner / Examen blanc) | `app/templates/_parcours_tile.html`, `/modules/ampcr` HTTP 200 |
| Extension future sans page par matière | Registre générique `app/v1/parcours.py` (diplôme → forme → option + formation commune : AMPCR, Français, FSE) | code |
| Navigation mobile | Menu hamburger Bootstrap (`navbar-toggler`), tuiles mobile-first (captures 390 px faites en #136) | `base.html`, rapport #136 |
| Cours publics, routes conservées | Oui | rapport #136, tests |
| Tests de routes/navigation | `tests/test_ticket136_parcours.py` (16 tests) | voir § 3 |

## 2. Liens pour tester

1. https://jury-central.lodylands.com/ → « Choisir mon parcours »
2. https://jury-central.lodylands.com/parcours → CESS → CESS P → Assistant/Assistante de maintenance PC-réseaux
3. https://jury-central.lodylands.com/mon-parcours → tuile Informatique AMPCR
4. https://jury-central.lodylands.com/modules/ampcr
5. Sur téléphone : menu hamburger, puis Déconnexion (une fois connecté)

## 3. Vérifications effectuées

- `pytest tests/test_ticket136_parcours.py` sur `origin/develop` : **16 passed**.
- Site public : `/`, `/parcours`, `/parcours?diplome=cess`, `/parcours?diplome=cess&forme=p`,
  `/subjects`, `/modules/ampcr` en HTTP 200 ; `/mon-parcours` 303 sans choix (normal : renvoie à l'assistant).
- Non effectué : soumission réelle du choix de parcours sur le site (évite d'écrire en base de
  production ; couvert par les tests), validation visuelle (faite en #136, à confirmer par le propriétaire).

## 4. Choix faits seul

1. Pas de nouveau code : refaire l'accueil ou l'en-tête dupliquerait #136 (règle « ne jamais refaire un travail livré »).
2. Statut « à vérifier » plutôt que « terminé » : le propriétaire peut valider #67 en même temps que #136 et fermer le ticket.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire. Si le parcours livré par #136 convient, #67 peut être fermé.

## 6. Reste à faire

Rien pour #67. Signalé (hors périmètre, déjà noté en #136) : sur téléphone 390 px, la barre
d'onglets Cours / S'entraîner / Examen blanc d'une page de cours déborde légèrement.
