# Référence officielle — AMPCR, examen pratique, cycle 2026-2027/1

Copie versionnée des consignes d'examen officielles du Jury de la Fédération
Wallonie-Bruxelles pour l'épreuve **pratique** (Laboratoire + T.P. et méthodes) de l'option
CESS P « Assistant·e de maintenance PC-réseaux » (AMPCR). **C'est la source qui fait foi**
pour la matrice de couverture (`/ampcr-pratique/matrice`, `app/v1/ampcr_pratique_plan.py`)
et pour tous les tickets de cours et d'exercices PR01–PR30 / EX01–EX06
(`docs/ampcr_pratique_tickets.md`).

| Élément | Valeur |
|---|---|
| Fichier | [`26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf`](26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf) |
| Source officielle | https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/Consignes_specifiques/CESS/CESS_P/OBG/AMPCR/26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf |
| Éditeur | Direction des Jurys de l'enseignement secondaire (FWB) |
| Cycle | 2026-2027/1 |
| Date | 2026-07-13 (date de création inscrite dans le PDF) |
| Pages | 6 |
| Taille | 337 687 octets |
| SHA-256 | `7a93c3858ffd67b42620bc5364aa9b8e964a379bdf255bbcd126b50c4df095e1` |
| Récupéré le | 2026-10-26 (deux téléchargements indépendants, empreinte identique) |
| Transcription | [`transcription.md`](transcription.md) (texte brut page par page, le PDF fait foi) |

Contrôle : `sha256sum` sur le fichier doit redonner l'empreinte ci-dessus ; le test
`tests/test_ticket192_ampcr_pratique_reference.py` vérifie l'empreinte, la présence des
6 pages et que chaque exigence AP-01…AP-38 de la matrice figure mot pour mot dans la
transcription, à la bonne page.

## Contenu des 6 pages

| Page | Contenu | Utilisé dans le code |
|---|---|---|
| 1 | Page de titre : cycle, titre CESS P, option, « EXAMEN PRATIQUE », matières Laboratoire et T.P. méthodes | `OFFICIAL_SOURCE` |
| 2 | Grille horaire de l'OBG, programme 345/2007/249, titre visé ; rappel « ces consignes ne se substituent pas au programme » | `DAY_INSTRUCTIONS` (« Programme »), `PROGRAMME_SOURCE` |
| 3 | Modalités : examen **uniquement écrit**, épreuve commune aux deux matières, dispense à 10/20 sans dispense partielle ; organisation (présence à l'épreuve théorique requise) | `DAY_INSTRUCTIONS` |
| 4 | Matériel autorisé / refusé, calculatrice non programmable sur annonce, objets connectés | `DAY_INSTRUCTIONS` |
| 5 | « Consignes d'examen et matières à maîtriser » : 18 puces | `OFFICIAL_REQUIREMENTS` AP-01…AP-18 |
| 6 | Suite de la liste : 20 puces | `OFFICIAL_REQUIREMENTS` AP-19…AP-38 |

Les consignes ne fixent **ni durée, ni barème détaillé, ni exemple de question** : ne pas en
inventer.

## Droits de redistribution

Document public, téléchargeable sans authentification sur le site officiel des Jurys. Aucune
condition de réutilisation n'y est publiée (l'adresse « Mentions légales » du site affichait « Page non
trouvée » le 2026-10-26). Il est reproduit **à l'identique, sans modification**, uniquement
pour que les agents et contributeurs disposent de la référence exacte. Motifs : il s'agit de
consignes administratives officielles d'un service public (les actes officiels de l'autorité
sont exclus du droit d'auteur, art. XI.172, § 2, du Code de droit économique belge), et le
dépôt versionne déjà des sources officielles (`docs/sources_cours/`). Jury Central n'est pas
affilié à la FWB. En cas de demande de l'éditeur, retirer le PDF et conserver l'URL,
l'empreinte et la transcription structurée (pages et citations) dans
`app/v1/ampcr_pratique_plan.py`.

## Mise à jour (cycle suivant)

Ne jamais écraser ce fichier. Créer `docs/references-officielles/ampcr/<cycle>/` avec le
nouveau PDF, son README et sa transcription, comparer les listes, puis mettre à jour
`OFFICIAL_SOURCE` / `OFFICIAL_REQUIREMENTS` dans un ticket dédié.
