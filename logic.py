import sys
import os
import numpy as np

def resource_path(relative_path): # Files are unpacked into sys._MEIPASS when running PyInstaller .exe
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def filter_1(text):
    words = text.split()
    return "|".join(f"*{w}" for w in words)

def filter_2(text):
    words = text.split()
    return "|".join(words)

def filter_3(text):
    words = text.split()

    result = ""

    for w in range(len(words)):
        result += words[w]

        if w != len(words) - 1:
            result += "&<>"

    return result

def remove_duplicates(text):
    words = text.split()

    seen = set() # fast check "have I already seen this?"
    result = []

    for word in words:
        if word not in seen:
            seen.add(word)
            result.append(word)

    return "\n".join(result) # one value per line

# ----------- Screenshot -> Text (RapidOCR) ----------------
ocr_engine = None # created on the first OCR click, then reused

def get_ocr_engine():
    global ocr_engine
    if ocr_engine is None:
        # Importing here so the app starts without loading the OCR models
        from rapidocr import RapidOCR
        ocr_engine = RapidOCR(params={"Global.log_level": "error"})
    return ocr_engine

def ocr_max_image_size():
    return 2000 # RapidOCR shrinks anything bigger than 2000px on its long side

def box_left(item):
    return item["left"]

def box_center_y(item):
    return item["center_y"]

def ocr_image(rgba_bytes, width, height):
    # Raw R, G, B, A bytes -> a height x width x 4 grid of numbers
    pixels = np.frombuffer(rgba_bytes, dtype=np.uint8).reshape(height, width, 4)
    # RapidOCR (OpenCV) wants B, G, R order and no alpha
    bgr = np.ascontiguousarray(pixels[:, :, [2, 1, 0]])

    result = get_ocr_engine()(bgr)
    if result.txts is None:
        return "" # nothing found

    pieces = []
    for box, text in zip(result.boxes, result.txts):
        top = min(box[0][1], box[1][1], box[2][1], box[3][1])
        bottom = max(box[0][1], box[1][1], box[2][1], box[3][1])
        left = min(box[0][0], box[1][0], box[2][0], box[3][0])
        pieces.append({"text": text, "top": top, "bottom": bottom,
                       "left": left, "center_y": (top + bottom) / 2})

    # Group pieces into lines
    pieces.sort(key=box_center_y)
    lines = []
    for piece in pieces:
        if len(lines) > 0:
            current = lines[-1]
            if current["top"] <= piece["center_y"] <= current["bottom"]:
                current["pieces"].append(piece)
                continue
        lines.append({"top": piece["top"], "bottom": piece["bottom"], "pieces": [piece]})

    # Inside each line: left to right, joined with spaces
    output = []
    for line in lines:
        line["pieces"].sort(key=box_left)
        words = []
        for piece in line["pieces"]:
            words.append(piece["text"])
        output.append(" ".join(words))

    return "\n".join(output)