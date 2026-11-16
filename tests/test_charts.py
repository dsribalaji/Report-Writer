import copy
import io
import zipfile
from pathlib import Path

import docx
import matplotlib.pyplot as plt
import pytest

from utils.chart_spec import validate_chart_spec
from utils.diagram_renderer import render_matplotlib, process_diagrams
from utils.assembler import insert_elements_into_doc
from utils.template_processor import extract_styles_and_create_blank

BASE = {"kind": "bar", "x": ["A", "B"], "y": [10, 20], "title": "Quarterly output"}


@pytest.mark.parametrize("kind", ["bar", "line", "scatter", "pie"])
def test_supported_charts(tmp_path, kind):
    spec = dict(BASE, kind=kind)
    if kind == "scatter":
        spec['x'] = [1, 2]
    path = Path(render_matplotlib(spec, tmp_path))
    assert path.parent == tmp_path
    assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert not plt.get_fignums()


@pytest.mark.parametrize("change", [
    {"kind": "unknown"}, {"y": [1]}, {"x": [], "y": []},
    {"y": [True, 1]}, {"y": [float('nan'), 1]}, {"y": [float('inf'), 1]},
    {"y": [10**20, 1]}, {"x": [None, "B"]}, {"title": "x" * 201},
    {"kind": "pie", "y": [-1, 2]}, {"kind": "pie", "y": [0, 0]},
    {"kind": "scatter"}, {"savefig": "/tmp/escape.png"},
    {"code": "import os"}, {"x": list(range(201)), "y": list(range(201))},
])
def test_rejects_invalid_specs(change):
    with pytest.raises(ValueError):
        validate_chart_spec(dict(BASE, **change))


def test_old_python_never_runs(tmp_path):
    marker = tmp_path / "outside-plot.txt"
    with pytest.raises(ValueError):
        render_matplotlib(f"open({str(marker)!r}, 'w').write('bad')", tmp_path)
    assert not marker.exists()
    assert list(tmp_path.iterdir()) == []


def test_old_element_does_not_reuse_image(tmp_path):
    elements = [{"type": "diagram_matplotlib", "code": "pass", "image_path": "/tmp/stale.png"}]
    with pytest.raises(ValueError):
        process_diagrams(elements, tmp_path)
    assert 'image_path' not in elements[0]


def test_spec_not_mutated(tmp_path):
    before = copy.deepcopy(BASE)
    render_matplotlib(BASE, tmp_path)
    assert BASE == before


def test_figures_closed_on_write_failure(tmp_path, monkeypatch):
    from matplotlib.figure import Figure
    def fail(*args, **kwargs):
        raise OSError('fixture')
    monkeypatch.setattr(Figure, 'savefig', fail)
    with pytest.raises(OSError):
        render_matplotlib(BASE, tmp_path)
    assert not plt.get_fignums()


def test_document_round_trip_with_chart(tmp_path):
    template = docx.Document()
    template.sections[0].header.paragraphs[0].text = 'Fixture header'
    template.add_paragraph('Remove template body')
    stream = io.BytesIO()
    template.save(stream)
    blank, temp_dir = extract_styles_and_create_blank(stream)
    try:
        elements = [{"type": "heading", "level": 1, "text": "Results"},
                    {"type": "paragraph", "text": "A measured comparison."},
                    {"type": "diagram_matplotlib", "spec": BASE}]
        process_diagrams(elements, tmp_path)
        insert_elements_into_doc(blank, elements)
        result = docx.Document(blank)
        assert result.sections[0].header.paragraphs[0].text == 'Fixture header'
        texts = [p.text for p in result.paragraphs]
        assert 'Results' in texts and 'A measured comparison.' in texts
        assert 'Remove template body' not in texts
        assert len(result.inline_shapes) == 1
        assert result.paragraphs[0].style.name == 'Heading 1'
        with zipfile.ZipFile(blank) as z:
            assert any(n.startswith('word/media/') for n in z.namelist())
        result.save(tmp_path / 'verified-report.docx')
    finally:
        import shutil
        shutil.rmtree(temp_dir)
