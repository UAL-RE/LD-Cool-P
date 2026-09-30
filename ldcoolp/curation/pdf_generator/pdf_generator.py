from pathlib import Path
from typing import Any

from fpdf import FPDF, TextStyle

# Default Directory & File Constants
DEFAULT_ASSETS_DIR = Path(__file__).parent.resolve() / "assets"
UA_LOGO_PATH = DEFAULT_ASSETS_DIR / "logo-uofa.png"
REDATA_LOGO_PATH = DEFAULT_ASSETS_DIR / "logo-redata.png"

# Color Palette Constants (RGB)
COLOR_RGB_UA_RED = (171, 5, 32)
COLOR_RGB_UA_BLUE = (12, 35, 75)
COLOR_RGB_BLACK = (0, 0, 0)
COLOR_RGB_WHITE = (255, 255, 255)

# Font Family Constants
FONT_FAMILY_LiberationSerif = "LiberationSerif"
FONT_FILES = (  # font family, style, filename
    (FONT_FAMILY_LiberationSerif, "", "LiberationSerif-Regular.ttf"),
    (FONT_FAMILY_LiberationSerif, "B", "LiberationSerif-Bold.ttf"),
    (FONT_FAMILY_LiberationSerif, "I", "LiberationSerif-Italic.ttf"),
    (FONT_FAMILY_LiberationSerif, "BI", "LiberationSerif-BoldItalic.ttf"),
    # NOTE: Additional font families can be added here as needed
)
FONT_FAMILY_PRIMARY = FONT_FAMILY_LiberationSerif

# Page Dimension & Layout Constants (Points)
INCH = 72.0  # 1 inch = 72 points

# fmt: off  # for black formatter
# Using inch conversion to keep MS Word consistent
DEFAULT_UNIT          = "pt"
DEFAULT_FORMAT        = "letter"
PAGE_WIDTH_PT         = 8.5 * INCH  # 612 points
PAGE_HEIGHT_PT        = 11.0 * INCH  # 792 points
MARGIN_TOP_PT         = 1.0 * INCH  # 72 points
MARGIN_BOTTOM_PT      = 1.0 * INCH  # 72 points
MARGIN_LEFT_PT        = 0.75 * INCH  # 54 points
MARGIN_RIGHT_PT       = 0.75 * INCH  # 54 points
BANNER_HEIGHT_PT      = 0.75 * INCH  # 54 points
UA_LOGO_HEIGHT_PT     = 0.5 * INCH  # 36 points
REDATA_LOGO_WIDTH_PT  = 2.61 * INCH  # 187.92 points
DEFAULT_FOOTER_TEXT   = "UA ReDATA - Deposit Agreement"

DEFAULT_HTML_TAG_STYLES = {
    "b": TextStyle(font_style="B", color=COLOR_RGB_BLACK, t_margin=0.1, b_margin=0.1),
    "i": TextStyle(font_style="I", color=COLOR_RGB_BLACK, t_margin=0.1, b_margin=0.1),
    "u": TextStyle(font_style="U", color=COLOR_RGB_BLACK, t_margin=0.1, b_margin=0.1),
    "a": TextStyle(font_style="U", color=COLOR_RGB_UA_RED, t_margin=0.1, b_margin=0.1),
    "ul": TextStyle(t_margin=-0.5, b_margin=0),
    "li": TextStyle(t_margin=5, b_margin=5, l_margin=24),
    "h1": TextStyle(font_size_pt=20, color=COLOR_RGB_BLACK, t_margin=6.0, b_margin=0.1, l_margin="C"),
    "h2": TextStyle(font_size_pt=16, color=COLOR_RGB_BLACK, t_margin=0.1, b_margin=0.1),
    "h3": TextStyle(font_size_pt=14, color=COLOR_RGB_BLACK, t_margin=0.1, b_margin=0.1),
}
# fmt: on  # for black formatter

# Embedded Data Filter Keys
INCLUDED_EMBEDDED_KEYS = (
    "article_id",
    "curation_id",
    "recordedDate",
    "ResponseID",
    "SurveyID",
)


class LayoutConfig:
    """Configuration class for dimensions, margins, and brand styling."""

    def __init__(
        self,
        unit: str = DEFAULT_UNIT,
        format: str = DEFAULT_FORMAT,
        page_width: float = PAGE_WIDTH_PT,
        page_height: float = PAGE_HEIGHT_PT,
        margin_top: float = MARGIN_TOP_PT,
        margin_bottom: float = MARGIN_BOTTOM_PT,
        margin_left: float = MARGIN_LEFT_PT,
        margin_right: float = MARGIN_RIGHT_PT,
        banner_height: float = BANNER_HEIGHT_PT,
    ) -> None:
        self.unit = unit
        self.format = format
        self.page_width = page_width
        self.page_height = page_height
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.banner_height = banner_height

    @property
    def printable_width(self) -> float:
        """Calculates effective printable horizontal width."""

        return self.page_width - self.margin_left - self.margin_right


class AccessiblePDF(FPDF):
    """
    FPDF subclass managing custom font loading, header/footer canvas drawing,
    and visual background banners.
    """

    def __init__(self, config: LayoutConfig, assets_path: Path) -> None:
        super().__init__(unit=config.unit, format=config.format)
        self.config = config
        self.assets_path = assets_path

        # Load local fonts from assets directory
        self._load_custom_fonts()

        # Core Document Setup
        self.set_margins(
            self.config.margin_left,
            self.config.margin_top,
            self.config.margin_right,
        )
        self.set_auto_page_break(auto=True, margin=self.config.margin_bottom)
        self.set_line_width(1.0)
        self.set_font(FONT_FAMILY_PRIMARY, "", 12)
        self.set_text_color(*COLOR_RGB_BLACK)
        self.alias_nb_pages()

    def _load_custom_fonts(self) -> None:
        """Registers local font files from the assets directory."""

        for family, style, filename in FONT_FILES:
            font_file = self.assets_path / filename
            if font_file.exists():
                self.add_font(family, style=style, fname=font_file)

    def _draw_banner(self, color: tuple[int, int, int], y: float) -> None:
        """Helper method to draw full-width header/footer background banners."""

        self.set_fill_color(*color)
        self.rect(
            x=0, y=y, w=self.config.page_width, h=self.config.banner_height, style="F"
        )

    def header(self) -> None:
        """Draws top header banner and embeds UA logo."""

        with self.local_context():
            self._draw_banner(COLOR_RGB_UA_RED, y=0)

            if UA_LOGO_PATH and UA_LOGO_PATH.exists():
                logo_y = (self.config.banner_height - UA_LOGO_HEIGHT_PT) / 2.0
                self.image(
                    str(UA_LOGO_PATH),
                    x=self.config.margin_left,
                    y=logo_y,
                    h=UA_LOGO_HEIGHT_PT,
                    alt_text="University of Arizona Logo",
                )

    def footer(self) -> None:
        """Draws bottom footer banner with title text and dynamic page numbers."""

        banner_y = self.config.page_height - self.config.banner_height

        with self.local_context():
            self._draw_banner(COLOR_RGB_UA_BLUE, y=banner_y)

            # Center text vertically within footer banner
            text_y = banner_y + (self.config.banner_height / 2.0) - 6.0
            self.set_y(text_y)
            self.set_font(FONT_FAMILY_PRIMARY, "I", 12)
            self.set_text_color(*COLOR_RGB_WHITE)

            # Left Footer Text
            self.set_x(self.config.margin_left)
            self.cell(w=250, h=12, text=DEFAULT_FOOTER_TEXT, align="L")

            # Right "Page {page_no} of {nb}"
            self.set_font(FONT_FAMILY_PRIMARY, "", 12)
            page_str = f"Page {self.page_no()} of {{nb}}"
            self.set_x(self.config.page_width - self.config.margin_right - 100)
            self.cell(w=100, h=12, text=page_str, align="R")


class DepositAgreementBuilder:
    """
    Document Orchestrator responsible for rendering structured content,
    survey QA maps, HTML elements, and metadata blocks.
    """

    def __init__(
        self, config: LayoutConfig | None = None, assets_path: Path | None = None
    ) -> None:
        self.config = config or LayoutConfig()
        self.assets_path = assets_path or DEFAULT_ASSETS_DIR

    def create_bulleted_list(self, qa_pairs: Any) -> str:
        """Transforms iterable question/answer pairs into an HTML unordered list."""

        bullet_list = "".join(
            f"<li><b>{question}:</b> {answer}</li>" for question, answer in qa_pairs
        )
        return f"<ul>{bullet_list}</ul>"

    def _render_header_logo_and_title(self, pdf: AccessiblePDF) -> None:
        """Draws top ReDATA logo, main document headings, and top divider line."""

        if REDATA_LOGO_PATH.exists():
            center_x = (self.config.page_width - REDATA_LOGO_WIDTH_PT) / 2.0
            pdf.image(
                str(REDATA_LOGO_PATH),
                x=center_x,
                w=REDATA_LOGO_WIDTH_PT,
                alt_text="UA ReDATA Logo",
            )

        # Main Title
        pdf.write_html(
            "<h1>University of Arizona Research Data Repository</h1>",
            li_prefix_color=COLOR_RGB_BLACK,
            tag_styles=DEFAULT_HTML_TAG_STYLES,
        )

        # Subtitle
        pdf.write_html(
            "<h1><b>Deposit Agreement</b></h1>",
            li_prefix_color=COLOR_RGB_BLACK,
            tag_styles=DEFAULT_HTML_TAG_STYLES,
        )

        # Divider Line
        pdf.ln()
        pdf.line(
            self.config.margin_left,
            pdf.get_y(),
            self.config.page_width - self.config.margin_right,
            pdf.get_y(),
        )
        pdf.ln()

    def _render_qa_section(self, pdf: AccessiblePDF, merged_qa: dict[str, Any]) -> None:
        """Iterates over QA dictionary to format section headers, infos, and questions."""

        page_break_flag = False
        qa_data: dict[str, str]  # Type hint for clarity

        for qid, qa_data in merged_qa.items():
            question_text = qa_data["questionText"]
            label = qa_data.get("questionLabel")

            if label == "SectionHeader":
                if page_break_flag:
                    pdf.add_page()

                pdf.write_html(
                    question_text,
                    li_prefix_color=COLOR_RGB_BLACK,
                    tag_styles=DEFAULT_HTML_TAG_STYLES,
                )
                pdf.ln()
                page_break_flag = True

            elif label == "Info":
                pdf.write_html(
                    question_text,
                    li_prefix_color=COLOR_RGB_BLACK,
                    tag_styles=DEFAULT_HTML_TAG_STYLES,
                )
                pdf.ln()

            elif label == "Question":
                if not qa_data.get("answer"):
                    continue

                if qa_data.get("questionType", "").endswith("FORM"):
                    qa_pairs = zip(
                        qa_data.get("formQuestions", []), qa_data.get("answer", [])
                    )
                    answer_text = self.create_bulleted_list(qa_pairs)
                else:
                    answer_text = f"<ul><li>{qa_data.get('answer', '')}</li></ul>"

                pdf.write_html(
                    question_text,
                    li_prefix_color=COLOR_RGB_BLACK,
                    tag_styles=DEFAULT_HTML_TAG_STYLES,
                )
                pdf.write_html(
                    answer_text,
                    ul_bullet_char="●",
                    li_prefix_color=COLOR_RGB_BLACK,
                    tag_styles=DEFAULT_HTML_TAG_STYLES,
                )
                pdf.ln()

    def _render_embedded_data(
        self, pdf: AccessiblePDF, embedded_data: dict[str, Any]
    ) -> None:
        """Renders bottom divider line and embedded metadata section."""

        # Divider Line
        pdf.ln()
        pdf.line(
            self.config.margin_left,
            pdf.get_y(),
            self.config.page_width - self.config.margin_right,
            pdf.get_y(),
        )
        pdf.ln()

        pdf.add_page()
        pdf.write_html(
            "<h3><b>Embedded Data</b></h3>",
            li_prefix_color=COLOR_RGB_BLACK,
            tag_styles=DEFAULT_HTML_TAG_STYLES,
        )
        pdf.ln()

        for key, value in sorted(embedded_data.items()):
            if key in INCLUDED_EMBEDDED_KEYS:
                pdf.write_html(
                    f"<b>{key}:</b> {value}",
                    li_prefix_color=COLOR_RGB_BLACK,
                    tag_styles=DEFAULT_HTML_TAG_STYLES,
                )

    def generate(self, data: dict[str, Any], output_path: str | Path) -> Path:
        """Main pipeline entry point: constructs document and exports to disk."""

        if not data or not isinstance(data, dict):
            raise ValueError(
                "Provided data is either empty or invalid."
            )  # Raises exception

        if not output_path or not isinstance(output_path, (str, Path)):
            raise ValueError(
                "Provided output_path is either empty or invalid."
            )  # Raises exception

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pdf = AccessiblePDF(config=self.config, assets_path=self.assets_path)
        pdf.add_page()

        # Render centered logo, titles, and top divider line
        self._render_header_logo_and_title(pdf)

        if "merged_qa" in data and data["merged_qa"]:
            self._render_qa_section(pdf, data["merged_qa"])

        if "embedded_data" in data and data["embedded_data"]:
            self._render_embedded_data(pdf, data["embedded_data"])

        pdf.output(str(output_path))
        return output_path
