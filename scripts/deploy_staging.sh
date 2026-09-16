#!/usr/bin/env bash
#
# Jury Central — déploiement staging.
#
# Met à jour /srv/jury-central depuis origin/develop et redémarre jury-central.service,
# uniquement si toutes les vérifications de sécurité passent. Voir
# docs/deployment_staging.md pour la procédure complète et le diagnostic en cas d'échec.
#
# Ce script ne touche jamais jury_central.db (pas de seed/reset), n'affiche, ne modifie
# ni ne commit jamais le contenu de .env, et ne modifie ni nginx, ni Certbot, ni la
# définition du service systemd.
#
# Usage : scripts/deploy_staging.sh
# Doit être exécuté depuis le dépôt de déploiement (/srv/jury-central), par un compte
# autorisé à faire `sudo systemctl restart jury-central.service`.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

REQUIRED_BRANCH="develop"
SERVICE_NAME="jury-central.service"
HEALTH_URL="http://127.0.0.1:8100/health"
VENV_DIR="$REPO_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
HEALTH_CHECK_ATTEMPTS=10
HEALTH_CHECK_DELAY_SECONDS=2

log() {
    printf '[deploy] %s\n' "$1"
}

fail() {
    printf '[deploy] ERREUR : %s\n' "$1" >&2
    exit 1
}

log "démarrage du déploiement staging depuis $REPO_DIR"

# --- 1. Le dépôt doit exister et être un dépôt git -------------------------------------
[ -d "$REPO_DIR/.git" ] || fail "$REPO_DIR n'est pas un dépôt git"

# --- 2. Refuser toute branche autre que develop -----------------------------------------
current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$current_branch" != "$REQUIRED_BRANCH" ]; then
    fail "branche actuelle '$current_branch' — seule la branche '$REQUIRED_BRANCH' peut être déployée. Aucune modification effectuée."
fi
log "branche vérifiée : $current_branch"

# --- 3. Refuser un working tree sale ------------------------------------------------------
if [ -n "$(git status --porcelain)" ]; then
    fail "working tree non propre (modifications ou fichiers non suivis présents) — commit, stash ou nettoie avant de redéployer. Aucune modification effectuée."
fi
log "working tree propre"

# --- 4. Synchroniser avec origin/develop, jamais en écrasant du travail local ------------
log "récupération de origin/$REQUIRED_BRANCH"
git fetch origin "$REQUIRED_BRANCH" || fail "échec de 'git fetch origin $REQUIRED_BRANCH'"

if ! git merge --ff-only "origin/$REQUIRED_BRANCH"; then
    fail "impossible d'avancer en fast-forward vers origin/$REQUIRED_BRANCH (historique divergent) — le script ne force jamais un reset ; résoudre manuellement puis relancer."
fi
new_commit="$(git rev-parse --short HEAD)"
log "synchronisé sur origin/$REQUIRED_BRANCH ($new_commit)"

# --- 5. Environnement virtuel existant, jamais recréé automatiquement --------------------
if [ ! -x "$VENV_PYTHON" ]; then
    fail ".venv introuvable ou incomplet ($VENV_DIR) — créer l'environnement virtuel manuellement avant le premier déploiement (voir docs/development.md)."
fi
log ".venv existant détecté"

# --- 6. Fichier .env présent (jamais lu ni affiché) ---------------------------------------
if [ ! -f "$REPO_DIR/.env" ]; then
    fail ".env absent de $REPO_DIR — le service ne pourra pas démarrer. Le déployer manuellement, hors Git, avant de relancer ce script."
fi
log ".env présent (contenu non lu, non affiché)"

# --- 7. Installer/mettre à jour les dépendances dans le .venv existant -------------------
log "installation/mise à jour des dépendances (.venv existant)"
"$VENV_PIP" install --quiet -e ".[dev]" || fail "échec de l'installation des dépendances"

# --- 8. Exécuter la suite de tests : aucun redémarrage si elle échoue --------------------
log "exécution de la suite de tests (pytest -q)"
if ! "$VENV_PYTHON" -m pytest -q; then
    fail "tests en échec — service NON redémarré. Corriger avant de redéployer."
fi
log "tests au vert"

# --- 9. Rappel explicite : ce script ne touche jamais la base ----------------------------
log "jury_central.db non modifiée (ni seed, ni reset — décision explicite séparée requise, voir docs/deployment_staging.md)"

# --- 10. Redémarrer le service systemd, uniquement maintenant ----------------------------
log "redémarrage de $SERVICE_NAME"
if ! sudo systemctl restart "$SERVICE_NAME"; then
    fail "échec de 'systemctl restart $SERVICE_NAME' — diagnostiquer avec : journalctl -u $SERVICE_NAME -n 50 --no-pager"
fi

# --- 11. Vérifier que le service est bien 'active' ----------------------------------------
service_active=""
for _ in $(seq 1 "$HEALTH_CHECK_ATTEMPTS"); do
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        service_active="1"
        break
    fi
    sleep "$HEALTH_CHECK_DELAY_SECONDS"
done
if [ -z "$service_active" ]; then
    fail "$SERVICE_NAME n'est pas 'active' après redémarrage — diagnostiquer avec : journalctl -u $SERVICE_NAME -n 50 --no-pager"
fi
log "$SERVICE_NAME est actif"

# --- 12. Vérifier qu'un endpoint local répond ----------------------------------------------
endpoint_ok=""
for _ in $(seq 1 "$HEALTH_CHECK_ATTEMPTS"); do
    if curl --fail --silent --show-error --max-time 5 "$HEALTH_URL" > /dev/null 2>&1; then
        endpoint_ok="1"
        break
    fi
    sleep "$HEALTH_CHECK_DELAY_SECONDS"
done
if [ -z "$endpoint_ok" ]; then
    fail "$HEALTH_URL ne répond pas après redémarrage — diagnostiquer avec : journalctl -u $SERVICE_NAME -n 50 --no-pager"
fi
log "$HEALTH_URL répond"

log "déploiement staging terminé avec succès (commit $new_commit)"
