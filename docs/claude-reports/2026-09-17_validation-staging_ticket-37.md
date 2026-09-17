# Validation staging — ticket #37 (MC01 Practice : ordre d'affichage)

**Date** : 2026-09-17
**PR mergée** : #50
**Commit develop déployé** : `1a4f2744230586e372263af786c5117f31257411`
**Environnement** : staging (`jury-central.lodylands.com`), déploiement via
`./scripts/deploy_staging.sh`, sans reset-db, sans suppression de `jury_central.db`.

---

## 1. Déploiement

```
git checkout develop
git pull --ff-only origin develop   → fast-forward a5596a0 → 1a4f274
./scripts/deploy_staging.sh
```

Résultat : **succès**.
- branche vérifiée : `develop`, working tree propre avant déploiement
- fast-forward propre vers `1a4f274` (aucune divergence)
- suite de tests exécutée par le script lui-même : **455 passed**, 2 warnings préexistants
  (httpx/anyio, sans lien avec #37)
- `jury_central.db` non touchée par le script (ni seed, ni reset)
- `jury-central.service` redémarré et actif, `http://127.0.0.1:8100/health` répond

Aucune modification apportée à nginx, Certbot ou à la définition systemd.

---

## 2. Migration (seed additif/idempotent)

### Premier `seed-db`

```
Seed terminé : Mathématiques (MB32, MQ32, MQ34), Informatique (AMPCR)
  Créé   : 0 matière(s), 0 module(s), 0 UAA, 0 bloc(s)
  Conservé (déjà présent, non modifié) : 2 matière(s), 4 module(s), 5 UAA, 140 bloc(s)
  Repositionné (ordre d'affichage MC01 corrigé, contenu inchangé) : 6 bloc(s)
```

Exactement les 6 blocs attendus (Exercice 9, Exercice 11, le bloc IA, la fiche mémo,
l'examen et son corrigé — voir `docs/claude-reports/2026-09-17_ticket-37_mc01-practice-order.md`
§ 2) ont été repositionnés. **0 création, 0 suppression** : aucune régression
pédagogique, aucun doublon possible par construction (le mécanisme ne touche jamais
`content`/`title`/`is_published`/`space`, uniquement `position` des 6 titres explicitement
listés).

### Second `seed-db` (preuve d'idempotence)

```
Seed terminé : Mathématiques (MB32, MQ32, MQ34), Informatique (AMPCR)
  Créé   : 0 matière(s), 0 module(s), 0 UAA, 0 bloc(s)
  Conservé (déjà présent, non modifié) : 2 matière(s), 4 module(s), 5 UAA, 140 bloc(s)
```

**Aucune ligne « Repositionné »** : 0 repositionnement supplémentaire. Idempotence
confirmée.

---

## 3. Audit base après migration

Requête directe sur `jury_central.db` (28 blocs MC01) :

- **0 collision** de `position` (toutes uniques, 1 à 28).
- Ordre des exercices par `position` croissante : **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12**
  — strictement conforme.
- **12/12** blocs `EDITORIAL_EXERCISE`, **12/12** en `space=PRACTICE`.
- **13** blocs `space=COURSE` (12 chapitres + fiche mémo, inchangé).
- **2** blocs `space=EXAM` (énoncé + corrigé, inchangé).
- **0** bloc `MARKDOWN` dont le titre contient « exercice » (aucun ancien contenu
  réapparu).

---

## 4. Validation page publique

`GET https://jury-central.lodylands.com/uaa/ampcr-mc01/practice` → **200**.

- Ordre des 12 titres d'exercice dans le HTML, tel que rendu : **1, 2, 3, 4, 5, 6, 7, 8,
  9, 10, 11, 12** — ordre pédagogique strict confirmé sur la page réellement servie.
- **12** blocs `.editorial-exercise-block` présents.
- **0** occurrence de « Correction : » (aucune correction visible avant action).
- Items inspectés via `data-items` (JSON) pour les 12 exercices : type et `requires_ai`
  cohérents (`classification`/`ordering` → `false` pour 1, 2, 9, 11 ; `long_answer`/
  `diagnostic`/`vocabulary` → `true` pour 3–8, 10, 12), **aucune fuite** de
  `accepted_answers`/`correct_index`/`correct_categories`/`correct_order`/`explanation`/
  `rubric` pour aucun des 12 — tous restent répondables sans qu'aucune réponse ne soit
  exposée au chargement.

Conformément à l'instruction reçue, **aucun appel OpenAI réel n'a été effectué** pour
cette validation (non nécessaire : le ticket #37 ne touche à aucun mécanisme de
correction, seulement à `position`).

---

## 5. État service / health

| Vérification | Résultat |
|---|---|
| `systemctl is-active jury-central.service` | `active` |
| `curl http://127.0.0.1:8100/health` | `200` |
| `curl https://jury-central.lodylands.com/health` | `200` |
| Page `/uaa/ampcr-mc01/practice` publique | `200` |

---

## 6. Conclusion

- Déploiement : OK, commit `1a4f274` actif.
- Migration : 6 blocs repositionnés au premier seed, 0 création, 0 suppression.
- Idempotence : confirmée (0 repositionnement au second seed).
- Ordre public : strictement 1→12.
- 12/12 exercices présents et répondables, aucune correction visible avant validation.
- COURSE (13 blocs) et EXAM (2 blocs) intacts.
- Service et santé (local + public) : OK.

**STAGING_37=PASS**
