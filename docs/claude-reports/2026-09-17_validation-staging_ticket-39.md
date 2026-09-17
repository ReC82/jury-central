# Validation staging — ticket #39 (Comptes V1 : authentification)

**Date** : 2026-09-17
**PR mergée** : #52
**Commit develop déployé** : `413ef38f59228210df786435425604af617dfe2c`
**Environnement** : staging (`jury-central.lodylands.com`), déploiement via
`./scripts/deploy_staging.sh`, sans reset-db, sans suppression de `jury_central.db`.

Aucun mot de passe ni hash n'apparaît dans ce rapport, conformément à l'instruction reçue.

---

## 1. Déploiement

```
git checkout develop && git pull --ff-only origin develop   → fast-forward 192c52a → 413ef38
./scripts/deploy_staging.sh
```

Résultat : **succès**. Branche `develop`, working tree propre, fast-forward propre,
suite de tests exécutée par le script lui-même : **508 passed**, 2 warnings préexistants
(httpx/anyio). `jury_central.db` non touchée par le script (ni seed, ni reset). Service
redémarré et actif, `http://127.0.0.1:8100/health` répond.

---

## 2. Migration réelle des colonnes d'authentification

`app/main.py` exécute `Base.metadata.create_all()` puis `ensure_schema_migrations()` au
démarrage — ce redémarrage de service (étape 1) a suffi à appliquer la migration, sans
étape séparée.

Vérifié directement en base après redémarrage :

- `v1_users` existe.
- Colonnes présentes (entre autres) : `password_hash` (VARCHAR(255)), `last_login_at`
  (DATETIME), plus `id`/`email`/`display_name`/`role`/`plan`/`is_active`/`created_at`/
  `updated_at`.
- Table `v1_users` vide avant le compte de validation créé à l'étape 8 (0 ligne) — cette
  table n'ayant jamais reçu de données réelles avant ce ticket (voir rapports #38/#39),
  elle a été créée directement dans sa forme complète par `create_all` plutôt que d'
  exercer concrètement le chemin `ALTER TABLE` sur une ligne existante ; ce chemin est
  couvert séparément par les tests automatisés du ticket (`tests/test_ticket39_v1_auth.py`,
  scénarios 20/21, base synthétique).
- **Tables/données historiques intactes** : `subjects=2`, `modules=4`, `uaas=5`,
  `lesson_blocks=140` — valeurs identiques à celles constatées lors des validations
  staging précédentes (#37).
- Aucun `reset-db`, aucune suppression de `jury_central.db` à aucun moment.

---

## 3. Service / health

| Vérification | Résultat |
|---|---|
| `systemctl is-active jury-central.service` | `active` |
| `curl http://127.0.0.1:8100/health` | `200` |
| `curl https://jury-central.lodylands.com/health` | `200` |

---

## 4. Cours publics (sans compte)

| Route | Résultat |
|---|---|
| `GET /` | `200` |
| `GET /subjects` | `200` |
| `GET /uaa/ampcr-mc01` | `200` |

Conforme : les cours restent consultables sans compte.

---

## 5. Practice/Exam protégés anonymement

| Route | Résultat |
|---|---|
| `GET /uaa/ampcr-mc01/practice` (anonyme) | `303` → `Location: /login?next=/uaa/ampcr-mc01/practice` |
| `GET /uaa/ampcr-mc01/exam` (anonyme) | `303` → `Location: /login?next=/uaa/ampcr-mc01/exam` |

`next` correct et local dans les deux cas (chemin exact de la page demandée).

---

## 6. Compte staging de validation

Un seul compte créé, adresse clairement temporaire du modèle
`staging-auth39-<timestamp>@example.invalid`, mot de passe aléatoire fort généré
localement (jamais affiché, jamais journalisé).

- **Inscription HTTP** : `POST /register` → `303` (succès).
- **`role`** : `STUDENT` (défaut confirmé).
- **`plan`** : `FREE` (défaut confirmé).
- **`password_hash`** : présent en base, format Argon2id confirmé (préfixe
  `$argon2id$`) — valeur jamais lue au-delà de cette vérification de format, jamais
  affichée.
- Aucun mot de passe en clair trouvé en base (seule la colonne `password_hash` existe
  pour cette donnée).
- Une seule ligne dans `v1_users` après l'ensemble de la validation — aucun compte
  supplémentaire créé (une tentative d'inscription avec un jeton CSRF invalide, faite
  exprès pour le test du § 8, a bien été rejetée sans créer de ligne).

---

## 7. Session réelle HTTPS avec cookies

- **Login** : `POST /login` avec les identifiants du compte de validation → `303`.
- **`GET /account`** (connecté) : `200`, email du compte affiché.
- **`GET /uaa/ampcr-mc01/practice`** (connecté) : `200`.
- **`GET /uaa/ampcr-mc01/exam`** (connecté) : `200`.
- **Cookie de session** (`Set-Cookie` réel observé) : `httponly; samesite=lax; secure`
  — les trois protections attendues sont actives, `secure` confirmé car le service est
  servi en HTTPS réel (`APP_ENV=staging` sur ce serveur, voir
  `docs/auth_v1.md` § 6.1).
- **Logout** : `POST /logout` avec jeton CSRF valide → `303`, cookie de session
  renouvelé sans l'identifiant utilisateur.
- **Après logout** : `GET /account` → `303` vers `/login?next=/account` ;
  `GET /uaa/ampcr-mc01/practice` → `303` vers `/login?next=/uaa/ampcr-mc01/practice`.
  Session bien invalidée.

---

## 8. CSRF

| Cas | Résultat |
|---|---|
| `POST /login` avec jeton CSRF invalide | `400` |
| `POST /register` avec jeton CSRF invalide | `400` (aucune ligne créée) |
| `POST /logout` avec jeton CSRF invalide (session active) | `303`, mais session **conservée** (échec silencieux volontaire — voir `docs/auth_v1.md` § 5) ; confirmé via `GET /account` toujours `200` juste après |
| Parcours normal avec jeton CSRF valide | Inscription, connexion et déconnexion fonctionnent (§ 6/7) |

Comportement conforme à la politique documentée dans `docs/auth_v1.md`.

---

## 9. Open redirect

`POST /login` avec `next=https://evil.example/` et identifiants valides →
`303` vers `Location: /` (jamais vers le domaine externe fourni). Protection confirmée
en conditions réelles.

---

## 10. Admin historique

`GET /admin/login` → `200`, page de connexion admin toujours servie normalement,
aucune modification apportée à ce mécanisme par ce ticket. Non-régression déjà
confirmée exhaustivement par la suite automatisée (508 tests, dont des tests dédiés
admin/V1 non-interférence) exécutée par le script de déploiement lui-même (§ 1) — aucun
identifiant admin réel n'a été utilisé pendant cette validation manuelle, pour ne pas
manipuler le compte admin réel sans nécessité.

---

## 11. Appels OpenAI

Aucun appel OpenAI réel effectué à aucune étape de cette validation (non nécessaire :
ticket #39 ne touche à aucun mécanisme de génération/correction IA).

---

## 12. Conclusion

- Déploiement : OK, commit `413ef38` actif.
- Migration des colonnes d'authentification : confirmée, données historiques intactes.
- Service et santé (local + public) : OK.
- Cours publics : accessibles sans compte.
- Practice/Exam : protégés anonymement, `next` correct.
- Inscription, connexion, `/account`, déconnexion : fonctionnels en conditions HTTPS
  réelles, un seul compte de validation créé.
- Cookie de session : HttpOnly + SameSite=Lax + Secure tous confirmés actifs.
- CSRF : protège inscription/connexion (400 si invalide), déconnexion fail-safe
  (session conservée si jeton invalide).
- Open redirect : rejeté, jamais de redirection externe.
- Admin historique : accessible, non modifié, non régressé.

**STAGING_39=PASS**
