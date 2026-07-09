document.addEventListener("click", (event) => {
    if (!event.target.classList.contains("quiz-choice-btn")) {
        return;
    }

    const button = event.target;
    const widget = button.closest(".quiz-widget");
    const correctIndex = parseInt(widget.dataset.correctIndex, 10);
    const chosenIndex = parseInt(button.dataset.index, 10);
    const isCorrect = chosenIndex === correctIndex;

    widget.querySelectorAll(".quiz-choice-btn").forEach((choiceButton) => {
        choiceButton.classList.remove("list-group-item-success", "list-group-item-danger");
        choiceButton.disabled = true;
    });

    button.classList.add(isCorrect ? "list-group-item-success" : "list-group-item-danger");
    if (!isCorrect) {
        const correctButton = widget.querySelector(`.quiz-choice-btn[data-index="${correctIndex}"]`);
        if (correctButton) {
            correctButton.classList.add("list-group-item-success");
        }
    }

    const feedback = widget.querySelector(".quiz-feedback");
    feedback.textContent = isCorrect ? "Bonne réponse !" : "Ce n'est pas la bonne réponse.";
    feedback.className = "quiz-feedback small mb-2 " + (isCorrect ? "text-success" : "text-danger");

    const explanation = widget.querySelector(".quiz-explanation");
    if (explanation) {
        explanation.classList.remove("d-none");
    }
});
