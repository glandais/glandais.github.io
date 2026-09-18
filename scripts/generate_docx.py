from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from scripts.resume_loader import get_filename_base, normalize_text

DIST_DIR = Path(__file__).resolve().parent.parent / "dist"

FONT_NAME = "Calibri"
FONT_SIZE_BODY = Pt(10.5)
FONT_SIZE_SMALL = Pt(10)
FONT_SIZE_NAME = Pt(14)
FONT_SIZE_SECTION = Pt(12)
MARGIN = Cm(1.8)
MARGIN_VERTICAL = Cm(1.5)
LANG = "fr-FR"


def _set_run_font(rpr_parent, name=FONT_NAME):
    """Force explicit fonts, dropping theme fonts that would override them."""
    rpr = rpr_parent.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(qn(attr), None)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def _set_font(run, size=FONT_SIZE_BODY, bold=False):
    run.font.name = FONT_NAME
    run.font.size = size
    run.bold = bold
    _set_run_font(run._r)


def _setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = FONT_SIZE_BODY
    _set_run_font(normal.element)
    fmt = normal.paragraph_format
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(2)
    fmt.line_spacing = 1.0

    # Document language (spell check, parsers relying on it)
    rpr_default = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    lang = rpr_default.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr_default.append(lang)
    lang.set(qn("w:val"), LANG)
    lang.set(qn("w:eastAsia"), LANG)

    heading = doc.styles["Heading 1"]
    heading.font.name = FONT_NAME
    heading.font.size = FONT_SIZE_SECTION
    heading.font.bold = True
    heading.font.color.rgb = RGBColor(0, 0, 0)
    _set_run_font(heading.element)
    hfmt = heading.paragraph_format
    hfmt.space_before = Pt(10)
    hfmt.space_after = Pt(4)
    hfmt.keep_with_next = True

    bullet = doc.styles["List Bullet"]
    bullet.paragraph_format.space_after = Pt(1)


def _add_heading_text(doc, text):
    p = doc.add_paragraph(style="Heading 1")
    run = p.add_run(text)
    _set_font(run, size=FONT_SIZE_SECTION, bold=True)
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def _add_body(doc, text, space_after=Pt(2)):
    p = doc.add_paragraph()
    run = p.add_run(text)
    _set_font(run)
    p.paragraph_format.space_after = space_after
    return p


def _add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    _set_font(run)
    p.paragraph_format.space_after = Pt(1)
    return p


def _add_hyperlink(paragraph, text, url, size=FONT_SIZE_SMALL):
    r_id = paragraph.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rfonts = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT_NAME)
    rpr.append(rfonts)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F4E9A")
    rpr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rpr.append(underline)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size.pt * 2)))
    rpr.append(sz)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def _url(value: str) -> str:
    return value if value.startswith(("http://", "https://", "mailto:")) else f"https://{value}"


def _format_date(d):
    if d is None:
        return "Présent"
    return d


def _set_core_properties(doc, data):
    basics = data["basics"]
    props = doc.core_properties
    props.author = basics["name"]
    props.last_modified_by = basics["name"]
    props.title = f"{basics['name']} – {basics['label']}"
    props.subject = "Curriculum vitae"
    props.language = LANG
    keywords = ", ".join(kw for group in data.get("skills", []) for kw in group.get("keywords", []))
    props.keywords = keywords[:255].rsplit(",", 1)[0] if len(keywords) > 255 else keywords
    now = datetime.now().replace(microsecond=0)
    props.created = now
    props.modified = now
    props.revision = 1


def generate_docx(data: dict) -> Path:
    doc = Document()
    _setup_styles(doc)
    _set_core_properties(doc, data)

    # A4 page, margins, no header/footer
    for section in doc.sections:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = MARGIN_VERTICAL
        section.bottom_margin = MARGIN_VERTICAL
        section.left_margin = MARGIN
        section.right_margin = MARGIN
        section.header.is_linked_to_previous = True
        section.footer.is_linked_to_previous = True
        section.different_first_page_header_footer = False

    basics = data["basics"]

    # Name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(basics["name"])
    _set_font(run, size=FONT_SIZE_NAME, bold=True)

    # Label
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(basics["label"])
    _set_font(run, size=FONT_SIZE_BODY)

    # Contact info — in body, NOT in header/footer
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    items = []
    if basics.get("email"):
        items.append((basics["email"], f"mailto:{basics['email']}"))
    if basics.get("phone"):
        items.append((basics["phone"], None))
    loc = basics.get("location", {})
    if loc.get("city"):
        city_str = loc["city"]
        if loc.get("postalCode"):
            city_str = f"{loc['postalCode']} {city_str}"
        items.append((city_str, None))
    for key in ("linkedin", "github"):
        if basics.get(key):
            items.append((basics[key], _url(basics[key])))
    for i, (text, url) in enumerate(items):
        if i:
            _set_font(p.add_run(" | "), size=FONT_SIZE_SMALL)
        if url:
            _add_hyperlink(p, text, url)
        else:
            _set_font(p.add_run(text), size=FONT_SIZE_SMALL)

    # Summary
    if basics.get("summary"):
        _add_heading_text(doc, "Profil")
        _add_body(doc, normalize_text(basics["summary"]))

    # Skills
    if data.get("skills"):
        _add_heading_text(doc, "Compétences")
        for group in data["skills"]:
            p = doc.add_paragraph()
            run = p.add_run(f"{group['category']} : ")
            _set_font(run, bold=True)
            run = p.add_run(", ".join(group["keywords"]))
            _set_font(run)

    # Experience
    if data.get("experience"):
        _add_heading_text(doc, "Expérience professionnelle")
        for exp in data["experience"]:
            start = _format_date(exp.get("startDate"))
            end = _format_date(exp.get("endDate"))

            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(f"{exp['title']} — {exp['company']}")
            _set_font(run, bold=True)

            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            meta = f"{start} – {end}"
            if exp.get("location"):
                meta += f" | {exp['location']}"
            if exp.get("freelance"):
                meta += " | Freelance"
            run = p.add_run(meta)
            _set_font(run, size=FONT_SIZE_SMALL)

            for h in exp.get("highlights", []):
                _add_bullet(doc, h)

            if exp.get("stack"):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run("Stack : ")
                _set_font(run, bold=True, size=FONT_SIZE_SMALL)
                run = p.add_run(exp["stack"])
                _set_font(run, size=FONT_SIZE_SMALL)

    # Early career (condensed, one paragraph per position)
    if data.get("early_career"):
        _add_heading_text(doc, "Début de carrière")
        for item in data["early_career"]:
            p = doc.add_paragraph()
            head = f"{item['period']} — {item['company']}"
            if item.get("title"):
                head += f", {item['title']}"
            run = p.add_run(f"{head} : ")
            _set_font(run, bold=True)
            run = p.add_run(item["summary"])
            _set_font(run)
            if item.get("stack"):
                run = p.add_run(f" ({item['stack']})")
                _set_font(run, size=FONT_SIZE_SMALL)

    # Projects
    if data.get("projects"):
        _add_heading_text(doc, "Projets et open source")
        for proj in data["projects"]:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(proj["name"])
            _set_font(run, bold=True)
            if proj.get("url"):
                _set_font(p.add_run(" — "))
                _add_hyperlink(p, proj["url"].removeprefix("https://"), proj["url"])

            _add_body(doc, proj["description"])
            if proj.get("keywords"):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(", ".join(proj["keywords"]))
                _set_font(run, size=FONT_SIZE_SMALL)

    # Education
    if data.get("education"):
        _add_heading_text(doc, "Formation")
        for edu in data["education"]:
            p = doc.add_paragraph()
            run = p.add_run(f"{edu['studyType']} {edu['area']}")
            _set_font(run, bold=True)
            years = f"{str(edu.get('startDate', ''))[:4]} – {str(edu.get('endDate', ''))[:4]}"
            run = p.add_run(f" — {edu['institution']} ({years})")
            _set_font(run)

    # Languages
    if data.get("languages"):
        _add_heading_text(doc, "Langues")
        _add_body(doc, " ; ".join(f"{lang['language']} : {lang['fluency']}" for lang in data["languages"]))

    # Interests
    if data.get("interests"):
        _add_heading_text(doc, "Centres d'intérêt")
        _add_body(doc, ", ".join(data["interests"]))

    # Save
    out_dir = DIST_DIR / "docx"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = get_filename_base(data) + ".docx"
    out_path = out_dir / filename
    doc.save(str(out_path))
    return out_path
