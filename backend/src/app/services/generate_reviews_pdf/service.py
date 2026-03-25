import asyncio
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from entities.comment import Comment
from entities.user import User
from services.get_comments_by_doc.service import GetCommentsByDocService
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService


@dataclass(frozen=True, slots=True)
class MockReview:
    position: int
    structural_element: str
    organization: str
    remark: str | None
    proposal: str | None
    justification: str | None
    developer_response: str


class GenerateReviewsPdfService:
    _FONT_NAME = "TimesNewRoman"
    _PAGE_SIZE = landscape(A4)
    _LEFT_MARGIN = 20 * mm
    _RIGHT_MARGIN = 20 * mm
    _TOP_MARGIN = 14 * mm
    _BOTTOM_MARGIN = 11 * mm
    _TITLE_MAX_WIDTH = _PAGE_SIZE[0] - _LEFT_MARGIN - _RIGHT_MARGIN
    _FONT_PATHS = {
        "normal": "Times New Roman.ttf",
        "bold": "Times New Roman Bold.ttf",
        "italic": "Times New Roman Italic.ttf",
        "boldItalic": "Times New Roman Bold Italic.ttf",
    }

    def __init__(
        self,
        get_comments_by_doc_service: GetCommentsByDocService,
        get_user_service: GetUserService,
        get_pdf_document_service: GetPdfDocumentService,
    ) -> None:
        self._get_comments_by_doc_service = get_comments_by_doc_service
        self._get_user_service = get_user_service
        self._get_pdf_document_service = get_pdf_document_service

    async def execute(self, doc_id: int) -> bytes:
        self._register_times_new_roman()
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=self._PAGE_SIZE,
            leftMargin=self._LEFT_MARGIN,
            rightMargin=self._RIGHT_MARGIN,
            topMargin=self._TOP_MARGIN,
            bottomMargin=self._BOTTOM_MARGIN,
        )

        styles = self._build_styles()
        pdf_document = await self._get_pdf_document_service.execute(doc_id)
        story = self._build_title_flowables(styles["title"], pdf_document.title)
        story.append(Spacer(1, 8 * mm))
        comments = await self._get_comments_by_doc_service.execute(doc_id)
        users_by_id = await self._get_users_by_id_for_top_comments(comments)
        reviews = self._build_mock_reviews(comments, users_by_id)
        story.append(self._build_table(styles["header"], styles["body"], styles["body_center"], reviews))

        document.build(story)
        return buffer.getvalue()

    def _build_title_flowables(
        self,
        title_style: ParagraphStyle,
        document_title: str,
    ) -> list[Paragraph]:
        title_lines = [
            "Приложение",
            "Сводная информация по предложениям, поступившим от организаций, "
            "по рассмотрению окончательной редакции проекта ПНСТ",
            *self._wrap_title_lines(self._format_document_title(document_title), title_style),
            "(Шифр: 1.11.057-1.121.25)",
        ]
        return [Paragraph(line, title_style) for line in title_lines]

    @classmethod
    def _wrap_title_lines(
        cls,
        title_text: str,
        title_style: ParagraphStyle,
    ) -> list[str]:
        words = title_text.split()
        if not words:
            return [title_text]

        lines: list[str] = []
        current_line = words[0]

        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if cls._fits_title_width(candidate, title_style):
                current_line = candidate
                continue

            lines.extend(cls._split_long_title_part(current_line, title_style))
            current_line = word

        lines.extend(cls._split_long_title_part(current_line, title_style))
        return lines

    @classmethod
    def _split_long_title_part(
        cls,
        title_part: str,
        title_style: ParagraphStyle,
    ) -> list[str]:
        if cls._fits_title_width(title_part, title_style):
            return [title_part]

        parts: list[str] = []
        current_part = ""
        for char in title_part:
            candidate = f"{current_part}{char}"
            if current_part and not cls._fits_title_width(candidate, title_style):
                parts.append(current_part)
                current_part = char
                continue
            current_part = candidate

        if current_part:
            parts.append(current_part)

        return parts

    @classmethod
    def _fits_title_width(
        cls,
        text: str,
        title_style: ParagraphStyle,
    ) -> bool:
        return stringWidth(text, title_style.fontName, title_style.fontSize) <= cls._TITLE_MAX_WIDTH

    @staticmethod
    def _format_document_title(document_title: str) -> str:
        normalized_title = " ".join(document_title.split())
        if not normalized_title:
            return "«»"

        quote_pairs = {
            ("«", "»"),
            ('"', '"'),
            ("'", "'"),
            ("“", "”"),
            ("„", "“"),
        }
        if (normalized_title[0], normalized_title[-1]) in quote_pairs:
            return normalized_title

        return f"«{normalized_title}»"

    def _build_table(
        self,
        header_style: ParagraphStyle,
        body_style: ParagraphStyle,
        body_center_style: ParagraphStyle,
        reviews: list[MockReview],
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

        for review in reviews:
            rows.append(
                [
                    Paragraph(str(review.position), body_center_style),
                    Paragraph(review.structural_element, body_style),
                    Paragraph(review.organization, body_style),
                    Paragraph(review.remark or "", body_style),
                    Paragraph(review.proposal or "", body_style),
                    Paragraph(review.justification or "", body_style),
                    Paragraph(review.developer_response or "", body_style),
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

        fonts_dir = self._get_fonts_dir()
        font_paths = {name: fonts_dir / filename for name, filename in self._FONT_PATHS.items()}

        missing = [name for name, path in font_paths.items() if not path.exists()]
        if missing:
            raise RuntimeError(
                "Times New Roman fonts not found: " + ", ".join(missing)
            )

        pdfmetrics.registerFont(TTFont(self._FONT_NAME, str(font_paths["normal"])))
        pdfmetrics.registerFont(TTFont(f"{self._FONT_NAME}-Bold", str(font_paths["bold"])))
        pdfmetrics.registerFont(TTFont(f"{self._FONT_NAME}-Italic", str(font_paths["italic"])))
        pdfmetrics.registerFont(
            TTFont(f"{self._FONT_NAME}-BoldItalic", str(font_paths["boldItalic"]))
        )
        pdfmetrics.registerFontFamily(
            self._FONT_NAME,
            normal=self._FONT_NAME,
            bold=f"{self._FONT_NAME}-Bold",
            italic=f"{self._FONT_NAME}-Italic",
            boldItalic=f"{self._FONT_NAME}-BoldItalic",
        )

    @staticmethod
    def _get_fonts_dir() -> Path:
        candidates = [
            Path("/static/fonts"),
            Path(__file__).resolve().parents[3] / "static" / "fonts",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return candidates[0]

    @staticmethod
    def _build_reply_map(comments: list[Comment]) -> dict[int, Comment]:
        """
        reply_to -> reply_comment
        Берём первое совпадение по reply_to, чтобы не дублировать данные.
        """
        out: dict[int, Comment] = {}
        # Сортируем по id, чтобы "первое совпадение" было детерминированным.
        for c in sorted(comments, key=lambda x: x.comment_id):
            if c.reply_to is None:
                continue
            out.setdefault(c.reply_to, c)
        return out

    async def _get_users_by_id_for_top_comments(
        self,
        comments: list[Comment],
    ) -> dict[int, User]:
        top_comments = [c for c in comments if c.reply_to is None]
        author_ids = sorted({c.user_id for c in top_comments})
        if not author_ids:
            return {}

        async def _fetch(aid: int) -> tuple[int, User | None]:
            try:
                return aid, await self._get_user_service.execute(aid)
            except UserNotFound:
                return aid, None

        fetched = await asyncio.gather(*(_fetch(aid) for aid in author_ids))
        return {aid: u for aid, u in fetched if u is not None}

    def _build_mock_reviews(
        self,
        comments: list[Comment],
        users_by_id: dict[int, User],
    ) -> list[MockReview]:
        comments_sorted = sorted(comments, key=lambda x: x.comment_id)
        reply_map = self._build_reply_map(comments_sorted)
        top_comments = [c for c in comments_sorted if c.reply_to is None]

        reviews: list[MockReview] = []
        for position, c in enumerate(top_comments, start=1):
            reply = reply_map.get(c.comment_id)
            developer_response = (reply.developer_response or "") if reply else ""
            organization = users_by_id.get(c.user_id).organization if c.user_id in users_by_id else ""

            reviews.append(
                MockReview(
                    position=position,
                    structural_element=(
                        f"Раздел {position}. Требования к подсистеме диспетчеризации "
                        "перевозок опасных грузов"
                    ),
                    organization=organization,
                    remark=c.remark,
                    proposal=c.proposal,
                    justification=c.justification,
                    developer_response=developer_response,
                )
            )

        return reviews
