import docx
import io
import shutil
import tempfile
import os

def extract_styles_and_create_blank(uploaded_file):
    """
    Takes an uploaded .docx file, creates a temporary copy,
    clears all content from the body, and returns the path to the new blank document
    that retains all the original styles.
    """
    # Save the uploaded file to a temporary file
    temp_dir = tempfile.mkdtemp()
    original_path = os.path.join(temp_dir, "original_template.docx")

    with open(original_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Open the document
    doc = docx.Document(original_path)

    # We want to clear the document body but keep styles, headers, footers, etc.
    # The safest way is to remove all elements from the document body

    # Access the body element
    body = doc.element.body

    # Clear all children of the body
    body.clear_content()

    # Save the cleared document
    blank_path = os.path.join(temp_dir, "blank_template.docx")
    doc.save(blank_path)

    return blank_path, temp_dir

def list_available_styles(doc_path):
    """
    Returns a list of paragraph styles available in the document.
    Useful for debugging and knowing what styles to apply.
    """
    doc = docx.Document(doc_path)
    styles = []
    for style in doc.styles:
        if style.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
            styles.append(style.name)
    return styles
