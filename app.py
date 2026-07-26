import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Import utilities
from utils.template_processor import extract_styles_and_create_blank
from utils.generator import perform_research, generate_report_content
from utils.diagram_renderer import process_diagrams
from utils.assembler import insert_elements_into_doc
from utils.pdf_converter import convert_docx_to_pdf

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Auto Report Generator", page_icon="📝", layout="wide")

st.title("📝 Automated Report & Diagram Generator")
st.markdown("Upload a template, provide a topic, and we'll generate a fully formatted report with diagrams!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    groq_api_key = os.getenv("GROQ_API_KEY")
    api2pdf_api_key = os.getenv("API2PDF_API_KEY")

    st.write("**API Status:**")
    if groq_api_key and groq_api_key != "your_groq_api_key_here":
        st.success("✅ Groq API Key found")
    else:
        st.error("❌ Groq API Key missing or invalid")

    if api2pdf_api_key and api2pdf_api_key != "your_api2pdf_api_key_here":
        st.success("✅ API2PDF Key found")
    else:
        st.warning("⚠️ API2PDF Key missing (PDF generation will fail)")

# Main app layout
st.header("1. Upload Template")
st.markdown("Upload a `.docx` file. We will extract its styles and use them for the new report.")
uploaded_file = st.file_uploader("Choose a .docx file", type="docx")

st.header("2. Define Topic")
topic = st.text_input("What is the report about?", placeholder="e.g., The impact of AI on modern healthcare")

st.header("3. Generate")
generate_button = st.button("Generate Report", type="primary")

if generate_button:
    if not uploaded_file:
        st.error("Please upload a .docx template first.")
    elif not topic:
        st.error("Please enter a topic.")
    elif not groq_api_key or groq_api_key == "your_groq_api_key_here":
        st.error("Groq API key is missing. Cannot proceed.")
    else:
        # State management to store paths between rerenders
        if 'docx_path' not in st.session_state:
            st.session_state.docx_path = None
        if 'pdf_path' not in st.session_state:
            st.session_state.pdf_path = None
        if 'content_elements' not in st.session_state:
            st.session_state.content_elements = None

        with st.status("Processing...", expanded=True) as status:
            try:
                st.write("📂 Processing template...")
                blank_template_path, temp_dir = extract_styles_and_create_blank(uploaded_file)

                st.write("🔍 Searching the web for information...")
                research_data = perform_research(topic)

                st.write("🧠 Generating content and diagram structures...")
                content_elements = generate_report_content(topic, research_data)

                st.write("🎨 Rendering diagrams...")
                content_elements = process_diagrams(content_elements, temp_dir)
                st.session_state.content_elements = content_elements

                st.write("📄 Formatting document...")
                final_docx_path = insert_elements_into_doc(blank_template_path, content_elements)
                st.session_state.docx_path = final_docx_path

                if api2pdf_api_key and api2pdf_api_key != "your_api2pdf_api_key_here":
                    st.write("🔄 Converting to PDF...")
                    pdf_output_path = os.path.join(temp_dir, "report.pdf")
                    final_pdf_path = convert_docx_to_pdf(final_docx_path, pdf_output_path)
                    st.session_state.pdf_path = final_pdf_path
                else:
                    st.write("⚠️ Skipping PDF conversion (API key missing)")

                status.update(label="Generation complete!", state="complete", expanded=False)
                st.success("Report generated successfully!")
            except Exception as e:
                status.update(label="Error occurred", state="error", expanded=True)
                st.error(f"An error occurred: {e}")

# If we have generated content, show preview and downloads
if st.session_state.get('content_elements'):
    st.header("Preview")
    with st.container(border=True):
        for element in st.session_state.content_elements:
            elem_type = element.get('type')
            if elem_type == 'heading':
                level = element.get('level', 1)
                st.markdown(f"{'#' * level} {element.get('text', '')}")
            elif elem_type == 'paragraph':
                st.write(element.get('text', ''))
            elif elem_type in ['diagram_matplotlib', 'diagram_graphviz']:
                img_path = element.get('image_path')
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption=f"Generated {elem_type.split('_')[1]} diagram")

    st.header("Download")
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.get('docx_path') and os.path.exists(st.session_state.docx_path):
            with open(st.session_state.docx_path, "rb") as file:
                st.download_button(
                    label="Download .docx",
                    data=file,
                    file_name="generated_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    with col2:
        if st.session_state.get('pdf_path') and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, "rb") as file:
                st.download_button(
                    label="Download .pdf",
                    data=file,
                    file_name="generated_report.pdf",
                    mime="application/pdf"
                )
        elif not os.getenv("API2PDF_API_KEY") or os.getenv("API2PDF_API_KEY") == "your_api2pdf_api_key_here":
            st.info("PDF download unavailable (Missing API key)")
