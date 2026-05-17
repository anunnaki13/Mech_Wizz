from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, select


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
REPORTS_DIR = REPO_ROOT / "reports"
REPORT_STEM = "MECH_WIZ_PLTU_Target_Screening_Report"
PDF_PATH = REPORTS_DIR / f"{REPORT_STEM}.pdf"

sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{BACKEND_ROOT / 'mechwiz.db'}")

from app.database import SessionLocal  # noqa: E402
from app.import_target_pltu import BME_EXISTING_COAL, CAPACITY_FACTOR, OPERATING_DAYS_PER_YEAR  # noqa: E402
from app.models import Plant, ScenarioResult  # noqa: E402
from app.services.scoring import latest_scoring_records, ranking_row_from_record  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402


def _fmt_number(value: float | int | None, digits: int = 0) -> str:
    if value is None:
        return "-"
    return f"{float(value):,.{digits}f}"


def _fmt_money(value: float | int | None) -> str:
    if value is None:
        return "-"
    absolute = abs(float(value))
    if absolute >= 1_000_000_000:
        return f"USD {float(value) / 1_000_000_000:,.2f} B"
    if absolute >= 1_000_000:
        return f"USD {float(value) / 1_000_000:,.2f} M"
    return f"USD {float(value):,.0f}"


def _fmt_percent(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%"


def _safe(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraph(value: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_safe(value), style)


def _load_report_data() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, int]]:
    with SessionLocal() as db:
        records = latest_scoring_records(db, scheme="align")
        rows = [ranking_row_from_record(record) for record in records]
        confidence_counts = {
            confidence: count
            for confidence, count in db.execute(
                select(Plant.confidence_level, func.count()).group_by(Plant.confidence_level)
            ).all()
        }
        totals = {
            "plants": int(db.scalar(select(func.count()).select_from(Plant)) or 0),
            "capacity_mw": db.scalar(select(func.sum(Plant.capacity_mw))) or 0,
            "co2_tpy": db.scalar(select(func.sum(ScenarioResult.total_co2_ton_per_year))) or 0,
            "captured_co2_tpy": db.scalar(select(func.sum(ScenarioResult.captured_co2_ton_per_year))) or 0,
            "methanol_tpy": db.scalar(select(func.sum(ScenarioResult.methanol_ton_per_year))) or 0,
            "h2_tpy": db.scalar(select(func.sum(ScenarioResult.h2_required_ton_per_year))) or 0,
            "electrolyzer_mw": db.scalar(select(func.sum(ScenarioResult.electrolyzer_required_mw))) or 0,
            "gross_revenue": db.scalar(select(func.sum(ScenarioResult.gross_revenue_usd_per_year))) or 0,
            "npv": db.scalar(select(func.sum(ScenarioResult.npv_usd))) or 0,
        }
    return totals, rows, confidence_counts


def _make_table(data: list[list[Any]], col_widths: list[float], *, repeat_rows: int = 1) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=repeat_rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7f0ed")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#10263d")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.3),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.0),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#ccd8e4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfe")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _ranking_table(rows: list[dict[str, Any]], styles: dict[str, ParagraphStyle], limit: int | None = None) -> Table:
    selected = rows if limit is None else rows[:limit]
    data: list[list[Any]] = [
        ["Rank", "Site", "Provinsi", "MW", "Score", "CO2 t/y", "Methanol t/y", "H2 t/y", "LCOM", "Conf."]
    ]
    for row in selected:
        data.append(
            [
                row["rank"],
                _paragraph(row["site_name"], styles["tiny"]),
                _paragraph(row["province"], styles["tiny"]),
                _fmt_number(row["capacity_mw"], 1),
                f"{float(row['composite_score']):.3f}",
                _fmt_number(row["co2_tpy"], 0),
                _fmt_number(row["methanol_tpy"], 0),
                _fmt_number(row["h2_required_tpy"], 0),
                _fmt_number(row["estimated_lcom_usd_ton"], 0),
                row["data_confidence_label"],
            ]
        )
    table = _make_table(data, [12 * mm, 33 * mm, 22 * mm, 14 * mm, 12 * mm, 21 * mm, 21 * mm, 19 * mm, 16 * mm, 12 * mm])
    table.setStyle(TableStyle([("ALIGN", (0, 1), (0, -1), "RIGHT"), ("ALIGN", (3, 1), (8, -1), "RIGHT")]))
    return table


def _metric_grid(totals: dict[str, Any], top_name: str) -> Table:
    items = [
        ("Target PLTU", str(totals["plants"])),
        ("Total kapasitas", f"{_fmt_number(totals['capacity_mw'], 1)} MW"),
        ("Top kandidat", top_name),
        ("Potensi CO2", f"{_fmt_number(totals['co2_tpy'], 0)} t/y"),
        ("Captured CO2 85%", f"{_fmt_number(totals['captured_co2_tpy'], 0)} t/y"),
        ("Potensi e-methanol", f"{_fmt_number(totals['methanol_tpy'], 0)} t/y"),
        ("Kebutuhan H2", f"{_fmt_number(totals['h2_tpy'], 0)} t/y"),
        ("Electrolyzer indikatif", f"{_fmt_number(totals['electrolyzer_mw'], 0)} MW"),
        ("Gross revenue benchmark", _fmt_money(totals["gross_revenue"])),
    ]
    rows = []
    for index in range(0, len(items), 3):
        row = []
        for label, value in items[index : index + 3]:
            row.append(Paragraph(f"<font size='7' color='#5f6b7d'>{label.upper()}</font><br/><font size='13'><b>{_safe(value)}</b></font>", getSampleStyleSheet()["BodyText"]))
        rows.append(row)
    table = Table(rows, colWidths=[58 * mm, 58 * mm, 58 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#d5e0eb")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfcfe")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _on_page(canvas: Any, doc: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(18 * mm, 10 * mm, "MECH WIZ PLTU Target Screening Report")
    canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf() -> Path:
    totals, rows, confidence_counts = _load_report_data()
    generated_at = datetime.now().strftime("%d %B %Y %H:%M")
    top_name = rows[0]["site_name"] if rows else "-"

    base_styles = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "Title",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#10263d"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base_styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#58667a"),
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#10263d"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle("Body", parent=base_styles["BodyText"], fontSize=9, leading=12, spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base_styles["BodyText"], fontSize=7.5, leading=10, textColor=colors.HexColor("#647084")),
        "tiny": ParagraphStyle("Tiny", parent=base_styles["BodyText"], fontSize=6.8, leading=8),
        "warning": ParagraphStyle(
            "Warning",
            parent=base_styles["BodyText"],
            fontSize=8.5,
            leading=11,
            backColor=colors.HexColor("#fff4dd"),
            borderColor=colors.HexColor("#b76d00"),
            borderWidth=0.4,
            borderPadding=6,
            spaceAfter=8,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base_styles["BodyText"],
            fontSize=8.5,
            leading=11,
            backColor=colors.HexColor("#eef8f4"),
            borderColor=colors.HexColor("#1c6b5a"),
            borderWidth=0.4,
            borderPadding=6,
            spaceAfter=8,
        ),
        "center": ParagraphStyle("Center", parent=base_styles["BodyText"], alignment=TA_CENTER, fontSize=8),
    }

    story: list[Any] = [
        Paragraph("MECH WIZ PLTU Target Screening Report", styles["title"]),
        Paragraph(
            "Laporan nilai, output, dan prioritas awal dari 26 site PLTU target untuk screening CO2 capture to e-methanol.",
            styles["subtitle"],
        ),
        Paragraph(f"Generated from local MECH WIZ runtime database - {generated_at} WIB", styles["small"]),
        Spacer(1, 5 * mm),
        Paragraph("Executive Summary", styles["h2"]),
        Paragraph(
            "Dataset ini mengubah aplikasi dari sekadar peta titik menjadi cockpit screening awal: sistem menghitung ketersediaan CO2, captured CO2, potensi e-methanol, kebutuhan H2, kebutuhan electrolyzer, ranking kandidat, dan confidence data.",
            styles["body"],
        ),
        _metric_grid(totals, top_name),
        Spacer(1, 3 * mm),
        Paragraph(
            "<b>Status laporan:</b> screening/pre-feasibility. Angka belum menggantikan konfirmasi PLN, site visit, data CEMS/DCS, stack test aktual, vendor quotation, terminal operator confirmation, atau offtake contract. Hasil ekonomi tetap harus dikalibrasi pada phase berikutnya.",
            styles["warning"],
        ),
        Paragraph("Input Yang Dipakai", styles["h2"]),
        Paragraph(
            f"Data input terdiri dari 26 PLTU target, total kapasitas {_fmt_number(totals['capacity_mw'], 1)} MW, koordinat publik, kapasitas publik/user target, dan status confidence per site.",
            styles["body"],
        ),
        Paragraph(
            f"Asumsi operasi: capacity factor {_fmt_percent(CAPACITY_FACTOR)}, operasi {OPERATING_DAYS_PER_YEAR} hari/tahun. Asumsi proses: capture rate 85%, process efficiency methanol 60%.",
            styles["body"],
        ),
        Paragraph(
            f"Baku mutu existing coal PLTU: SO2 {BME_EXISTING_COAL['so2_mg_nm3']:.0f}, NOx {BME_EXISTING_COAL['nox_mg_nm3']:.0f}, PM {BME_EXISTING_COAL['particulate_mg_nm3']:.0f}, Hg {BME_EXISTING_COAL['hg_mg_nm3']:.2f} mg/Nm3.",
            styles["body"],
        ),
        Paragraph(
            "Confidence data: "
            + ", ".join(f"{label}: {confidence_counts.get(label, 0)}" for label in ("high", "medium", "low", "unknown")),
            styles["note"],
        ),
        Paragraph("Apa Yang Dihitung Aplikasi", styles["h2"]),
        _make_table(
            [
                ["Output", "Makna", "Dipakai untuk"],
                ["Total CO2 t/y", "Estimasi CO2 tahunan dari benchmark stack berbasis kapasitas.", "Menilai besar sumber karbon."],
                ["Captured CO2 t/y", "CO2 yang dapat masuk proses dengan capture rate 85%.", "Menentukan skala capture plant."],
                ["Methanol t/y", "Potensi e-methanol setelah konversi dan efisiensi proses.", "Menilai ukuran market/offtake."],
                ["H2 required t/y", "Kebutuhan hydrogen untuk sintesis methanol.", "Menilai beban supply H2 dan power."],
                ["Electrolyzer MW", "Ukuran electrolyzer indikatif.", "Menilai kebutuhan CAPEX dan listrik hijau."],
                ["Composite score", "Gabungan opportunity, readiness, dan confidence.", "Ranking kandidat pilot."],
                ["Heatmap weight", "Bobot visual map untuk opportunity/readiness/ekonomi/confidence.", "Layer heatmap dan economic zone."],
            ],
            [36 * mm, 82 * mm, 62 * mm],
        ),
        Paragraph("Top 10 Kandidat Screening", styles["h2"]),
        _ranking_table(rows, styles, 10),
        Paragraph(
            "Ranking saat ini didominasi oleh skala kapasitas/CO2. Phase berikutnya perlu menambah validasi pelabuhan, lahan, grid, vendor CAPEX, dan offtake untuk membuat shortlist investasi yang lebih defensible.",
            styles["small"],
        ),
        Paragraph("Interpretasi Value", styles["h2"]),
        _make_table(
            [
                ["Value", "Penjelasan"],
                ["Strategic shortlist", "Membantu memilih site prioritas untuk studi lanjut, bukan mengejar semua 26 site sekaligus."],
                ["Scale sizing", "Menunjukkan apakah konsepnya pilot kecil, cluster besar, atau perlu diperkecil karena kebutuhan H2/electrolyzer sangat besar."],
                ["Data gap control", "Menunjukkan site mana yang datanya kuat dan mana yang belum layak dipakai untuk keputusan komite."],
                ["Map intelligence", "Map menampilkan potensi berdasarkan ranking, heatmap, dan integrasi pelabuhan/koridor ekspor."],
                ["Pre-FEED preparation", "Output menjadi daftar pertanyaan teknis dan komersial sebelum vendor quote dan site survey."],
            ],
            [45 * mm, 135 * mm],
        ),
        Paragraph("Ekonomi Awal", styles["h2"]),
        Paragraph(
            f"Gross revenue benchmark agregat adalah {_fmt_money(totals['gross_revenue'])} per tahun dari methanol dan carbon credit benchmark. Namun NPV agregat masih negatif dalam asumsi awal karena biaya H2, listrik, dan CAPEX masih benchmark konservatif. Output saat ini lebih kuat untuk screening prioritas daripada investment decision.",
            styles["body"],
        ),
        Paragraph(
            "Phase berikutnya harus mengkalibrasi financial assumptions: CAPEX capture, electrolyzer, methanol plant, storage/port, harga H2, listrik hijau, harga methanol, carbon credit, dan skema offtake.",
            styles["note"],
        ),
        Paragraph("Recommended Next Phase", styles["h2"]),
        _make_table(
            [
                ["Phase 10 - Economic Calibration & Shortlist Validation"],
                ["Kalibrasi CAPEX/OPEX dengan basis vendor atau benchmark yang eksplisit per komponen."],
                ["Validasi nearest port dan kesiapan pelabuhan untuk Top 10."],
                ["Tambah scoring logistik: jarak pelabuhan, draft, liquid bulk, export corridor, dan Singapore proxy route."],
                ["Buat shortlist Top 3/Top 5 dengan alasan teknis, ekonomi, dan data gap."],
                ["Generate investor/committee memo per kandidat."],
            ],
            [180 * mm],
            repeat_rows=0,
        ),
        PageBreak(),
        Paragraph("Appendix - Full 26 Site Ranking", styles["h2"]),
        _ranking_table(rows, styles, None),
        Spacer(1, 4 * mm),
        Paragraph("Source Trace", styles["h2"]),
        Paragraph(
            "Detail sumber per site dan catatan confidence tersedia di repository: docs/PLTU_CURATED_DATASET_SOURCES.md. Importer dataset: backend/app/import_target_pltu.py.",
            styles["body"],
        ),
    ]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm,
        title="MECH WIZ PLTU Target Screening Report",
        author="MECH WIZ",
    )
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    if not PDF_PATH.exists() or PDF_PATH.stat().st_size < 10_000:
        raise RuntimeError(f"PDF generation failed or output is too small: {PDF_PATH}")
    return PDF_PATH


def main() -> None:
    print(build_pdf())


if __name__ == "__main__":
    main()
