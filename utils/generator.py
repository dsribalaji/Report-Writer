import json
from duckduckgo_search import DDGS
from groq import Groq
import os

def perform_research(topic, num_results=3):
    """
    Searches DuckDuckGo for the given topic and returns a summarized text of findings.
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(topic, max_results=num_results)

        research_data = ""
        if results:
            for i, result in enumerate(results):
                research_data += f"Source {i+1} - {result.get('title', '')}:\n{result.get('body', '')}\n\n"

        return research_data
    except Exception as e:
        print(f"Error during search: {e}")
        return "Could not fetch internet results."

def generate_report_content(topic, research_data):
    """
    Calls the Groq API to generate the structure, text, and diagram definitions for the report.
    Expects a JSON response with headings, paragraphs, and diagrams.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    client = Groq(api_key=api_key)

    prompt = f"""
    You are an expert report writer and system architect.
    Write a detailed, professional report on the following topic: "{topic}"

    Use the following research data to inform your report:
    {research_data}

    You must return ONLY a raw JSON object (no markdown formatting, no code blocks) representing the document structure.

    The JSON structure must be a list of "elements", where each element is a block in the document.

    Types of elements:
    1. "heading": {{"type": "heading", "level": 1|2|3, "text": "Heading Text"}}
    2. "paragraph": {{"type": "paragraph", "text": "Detailed paragraph text."}}
    3. "diagram_mermaid": {{"type": "diagram_mermaid", "code": "mermaid graph TD code here"}}
    4. "diagram_matplotlib": {{"type": "diagram_matplotlib", "code": "import matplotlib.pyplot as plt\\n... code that saves to 'temp_graph.png'"}}
    5. "diagram_graphviz": {{"type": "diagram_graphviz", "code": "digraph G {{ ... }}"}}

    Include at least one diagram in the report to illustrate a concept.

    Output exactly in this format:
    [
        {{"type": "heading", "level": 1, "text": "Introduction"}},
        {{"type": "paragraph", "text": "..."}}
    ]
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized JSON generator. You output only valid JSON without markdown wrapping."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=4000,
        )

        content = response.choices[0].message.content.strip()

        # In case the model still outputs markdown code blocks, clean it
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content)

    except Exception as e:
        print(f"Error generating content: {e}")
        # Fallback basic structure if API fails
        return [
            {"type": "heading", "level": 1, "text": f"Report on {topic}"},
            {"type": "paragraph", "text": f"Error occurred during generation: {str(e)}"},
        ]
