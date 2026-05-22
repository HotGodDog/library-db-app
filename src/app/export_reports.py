"""CSV and PDF export for librarian reports."""

import csv
import io
import os
from pathlib import Path

from flask import Response

from fpdf import FPDF

REPORT_LOANS_COLUMNS = [
    ("loan_id", "ID"),
    ("book_title", "Книга"),
    ("reader_name", "Читатель"),
    ("loan_date", "Выдана"),
    ("due_date", "Срок"),
    ("return_date", "Возвращена"),
    ("status", "Статус"),
]

REPORT_ACTIVE_COLUMNS = [
    ("loan_id", "ID"),
    ("book_title", "Книга"),
    ("reader_name", "Читатель"),
    ("reader_phone", "Телефон"),
    ("loan_date", "Выдана"),
    ("due_date", "Вернуть до"),
    ("extension_count", "Продления"),
    ("status", "Статус"),
]


def _cell_value(row: dict, key: str) -> str:
    val = row.get(key)
    if val is None or val == "":
        return "—"
    return str(val)


def _find_unicode_font() -> str | None:
    base = Path(__file__).resolve().parent
    candidates = [
        base / "static" / "fonts" / "DejaVuSans.ttf",
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf",
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "Arial.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return None


def build_csv(rows: list[dict], columns: list[tuple[str, str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([label for _, label in columns])
    for row in rows:
        writer.writerow([_cell_value(row, key) for key, _ in columns])
    return ("\ufeff" + buffer.getvalue()).encode("utf-8-sig")


def build_pdf(rows: list[dict], columns: list[tuple[str, str]], title: str) -> bytes:
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    font_path = _find_unicode_font()
    font_name = "Helvetica"
    if font_path:
        font_name = "UnicodeFont"
        pdf.add_font(font_name, "", font_path)
    pdf.add_page()
    pdf.set_font(font_name, size=12)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, size=8)
    col_width = max(20, (pdf.w - 20) / len(columns))
    for _, label in columns:
        pdf.cell(col_width, 7, label, border=1)
    pdf.ln()
    for row in rows:
        for key, _ in columns:
            text = _cell_value(row, key)
            if len(text) > 28:
                text = text[:25] + "..."
            pdf.cell(col_width, 6, text, border=1)
        pdf.ln()
    if not rows:
        pdf.cell(0, 8, "Нет данных", new_x="LMARGIN", new_y="NEXT")
    return pdf.output()


def csv_response(rows: list[dict], columns: list[tuple[str, str]], filename: str) -> Response:
    return Response(
        build_csv(rows, columns),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def pdf_response(
    rows: list[dict], columns: list[tuple[str, str]], title: str, filename: str
) -> Response:
    return Response(
        build_pdf(rows, columns, title),
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
