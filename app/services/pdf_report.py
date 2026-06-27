from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.schemas import InsightsResponse, StatsResponse, TrendsResponse


def generate_pdf_report(
    stats: StatsResponse,
    trends: TrendsResponse,
    insights: InsightsResponse,
    manager_name: str | None = None,
) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch

    def write_line(text: str, size: int = 11, gap: float = 16):
        nonlocal y
        if y < inch:
            pdf.showPage()
            y = height - inch
        pdf.setFont("Helvetica", size)
        pdf.drawString(inch, y, text[:100])
        y -= gap

    pdf.setTitle("Hotel Sentiment Report")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(inch, y, "Hotel Guest Sentiment Report")
    y -= 24

    write_line(f"Prepared for: {manager_name or 'Hotel Manager'}", 10, 14)
    write_line(f"Total reviews analyzed: {stats.total_reviews}", 11)

    write_line("Executive Summary", 14, 20)
    for chunk in _wrap_text(insights.summary, 90):
        write_line(chunk, 10, 14)

    write_line("Top Strength: " + (insights.top_strength or "N/A"), 11)
    write_line("Top Weakness: " + (insights.top_weakness or "N/A"), 11, 22)

    write_line("Aspect Breakdown", 14, 20)
    for aspect in stats.aspect_breakdown:
        write_line(
            f"- {aspect.aspect}: {aspect.avg_score * 100:.1f}% ({aspect.count} mentions)",
            10,
            14,
        )

    write_line("Recommendations", 14, 20)
    for item in insights.recommendations:
        write_line(f"[{item.priority}] {item.title}", 10, 14)
        for chunk in _wrap_text(item.detail, 88):
            write_line("  " + chunk, 9, 12)

    if trends.points:
        write_line("Recent Trend", 14, 20)
        for point in trends.points[-6:]:
            write_line(
                f"- {point.period}: {point.avg_sentiment * 100:.1f}% ({point.review_count} reviews)",
                10,
                14,
            )

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) <= width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines
