@echo off
REM Скрипт упрощённой сборки .exe через PyInstaller
REM Рекомендуется запускать из корня проекта

python -m pip install -r requirements.txt

REM onefile — собрать в один файл, noconsole — скрыть консоль
pyinstaller --onefile --noconsole --name AutoClicker main.py

echo Сборка завершена. Исполняемый файл находится в папке dist\AutoClicker.exe
pause
