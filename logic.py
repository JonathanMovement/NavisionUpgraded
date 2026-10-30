import sys
import os

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
