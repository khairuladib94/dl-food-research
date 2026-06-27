#!/usr/bin/env python3
"""Build the participant quick-start PDF and stable landing-page QR code."""

from __future__ import annotations

from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LANDING_URL = "https://khairuladib94.github.io/dl-food-research/"
GUIDE_PATH = ASSETS / "participant-guide.pdf"
QR_PATH = ASSETS / "workshop-qr.png"

INK = HexColor("#13251D")
FOREST = HexColor("#173C2A")
LEAF = HexColor("#347C4D")
LIME = HexColor("#C7EF6B")
CITRUS = HexColor("#FFB229")
CREAM = HexColor("#F2EFE3")
PAPER = HexColor("#FBF9F2")
MUTED = HexColor("#647067")

GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Georgia", GEORGIA))
    pdfmetrics.registerFont(TTFont("Georgia-Bold", GEORGIA_BOLD))


def build_qr() -> None:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=12, border=3)
    qr.add_data(LANDING_URL)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#13251D", back_color="#F2EFE3")
    image.save(QR_PATH)


def text(c: canvas.Canvas, value: str, x: float, y: float, font: str, size: float, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, value)


def wrapped(c: canvas.Canvas, value: str, x: float, y: float, width: float, font: str, size: float,
            leading: float, color=INK) -> float:
    words = value.split()
    line = ""
    lines: list[str] = []
    for word in words:
        candidate = f"{line} {word}".strip()
        if c.stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    c.setFillColor(color)
    c.setFont(font, size)
    for item in lines:
        c.drawString(x, y, item)
        y -= leading
    return y


def header(c: canvas.Canvas, page_no: int) -> None:
    width, height = A4
    c.setFillColor(FOREST)
    c.rect(0, height - 52, width, 52, fill=1, stroke=0)
    text(c, "FOOD / AI LAB", 36, height - 33, "Helvetica-Bold", 9, LIME)
    text(c, "PARTICIPANT QUICK-START", width - 190, height - 33, "Helvetica", 8, CREAM)
    c.setStrokeColor(INK)
    c.setLineWidth(.5)
    c.line(36, 31, width - 36, 31)
    text(c, f"ML & DL for Food Research  |  2026  |  {page_no}/2", 36, 18, "Helvetica", 7, MUTED)


def step(c: canvas.Canvas, number: str, title: str, body: str, y: float) -> float:
    c.setFillColor(LIME)
    c.circle(53, y + 4, 16, fill=1, stroke=0)
    text(c, number, 45.5, y, "Helvetica-Bold", 9, INK)
    text(c, title, 82, y + 8, "Georgia-Bold", 15, INK)
    next_y = wrapped(c, body, 82, y - 10, 440, "Helvetica", 9.5, 13, MUTED)
    c.setStrokeColor(HexColor("#D6D9CD"))
    c.line(82, next_y - 4, 540, next_y - 4)
    return next_y - 30


def pill(c: canvas.Canvas, value: str, x: float, y: float, width: float) -> None:
    c.setFillColor(HexColor("#E6EDD5"))
    c.roundRect(x, y, width, 22, 11, fill=1, stroke=0)
    text(c, value, x + 10, y + 7, "Helvetica-Bold", 7.5, LEAF)


def build_pdf() -> None:
    width, height = A4
    c = canvas.Canvas(str(GUIDE_PATH), pagesize=A4, pageCompression=1)
    c.setTitle("Participant Quick-start - ML & DL for Food Research")
    c.setAuthor("Adib Yusof")
    c.setSubject("Google Colab workshop instructions")

    # Page 1
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    header(c, 1)
    text(c, "No installation.", 36, 733, "Georgia-Bold", 30, INK)
    text(c, "Just open, copy and run.", 36, 697, "Georgia-Bold", 30, LEAF)
    wrapped(
        c,
        "You need a modern web browser, a reliable internet connection and a Google account. "
        "The exercises run in Google Colab using compact TensorFlow/Keras models.",
        36, 666, 485, "Helvetica", 10, 15, MUTED,
    )
    pill(c, "BROWSER", 36, 605, 78)
    pill(c, "GOOGLE ACCOUNT", 122, 605, 118)
    pill(c, "NO LOCAL PYTHON", 248, 605, 120)

    y = 560
    y = step(c, "01", "Open the workshop page", "Scan the QR code or visit the address below. Choose your session and notebook.", y)
    y = step(c, "02", "Open in Google Colab", "Select Open in Colab. When the notebook appears, wait for Colab to connect to a runtime.", y)
    y = step(c, "03", "Save your own copy", "Before editing, choose File > Save a copy in Drive. Continue working in the new browser tab.", y)
    y = step(c, "04", "Run from top to bottom", "Choose Runtime > Run all. Allow the first setup cell to download the matching teaching dataset.", y)

    c.setFillColor(CREAM)
    c.roundRect(36, 67, 503, 88, 5, fill=1, stroke=0)
    c.drawImage(str(QR_PATH), 49, 78, 64, 64, mask="auto")
    text(c, "WORKSHOP HOME", 129, 127, "Helvetica-Bold", 8, LEAF)
    text(c, LANDING_URL, 129, 105, "Helvetica", 9, INK)
    wrapped(c, "This is the stable link for notebooks, slide decks, the guide and updates.", 129, 86, 380, "Helvetica", 8.5, 12, MUTED)
    c.linkURL(LANDING_URL, (129, 96, 510, 118), relative=0)
    c.showPage()

    # Page 2
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    header(c, 2)
    text(c, "Working safely in Colab", 36, 730, "Georgia-Bold", 28, INK)
    wrapped(c, "Your notebook copy is stored in Google Drive. The temporary runtime and downloaded dataset are not.", 36, 700, 500, "Helvetica", 10, 14, MUTED)

    cards = [
        ("SAVE", "Use File > Save a copy in Drive before making changes."),
        ("RUN", "Use Runtime > Run all. A CPU runtime is sufficient."),
        ("EXPORT", "Use File > Download to keep an .ipynb or .py copy."),
        ("PRIVACY", "The workshop does not mount or inspect your Google Drive."),
    ]
    card_width = 242
    for index, (label, body) in enumerate(cards):
        col, row = index % 2, index // 2
        x = 36 + col * 261
        y_card = 617 - row * 93
        c.setFillColor(CREAM if index != 3 else HexColor("#E6EDD5"))
        c.roundRect(x, y_card, card_width, 76, 4, fill=1, stroke=0)
        text(c, label, x + 13, y_card + 53, "Helvetica-Bold", 8, LEAF)
        wrapped(c, body, x + 13, y_card + 33, 214, "Helvetica", 8.5, 12, INK)

    text(c, "Fast recovery", 36, 474, "Georgia-Bold", 20, INK)
    problems = [
        ("File not found", "Run the first setup cell again. It downloads only this notebook's dataset."),
        ("Runtime disconnected", "Reconnect and run all cells again. Your Drive copy remains saved."),
        ("Old or confusing output", "Use Runtime > Disconnect and delete runtime, reconnect, then Run all."),
        ("No GPU available", "Continue with CPU. The teaching models are designed for it."),
    ]
    y_problem = 442
    for title, body in problems:
        text(c, title, 36, y_problem, "Helvetica-Bold", 9, INK)
        wrapped(c, body, 168, y_problem, 360, "Helvetica", 8.5, 11, MUTED)
        c.setStrokeColor(HexColor("#D6D9CD"))
        c.line(36, y_problem - 15, 539, y_problem - 15)
        y_problem -= 48

    text(c, "Choose your route", 36, 238, "Georgia-Bold", 20, INK)
    c.setFillColor(FOREST)
    c.roundRect(36, 102, 503, 116, 5, fill=1, stroke=0)
    text(c, "SESSION 6", 53, 190, "Helvetica-Bold", 8, LIME)
    text(c, "Five guided case studies", 53, 168, "Georgia-Bold", 14, CREAM)
    wrapped(c, "Shelf life, fruit defects, NIR adulteration, fermentation risk and anomaly screening.", 53, 148, 205, "Helvetica", 8.5, 12, HexColor("#C6CEC8"))
    c.setStrokeColor(HexColor("#4D6859"))
    c.line(286, 118, 286, 201)
    text(c, "SESSION 9", 309, 190, "Helvetica-Bold", 8, CITRUS)
    text(c, "Five group challenges", 309, 168, "Georgia-Bold", 14, CREAM)
    wrapped(c, "Run a baseline, make two controlled changes, and present evidence in five slides.", 309, 148, 205, "Helvetica", 8.5, 12, HexColor("#C6CEC8"))
    c.linkURL(LANDING_URL + "#session-6", (36, 102, 286, 218), relative=0)
    c.linkURL(LANDING_URL + "#session-9", (286, 102, 539, 218), relative=0)

    text(c, "Need the slide decks or backup ZIP?", 36, 70, "Helvetica-Bold", 9, INK)
    text(c, "Return to the workshop home:", 36, 53, "Helvetica", 8.5, MUTED)
    text(c, LANDING_URL, 176, 53, "Helvetica", 8.5, LEAF)
    c.linkURL(LANDING_URL, (176, 45, 500, 65), relative=0)

    c.save()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    register_fonts()
    build_qr()
    build_pdf()
    print(f"Built {QR_PATH}")
    print(f"Built {GUIDE_PATH}")


if __name__ == "__main__":
    main()
