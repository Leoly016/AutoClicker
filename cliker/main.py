# existing content

import threading
import time
import json
import os
import tkinter as tk
from tkinter import messagebox

try:
	from pynput.mouse import Controller, Button
	from pynput import keyboard
except ImportError:
	message = (
		"Требуется установка зависимостей. Запустите:\n"
		"pip install -r requirements.txt"
	)
	raise SystemExit(message)


class AutoClicker:
	def __init__(self, root):
		self.root = root
		self.root.title('Auto Clicker')
		self.mouse = Controller()

		self.button_var = tk.StringVar(value='left')
		self.interval_var = tk.StringVar(value='100')  # ms
		self.hotkey_var = tk.StringVar(value='F6')
		self.stop_hotkey_var = tk.StringVar(value='F7')
		self.running = False
		self.thread = None
		self.stop_event = threading.Event()

		self._build_ui()
		# config file path
		self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
		# load saved settings (if any) then start hotkeys
		self.load_settings()
		# center window on screen
		self.center_window()
		self._start_hotkeys()

	def _build_ui(self):
		frame = tk.Frame(self.root, padx=10, pady=10)
		frame.pack()

		tk.Label(frame, text='Кнопка:').grid(row=0, column=0, sticky='w')
		tk.Radiobutton(frame, text='Левая', variable=self.button_var, value='left').grid(row=0, column=1)
		tk.Radiobutton(frame, text='Правая', variable=self.button_var, value='right').grid(row=0, column=2)

		tk.Label(frame, text='Интервал (мс):').grid(row=1, column=0, sticky='w')
		self.interval_entry = tk.Entry(frame, textvariable=self.interval_var, width=10)
		self.interval_entry.grid(row=1, column=1, columnspan=2, sticky='w')

		self.start_btn = tk.Button(frame, text='Старт', command=self.toggle)
		self.start_btn.grid(row=2, column=0, pady=(10, 0))

		self.stop_btn = tk.Button(frame, text='Стоп', command=self.stop)
		self.stop_btn.grid(row=2, column=1, pady=(10, 0))

		tk.Button(frame, text='Выход (Esc)', command=self.on_exit).grid(row=2, column=2, pady=(10, 0))

		self.hotkey_info_label = tk.Label(frame, text='')
		self.hotkey_info_label.grid(row=3, column=0, columnspan=3, pady=(8,0))

		# Настройка горячей клавиши
		tk.Label(frame, text='Клавиша запуска:').grid(row=4, column=0, sticky='w', pady=(8,0))
		self.hotkey_entry = tk.Entry(frame, textvariable=self.hotkey_var, width=12)
		self.hotkey_entry.grid(row=4, column=1, sticky='w', pady=(8,0))
		tk.Button(frame, text='Применить', command=self.apply_hotkey).grid(row=4, column=2, pady=(8,0))

		tk.Label(frame, text='Клавиша стопа:').grid(row=5, column=0, sticky='w', pady=(6,0))
		self.stop_hotkey_entry = tk.Entry(frame, textvariable=self.stop_hotkey_var, width=12)
		self.stop_hotkey_entry.grid(row=5, column=1, sticky='w', pady=(6,0))

	def _click_loop(self, interval_s, button):
		while not self.stop_event.is_set():
			try:
				self.mouse.click(button)
			except Exception:
				pass
			# wait with early exit
			if self.stop_event.wait(interval_s):
				break

	def start(self):
		if self.running:
			return
		try:
			interval_ms = float(self.interval_var.get())
			if interval_ms <= 0:
				raise ValueError
		except Exception:
			messagebox.showerror('Ошибка', 'Интервал должен быть положительным числом (мс).')
			return

		self.stop_event.clear()
		interval_s = interval_ms / 1000.0
		button = Button.left if self.button_var.get() == 'left' else Button.right

		self.thread = threading.Thread(target=self._click_loop, args=(interval_s, button), daemon=True)
		self.thread.start()
		self.running = True
		self.start_btn.config(text='Стоп (F6)')

	def stop(self):
		if not self.running:
			return
		self.stop_event.set()
		if self.thread:
			self.thread.join(timeout=1)
		self.running = False
		self.start_btn.config(text='Старт (F6)')

	def toggle(self):
		if self.running:
			self.stop()
		else:
			self.start()

	def on_exit(self):
		self.stop()
		try:
			self.hotkey_listener.stop()
		except Exception:
			pass
		# save current settings on exit
		try:
			self.save_settings()
		except Exception:
			pass
		self.root.quit()

	def _start_hotkeys(self):
		# start hotkeys using current value
		self.restart_hotkeys()

	def center_window(self):
		# Центрирует окно приложения на экране
		try:
			self.root.update_idletasks()
			w = self.root.winfo_width()
			h = self.root.winfo_height()
			# fallback to requested size
			if w <= 1:
				w = self.root.winfo_reqwidth()
			if h <= 1:
				h = self.root.winfo_reqheight()
			sw = self.root.winfo_screenwidth()
			sh = self.root.winfo_screenheight()
			x = (sw - w) // 2
			y = (sh - h) // 2
			self.root.geometry(f"{w}x{h}+{x}+{y}")
		except Exception:
			pass

	def load_settings(self):
		try:
			if os.path.exists(self.config_path):
				with open(self.config_path, 'r', encoding='utf-8') as f:
					data = json.load(f)
				# apply settings if present
				if 'button' in data:
					self.button_var.set(data.get('button', self.button_var.get()))
				if 'interval' in data:
					self.interval_var.set(str(data.get('interval', self.interval_var.get())))
				if 'hotkey' in data:
					self.hotkey_var.set(data.get('hotkey', self.hotkey_var.get()))
				if 'stop_hotkey' in data:
					self.stop_hotkey_var.set(data.get('stop_hotkey', self.stop_hotkey_var.get()))
		except Exception:
			pass
		# update visible info label after loading
		try:
			self.update_hotkey_info()
		except Exception:
			pass

	def save_settings(self):
		try:
			data = {
				'button': self.button_var.get(),
				'interval': self.interval_var.get(),
				'hotkey': self.hotkey_var.get(),
				'stop_hotkey': self.stop_hotkey_var.get(),
			}
			with open(self.config_path, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
		except Exception:
			pass

	def normalize_hotkey(self, raw: str) -> str:
		key = raw.strip().lower()
		if not key:
			return '<f6>'
		# if user provided a combination (contains +) assume they use <..> tokens
		if key.startswith('<') and key.endswith('>'):
			return key
		if '+' in key:
			parts = [p.strip() for p in key.split('+')]
			norm_parts = []
			for p in parts:
				if p.startswith('<') and p.endswith('>'):
					norm_parts.append(p)
				else:
					norm_parts.append(f'<{p}>')
			return '+'.join(norm_parts)
		# single token
		return f'<{key}>'

	def restart_hotkeys(self):
		# stop existing listener if present
		try:
			if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
				self.hotkey_listener.stop()
		except Exception:
			pass

		def on_toggle():
			self.root.after(0, self.toggle)

		def on_stop():
			self.root.after(0, self.stop)

		def on_exit():
			self.root.after(0, self.on_exit)

		hotkey_token = self.normalize_hotkey(self.hotkey_var.get())
		stop_token = self.normalize_hotkey(self.stop_hotkey_var.get())
		hotkeys = {hotkey_token: on_toggle, stop_token: on_stop, '<esc>': on_exit}

		self.hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
		t = threading.Thread(target=self.hotkey_listener.start, daemon=True)
		t.start()

	def update_hotkey_info(self):
		# Обновляет текст метки, показывающей текущие назначенные клавиши
		try:
			start = self.hotkey_var.get() or 'F6'
			stop = self.stop_hotkey_var.get() or 'F7'
			text = f'Горячие клавиши: {start} — старт/стоп, {stop} — стоп, Esc — выход'
			self.hotkey_info_label.config(text=text)
		except Exception:
			pass

	def apply_hotkey(self):
		# user clicked Apply — restart listener with new hotkey
		try:
			self.restart_hotkeys()
			# save new values
			self.save_settings()
			# update info label
			try:
				self.update_hotkey_info()
			except Exception:
				pass
			messagebox.showinfo('Горячие клавиши', f'Установлены: запуск={self.hotkey_var.get()}, стоп={self.stop_hotkey_var.get()}')
		except Exception as e:
			messagebox.showerror('Ошибка', f'Не удалось применить горячие клавиши:\n{e}')


def main():
	root = tk.Tk()
	app = AutoClicker(root)
	root.protocol('WM_DELETE_WINDOW', app.on_exit)
	root.mainloop()


if __name__ == '__main__':
	main()
