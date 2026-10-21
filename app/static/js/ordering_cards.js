/*
 * Remise en ordre par cartes (ticket #153) — composant partagé entraînement / examen
 * blanc / quiz (gabarit `app/templates/_ordering_cards.html`).
 *
 * - Glisser-déposer souris et tactile via SortableJS (MIT, vendorisé dans
 *   `app/static/vendor/sortablejs/`). Le déplacement ne démarre QUE depuis la poignée :
 *   ailleurs sur la carte, le doigt fait défiler la page normalement sur téléphone.
 * - Alternative sans glisser : boutons Monter/Descendre et Alt + ↑ / Alt + ↓ sur une
 *   carte ; le focus reste sur la carte déplacée et le changement est annoncé
 *   (zone aria-live).
 * - Réponse = champs cachés `position__<id>` (même contrat serveur qu'avant). L'ordre
 *   affiché au chargement n'est JAMAIS enregistré sans action : seuls un déplacement ou
 *   « Conserver cet ordre » remplissent les positions.
 * - Si `data-autosave-url` est présent (entraînement/examen), l'ordre est sauvegardé
 *   tout de suite par identifiants via l'API d'autosave existante. Aucune correction,
 *   aucune solution : le serveur ne renvoie que la confirmation d'enregistrement.
 */
(function () {
    "use strict";

    function initOrdering(root) {
        const fallback = root.querySelector("[data-jc-order-fallback]");
        const enhanced = root.querySelector("[data-jc-order-enhanced]");
        const list = root.querySelector("[data-jc-order-list]");
        const status = root.querySelector("[data-jc-order-status]");
        const live = root.querySelector("[data-jc-order-live]");
        const keepButton = root.querySelector("[data-jc-order-keep]");
        const autosaveUrl = root.dataset.autosaveUrl || "";
        if (!fallback || !enhanced || !list) {
            return;
        }

        // Les listes de positions (repli sans JS) cèdent la place à des champs cachés qui
        // gardent EXACTEMENT les valeurs enregistrées (y compris une saisie partielle).
        const inputs = {};
        fallback.querySelectorAll("select[name^='position__']").forEach((select) => {
            const hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.name = select.name;
            hidden.value = select.value || "0";
            inputs[select.name.slice("position__".length)] = hidden;
            root.appendChild(hidden);
        });
        fallback.remove();
        enhanced.hidden = false;

        let answered = root.dataset.answered === "true";
        let saveTimer = null;
        let saveSeq = 0;

        function cards() {
            return Array.from(list.querySelectorAll(".jc-order-card"));
        }

        function currentOrder() {
            return cards().map((card) => card.dataset.id);
        }

        function setStatus(text, tone) {
            if (!status) {
                return;
            }
            status.textContent = text;
            status.dataset.tone = tone || "";
        }

        function refresh() {
            const all = cards();
            all.forEach((card, index) => {
                card.querySelector(".jc-order-pos").textContent = String(index + 1);
                card.querySelector("[data-move='-1']").disabled = index === 0;
                card.querySelector("[data-move='1']").disabled = index === all.length - 1;
            });
            root.classList.toggle("is-answered", answered);
            if (keepButton) {
                keepButton.hidden = answered;
            }
        }

        function renderInitialStatus() {
            if (answered) {
                setStatus(autosaveUrl ? "Ordre enregistré." : "Ordre choisi.", "ok");
            } else {
                setStatus(
                    "Pas encore répondu : déplace les cartes, ou choisis « Conserver cet ordre » si cet ordre te semble juste.",
                    "todo"
                );
            }
        }

        function autosave() {
            if (!autosaveUrl) {
                return;
            }
            window.clearTimeout(saveTimer);
            setStatus("Enregistrement…", "pending");
            saveTimer = window.setTimeout(async () => {
                const seq = ++saveSeq;
                try {
                    const response = await fetch(autosaveUrl, {
                        method: "POST",
                        credentials: "same-origin",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ answer_json: { order: currentOrder() } }),
                    });
                    if (seq !== saveSeq) {
                        return;
                    }
                    if (!response.ok) {
                        throw new Error(String(response.status));
                    }
                    setStatus("Ordre enregistré.", "ok");
                } catch (error) {
                    if (seq === saveSeq) {
                        setStatus(
                            "Ordre choisi, pas encore enregistré : il le sera en passant à une autre question.",
                            "warn"
                        );
                    }
                }
            }, 350);
        }

        // Après une action de l'élève : l'ordre visible devient la réponse.
        function commit() {
            currentOrder().forEach((id, index) => {
                if (inputs[id]) {
                    inputs[id].value = String(index + 1);
                }
            });
            answered = true;
            refresh();
            if (autosaveUrl) {
                autosave();
            } else {
                setStatus("Ordre choisi. Valide quand tu es prêt·e.", "ok");
            }
        }

        function announce(card) {
            if (!live) {
                return;
            }
            const all = cards();
            const label = card.querySelector(".jc-order-label").textContent.trim();
            live.textContent =
                "« " + label + " » déplacé en position " + (all.indexOf(card) + 1) + " sur " + all.length + ".";
        }

        function move(card, delta) {
            const all = cards();
            const index = all.indexOf(card);
            const target = index + delta;
            if (target < 0 || target >= all.length) {
                return false;
            }
            if (delta < 0) {
                list.insertBefore(card, all[target]);
            } else {
                list.insertBefore(card, all[target].nextSibling);
            }
            card.classList.remove("is-moved");
            void card.offsetWidth; // relance l'animation de retour visuel
            card.classList.add("is-moved");
            commit();
            announce(card);
            return true;
        }

        list.addEventListener("click", (event) => {
            const button = event.target.closest(".jc-order-btn");
            if (!button || button.disabled) {
                return;
            }
            const card = button.closest(".jc-order-card");
            const delta = parseInt(button.dataset.move, 10);
            if (move(card, delta)) {
                // Focus conservé : même bouton s'il reste utilisable, sinon l'autre.
                const same = card.querySelector("[data-move='" + delta + "']");
                const other = card.querySelector("[data-move='" + -delta + "']");
                (same.disabled ? other : same).focus();
            }
        });

        list.addEventListener("keydown", (event) => {
            if (!event.altKey || (event.key !== "ArrowUp" && event.key !== "ArrowDown")) {
                return;
            }
            const card = event.target.closest(".jc-order-card");
            if (!card) {
                return;
            }
            event.preventDefault();
            const focused = document.activeElement;
            move(card, event.key === "ArrowUp" ? -1 : 1);
            if (focused && card.contains(focused) && !focused.disabled) {
                focused.focus();
            } else {
                card.focus();
            }
        });

        if (keepButton) {
            keepButton.addEventListener("click", () => {
                commit();
                if (live) {
                    live.textContent = "Ordre affiché conservé comme réponse.";
                }
                const first = cards()[0];
                if (first) {
                    first.focus();
                }
            });
        }

        if (window.Sortable) {
            window.Sortable.create(list, {
                handle: ".jc-order-handle",
                draggable: ".jc-order-card",
                animation: 160,
                ghostClass: "is-ghost",
                chosenClass: "is-chosen",
                dragClass: "is-dragging",
                // Tactile : léger appui sur la poignée avant de déplacer, pour qu'un simple
                // balayage fasse toujours défiler la page.
                delay: 120,
                delayOnTouchOnly: true,
                touchStartThreshold: 4,
                fallbackTolerance: 3,
                onStart: () => root.classList.add("is-sorting"),
                onEnd: (event) => {
                    root.classList.remove("is-sorting");
                    if (event.oldIndex !== event.newIndex) {
                        commit();
                        announce(event.item);
                    }
                },
            });
        } else {
            root.classList.add("no-drag");
        }

        // Quiz (pas d'autosave) : la validation est volontaire et suppose une réponse ;
        // on l'explique ici plutôt que d'envoyer un formulaire incomplet. En entraînement
        // et en examen, passer une question sans réponse reste toujours permis.
        const form = root.closest("form");
        if (!autosaveUrl && form) {
            form.addEventListener("submit", (event) => {
                if (!answered) {
                    event.preventDefault();
                    event.stopImmediatePropagation();
                    setStatus(
                        "Déplace les cartes, ou choisis « Conserver cet ordre », avant de valider.",
                        "warn"
                    );
                    if (keepButton) {
                        keepButton.focus();
                    }
                }
            });
        }

        refresh();
        renderInitialStatus();
    }

    function initAll() {
        document.querySelectorAll("[data-jc-ordering]").forEach(initOrdering);
    }

    // Script chargé en fin de page, après le formulaire : initialisation immédiate, pour
    // que la garde de validation du quiz passe avant l'anti-double soumission de la page.
    initAll();
})();
