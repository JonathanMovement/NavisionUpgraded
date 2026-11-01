# NavisionUpgraded

A small Windows desktop utility tool for Business Central and Microsoft Dynamics NAV that can prepare lists of values for Navision filters. Paste or OCR a list of codes/words, join them with the filter separator you need, remove duplicates and do quick math on the side - all in one dark-themed window that ships as a single .exe

It's the modernized remake of The BETTER Navision:
(https://github.com/JonathanMovement/Navision_UtilityTool) 

> This is the **RapidOCR** version (branch `rapidocr`). The lighter version using Windows' built-in OCR
> lives on the `main` branch.

![app_animation](app_animation.gif)

## Features
```
  Button  |   Description
----------------------------------------
 |*       | Joins every value with | and puts * in front of each other
 |        | Joins every value with |
 &<>      | Joins every value with &<>
 RemDupes | Removes duplicate values, one value per line
 OCR      | Reads text from a screenshot in the clipboard
 Clear    | Empties the text area
 Expand   | Slides the window open to show the calculator
```

## Calculator
- Click the buttons or type on the keyboard (number row or numpad) while the calculator display is active.
- Enter = =, Esc = clear, Backspace = delete last character, * or x = multiply.
- The display is read-only, so results can be selected and copied (Ctrl+C) but not edited by hand.

## OCR 
OCR uses [RapidOCR](https://github.com/RapidAI/RapidOCR) with its built-in models, so it works offline
and needs no Windows language packs or admin rights.

- **Always double-check OCR results before using them in Navision.**
- `l` and `I` can still be mixed up in some fonts.
- The first OCR after starting the app takes a second longer while the models load.

## Running from source
**Required fix (PyQt5 + onnxruntime crash):** PyQt5 ships old copies of Microsoft's C++ runtime that make
onnxruntime crash with an access violation on the first OCR. Move them out of the virtual environment once
after installing:

```powershell
mkdir old_qt_runtime
Move-Item .venv-rapid\Lib\site-packages\PyQt5\Qt5\bin\msvcp140*.dll old_qt_runtime\
Move-Item .venv-rapid\Lib\site-packages\PyQt5\Qt5\bin\vcruntime140*.dll old_qt_runtime\
```
Repeat this whenever PyQt5 is reinstalled.

```powershell
python -m venv .venv-rapid
.venv-rapid\Scripts\activate
pip install -r requirements.txt
python main.py
```

The `icons` folder (button icons, logo) is not part of the repository because it contains company images. Without it the app still runs; buttons just show no icons and there is no background logo.

## Building the .exe
Build from a clean virtual environment with only `requirements.txt` installed, and after the
PyQt5 runtime fix above - otherwise the `.exe` crashes on the first OCR too.

```powershell
pyinstaller --onefile --windowed --name NavisionUpgraded-RapidOCR --icon icons/KTNlogo.ico --add-data "icons;icons" --collect-data rapidocr --hidden-import rapidocr.main main.py
```

The finished file is `dist\NavisionUpgraded-RapidOCR.exe`. It's much bigger than the Windows OCR version
because it carries the OCR engine and models, and it starts a few seconds slower.