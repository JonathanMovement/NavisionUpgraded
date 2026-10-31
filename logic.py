import sys
import os
import asyncio

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

# ----------- Screenshot -> Text (Windows OCR) ----------------
OCR_LANGUAGES = ["nl", "en"] 

def get_ocr_engine():
    # Importing here so the app starts without loading OCR
    from winrt.windows.media.ocr import OcrEngine

    installed = OcrEngine.available_recognizer_languages

    for wanted in OCR_LANGUAGES:
        for language in installed:
            if language.language_tag.lower().startswith(wanted):
                return OcrEngine.try_create_from_language(language)

    return None

def ocr_max_image_size():
    from winrt.windows.media.ocr import OcrEngine
    return OcrEngine.max_image_dimension

async def wait_for(operation):
    # Windows OCR works asynchronously - this waits until the result is ready
    return await operation

def ocr_image(rgba_bytes, width, height):
    from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat

    engine = get_ocr_engine()
    if engine is None:
        raise RuntimeError(
            "No English or Dutch OCR language is installed on this PC.\n\n"
            "Ask IT to install one, or run this in PowerShell as administrator:\n"
            'Add-WindowsCapability -Online -Name "Language.OCR~~~en-US~0.0.1.0"\n'
            'Add-WindowsCapability -Online -Name "Language.OCR~~~nl-NL~0.0.1.0"'
        )

    bitmap = SoftwareBitmap.create_copy_from_buffer(rgba_bytes, BitmapPixelFormat.RGBA8, width, height)
    result = asyncio.run(wait_for(engine.recognize_async(bitmap)))

    lines = []
    for line in result.lines:
        lines.append(line.text)

    return "\n".join(lines) # one OCR line per line