import os
import uuid
from graphviz import Source
import matplotlib.pyplot as plt

def render_matplotlib(spec, output_dir):
    """Render validated chart data with a fixed renderer, never generated code.

    Old Python-code payloads are intentionally rejected rather than executed.
    """
    from .chart_spec import validate_chart_spec

    spec = validate_chart_spec(spec)
    image_path = os.path.join(output_dir, f"plot_{uuid.uuid4().hex}.png")
    # rc_context prevents host rc settings from enabling TeX execution or mathtext.
    with plt.rc_context({"text.usetex": False, "text.parse_math": False}):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        try:
            x, y = spec["x"], spec["y"]
            if spec["kind"] == "pie":
                ax.pie(y, labels=[str(v) for v in x], autopct="%1.1f%%")
            elif spec["kind"] == "bar":
                ax.bar(x, y)
            elif spec["kind"] == "line":
                ax.plot(x, y, marker="o")
            else:
                ax.scatter(x, y)
            ax.set_title(spec.get("title", ""))
            ax.set_xlabel(spec.get("xlabel", ""))
            ax.set_ylabel(spec.get("ylabel", ""))
            fig.tight_layout()
            fig.savefig(image_path, dpi=150)
        finally:
            plt.close(fig)
    return image_path

def render_graphviz(code, output_dir):
    """
    Renders graphviz DOT language to a PNG image.
    """
    image_path = os.path.join(output_dir, f"graph_{uuid.uuid4().hex}")

    try:
        s = Source(code, filename=image_path, format="png")
        s.render()

        # Graphviz render creates the file with the format extension appended
        actual_path = f"{image_path}.png"

        if os.path.exists(actual_path):
            return actual_path
        return None
    except Exception as e:
        print(f"Error rendering graphviz: {e}")
        return None

def process_diagrams(content_elements, output_dir):
    """
    Iterates through the generated content, renders diagrams,
    and adds the local image paths back into the element dictionary.
    """
    for element in content_elements:
        if element['type'] == 'diagram_matplotlib':
            element.pop('image_path', None)
            img_path = render_matplotlib(element.get('spec'), output_dir)
            if img_path:
                element['image_path'] = img_path

        elif element['type'] == 'diagram_graphviz':
            img_path = render_graphviz(element['code'], output_dir)
            if img_path:
                element['image_path'] = img_path

        # For mermaid, we might just pass the code directly to streamlit later
        # or render via an external API. Streamlit has a st_mermaid component,
        # but for .docx we might need an image.
        # For this prototype, we will handle mermaid rendering externally or skip docx embed
        # if an image renderer isn't easily available in pure python.

    return content_elements
