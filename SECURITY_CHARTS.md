# Data-only chart generation

Matplotlib elements now accept a `spec`, never executable Python:

```json
{"type":"diagram_matplotlib","spec":{"kind":"bar","x":["A","B"],"y":[10,20],"title":"Comparison","xlabel":"Category","ylabel":"Value"}}
```

Supported kinds: bar, line, scatter and pie. Arrays must have equal lengths of 1-200 points. Numeric values must be finite, non-boolean and within +/-1e12. Scatter requires numeric x values. Pie values must be nonnegative and have a positive sum. Titles and labels are limited to 200 characters. Unknown fields, output paths and old Python-code strings are rejected. The renderer alone chooses the image path and closes its own figure, including on errors. TeX and mathtext are disabled for generated labels.

The generation prompt and renderer changed together. Previously saved `diagram_matplotlib` elements with a `code` field must be regenerated or manually converted to specs; they will not be executed or silently accepted. Validation errors use the app's existing generation-error path.

## Local regression checks

Install the application requirements and pytest, then run from the repository root:

```sh
python -m pytest -q
```

The tests require no model credentials or network calls. They check valid chart kinds, invalid data and legacy-code rejection, figure cleanup, and DOCX text/style/header/image round trips. `tests/test_generator.py` also checks the actual generation prompt and response path with a fake API client.

This change removes the generated-Python execution path. Graphviz DOT handling, Mermaid handling, external model quality, web research, the hosted application and API2PDF conversion are not security-certified or end-to-end tested by this patch. No production services or remote accounts are changed by these tests.
