import docx
from docx.shared import Inches
import os

def insert_elements_into_doc(doc_path, content_elements):
    """
    Opens the template document, inserts headings, text, and images
    according to the generated content_elements JSON, and saves it.
    """
    doc = docx.Document(doc_path)

    # We will try to map Heading levels to built-in styles
    # If the style doesn't exist, python-docx will fall back to normal

    for element in content_elements:
        element_type = element.get('type')

        if element_type == 'heading':
            level = element.get('level', 1)
            text = element.get('text', '')
            try:
                doc.add_heading(text, level=level)
            except ValueError:
                # Fallback if specific heading level style is missing
                p = doc.add_paragraph(text)
                p.style = 'Normal'

        elif element_type == 'paragraph':
            text = element.get('text', '')
            doc.add_paragraph(text, style='Normal')

        elif element_type in ['diagram_matplotlib', 'diagram_graphviz']:
            img_path = element.get('image_path')
            if img_path and os.path.exists(img_path):
                # Add image, restricting width to fit on page
                doc.add_picture(img_path, width=Inches(6.0))

                # Optional caption
                doc.add_paragraph(f"Figure: {element_type.split('_')[1].capitalize()} Diagram", style='Caption')

    # Save over the same file
    doc.save(doc_path)
    return doc_path
