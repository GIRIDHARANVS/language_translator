import chardet
import fitz  # PyMuPDF for PDFs
from docx import Document  # For DOCX files
from flask import Flask, render_template, request
from googletrans import Translator, LANGUAGES
from striprtf.striprtf import rtf_to_text  # Convert RTF to plain text

app = Flask(__name__)
translator = Translator()

def detect_encoding(file):
    """Detects the encoding of a given file."""
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result.get('encoding') or 'utf-8'  # Default to UTF-8 if detection fails
    file.seek(0)  # Reset file pointer for reading
    return encoding

def extract_text(file, filename, encoding):
    """Extracts plain text from TXT, RTF, DOCX, and PDF files."""
    if filename.endswith(".txt"):
        return file.read().decode(encoding, errors="replace").strip()
    
    elif filename.endswith(".rtf"):
        contents = file.read().decode(encoding, errors="replace").strip()
        return rtf_to_text(contents)

    elif filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    elif filename.endswith(".pdf"):
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in pdf_document])
        return text.strip()

    else:
        return None  # Unsupported file type

@app.route("/", methods=["GET", "POST"])
def translate_file():
    translated_text = ""
    if request.method == "POST":
        file = request.files.get("file")
        target_language = request.form.get("target_language", "en")

        if not file or file.filename == "":
            return "Error: No file selected."

        try:
            encoding = detect_encoding(file)
            contents = extract_text(file, file.filename, encoding)

            if not contents:
                return "Error: Unsupported file type or empty file."

            translated = translator.translate(contents, dest=target_language)
            translated_text = translated.text if translated and translated.text else "Translation failed."

        except Exception as e:
            translated_text = f"Error during translation: {str(e)}"
    
    return render_template("index.html", translated_text=translated_text, languages=LANGUAGES)

if __name__ == "__main__":
    app.run(debug=True)
