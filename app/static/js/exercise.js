async function postJson(url, body) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        return null;
    }
    return response.json();
}

function exerciseWidgetPayload(widget) {
    return {
        generator: widget.dataset.generator,
        difficulty: parseInt(widget.dataset.difficulty, 10),
        seed: parseInt(widget.dataset.seed, 10),
    };
}

async function checkExerciseAnswer(button) {
    const widget = button.closest(".exercise-widget");
    const input = widget.querySelector(".exercise-answer-input");
    const feedback = widget.querySelector(".exercise-feedback");

    if (!input.value.trim()) {
        feedback.textContent = "Merci d'entrer une réponse.";
        feedback.className = "exercise-feedback small mb-2 text-warning";
        return;
    }

    const result = await postJson("/practice/api/verify", {
        ...exerciseWidgetPayload(widget),
        answer: input.value,
    });
    if (!result) {
        return;
    }

    feedback.textContent = result.correct ? "Correct !" : "Incorrect, réessaie.";
    feedback.className = "exercise-feedback small mb-2 " + (result.correct ? "text-success" : "text-danger");
}

function showExerciseHint(button) {
    const widget = button.closest(".exercise-widget");
    const hintBox = widget.querySelector(".exercise-hint");
    hintBox.textContent = button.dataset.hint;
    hintBox.classList.remove("d-none");
}

async function revealExerciseCorrection(button) {
    const widget = button.closest(".exercise-widget");
    const stepsList = widget.querySelector(".exercise-steps");

    const result = await postJson("/practice/api/reveal", exerciseWidgetPayload(widget));
    if (!result) {
        return;
    }

    stepsList.innerHTML = "";
    result.solution_steps.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        stepsList.appendChild(li);
    });
    stepsList.classList.remove("d-none");
    button.disabled = true;
}

async function newExercise(button) {
    const widget = button.closest(".exercise-widget");
    const generator = widget.dataset.generator;
    const difficulty = widget.dataset.difficulty;

    const response = await fetch(
        `/practice/api/generate?generator=${encodeURIComponent(generator)}&difficulty=${encodeURIComponent(difficulty)}`
    );
    if (!response.ok) {
        return;
    }
    const data = await response.json();

    widget.dataset.seed = data.seed;
    widget.querySelector(".exercise-statement").textContent = data.statement;
    widget.querySelector(".exercise-answer-input").value = "";

    const feedback = widget.querySelector(".exercise-feedback");
    feedback.textContent = "";
    feedback.className = "exercise-feedback small mb-2";

    const hintButton = widget.querySelector(".exercise-hint-btn");
    if (hintButton) {
        hintButton.dataset.hint = data.hint || "";
    }
    const hintBox = widget.querySelector(".exercise-hint");
    if (hintBox) {
        hintBox.classList.add("d-none");
        hintBox.textContent = "";
    }

    const stepsList = widget.querySelector(".exercise-steps");
    stepsList.innerHTML = "";
    stepsList.classList.add("d-none");

    const revealButton = widget.querySelector(".exercise-reveal-btn");
    if (revealButton) {
        revealButton.disabled = false;
    }
}

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("exercise-check-btn")) {
        checkExerciseAnswer(event.target);
    }
    if (event.target.classList.contains("exercise-hint-btn")) {
        showExerciseHint(event.target);
    }
    if (event.target.classList.contains("exercise-reveal-btn")) {
        revealExerciseCorrection(event.target);
    }
    if (event.target.classList.contains("exercise-new-btn")) {
        newExercise(event.target);
    }
});
