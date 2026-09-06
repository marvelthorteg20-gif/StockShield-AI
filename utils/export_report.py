"""Export a StockShield analysis payload to PDF, CSV, and JSON."""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _flatten(payload: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Any]]:
    """Flatten nested dicts/lists into dotted field paths."""
    rows = []
    for key, value in payload.items():
        path = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            rows.extend(_flatten(value, path))
        elif isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                for index, item in enumerate(value):
                    rows.extend(_flatten(item, f"{path}[{index}]"))
            else:
                rows.append((path, "; ".join(str(item) for item in value)))
        else:
            rows.append((path, value))
    return rows


def export_json(payload: Dict[str, Any], path: str) -> str:
    """Write *payload* as pretty-printed JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
    return path


def export_csv(payload: Dict[str, Any], path: str) -> str:
    """Write a two-column field/value CSV of the flattened payload."""
    rows = _flatten(payload)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "value"])
        writer.writerows(rows)
    return path


def _pdf_escape(text: Any) -> str:
    """Escape text for a simple Latin-1 PDF content stream."""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def export_pdf(payload: Dict[str, Any], path: str, title: str = "StockShield AI Report") -> str:
    """Write a simple text PDF without third-party libraries."""
    lines = [title, "=" * 40, ""]
    for key, value in _flatten(payload):
        lines.append(f"{key}: {value}")

    wrapped = []
    for line in lines:
        text = str(line)
        while len(text) > 95:
            wrapped.append(text[:95])
            text = text[95:]
        wrapped.append(text)

    y_start = 800
    max_lines = 60
    pages = [wrapped[i:i + max_lines] for i in range(0, len(wrapped), max_lines)] or [[]]

    content_streams = []
    for page_lines in pages:
        stream_lines = ["BT", "/F1 9 Tf", "14 TL", f"48 {y_start} Td"]
        for line in page_lines:
            stream_lines.append(f"({_pdf_escape(line)}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        content_streams.append("\n".join(stream_lines).encode("latin-1", "replace"))

    n_pages = len(pages)
    catalog_id = 1
    pages_id = 2
    font_id = 3
    page_ids = list(range(4, 4 + n_pages))
    stream_ids = list(range(4 + n_pages, 4 + 2 * n_pages))

    body_objects = []
    body_objects.append((catalog_id, f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()))
    kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
    body_objects.append(
        (pages_id, f"<< /Type /Pages /Kids [{kids_str}] /Count {n_pages} >>".encode())
    )
    body_objects.append(
        (font_id, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    )
    for page_id, stream_id, stream in zip(page_ids, stream_ids, content_streams):
        page_dict = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
            f"/Contents {stream_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        ).encode()
        body_objects.append((page_id, page_dict))
        stream_obj = f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        body_objects.append((stream_id, stream_obj))

    body_objects.sort(key=lambda item: item[0])
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = {0: 0}
    for obj_id, data in body_objects:
        offsets[obj_id] = len(pdf)
        pdf.extend(f"{obj_id} 0 obj\n".encode())
        pdf.extend(data)
        pdf.extend(b"\nendobj\n")

    xref_pos = len(pdf)
    max_id = body_objects[-1][0]
    pdf.extend(f"xref\n0 {max_id + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, max_id + 1):
        pdf.extend(f"{offsets[obj_id]:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(pdf)
    return path


def export_reports(
    payload: Dict[str, Any],
    directory: Optional[str] = None,
    symbol: str = "STOCK",
) -> Dict[str, str]:
    """Write PDF, CSV, and JSON reports into directory. Returns file paths."""
    if directory is None:
        import config as _config

        directory = _config.EXPORT_FOLDER
    os.makedirs(directory, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = os.path.join(directory, f"{symbol}_{stamp}")
    paths = {
        "json": export_json(payload, base + ".json"),
        "csv": export_csv(payload, base + ".csv"),
        "pdf": export_pdf(payload, base + ".pdf", title=f"StockShield AI - {symbol}"),
    }
    return paths
