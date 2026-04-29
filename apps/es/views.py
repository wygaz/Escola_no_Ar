from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import render


PUBLICACAO_DIR = (Path(settings.BASE_DIR) / "apps" / "es" / "publicacao_site").resolve()
VISIT_COUNTER_FILE = PUBLICACAO_DIR / "visit_counter.json"

DAY_CHOICES = [
    {"code": "0", "label": "Sabado"},
    {"code": "1", "label": "Domingo"},
    {"code": "2", "label": "Segunda"},
    {"code": "3", "label": "Terca"},
    {"code": "4", "label": "Quarta"},
    {"code": "5", "label": "Quinta"},
    {"code": "6", "label": "Sexta"},
]

DEFAULT_SEARCH = {
    "year": 2026,
    "quarter": 2,
    "week": 5,
    "day": "1",
}


def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "es/home.html",
        {
            "page_title": "Escola Sabatina",
            "search_defaults": DEFAULT_SEARCH,
            "day_choices": DAY_CHOICES,
        },
    )


def _resolve_publicacao_file(relative_path: str) -> Path:
    normalized = (relative_path or "").replace("\\", "/").lstrip("/")
    if not normalized:
        raise Http404

    candidate = (PUBLICACAO_DIR / normalized).resolve()
    if PUBLICACAO_DIR not in candidate.parents and candidate != PUBLICACAO_DIR:
        raise Http404

    if not candidate.is_file():
        raise Http404

    return candidate


def publicacao_site(request: HttpRequest, path: str) -> HttpResponse:
    file_path = _resolve_publicacao_file(path)
    suffix = file_path.suffix.lower()

    if suffix in {".html", ".htm"}:
        content_type = "text/html; charset=utf-8"
    elif suffix == ".json":
        content_type = "application/json; charset=utf-8"
    elif suffix == ".svg":
        content_type = "image/svg+xml; charset=utf-8"
    elif suffix == ".php":
        content_type = "application/octet-stream"
    else:
        guessed, _ = mimetypes.guess_type(file_path.name)
        content_type = guessed or "application/octet-stream"

    return FileResponse(file_path.open("rb"), content_type=content_type)


def _load_visit_counter() -> dict[str, int]:
    if not VISIT_COUNTER_FILE.is_file():
        return {}

    try:
        raw = VISIT_COUNTER_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            return {str(k): int(v) for k, v in data.items()}
    except Exception:
        pass

    return {}


def _save_visit_counter(data: dict[str, int]) -> None:
    PUBLICACAO_DIR.mkdir(parents=True, exist_ok=True)
    VISIT_COUNTER_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def counter_php(request: HttpRequest) -> HttpResponse:
    page_id = (request.GET.get("id") or "publicacao").strip() or "publicacao"

    counters = _load_visit_counter()
    counters[page_id] = int(counters.get(page_id, 0)) + 1
    _save_visit_counter(counters)

    count = counters[page_id]
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="220" height="34" viewBox="0 0 220 34" role="img" aria-label="Visitas: {count}">
  <rect x="0" y="0" width="220" height="34" rx="10" fill="#eef4ff"/>
  <text x="12" y="22" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#1c4f8c">Visitas: {count}</text>
</svg>
"""
    return HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")
