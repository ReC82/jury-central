const PROGRESS_STORAGE_KEY = "jury-central-progress";

// Ticket #136 : libellés de LECTURE uniquement (stockés sur cet appareil) — jamais
// confondus avec « entraîné » ou « examen blanc réussi », calculés côté serveur.
const PROGRESS_LABELS = {
    todo: "Pas encore ouvert",
    in_progress: "Consulté",
    done: "Lu jusqu'au bout",
};

const PROGRESS_CLASSES = {
    todo: "text-bg-secondary",
    in_progress: "text-bg-warning",
    done: "text-bg-success",
};

function loadProgress() {
    try {
        return JSON.parse(localStorage.getItem(PROGRESS_STORAGE_KEY)) || {};
    } catch (error) {
        return {};
    }
}

function saveProgress(progress) {
    localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(progress));
}

function getUaaStatus(slug) {
    return loadProgress()[slug] || "todo";
}

function setUaaStatus(slug, status) {
    const progress = loadProgress();
    if (status === "todo") {
        delete progress[slug];
    } else {
        progress[slug] = status;
    }
    saveProgress(progress);
}

function markVisited(slug) {
    if (getUaaStatus(slug) === "todo") {
        setUaaStatus(slug, "in_progress");
    }
}

function aggregateStatus(slugs) {
    if (slugs.length === 0) {
        return "todo";
    }
    const statuses = slugs.map(getUaaStatus);
    if (statuses.every((status) => status === "done")) {
        return "done";
    }
    if (statuses.every((status) => status === "todo")) {
        return "todo";
    }
    return "in_progress";
}

function renderBadge(el, status) {
    el.textContent = PROGRESS_LABELS[status];
    el.className = "badge progress-badge " + PROGRESS_CLASSES[status];
}

function refreshProgressBadges() {
    document.querySelectorAll("[data-uaa-slug-badge]").forEach((el) => {
        renderBadge(el, getUaaStatus(el.dataset.uaaSlugBadge));
    });
    document.querySelectorAll("[data-uaa-slugs]").forEach((el) => {
        const slugs = el.dataset.uaaSlugs.split(",").filter(Boolean);
        renderBadge(el, aggregateStatus(slugs));
    });
}

function initCompleteButton() {
    const button = document.querySelector(".mark-complete-btn");
    if (!button) {
        return;
    }
    const slug = button.dataset.uaaSlug;
    markVisited(slug);

    function updateButton() {
        const status = getUaaStatus(slug);
        if (status === "done") {
            button.textContent = "Lu jusqu'au bout ✓ (annuler)";
            button.classList.remove("btn-dark");
            button.classList.add("btn-outline-success");
        } else {
            button.textContent = "J'ai lu ce cours jusqu'au bout";
            button.classList.remove("btn-outline-success");
            button.classList.add("btn-dark");
        }
    }

    button.addEventListener("click", () => {
        const current = getUaaStatus(slug);
        setUaaStatus(slug, current === "done" ? "in_progress" : "done");
        updateButton();
        refreshProgressBadges();
    });

    updateButton();
}

document.addEventListener("DOMContentLoaded", () => {
    initCompleteButton();
    refreshProgressBadges();
});
