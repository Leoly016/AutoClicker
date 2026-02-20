# Auto Clicker

Простой автокликер на Python (Windows).

Функции:
- Клик левой или правой кнопкой мыши
- Интервал в миллисекундах
- Старт/стоп через кнопку или горячую клавишу F6
- Выход через Esc

Установка:

```powershell
python -m pip install -r requirements.txt
```

Запуск:

```powershell
python main.py
```

Примечание: если используете виртуальное окружение, активируйте его перед установкой.

Сборка в .exe (Windows)

1) Установите зависимости (включая PyInstaller):

```powershell
python -m pip install -r requirements.txt
```

2) Запустите скрипт сборки:

```powershell
.\build_exe.bat
```

По умолчанию скрипт использует `pyinstaller --onefile --noconsole --name AutoClicker main.py` и создаст исполняемый файл в папке `dist`.

Если хотите следить за процессом или добавить иконку, откройте `build_exe.bat` и измените параметры PyInstaller.
