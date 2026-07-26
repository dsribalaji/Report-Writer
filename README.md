# Automated Report & Diagram Generator

This Streamlit application takes an uploaded `.docx` template and a research topic, fetches information from the web (using DuckDuckGo), and leverages the Groq API to generate a fully formatted report. It generates architecture diagrams (via Matplotlib and Graphviz) on the fly, applies your template's styles, and outputs downloadable `.docx` and `.pdf` files.

## Setup Instructions

1. **Install system dependencies:**
   This app requires `graphviz` for rendering some diagram types.
   ```bash
   sudo apt-get update && sudo apt-get install -y graphviz
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy the example environment file and add your keys:
   ```bash
   cp .env.example .env
   ```
   - **GROQ_API_KEY**: Get this from [Groq Console](https://console.groq.com/keys)
   - **API2PDF_API_KEY**: Get this from [Api2Pdf](https://portal.api2pdf.com/)

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```
