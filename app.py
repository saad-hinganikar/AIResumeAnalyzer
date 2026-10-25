
import os
import tempfile

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from analyzer import extract_resume_text, analyze_resume

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}


@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    error = None
    job_description = ""

    if request.method == "POST":
        job_description = request.form.get(
            "job_description", ""
        ).strip()

        uploaded_file = request.files.get("resume")

        if not uploaded_file or not uploaded_file.filename:
            error = "Please upload your resume."
        elif "." not in uploaded_file.filename:
            error = "Please upload a PDF or DOCX file."
        elif uploaded_file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
            error = "Only PDF and DOCX files are supported."
        elif not job_description:
            error = "Please enter a job description."
        else:
            filename = secure_filename(uploaded_file.filename)
            extension = filename.rsplit(".", 1)[1].lower()
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix="." + extension,
                    delete=False
                ) as temp_file:
                    temp_path = temp_file.name
                    uploaded_file.save(temp_path)

                resume_text = extract_resume_text(temp_path)
                results = analyze_resume(
                    resume_text, job_description
                )

            except Exception as exc:
                app.logger.exception("Resume analysis failed")
                error = (
                    "Could not analyze this file. Check that it is "
                    "a readable PDF or DOCX and try again."
                )

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    return render_template(
        "index.html",
        results=results,
        error=error,
        job_description=job_description
    )


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        results=None,
        error="File is too large. Maximum size is 5 MB.",
        job_description=""
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
