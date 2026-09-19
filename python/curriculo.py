from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    CondPageBreak,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INK = colors.HexColor("#16283F")      
ACCENT = colors.HexColor("#2E7CB8")  
MUTED = colors.HexColor("#5F6F82")   
BODY = colors.HexColor("#2B3440")    
RULE = colors.HexColor("#D6DFEA")     
TINT = colors.HexColor("#EDF3F9")     

PAGE_W, PAGE_H = A4
MARGIN_X = 1.25 * cm  
MARGIN_TOP = 1.0 * cm
MARGIN_BOTTOM = 1.3 * cm
FRAME_PAD = 6  
CONTENT_X = MARGIN_X + FRAME_PAD  
CONTENT_W = PAGE_W - 2 * CONTENT_X

NAME = "ADAM RODRIGUES"
HEADLINE = "Database Reliability Engineer Sr. / DBA"
CONTACT_1 = "adamrodrigues98@gmail.com   ·   (31) 97163-8205   ·   Matozinhos, MG"
CONTACT_2 = "linkedin.com/in/adam-rodrigues-067a54150   ·   github.com/AdamRodrigues98"


class HeaderBand(Flowable):

    def __init__(self, width: float, height: float = 2.70 * cm):
        super().__init__()
        self.w = width
        self.h = height

    def wrap(self, avail_w, avail_h):
        return self.w, self.h

    def draw(self):
        c = self.canv
        bleed = 6 
        bleed_top = MARGIN_TOP  

        c.setFillColor(INK)
        c.rect(
            -CONTENT_X - bleed,
            0,
            PAGE_W + 2 * bleed,
            self.h + bleed_top + bleed,
            stroke=0,
            fill=1,
        )

        c.setFillColor(ACCENT)
        c.rect(-CONTENT_X - bleed, 0, PAGE_W + 2 * bleed, 0.12 * cm, stroke=0, fill=1)

        top = self.h + bleed_top
        mid = PAGE_W / 2.0 - CONTENT_X  

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(mid, top - 1.05 * cm, NAME)

        c.setFillColor(colors.HexColor("#A9C6E0"))
        c.setFont("Helvetica", 9.8)
        c.drawCentredString(mid, top - 1.62 * cm, HEADLINE)

        c.setFillColor(colors.HexColor("#DCE7F2"))
        c.setFont("Helvetica", 8.4)
        c.drawCentredString(mid, top - 2.28 * cm, CONTACT_1)
        c.drawCentredString(mid, top - 2.74 * cm, CONTACT_2)


class TagCloud(Flowable):
    FONT = "Helvetica"
    SIZE = 8.2
    PAD_X = 5.0
    ROW_H = 13.0
    GAP_X = 4.0
    GAP_Y = 3.5

    def __init__(self, tags: list[str], width: float | None = None):
        super().__init__()
        self.tags = tags
        self.w = width
        self._rows: list[list[tuple[str, float]]] = []
        self.h = 0

    def _layout(self, avail_w: float):
        rows, current, used = [], [], 0.0
        for tag in self.tags:
            tag_w = stringWidth(tag, self.FONT, self.SIZE) + 2 * self.PAD_X
            extra = tag_w if not current else tag_w + self.GAP_X
            if current and used + extra > avail_w:
                rows.append(current)
                current, used = [(tag, tag_w)], tag_w
            else:
                current.append((tag, tag_w))
                used += extra
        if current:
            rows.append(current)
        self._rows = rows
        self.h = len(rows) * self.ROW_H + max(0, len(rows) - 1) * self.GAP_Y

    def wrap(self, avail_w, avail_h):
        self.w = self.w or avail_w
        self._layout(self.w)
        return self.w, self.h

    def draw(self):
        c = self.canv
        y = self.h - self.ROW_H
        for row in self._rows:
            x = 0.0
            for tag, tag_w in row:
                c.setFillColor(TINT)
                c.setStrokeColor(RULE)
                c.setLineWidth(0.5)
                c.roundRect(x, y, tag_w, self.ROW_H, 2.5, stroke=1, fill=1)
                c.setFillColor(INK)
                c.setFont(self.FONT, self.SIZE)
                c.drawString(x + self.PAD_X, y + 3.9, tag)
                x += tag_w + self.GAP_X
            y -= self.ROW_H + self.GAP_Y


class TimelineMarker(Flowable):

    def __init__(self, height: float, is_current: bool):
        super().__init__()
        self.h = height
        self.w = 0.85 * cm
        self.is_current = is_current
        self.line_x = 0.3 * cm
        self.radius = 0.11 * cm

    def wrap(self, avail_w, avail_h):
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.setStrokeColor(RULE)
        c.setLineWidth(1)
        c.line(self.line_x, 0, self.line_x, self.h)

        y_mid = self.h - 0.32 * cm
        if self.is_current:
            c.setFillColor(ACCENT)
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1.2)
        else:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor("#9FB3C8"))
            c.setLineWidth(1)
        c.circle(self.line_x, y_mid, self.radius, stroke=1, fill=1)

def _footer(canv, doc):
    canv.saveState()
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.5)
    y = MARGIN_BOTTOM - 0.35 * cm
    canv.line(CONTENT_X, y, PAGE_W - CONTENT_X, y)
    canv.setFont("Helvetica", 7.6)
    canv.setFillColor(MUTED)
    canv.drawString(CONTENT_X, y - 0.38 * cm, "Adam Rodrigues  ·  Currículo")
    canv.drawRightString(PAGE_W - CONTENT_X, y - 0.38 * cm, f"Página {doc.page}")
    canv.restoreState()


RESUMO = (
    "DBA e Engenheiro de Dados com mais de 8 anos em ambientes críticos de alta "
    "disponibilidade e grande volume. Atuo em PostgreSQL, MySQL, SQL Server e MongoDB "
    "na AWS, unindo performance tuning, práticas de DBRE (observabilidade, RCA e "
    "capacity planning) e plataformas analíticas com Python, Airflow e Trino."
)

SKILL_GROUPS = [
    (
        "Bancos de Dados",
        ["MySQL", "PostgreSQL", "SQL Server", "Oracle / PL-SQL", "MongoDB",
         "Amazon Aurora", "DynamoDB", "SQL / T-SQL"],
    ),
    (
        "Cloud & Infraestrutura",
        ["AWS", "Azure", "Kubernetes / EKS", "Docker", "Terraform", "ArgoCD / GitOps",
         "Jenkins / CI-CD", "EC2"],
    ),
    (
        "Dados & Automação",
        ["Python", "Airflow", "Trino", "ETL / ELT", "Data Lake", "Data Warehouse",
         "Lakehouse", "Kafka"],
    ),
    (
        "Confiabilidade",
        ["Performance Tuning", "Observabilidade", "Alta Disponibilidade", "Replicação",
         "Grafana / Prometheus", "Datadog", "CloudWatch", "Capacity Planning"],
    ),
]

NEXTI_ROLES = [
    {
        "title": "Database Reliability Engineer Sr.",
        "period": "abr/2026 – Atual",
        "is_current": True,
        "bullets": [
            "Administração de PostgreSQL, MySQL e SQL Server na AWS com tuning de queries, "
            "índices, planos de execução e parâmetros, sustentando escalabilidade e estabilidade "
            "de ambientes críticos.",
            "Práticas de DBRE: observabilidade, resposta a incidentes, RCA, capacity planning, "
            "redução de toil e automação operacional, com atuação em War Rooms junto a "
            "Desenvolvimento, Infraestrutura e negócio.",
            "Automação de rotinas ETL/ELT com Python, Airflow e Trino, e arquiteturas "
            "Data Lake/Lakehouse que reduzem carga em sistemas OLTP.",
            "Operação de ambientes containerizados com Kubernetes/EKS, Docker, Terraform, "
            "Jenkins e ArgoCD; monitoramento em Grafana, Prometheus, Datadog e CloudWatch.",
        ],
    },
    {
        "title": "DBA & Data Engineer",
        "period": "mar/2025 – abr/2026",
        "is_current": False,
        "bullets": [
            "Construção e manutenção de pipelines de dados e processos ETL/ELT para relatórios "
            "e análises históricas.",
            "Implementação de Data Lake, Data Warehouse e Lakehouse, com governança das camadas "
            "históricas para geração de indicadores.",
            "Automação de cargas e integrações com Python, Airflow, Jenkins, Terraform e ArgoCD; "
            "versionamento com Git/GitFlow.",
        ],
    },
    {
        "title": "DBA Pleno",
        "period": "fev/2024 – fev/2025",
        "is_current": False,
        "bullets": [
            "Projetos de migração, replicação e criação de bases com foco em alta disponibilidade "
            "e distribuição de carga entre ambientes.",
            "Otimização de desempenho e acompanhamento contínuo de saúde das bases com Grafana, "
            "Prometheus, Datadog, Performance Insights e CloudWatch.",
            "Suporte técnico a times de Desenvolvimento, Suporte e Infraestrutura em modelagem, "
            "acesso e boas práticas de banco.",
        ],
    },
]

MOOT_ROLES = [
    {
        "title": "Database Analyst T-SQL Sênior · Sustentação",
        "period": "jan/2023 – jan/2024",
        "is_current": False,
        "bullets": [
            "Suporte N3 em ambiente de alta criticidade, com troubleshooting e análise de causa "
            "raiz em banco de dados, APIs, infraestrutura e observabilidade.",
            "Rotinas de atualização e correção em SQL Server e MongoDB, estruturação de "
            "monitoramento e alertas e alinhamentos técnicos com stakeholders e clientes.",
            "Datadog, Graylog, Site24x7, ServiceNow, Azure DevOps, Postman/Swagger, AWS e Azure; "
            "scripts em Python e JavaScript.",
        ],
    },
    {
        "title": "Database Analyst T-SQL Pleno · Sustentação",
        "period": "fev/2022 – jan/2023",
        "is_current": False,
        "bullets": [
            "Sustentação N2 com diagnóstico e mitigação de falhas em produção via análise de logs, "
            "métricas e rastreabilidade de requisições.",
            "Monitoramento proativo e processos ITSM (incidentes, mudanças e problem management), "
            "reduzindo indisponibilidades e reincidências.",
            "Validação de integrações via APIs REST e SOAP; consultas e análises em SQL Server "
            "e MongoDB.",
        ],
    },
]

SINGLE_ROLES = [
    {
        "title": "Database Analyst N3 · Oracle PL-SQL",
        "company": "Unimed-BH  ·  Belo Horizonte, MG",
        "period": "out/2020 – dez/2021",
        "bullets": [
            "Desenvolvimento de scripts PL/SQL em Oracle Database para diagnóstico e "
            "identificação de falhas na aplicação.",
            "Acompanhamento de KPIs e incidentes via ServiceNow, com gestão de demandas "
            "em Azure DevOps e cerimônias Scrum.",
        ],
    },
    {
        "title": "Analista de Tecnologia da Informação SQL Server & T-SQL",
        "company": "Mastermaq Software  ·  Belo Horizonte, MG",
        "period": "jun/2018 – jan/2020",
        "bullets": [
            "Sustentação do ERP e administração do ambiente SQL Server: T-SQL, rotinas de "
            "backup/restore e otimização de desempenho em bases de clientes.",
        ],
    },
]

EARLIER = (
    "<b>Técnico de Suporte N2</b> · Santa Casa de Misericórdia de BH (dez/2017 – jun/2018)"
    " &nbsp;•&nbsp; <b>Técnico de Suporte</b> · Yazaki Mercosul (fev/2013 – mai/2014)"
)

AWS_CERTS = [
    "Solutions Architect – Associate",
    "Developer – Associate",
    "Data Engineer – Associate",
    "Cloud Practitioner",
]

MS_CERTS = [
    "Azure Administrator Associate (AZ-104)",
    "Azure Database Administrator Associate (DP-300)",
    "Azure Fundamentals (AZ-900)",
    "Azure Data Fundamentals (DP-900)",
]

EDUCATION = [
    ("jun/2025 – jun/2026", "Pós-graduação em Engenharia de Dados", "PUC Minas"),
    ("jun/2023 – dez/2024", "Pós-graduação em Cloud Computing", "PUC Minas"),
    ("2015 – 2018", "Bacharelado em Sistemas de Informação", "Faculdade Pitágoras"),
    ("2012 – 2014", "Técnico em Programação", "SENAI"),
]

LANGUAGES = (
    "<b>Português</b> nativo &nbsp;•&nbsp; <b>Inglês</b> B2 (intermediário) "
    "&nbsp;•&nbsp; <b>Espanhol</b> B2 (intermediário)"
)


def build_pdf(output_path: str) -> Path:
    out_path = Path(output_path)
    styles = getSampleStyleSheet()

    base = ParagraphStyle(
        "Base",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=11.0,
        textColor=BODY,
        spaceAfter=0,
    )
    small = ParagraphStyle("Small", parent=base, fontSize=8.2, leading=10.3)
    muted = ParagraphStyle("Muted", parent=small, textColor=MUTED)
    section = ParagraphStyle(
        "Section",
        parent=base,
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=13,
        textColor=INK,
        spaceAfter=0,
    )
    company = ParagraphStyle(
        "Company",
        parent=base,
        fontName="Helvetica-Bold",
        fontSize=9.6,
        leading=12.5,
        textColor=INK,
        keepWithNext=1,
    )
    role = ParagraphStyle(
        "Role",
        parent=base,
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=12,
        textColor=ACCENT,
    )
    period = ParagraphStyle(
        "Period", parent=muted, fontSize=8.2, leading=12, alignment=TA_RIGHT
    )
    skill_label = ParagraphStyle(
        "SkillLabel",
        parent=base,
        fontName="Helvetica-Bold",
        fontSize=8.6,
        leading=11,
        textColor=INK,
    )

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=f"Currículo – {NAME.title()}",
        author=NAME.title(),
        subject="Currículo profissional",
    )

    measure_canvas = canvas.Canvas(BytesIO())

    def measure(flowables, width):
        return sum(f.wrapOn(measure_canvas, width, 10_000)[1] for f in flowables)

    def heading(text: str, first: bool = False):
        return [
            Spacer(1, 3 if first else 7),
            Paragraph(text.upper(), section),
            Spacer(1, 2),
            HRFlowable(width="100%", thickness=1.1, color=ACCENT, spaceAfter=0),
            Spacer(1, 5),
        ]

    def bullets(items, style=base, indent=9):
        return ListFlowable(
            [
                ListItem(
                    Paragraph(text, style),
                    leftIndent=indent,
                    bulletColor=ACCENT,
                    spaceAfter=1.5,
                )
                for text in items
            ],
            bulletType="bullet",
            start="•",
            leftIndent=indent + 3,
            bulletFontSize=8,
            spaceAfter=0,
        )

    def role_header(title, period_text):
        return Paragraph(
            f"<b>{title}</b>"
            f'<font color="#{MUTED.hexval()[2:]}" size="8.2">'
            f"&nbsp;&nbsp;·&nbsp;&nbsp;{period_text}</font>",
            role,
        )

    def timeline(company_line: str, roles: list[dict]):
        marker_w = 0.85 * cm
        right_w = CONTENT_W - marker_w
        blocks = [CondPageBreak(3.2 * cm), Paragraph(company_line, company)]

        rows = []
        for item in roles:
            content = [
                role_header(item["title"], item["period"]),
                bullets(item["bullets"]),
                Spacer(1, 7),
            ]
            rows.append(
                [
                    TimelineMarker(measure(content, right_w), bool(item.get("is_current"))),
                    content,
                ]
            )

        table = Table(rows, colWidths=[marker_w, right_w], splitByRow=1)
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, 0), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        blocks.append(table)
        blocks.append(Spacer(1, 4))
        return blocks

    story: list = []

    story.append(HeaderBand(CONTENT_W))
    story.append(Spacer(1, 10))

    story += heading("Resumo profissional", first=True)
    story.append(Paragraph(RESUMO, base))

    label_w = 3.5 * cm
    skill_rows = [
        [Paragraph(label, skill_label), TagCloud(tags, CONTENT_W - label_w - 6)]
        for label, tags in SKILL_GROUPS
    ]
    skills_table = Table(skill_rows, colWidths=[label_w, CONTENT_W - label_w])
    skills_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
            ]
        )
    )

    story += heading("Experiência profissional")
    story += timeline("NEXTI  ·  Florianópolis, SC  ·  Home office", NEXTI_ROLES)
    story += timeline("Moot Consulting  ·  São Paulo, SP  ·  Home office", MOOT_ROLES)
    for job in SINGLE_ROLES:
        story += timeline(job["company"], [job])
    story.append(Paragraph(EARLIER, small))

    story += heading("Certificações")
    col_w = CONTENT_W / 2
    cert_table = Table(
        [
            [
                Paragraph("AWS", skill_label),
                Paragraph("Microsoft Azure", skill_label),
            ],
            [bullets(AWS_CERTS, small), bullets(MS_CERTS, small)],
        ],
        colWidths=[col_w, col_w],
    )
    cert_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBEFORE", (1, 0), (1, 1), 0.5, RULE),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("LEFTPADDING", (1, 0), (1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(cert_table)

    story += heading("Formação acadêmica")
    edu_rows = [
        [
            Paragraph(f"<b>{course}</b><br/><font color='#5F6F82'>{school}</font>", small),
            Paragraph(years, period),
        ]
        for years, course, school in EDUCATION
    ]
    edu_table = Table(edu_rows, colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
    edu_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
            ]
        )
    )
    story.append(edu_table)

    story.append(
        KeepTogether(heading("Idiomas") + [Paragraph(LANGUAGES, base)])
    )

    story.append(KeepTogether(heading("Competências técnicas") + [skills_table]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"OK: PDF gerado em {out_path.resolve()}")
    return out_path


if __name__ == "__main__":
    build_pdf("Adam_Rodrigues_2026.pdf")
