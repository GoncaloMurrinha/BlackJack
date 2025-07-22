@echo off
echo Gerando EXE...
C:\Users\gonca\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe --noconfirm --windowed --onefile --add-data "cartas;cartas" --add-data "sons;sons" blackjack_mesa.py
pause
