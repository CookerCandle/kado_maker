import json
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import red, black

def load_font(font_path):
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Файл шрифта {font_path} не найден! Укажи правильный путь.")
    pdfmetrics.registerFont(TTFont("JapaneseFont", font_path))

def load_words(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    name = str(data[0]['dars'])
    words = []
    for lesson in data:
        for word in lesson["so'zlar"]:
            words.append({
                "word": word["kana"],
                "reading": word["jp"],
                "translation": word["uzb"]
            })
    return words, name

def wrap_text(text, max_width, font_name, font_size, canvas):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if canvas.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def create_flashcards_pdf(words, name, pdf_filename, font_path):
    c = canvas.Canvas(pdf_filename, pagesize=landscape(A4))
    load_font(font_path)
    width, height = landscape(A4)
    margin = 40
    cards_per_row, cards_per_col = 4, 4
    card_width = (width - 2 * margin) / cards_per_row
    card_height = (height - 2 * margin) / cards_per_col
    x_start, y_start = margin, height - margin
    kanji_positions_per_page = []
    current_page_positions = []
    row, col = 0, 0
    
    # Первый лист: Кандзи
    for i, word in enumerate(words):
        x_pos = x_start + col * card_width
        y_pos = y_start - (row + 1) * card_height
        current_page_positions.append((x_pos, y_pos, word))
        c.setFillColor(black) # устанавливает цвет
        c.rect(x_pos, y_pos, card_width, card_height) # рисует линии для карточек
        c.setFont("JapaneseFont", 10)
        c.drawCentredString(x_pos + card_width / 2, y_pos + card_height / 1.15, f"{name}-kanji") # пишет буквы в центре
        c.setFillColor(red) # устанавливает цвет
        c.setFont("JapaneseFont", 35)
        c.drawCentredString(x_pos + card_width / 2, y_pos + card_height / 2.5, word["word"]) # пишет буквы в центре
        col += 1
        if col >= cards_per_row:
            col = 0
            row += 1
        if row >= cards_per_col:
            kanji_positions_per_page.append(current_page_positions)
            current_page_positions = []
            c.showPage()
            row, col = 0, 0
    if current_page_positions:
        kanji_positions_per_page.append(current_page_positions)
    c.showPage()
    
    # Второй лист: Чтение и перевод (отзеркалено только по оси X)
    for page_positions in kanji_positions_per_page:
        for (x_pos, y_pos, word) in page_positions:
            mirrored_x_pos = width - x_pos - card_width
            # c.rect(mirrored_x_pos, y_pos, card_width, card_height)
            c.setFillColor(red)
            c.setFont("JapaneseFont", 20)
            c.drawCentredString(mirrored_x_pos + card_width / 2, y_pos + card_height / 1.8, word["reading"])
            c.setFillColor(black)
            c.setFont("JapaneseFont", 12)
            translation_lines = wrap_text(word["translation"], card_width - 10, "JapaneseFont", 12, c)
            line_y = y_pos + card_height - 85
            for line in translation_lines:
                c.drawCentredString(mirrored_x_pos + card_width / 2, line_y, line)
                line_y -= 15
        c.showPage()
    
    c.save()
    print(f"Файл {pdf_filename} создан!")

if __name__ == "__main__":
    font_path = "files/NotoSans.ttf"
    json_path = "files/words.json"
    words = load_words(json_path)
    pdf_filename = f"output/{words[1]}-dars.pdf"
    create_flashcards_pdf(words[0],words[1], pdf_filename, font_path)
