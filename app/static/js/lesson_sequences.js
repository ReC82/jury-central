/*
 * Leçon en séquences courtes (ticket #136).
 *
 * Découpe l'AFFICHAGE d'un cours en séquences — jamais le contenu : aucun nœud n'est
 * supprimé ni réécrit, on regroupe seulement les éléments existants et on masque ceux qui
 * ne sont pas la séquence courante. Deux cas :
 * - un seul bloc de cours long (AMPCR, Français) : une séquence par titre <h2> ;
 * - plusieurs cartes (FSE, Mathématiques) : une séquence par carte.
 * Chaque séquence reçoit une étape « Comprendre / Observer un exemple / Essayer / Retenir »
 * déduite de son titre (icône + texte, jamais la couleur seule). « Tout afficher » rend le
 * cours complet ; sans JS et à l'impression, tout reste visible. Séquences vues et
 * position mémorisées sur cet appareil (localStorage), comme `progress.js`.
 */
(function () {
    "use strict";

    const PHASES = [
        { key: "understand", label: "Comprendre", icon: "bi-lightbulb" },
        { key: "observe", label: "Observer un exemple", icon: "bi-eye" },
        { key: "try", label: "Essayer", icon: "bi-pencil" },
        { key: "remember", label: "Retenir", icon: "bi-bookmark-star" },
    ];

    function phaseFor(title) {
        const t = (title || "").toLowerCase();
        if (/(retenir|mémo|memo|résumé|synthèse|vocabulaire|lexique|fiche)/.test(t)) return "remember";
        if (/(exercice|corrigé|entraîn|à toi|quiz|mini-test|essaie|application)/.test(t)) return "try";
        if (/(exemple|cas concret|situation|illustration|transfert|comparées|comparer)/.test(t)) return "observe";
        return "understand";
    }

    function storageKey(slug) {
        return "jury-central-sequences:" + slug;
    }

    function loadState(slug) {
        try {
            return JSON.parse(localStorage.getItem(storageKey(slug))) || {};
        } catch (error) {
            return {};
        }
    }

    function saveState(slug, state) {
        try {
            localStorage.setItem(storageKey(slug), JSON.stringify(state));
        } catch (error) {
            /* stockage indisponible : la navigation fonctionne quand même */
        }
    }

    function splitByHeadings(container) {
        const headings = Array.from(container.children).filter((el) => el.tagName === "H2");
        if (headings.length < 3) return null;
        const sections = [];
        let current = { title: "Introduction", nodes: [] };
        Array.from(container.childNodes).forEach((node) => {
            if (node.nodeType === 1 && node.tagName === "H2") {
                if (current.nodes.some((n) => n.nodeType === 1 || (n.textContent || "").trim())) {
                    sections.push(current);
                }
                current = { title: node.textContent.trim(), nodes: [] };
            }
            current.nodes.push(node);
        });
        sections.push(current);
        // Une introduction réduite à un titre <h1> (+ blancs) est fusionnée avec la 1re séquence
        if (sections.length > 1 && sections[0].title === "Introduction") {
            const meaningful = sections[0].nodes.filter(
                (n) => n.nodeType === 1 && n.tagName !== "H1"
            );
            if (meaningful.length === 0) {
                sections[1].nodes = sections[0].nodes.concat(sections[1].nodes);
                sections.shift();
            }
        }
        return sections.map((section) => {
            const wrapper = document.createElement("section");
            wrapper.className = "jc-seq";
            container.insertBefore(wrapper, section.nodes[0]);
            section.nodes.forEach((n) => wrapper.appendChild(n));
            return { title: section.title, el: wrapper };
        });
    }

    function buildSequences(root) {
        const cards = Array.from(root.querySelectorAll(":scope > .jc-card"));
        if (cards.length === 1) {
            const md = cards[0].querySelector(".content-markdown");
            return md ? splitByHeadings(md) : null;
        }
        if (cards.length >= 3) {
            return cards.map((card) => {
                const titleEl = card.querySelector(".jc-card-title");
                const label = card.querySelector(".jc-card-label");
                return {
                    title: (titleEl || label || card).textContent.trim(),
                    el: card,
                };
            });
        }
        return null;
    }

    function el(tag, attrs, html) {
        const node = document.createElement(tag);
        Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, v));
        if (html !== undefined) node.innerHTML = html;
        return node;
    }

    function init() {
        const root = document.getElementById("jc-lesson");
        if (!root) return;
        const sequences = buildSequences(root);
        if (!sequences || sequences.length < 3) return;

        const slug = root.dataset.uaaSlug;
        const practiceUrl = root.dataset.practiceUrl;
        const state = loadState(slug);
        const seen = new Set(state.seen || []);
        let mode = state.mode === "all" ? "all" : "steps";
        let index = Math.min(state.index || 0, sequences.length - 1);
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        sequences.forEach((seq, i) => {
            seq.phase = phaseFor(seq.title);
            seq.el.id = seq.el.id || "sequence-" + (i + 1);
            seq.el.setAttribute("data-seq-index", String(i));
            const phase = PHASES.find((p) => p.key === seq.phase);
            const chip = el(
                "p",
                { class: "jc-seq-phase-chip d-print-none" },
                '<span class="jc-pill jc-pill-primary"><i class="bi ' + phase.icon +
                    '" aria-hidden="true"></i> Séquence ' + (i + 1) + "/" + sequences.length +
                    " · " + phase.label + "</span>"
            );
            seq.el.insertBefore(chip, seq.el.firstChild);
        });

        // Barre : étapes + pastilles numérotées + bascule d'affichage
        const bar = el("div", { class: "jc-seq-bar d-print-none", role: "region", "aria-label": "Séquences du cours" });
        const phases = el("ol", { class: "jc-seq-phases", "aria-label": "Étapes de la leçon" });
        PHASES.forEach((p) => {
            const li = el("li", { "data-phase": p.key }, '<i class="bi ' + p.icon + '" aria-hidden="true"></i>' + p.label);
            if (!sequences.some((s) => s.phase === p.key)) li.classList.add("is-empty");
            phases.appendChild(li);
        });
        const dots = el("div", { class: "jc-seq-dots", "aria-label": "Aller à une séquence" });
        sequences.forEach((seq, i) => {
            const b = el("button", { type: "button", title: seq.title, "aria-label": "Séquence " + (i + 1) + " : " + seq.title }, String(i + 1));
            b.addEventListener("click", () => go(i, true));
            dots.appendChild(b);
        });
        const toggle = el("button", { type: "button", class: "btn btn-link btn-sm p-0 mt-2" });
        toggle.addEventListener("click", () => {
            mode = mode === "all" ? "steps" : "all";
            render(false);
        });
        bar.appendChild(phases);
        bar.appendChild(dots);
        bar.appendChild(toggle);
        root.parentNode.insertBefore(bar, root);

        const nav = el("div", { class: "jc-seq-nav d-print-none" });
        const prev = el("button", { type: "button", class: "jc-btn jc-btn-ghost jc-btn-sm" }, '<i class="bi bi-arrow-left" aria-hidden="true"></i> Précédent');
        const counter = el("span", { class: "jc-stat", "aria-live": "polite" });
        const next = el("button", { type: "button", class: "jc-btn jc-btn-primary jc-btn-sm" });
        const finish = el("a", { class: "jc-btn jc-btn-primary jc-btn-sm", href: practiceUrl }, '<i class="bi bi-pencil-square" aria-hidden="true"></i> Passer à l\'entraînement');
        prev.addEventListener("click", () => go(index - 1, true));
        next.addEventListener("click", () => go(index + 1, true));
        nav.appendChild(prev);
        nav.appendChild(counter);
        nav.appendChild(next);
        nav.appendChild(finish);
        root.parentNode.insertBefore(nav, root.nextSibling);

        function persist() {
            saveState(slug, { seen: Array.from(seen), index: index, mode: mode });
        }

        function go(i, scroll) {
            index = Math.max(0, Math.min(sequences.length - 1, i));
            mode = "steps";
            render(scroll);
        }

        function render(scroll) {
            const steps = mode === "steps";
            if (steps) seen.add(index);
            sequences.forEach((seq, i) => {
                const hidden = steps && i !== index;
                seq.el.classList.toggle("jc-seq-hidden", hidden);
                if (!hidden && steps && !reduceMotion) {
                    seq.el.classList.remove("jc-seq-enter");
                    void seq.el.offsetWidth;
                    seq.el.classList.add("jc-seq-enter");
                }
            });
            Array.from(dots.children).forEach((b, i) => {
                b.classList.toggle("is-seen", seen.has(i));
                if (steps && i === index) b.setAttribute("aria-current", "step");
                else b.removeAttribute("aria-current");
            });
            const currentPhase = sequences[index].phase;
            Array.from(phases.children).forEach((li) => {
                li.classList.toggle("is-current", steps && li.dataset.phase === currentPhase);
            });
            toggle.textContent = steps ? "Afficher tout le cours sur une page" : "Revenir au mode séquence par séquence";
            nav.style.display = steps ? "" : "none";
            prev.disabled = index === 0;
            const last = index === sequences.length - 1;
            next.style.display = last ? "none" : "";
            finish.style.display = last ? "" : "none";
            next.innerHTML = 'Séquence suivante <i class="bi bi-arrow-right" aria-hidden="true"></i>';
            counter.textContent = "Séquence " + (index + 1) + " sur " + sequences.length +
                " — " + seen.size + " vue" + (seen.size > 1 ? "s" : "");
            persist();
            // Graphiques (Plotly) d'une séquence auparavant masquée : recalcul de taille
            window.dispatchEvent(new Event("resize"));
            if (scroll) {
                bar.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
            }
        }

        // Lien direct vers une ancre : afficher la séquence qui la contient
        if (location.hash) {
            const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
            const host = target && target.closest("[data-seq-index]");
            if (host) index = Number(host.getAttribute("data-seq-index"));
        }
        render(false);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
