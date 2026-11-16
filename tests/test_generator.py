"""Run generator logic offline without installing or calling network SDKs."""
import importlib.util
import json
import sys
import types
from pathlib import Path


def test_generator_requests_spec_and_accepts_json(monkeypatch):
    captured = {}
    payload = [{"type": "diagram_matplotlib", "spec": {"kind": "bar", "x": ["A"], "y": [1]}}]
    class FakeGroq:
        def __init__(self, **kwargs):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=json.dumps(payload)))])
    monkeypatch.setenv('GROQ_API_KEY', 'offline-fixture-not-a-real-key')
    monkeypatch.setitem(sys.modules, 'groq', types.SimpleNamespace(Groq=FakeGroq))
    monkeypatch.setitem(sys.modules, 'duckduckgo_search', types.SimpleNamespace(DDGS=object))
    path = Path(__file__).resolve().parents[1] / 'utils/generator.py'
    spec = importlib.util.spec_from_file_location('offline_generator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.generate_report_content('Fixture', 'Fixture research') == payload
    prompt = captured['messages'][1]['content']
    assert '"spec"' in prompt
    assert 'never Python' in prompt
    assert 'import matplotlib' not in prompt
    assert 'temp_graph.png' not in prompt
