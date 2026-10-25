
const resumeInput = document.getElementById("resume");
const jobDescription = document.getElementById("job_description");
const form = document.querySelector("form");

resumeInput.addEventListener("change", () => {
    const file = resumeInput.files[0];

    if (!file) return;

    const allowedExtensions = [".pdf", ".docx"];
    const validExtension = allowedExtensions.some(ext =>
        file.name.toLowerCase().endsWith(ext)
    );

    if (!validExtension) {
        resumeInput.setCustomValidity(
            "Please select a PDF or DOCX resume."
        );
    } else if (file.size > 5 * 1024 * 1024) {
        resumeInput.setCustomValidity(
            "The file must be smaller than 5 MB."
        );
    } else {
        resumeInput.setCustomValidity("");
    }

    resumeInput.reportValidity();
});

form.addEventListener("submit", event => {
    if (!jobDescription.value.trim()) {
        event.preventDefault();
        jobDescription.setCustomValidity(
            "Please enter a job description."
        );
        jobDescription.reportValidity();
    } else {
        jobDescription.setCustomValidity("");
    }
});

jobDescription.addEventListener("input", () => {
    jobDescription.setCustomValidity("");
});
