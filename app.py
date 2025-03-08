from flask import Flask, render_template, request
from googletrans import Translator, LANGUAGES

app = Flask(__name__)
translator = Translator()

@app.route("/", methods=["GET", "POST"])
def translate_file():
    translated_text = ""
    error_message = ""

    if request.method == "POST":
        if "file" not in request.files:
            error_message = "No file uploaded."
        else:
            file = request.files["file"]
            target_language = request.form.get("target_language", "en")  # Default to English
            
            if file.filename == "":
                error_message = "No file selected."
            elif target_language not in LANGUAGES:
                error_message = "Invalid target language selected."
            else:
                try:
                    contents = file.read().decode("utf-8").strip()
                    if not contents:
                        error_message = "The file is empty."
                    else:
                        translated = translator.translate(contents, dest=target_language)
                        translated_text = translated.text
                except Exception as e:
                    error_message = f"Error during translation: {str(e)}"

    return render_template("index.html", translated_text=translated_text, error_message=error_message, languages=LANGUAGES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)

