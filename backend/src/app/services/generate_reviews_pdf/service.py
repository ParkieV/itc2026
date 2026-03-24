from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@dataclass(frozen=True, slots=True)
class MockReview:
    position: int
    structural_element: str
    organization: str
    comment: str
    proposed_revision: str
    rationale: str
    developer_response: str


class GenerateReviewsPdfService:
    _FONT_NAME = "TimesNewRoman"
    _FONT_PATHS = {
        "normal": Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        "bold": Path("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"),
        "italic": Path("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"),
        "boldItalic": Path("/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf"),
    }

    def execute(self) -> bytes:
        self._register_times_new_roman()
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=14 * mm,
            bottomMargin=11 * mm,
        )

        styles = self._build_styles()
        story = self._build_title_flowables(styles["title"])
        story.append(Spacer(1, 8 * mm))
        story.append(self._build_table(styles["header"], styles["body"], styles["body_center"]))

        document.build(story)
        return buffer.getvalue()

    def _build_title_flowables(self, title_style: ParagraphStyle) -> list[Paragraph]:
        title_lines = [
            "Приложение",
            "Сводная информация по предложениям, поступившим от организаций, "
            "по рассмотрению окончательной редакции проекта ПНСТ",
            "«Интеллектуальные транспортные системы. Подсистема диспетчеризации "
            "перевозок опасных грузов. Общие требования»",
            "(Шифр: 1.11.057-1.121.25)",
        ]
        return [Paragraph(line, title_style) for line in title_lines]

    def _build_table(
        self,
        header_style: ParagraphStyle,
        body_style: ParagraphStyle,
        body_center_style: ParagraphStyle,
    ) -> Table:
        rows: list[list[Paragraph]] = [
            [
                Paragraph("п/п", header_style),
                Paragraph("Структурный элемент проекта", header_style),
                Paragraph("Наименование организации или иного лица (номер письма, дата)", header_style),
                Paragraph("Замечание, предложение", header_style),
                Paragraph("Предлагаемая редакция", header_style),
                Paragraph("Обоснование предлагаемой редакции", header_style),
                Paragraph("Ответ разработчика", header_style),
            ]
        ]

        for review in self._build_mock_reviews():
            rows.append(
                [
                    Paragraph(str(review.position), body_center_style),
                    Paragraph(review.structural_element, body_style),
                    Paragraph(review.organization, body_style),
                    Paragraph(review.comment, body_style),
                    Paragraph(review.proposed_revision, body_style),
                    Paragraph(review.rationale, body_style),
                    Paragraph(review.developer_response, body_style),
                ]
            )

        table = Table(
            rows,
            colWidths=[
                24,
                82,
                110,
                145,
                145,
                140,
                82,
            ],
            repeatRows=1,
            splitByRow=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), self._FONT_NAME),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _build_styles(self) -> dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "reviews_title",
                parent=styles["Normal"],
                fontName=self._FONT_NAME,
                fontSize=12,
                leading=14,
                alignment=TA_CENTER,
                spaceAfter=0,
            ),
            "header": ParagraphStyle(
                "reviews_header",
                parent=styles["Normal"],
                fontName=self._FONT_NAME,
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
            ),
            "body": ParagraphStyle(
                "reviews_body",
                parent=styles["Normal"],
                fontName=self._FONT_NAME,
                fontSize=10,
                leading=12,
                alignment=TA_LEFT,
            ),
            "body_center": ParagraphStyle(
                "reviews_body_center",
                parent=styles["Normal"],
                fontName=self._FONT_NAME,
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
            ),
        }

    def _register_times_new_roman(self) -> None:
        if self._FONT_NAME in pdfmetrics.getRegisteredFontNames():
            return

        missing = [name for name, path in self._FONT_PATHS.items() if not path.exists()]
        if missing:
            raise RuntimeError(
                "Times New Roman fonts not found: " + ", ".join(missing)
            )

        pdfmetrics.registerFont(TTFont(self._FONT_NAME, str(self._FONT_PATHS["normal"])))
        pdfmetrics.registerFont(TTFont(f"{self._FONT_NAME}-Bold", str(self._FONT_PATHS["bold"])))
        pdfmetrics.registerFont(TTFont(f"{self._FONT_NAME}-Italic", str(self._FONT_PATHS["italic"])))
        pdfmetrics.registerFont(
            TTFont(f"{self._FONT_NAME}-BoldItalic", str(self._FONT_PATHS["boldItalic"]))
        )
        pdfmetrics.registerFontFamily(
            self._FONT_NAME,
            normal=self._FONT_NAME,
            bold=f"{self._FONT_NAME}-Bold",
            italic=f"{self._FONT_NAME}-Italic",
            boldItalic=f"{self._FONT_NAME}-BoldItalic",
        )

    def _build_mock_reviews(self) -> list[MockReview]:
        return [
            MockReview(
                position=index,
                structural_element=f"Раздел {index}. Требования к подсистеме диспетчеризации перевозок опасных грузов",
                organization=(
                    f"ООО «Организация {index}» "
                    f"(исх. № {100 + index} от {index:02d}.03.2026)"
                ),
                comment=(
                    "Предлагается уточнить состав обязательных данных, которые должны "
                    "передаваться в подсистему, а также порядок обновления этих сведений."
                ),
                proposed_revision=(
                    "Установить минимальный обязательный набор данных о транспортном средстве, "
                    "маршруте, грузе и статусе перевозки с обновлением не реже одного раза в 5 минут."
                ),
                rationale=(
                    "Такая редакция исключает неоднозначность при внедрении стандарта в "
                    "региональных системах и облегчает контроль полноты передаваемой информации."
                ),
                developer_response=(
                    "Принято частично. В окончательной редакции будут уточнены состав обязательных "
                    "полей и минимальная периодичность обновления сведений."
                ),
            )
            for index in range(1, 19)
        ]
