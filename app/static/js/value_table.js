/*
 * Jury Central — composant d'exercice interactif "value_table" (docs/EXERCISE_TYPES.md).
 *
 * Le générateur ne fournit que des données JSON (question, data.columns, data.rows,
 * hint) ; ce fichier construit entièrement le tableau et son interactivité. Aucune
 * dépendance externe (vanilla JS uniquement, comme le reste du projet).
 *
 * Structure attendue sur le conteneur racine (`.value-table-exercise`) :
 *   data-exercise    JSON de l'exercice, sans la réponse (InteractiveExercise.to_public_dict())
 *   data-verify-url  URL POST acceptant {"answers": [...]}, voir app/value_table.py
 */

function buildValueTableElement(exercise) {
    const table = document.createElement("table");
    table.className = "value-table";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headRow.appendChild(document.createElement("th"));
    exercise.data.columns.forEach((column) => {
        const th = document.createElement("th");
        th.textContent = column;
        headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    exercise.data.rows.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");

        const th = document.createElement("th");
        th.scope = "row";
        th.textContent = row.label;
        tr.appendChild(th);

        row.editable.forEach((isEditable, colIndex) => {
            const td = document.createElement("td");
            if (isEditable) {
                const input = document.createElement("input");
                input.type = "text";
                input.className = "jc-fill-input value-table-input";
                input.setAttribute("aria-label", `${row.label}, colonne ${exercise.data.columns[colIndex]}`);
                input.dataset.row = String(rowIndex);
                input.dataset.col = String(colIndex);
                td.appendChild(input);
            } else {
                const value = row.values[colIndex];
                td.textContent = value === null || value === undefined ? "" : value;
            }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    const wrapper = document.createElement("div");
    wrapper.className = "table-responsive";
    wrapper.appendChild(table);
    return wrapper;
}

function collectSubmittedAnswers(root) {
    const inputs = Array.from(root.querySelectorAll(".value-table-input"));
    inputs.sort((a, b) => {
        const rowDiff = Number(a.dataset.row) - Number(b.dataset.row);
        return rowDiff !== 0 ? rowDiff : Number(a.dataset.col) - Number(b.dataset.col);
    });
    return { inputs, answers: inputs.map((input) => input.value) };
}

function findInput(root, rowIndex, colIndex) {
    return root.querySelector(
        `.value-table-input[data-row="${rowIndex}"][data-col="${colIndex}"]`
    );
}

function applyCorrection(root, correction) {
    correction.cells.forEach((cell) => {
        const input = findInput(root, cell.row, cell.col);
        if (!input) {
            return;
        }
        input.disabled = true;
        input.classList.remove("jc-fill-input--correct", "jc-fill-input--incorrect");
        input.classList.add(cell.correct ? "jc-fill-input--correct" : "jc-fill-input--incorrect");
        if (!cell.correct) {
            const answerHint = document.createElement("span");
            answerHint.className = "value-table-correct-value";
            answerHint.textContent = `→ ${cell.correct_value}`;
            input.insertAdjacentElement("afterend", answerHint);
        }
    });

    const feedback = root.querySelector(".value-table-feedback");
    feedback.innerHTML = "";
    const verdict = document.createElement("p");
    verdict.className = "fw-semibold mb-1 " + (correction.all_correct ? "text-success" : "text-danger");
    verdict.textContent = correction.all_correct
        ? "✅ Toutes les cellules sont correctes"
        : "❌ Certaines cellules sont incorrectes";
    feedback.appendChild(verdict);

    const correctionBox = root.querySelector(".value-table-correction");
    correctionBox.innerHTML = "";
    if (correction.explanation) {
        const explanationP = document.createElement("p");
        explanationP.className = "mb-1";
        explanationP.textContent = correction.explanation;
        correctionBox.appendChild(explanationP);
    }
    correctionBox.classList.remove("d-none");
}

function buildVerifyPayload(root, answers) {
    const payload = { answers };
    // Présent uniquement quand le tableau vient d'un générateur (page publique, outil de
    // debug /admin/generators) : le serveur régénère l'exercice à partir de ces valeurs
    // pour vérifier, sans jamais avoir stocké la réponse côté client. Absent pour un
    // exercice fixe (ex. /admin/value-table-demo), qui n'en a pas besoin.
    if (root.dataset.generator) {
        payload.generator = root.dataset.generator;
        payload.difficulty = Number(root.dataset.difficulty);
        payload.seed = Number(root.dataset.seed);
    }
    return payload;
}

async function verifyValueTable(root, exercise, verifyUrl) {
    const { inputs, answers } = collectSubmittedAnswers(root);
    if (answers.some((value) => value.trim() === "")) {
        const feedback = root.querySelector(".value-table-feedback");
        feedback.innerHTML = '<p class="text-warning mb-0">Complète toutes les cellules avant de vérifier.</p>';
        return;
    }

    const response = await fetch(verifyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildVerifyPayload(root, answers)),
    });
    if (!response.ok) {
        return;
    }
    const correction = await response.json();

    inputs.forEach((input) => {
        input.disabled = true;
    });
    const verifyButton = root.querySelector(".value-table-verify-btn");
    if (verifyButton) {
        verifyButton.disabled = true;
    }

    applyCorrection(root, correction);
}

function showValueTableHint(root, hint) {
    const hintBox = root.querySelector(".value-table-hint");
    if (!hintBox) {
        return;
    }
    hintBox.textContent = hint;
    hintBox.classList.remove("d-none");
}

function initValueTableExercise(root) {
    let exercise;
    try {
        exercise = JSON.parse(root.dataset.exercise);
    } catch (error) {
        return;
    }
    const verifyUrl = root.dataset.verifyUrl;

    const question = document.createElement("p");
    question.className = "value-table-question fw-semibold mb-3";
    question.textContent = exercise.question;
    root.appendChild(question);

    root.appendChild(buildValueTableElement(exercise));

    const controls = document.createElement("div");
    controls.className = "value-table-controls d-print-none mt-3 d-flex gap-3 align-items-center flex-wrap";

    const verifyButton = document.createElement("button");
    verifyButton.type = "button";
    verifyButton.className = "btn btn-outline-primary value-table-verify-btn";
    verifyButton.textContent = "Vérifier";
    verifyButton.addEventListener("click", () => verifyValueTable(root, exercise, verifyUrl));
    controls.appendChild(verifyButton);

    if (exercise.hint) {
        const hintButton = document.createElement("button");
        hintButton.type = "button";
        hintButton.className = "btn btn-link btn-sm value-table-hint-btn";
        hintButton.textContent = "Indice";
        hintButton.addEventListener("click", () => showValueTableHint(root, exercise.hint));
        controls.appendChild(hintButton);
    }

    root.appendChild(controls);

    const hintBox = document.createElement("div");
    hintBox.className = "value-table-hint d-print-none small text-muted mt-2 d-none";
    root.appendChild(hintBox);

    const feedback = document.createElement("div");
    feedback.className = "value-table-feedback d-print-none mt-3";
    root.appendChild(feedback);

    const correctionBox = document.createElement("div");
    correctionBox.className = "value-table-correction d-print-none mt-2 d-none";
    root.appendChild(correctionBox);
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".value-table-exercise").forEach(initValueTableExercise);
});
