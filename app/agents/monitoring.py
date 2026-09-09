import hashlib
import html
import ssl
import urllib.request
import os
import re
import difflib
from datetime import datetime, timezone
import certifi
from sqlalchemy.orm import Session


from app.models import Source, SourceVersion, Task
from app.agents.parsing import ParsingAgent

# Uses certifi's bundled Mozilla CA store instead of the OS trust store, since
# minimal Docker base images (e.g. python:3.11-slim) don't reliably ship a
# populated system cert store even after installing ca-certificates - this
# keeps HTTPS source verification working regardless of OS-level cert config.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# adilet.zan.kz (Kazakhstan's official legal information system - a primary
# monitored source for this app) is misconfigured: its server sends only its
# leaf certificate, omitting the required intermediate CA. Browsers mask this
# via out-of-band AIA chasing, but strict clients (OpenSSL/Python's ssl
# module, including certifi-backed contexts) correctly reject it with
# "unable to get local issuer certificate". The missing intermediate is
# bundled here explicitly, retrieved from its own AIA "CA Issuers" URL
# (http://cacerts.digicert.com/GoGetSSLG2TLSRSA4096SHA2562022CA-1.crt); it
# chains up to DigiCert Global Root G2, which is already trusted via certifi.
_ADILET_ZAN_KZ_MISSING_INTERMEDIATE = """-----BEGIN CERTIFICATE-----
MIIFyjCCBLKgAwIBAgIQAj0aJv70U8kh5Zg6YeVmEzANBgkqhkiG9w0BAQsFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH
MjAeFw0yMjA2MjMwMDAwMDBaFw0zMjA2MjIyMzU5NTlaMFsxCzAJBgNVBAYTAkxW
MRkwFwYDVQQKExBFblZlcnMgR3JvdXAgU0lBMTEwLwYDVQQDEyhHb0dldFNTTCBH
MiBUTFMgUlNBNDA5NiBTSEEyNTYgMjAyMiBDQS0xMIICIjANBgkqhkiG9w0BAQEF
AAOCAg8AMIICCgKCAgEAvbTWrKE7Sy3UTrr0xofDMCQN3E9dYWmbb8NEumw8l83l
ZRNmbaoGyy/TRosCluEfbeYUVcdTrct4Y9/hrGkaH19udFm/adnoSq2l34ZBMh3O
SvODjM871urT3vcB2b2Z1jKOujsujlRI+JYC2tJQ011psrNhJM6XIDzqKlFQkpYO
sQ5obVUjzKHVYjaCLQNDq/hWv/6dYUHvYLukESRbKX6y17odvu2LsNnS0gh6c7I7
w4plTU1ha9P+zuyGrd2WcWvlqppIQLHttLpx8EC/NbEma6V2Hj6T244mf6Xn+BXy
UJU8N4EUsEib6XWo6wb+r0rSk6Zensgn3pLcdhJRNGdivV/Pgn68aLkfYA4zOyiC
0w/Ihg/Y39IcKrDvab1m8D35AMu+fpDaqp8O1cBeOttxz5S7URN+Vl35bV3ckch4
zr7o9CHOfkoutZtQGQ7yOMGBw7xES8L58PoaUOHQB8JOk3uvgcFSTPPtXwOSWwaN
konMh0nes1UktOoOCeoQ4hRCPuFxjrhOD04s//5tpM6Qb+YQP/6pC9NH4smp0ho3
ExWMAvete/M+/Q2Y3UuN1PVJsVBVeQPip7x2jUI5JvB/ugT5Kuh3GAtNDlCa/EuR
RveLqlTbZF5rK6FCOd3lgbH87KrcL5S/neeJy8UFazCnAlc2aGPtdpgeYSr8zPMC
AwEAAaOCAYIwggF+MBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFIWrzO4+
E0NrAfHwegXxojihDSpjMB8GA1UdIwQYMBaAFE4iVCAYlebjbuYP+vq5Eu0GF485
MA4GA1UdDwEB/wQEAwIBhjAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIw
dgYIKwYBBQUHAQEEajBoMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdpY2Vy
dC5jb20wQAYIKwYBBQUHMAKGNGh0dHA6Ly9jYWNlcnRzLmRpZ2ljZXJ0LmNvbS9E
aWdpQ2VydEdsb2JhbFJvb3RHMi5jcnQwQgYDVR0fBDswOTA3oDWgM4YxaHR0cDov
L2NybDMuZGlnaWNlcnQuY29tL0RpZ2lDZXJ0R2xvYmFsUm9vdEcyLmNybDA9BgNV
HSAENjA0MAsGCWCGSAGG/WwCATAHBgVngQwBATAIBgZngQwBAgEwCAYGZ4EMAQIC
MAgGBmeBDAECAzANBgkqhkiG9w0BAQsFAAOCAQEAGhl3IVUbRlj28G/Ger5S2/4E
P2cTPTmHI1SroMIfIOsZ6IsRf7BSIoGMf/fTCsN8OnIiNywo9M9cJ4taNayYseW7
YqPVXLIROsOh8zOecUts9wf+WCwiKCfcq1m26UoB6SIQwWVzm6uUQrsSdWpW8bpB
VjsxSTHLKzRAaH6N+kDJJY7Rg7MVL/BInP9gvupH3+eA/LGAnlTSNQ4plu79rpU5
cBfv6XjQ1lYzxY6epOB76s/rJvN3miTvgy4BOkpnrukofS9HbwVAd0eisdontIVu
9cKNh5sjxJMkOIKhOHCVVMawyzftJ2KpXzgesZswdet61XJBlDkFGAtbovVi7A==
-----END CERTIFICATE-----
"""
_SSL_CONTEXT.load_verify_locations(cadata=_ADILET_ZAN_KZ_MISSING_INTERMEDIATE)

class MonitoringAgent:
    """
    MonitoringAgent is responsible for downloading legislation documents,
    checking for content changes using SHA256 hashes, generating colorized 
    side-by-side diffs, and triggering the analysis pipeline.
    """

    @staticmethod
    def calculate_sha256(content: str) -> str:
        """Calculates SHA256 hash of a text string."""
        return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    @classmethod
    def fetch_source_content(cls, url: str) -> bytes:
        """Downloads content from a URL or reads it from a local file path."""
        if url.startswith("http://") or url.startswith("https://"):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as response:
                return response.read()
        else:
            # Assume local file path
            if not os.path.isabs(url):
                # Resolve relative to project root or workspace
                url = os.path.abspath(url)
            with open(url, "rb") as f:
                return f.read()

    @classmethod
    def run_check(cls, source_id: int, db: Session) -> dict:
        """
        Executes monitoring check on a single Source.
        Returns check results containing whether changes were detected and processed.
        """
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.is_active:
            return {"status": "skipped", "reason": "Source inactive or not found"}

        try:
            raw_bytes = cls.fetch_source_content(source.url)
            # Find extension from URL or filename (handles both / and \ paths on Windows)
            clean_url = source.url.replace('\\', '/').split('?')[0]
            file_name = os.path.basename(clean_url) if clean_url else "doc.html"
            if '.' not in file_name:
                file_name += ".html"  # Default fallback
                
            # Parse document to Markdown and structure
            markdown_content, parsed_structure = ParsingAgent.parse_content(raw_bytes, file_name)
            current_sha = cls.calculate_sha256(markdown_content)
            
            source.last_checked = datetime.now(timezone.utc)
            
            # Check if there is a previous version
            last_version = db.query(SourceVersion).filter(
                SourceVersion.source_id == source.id
            ).order_by(SourceVersion.version_num.desc()).first()
            
            if last_version and last_version.sha256 == current_sha:
                source.last_sha256 = current_sha
                db.commit()
                return {"status": "unchanged", "reason": "SHA256 hashes are identical", "source": source.title}
                
            # SHA changed or first run!
            new_version_num = (last_version.version_num + 1) if last_version else 1
            
            new_version = SourceVersion(
                source_id=source.id,
                version_num=new_version_num,
                sha256=current_sha,
                content_markdown=markdown_content,
                parsed_structure=parsed_structure
            )
            db.add(new_version)
            db.flush()  # Generate new_version.id
            
            source.last_sha256 = current_sha
            
            # Compare with previous version if it exists
            has_real_changes = True
            diff_html = ""
            
            if last_version:
                # Run Difference Engine
                has_real_changes, diff_html = cls.diff_documents(
                    last_version.content_markdown, 
                    new_version.content_markdown
                )
                db.commit()

                if not has_real_changes:
                    return {
                        "status": "cosmetic_only",
                        "reason": "Cosmetic changes detected only, skipping AI analysis",
                        "source": source.title,
                        "version": new_version_num,
                        "has_real_changes": False
                    }

                # If real changes exist between versions, create a analysis Task
                task = Task(
                    source_id=source.id,
                    old_version_id=last_version.id,
                    new_version_id=new_version.id,
                    diff_html=diff_html,
                    status="Pending"
                )
                db.add(task)
                db.commit()

                return {
                    "status": "changed",
                    "task_id": task.id,
                    "source": source.title,
                    "version": new_version_num,
                    "has_real_changes": True
                }
            else:
                # First version = baseline established! No diff analysis task needed
                diff_html = cls.generate_full_added_diff(new_version.content_markdown)
                db.commit()
                return {
                    "status": "baseline_established",
                    "reason": "Первоначальный эталон успешно зафиксирован в мониторинге (SHA256).",
                    "source": source.title,
                    "version": new_version_num,
                    "has_real_changes": False
                }
            
        except Exception as e:
            db.rollback()
            return {"status": "error", "error": str(e), "source": source.title}

    @classmethod
    def _highlight_inline_diff(cls, old_str: str, new_str: str) -> tuple[str, str]:
        """Highlights word-level insertions and deletions within changed lines."""
        if not old_str:
            return "", f"<ins class='inline-ins'>{html.escape(new_str)}</ins>"
        if not new_str:
            return f"<del class='inline-del'>{html.escape(old_str)}</del>", ""

        old_words = re.findall(r'\S+|\s+', old_str)
        new_words = re.findall(r'\S+|\s+', new_str)
        matcher = difflib.SequenceMatcher(None, old_words, new_words)

        out_old = []
        out_new = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            sub_old = "".join(old_words[i1:i2])
            sub_new = "".join(new_words[j1:j2])
            if tag == 'equal':
                out_old.append(html.escape(sub_old))
                out_new.append(html.escape(sub_new))
            elif tag == 'replace':
                if sub_old:
                    out_old.append(f"<del class='inline-del'>{html.escape(sub_old)}</del>")
                if sub_new:
                    out_new.append(f"<ins class='inline-ins'>{html.escape(sub_new)}</ins>")
            elif tag == 'delete':
                out_old.append(f"<del class='inline-del'>{html.escape(sub_old)}</del>")
            elif tag == 'insert':
                out_new.append(f"<ins class='inline-ins'>{html.escape(sub_new)}</ins>")

        return "".join(out_old), "".join(out_new)

    @classmethod
    def _extract_document_articles(cls, text: str) -> list[dict]:
        """
        Splits legal text into ordered articles / chapters with canonized identifiers.
        """
        lines = text.splitlines()
        articles = []
        cur_article = {
            "id": "sec_preamble",
            "key": "преамбула",
            "title": "Преамбула",
            "lines": []
        }
        
        art_regex = re.compile(r'^(статья\s+\d+[\-\d]*|глава\s+\d+|раздел\s+\d+|параграф\s+\d+)\.?\s*(.*)$', re.IGNORECASE)
        header_regex = re.compile(r'^#+\s+(.*)$')
        
        for line in lines:
            line_str = line.strip()
            clean_hdr = header_regex.sub(r'\1', line_str).strip()
            match = art_regex.match(clean_hdr)
            if match:
                if cur_article["lines"] or cur_article["key"] != "преамбула":
                    articles.append(cur_article)
                art_key = match.group(1).lower()
                cur_article = {
                    "id": f"sec_{len(articles)+1}",
                    "key": art_key,
                    "title": clean_hdr,
                    "lines": [line]
                }
            else:
                cur_article["lines"].append(line)
                
        if cur_article["lines"] or cur_article["key"] != "преамбула":
            articles.append(cur_article)
            
        return articles

    @classmethod
    def _diff_article_lines(cls, old_lines: list[str], new_lines: list[str], article_title: str) -> tuple[int, list[str]]:
        """Compares lines of a single article and returns (real_change_count, diff_rows)."""
        differ = difflib.SequenceMatcher(None, old_lines, new_lines)
        diff_rows = []
        real_change_count = 0

        cosmetic_patterns = [
            r'^\s*$',
            r'^согласовано:.*$',
            r'^подпись:.*$',
            r'^дата:.*$',
            r'^версия:.*$',
            r'^утверждено\s+приказом.*$'
        ]

        def is_cosmetic(line: str) -> bool:
            line_clean = line.strip().lower()
            if not line_clean:
                return True
            for pattern in cosmetic_patterns:
                if re.match(pattern, line_clean):
                    return True
            return False

        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    o_line = old_lines[i1 + k]
                    n_line = new_lines[j1 + k]
                    is_header = (k == 0 and (o_line.strip().startswith('#') or 'статья' in o_line.lower()))
                    header_cls = " class='diff-header-row'" if is_header else ""
                    row_type = "article-header" if is_header else "equal"
                    diff_rows.append(
                        f"<tr{header_cls} data-row-type='{row_type}' data-article='{html.escape(article_title)}'>"
                        f"<td class='ln'>{i1+k+1}</td><td>{html.escape(o_line)}</td>"
                        f"<td class='ln'>{j1+k+1}</td><td>{html.escape(n_line)}</td></tr>"
                    )
            elif tag == 'replace':
                for k in range(max(i2 - i1, j2 - j1)):
                    o_line = old_lines[i1 + k] if k < (i2 - i1) else ""
                    n_line = new_lines[j1 + k] if k < (j2 - j1) else ""
                    o_ln = i1 + k + 1 if k < (i2 - i1) else ""
                    n_ln = j1 + k + 1 if k < (j2 - j1) else ""

                    is_cos_change = is_cosmetic(o_line) and is_cosmetic(n_line)
                    o_norm = re.sub(r'["\'«»“”\s]', '', o_line.lower())
                    n_norm = re.sub(r'["\'«»“”\s]', '', n_line.lower())
                    if o_norm == n_norm:
                        is_cos_change = True

                    if not is_cos_change:
                        real_change_count += 1

                    td_old_class = "class='del'" if o_line else ""
                    td_new_class = "class='add'" if n_line else ""
                    old_rendered, new_rendered = cls._highlight_inline_diff(o_line, n_line)

                    diff_rows.append(
                        f"<tr data-row-type='change' class='diff-row-changed' data-article='{html.escape(article_title)}'>"
                        f"<td class='ln'>{o_ln}</td><td {td_old_class}>{old_rendered}</td>"
                        f"<td class='ln'>{n_ln}</td><td {td_new_class}>{new_rendered}</td></tr>"
                    )
            elif tag == 'delete':
                for k in range(i2 - i1):
                    o_line = old_lines[i1 + k]
                    if not is_cosmetic(o_line):
                        real_change_count += 1
                    diff_rows.append(
                        f"<tr data-row-type='change' class='diff-row-changed' data-article='{html.escape(article_title)}'>"
                        f"<td class='ln'>{i1+k+1}</td><td class='del'><del class='inline-del'>{html.escape(o_line)}</del></td>"
                        f"<td class='ln'></td><td></td></tr>"
                    )
            elif tag == 'insert':
                for k in range(j2 - j1):
                    n_line = new_lines[j1 + k]
                    if not is_cosmetic(n_line):
                        real_change_count += 1
                    diff_rows.append(
                        f"<tr data-row-type='change' class='diff-row-changed' data-article='{html.escape(article_title)}'>"
                        f"<td class='ln'></td><td></td>"
                        f"<td class='ln'>{j1+k+1}</td><td class='add'><ins class='inline-ins'>{html.escape(n_line)}</ins></td></tr>"
                    )

        return real_change_count, diff_rows

    @classmethod
    def diff_documents(cls, old_text: str, new_text: str) -> tuple[bool, str]:
        """
        Two-Level Article-Aware Difference Engine.
        1. Aligns articles by identifier (Статья 1, Статья 2, etc.)
        2. Compares lines within aligned articles with word-level inline diff.
        """
        old_articles = cls._extract_document_articles(old_text)
        new_articles = cls._extract_document_articles(new_text)

        # If both documents have structured articles, use article-level alignment
        if len(old_articles) > 1 or len(new_articles) > 1:
            old_map = {a["key"]: a for a in old_articles}
            new_map = {a["key"]: a for a in new_articles}

            # Build unified ordered keys: prioritize new_articles order, then add repealed old articles
            all_keys = []
            seen = set()
            for a in new_articles:
                if a["key"] not in seen:
                    all_keys.append(a["key"])
                    seen.add(a["key"])
            for a in old_articles:
                if a["key"] not in seen:
                    all_keys.append(a["key"])
                    seen.add(a["key"])

            all_diff_rows = []
            total_real_changes = 0

            for key in all_keys:
                old_art = old_map.get(key)
                new_art = new_map.get(key)
                art_title = (new_art or old_art)["title"]

                if old_art and new_art:
                    ch_cnt, rows = cls._diff_article_lines(old_art["lines"], new_art["lines"], art_title)
                    total_real_changes += ch_cnt
                    all_diff_rows.extend(rows)
                elif new_art and not old_art:
                    # Entire new article added
                    total_real_changes += len(new_art["lines"])
                    for j, n_line in enumerate(new_art["lines"]):
                        all_diff_rows.append(
                            f"<tr data-row-type='change' class='diff-row-changed' data-article='{html.escape(art_title)}'>"
                            f"<td class='ln'></td><td></td>"
                            f"<td class='ln'>{j+1}</td><td class='add'><ins class='inline-ins'>{html.escape(n_line)}</ins></td></tr>"
                        )
                elif old_art and not new_art:
                    # Entire article deleted / repealed
                    total_real_changes += len(old_art["lines"])
                    for i, o_line in enumerate(old_art["lines"]):
                        all_diff_rows.append(
                            f"<tr data-row-type='change' class='diff-row-changed' data-article='{html.escape(art_title)}'>"
                            f"<td class='ln'>{i+1}</td><td class='del'><del class='inline-del'>{html.escape(o_line)}</del></td>"
                            f"<td class='ln'></td><td></td></tr>"
                        )

            html_table = (
                "<table class='diff-table'>"
                "<thead><tr><th>LN</th><th>Предыдущая редакция (Было)</th><th>LN</th><th>Новая редакция (Стало)</th></tr></thead>"
                f"<tbody>{''.join(all_diff_rows)}</tbody>"
                "</table>"
            )
            return (total_real_changes > 0), html_table

        # Fallback for plain unstructured texts
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        ch_cnt, diff_rows = cls._diff_article_lines(old_lines, new_lines, "Текст документа")

        html_table = (
            "<table class='diff-table'>"
            "<thead><tr><th>LN</th><th>Предыдущая редакция (Было)</th><th>LN</th><th>Новая редакция (Стало)</th></tr></thead>"
            f"<tbody>{''.join(diff_rows)}</tbody>"
            "</table>"
        )
        return (ch_cnt > 0), html_table

    @classmethod
    def generate_comparative_table_docx(cls, task_id: int, db) -> bytes:
        """
        Generates a professional 3-column Comparative Table of Amendments in DOCX format:
        [ № Статьи | Предыдущая редакция (Было) | Новая редакция (Стало) | Характер изменений ]
        """
        import io
        import docx
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from app.models import Task

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task #{task_id} not found")

        doc = docx.Document()

        # Set page margins
        for section in doc.sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.7)
            section.right_margin = Inches(0.7)

        title = doc.add_heading("СРАВНИТЕЛЬНАЯ ТАБЛИЦА ИЗМЕНЕНИЙ", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        source_title = task.source.title if task.source else "Нормативный правовой акт"
        p_sub = doc.add_paragraph(f"к нормативному правовому акту: «{source_title}»")
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.runs[0].font.italic = True

        v_old_num = task.old_version.version_num if task.old_version else 1
        v_new_num = task.new_version.version_num if task.new_version else 2
        p_meta = doc.add_paragraph(f"Сравнение редакции №{v_old_num} и редакции №{v_new_num} (Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')})")
        p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()

        # Extract articles and compare
        old_text = task.old_version.content_markdown if task.old_version else ""
        new_text = task.new_version.content_markdown if task.new_version else ""

        old_articles = cls._extract_document_articles(old_text)
        new_articles = cls._extract_document_articles(new_text)
        old_map = {a["key"]: a for a in old_articles}
        new_map = {a["key"]: a for a in new_articles}

        all_keys = []
        seen = set()
        for a in new_articles:
            if a["key"] not in seen:
                all_keys.append(a["key"])
                seen.add(a["key"])
        for a in old_articles:
            if a["key"] not in seen:
                all_keys.append(a["key"])
                seen.add(a["key"])

        # Create Table
        table = doc.add_table(rows=1, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = 'Table Grid'

        hdr_cells = table.rows[0].cells
        hdr_titles = ["№ / Статья", "Предыдущая редакция (Было)", "Новая редакция (Стало)", "Характер изменений"]
        for idx, text in enumerate(hdr_titles):
            hdr_cells[idx].text = text
            hdr_cells[idx].paragraphs[0].runs[0].font.bold = True
            hdr_cells[idx].paragraphs[0].runs[0].font.size = Pt(10)

        for key in all_keys:
            old_art = old_map.get(key)
            new_art = new_map.get(key)
            art_title = (new_art or old_art)["title"]

            old_lines_str = "\n".join(old_art["lines"]) if old_art else ""
            new_lines_str = "\n".join(new_art["lines"]) if new_art else ""

            if old_art and new_art:
                has_diff, _ = cls._diff_article_lines(old_art["lines"], new_art["lines"], art_title)
                if has_diff:
                    row_cells = table.add_row().cells
                    row_cells[0].text = art_title
                    row_cells[1].text = old_lines_str
                    row_cells[2].text = new_lines_str
                    row_cells[3].text = "Внесены поправки"
            elif new_art and not old_art:
                row_cells = table.add_row().cells
                row_cells[0].text = art_title
                row_cells[1].text = "—"
                row_cells[2].text = new_lines_str
                row_cells[3].text = "Новая статья (Добавлена)"
            elif old_art and not new_art:
                row_cells = table.add_row().cells
                row_cells[0].text = art_title
                row_cells[1].text = old_lines_str
                row_cells[2].text = "—"
                row_cells[3].text = "Исключена (Утратила силу)"

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.getvalue()
                    
        html_table = (
            "<table class='diff-table'>"
            "<thead><tr><th>LN</th><th>Предыдущая редакция (Было)</th><th>LN</th><th>Новая редакция (Стало)</th></tr></thead>"
            f"<tbody>{''.join(diff_rows)}</tbody>"
            "</table>"
        )
        
        has_real_changes = real_change_count > 0
        return has_real_changes, html_table

    @classmethod
    def generate_full_added_diff(cls, text: str) -> str:
        """Generates diff markup showing the entire document as added."""
        lines = text.splitlines()
        rows = []
        for i, line in enumerate(lines):
            rows.append(
                f"<tr><td class='ln'></td><td></td>"
                f"<td class='ln'>{i+1}</td><td class='add'>{html.escape(line)}</td></tr>"
            )
        return (
            "<table class='diff-table'>"
            "<thead><tr><th>LN</th><th>Предыдущая редакция</th><th>LN</th><th>Новая редакция</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )
