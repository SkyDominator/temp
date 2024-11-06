#pyinstaller --onefile --windowed --distpath 'C:\Users\raykim\Documents\dist' 'workspace/toolbox/llm/unified/v1_GUI_realtime/ui.py'

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from translate import Model, translate_text, MODEL_OPTIONS
import threading

def update_model_options(*args):
    platform = platform_var.get()
    model_menu['menu'].delete(0, 'end')
    for model in MODEL_OPTIONS[platform]:
        model_menu['menu'].add_command(label=model, command=tk._setit(model_name_var, model))
    model_name_var.set(MODEL_OPTIONS[platform][0])

def translate():
    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter some text.")
        return
    
    model_platform = platform_var.get()
    model_name = model_name_var.get()
    if not model_platform or not model_name:
        messagebox.showerror("Error", "Please select a model platform and name.")
        return
    
    progress_bar['value'] = 0
    translate_button.config(state=tk.DISABLED)
    
    def run_translation():
        try:
            model = Model(model_platform, model_name)
            translated_text = translate_text(text, model, to_lang_var.get())
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, translated_text)
            messagebox.showinfo("Success", "Translation completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            translate_button.config(state=tk.NORMAL)
            progress_bar['value'] = 100
    
    threading.Thread(target=run_translation).start()

root = tk.Tk()
root.title("Text Translator")

tk.Label(root, text="Enter Text:").grid(row=0, column=0, padx=10, pady=10)
text_entry = tk.Text(root, height=10, width=50)
text_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Model Platform:").grid(row=1, column=0, padx=10, pady=10)
platform_var = tk.StringVar(value="google")
platform_menu = tk.OptionMenu(root, platform_var, *MODEL_OPTIONS.keys())
platform_menu.grid(row=1, column=1, padx=10, pady=10)
platform_var.trace('w', update_model_options)

tk.Label(root, text="Model Name:").grid(row=2, column=0, padx=10, pady=10)
model_name_var = tk.StringVar()
model_menu = tk.OptionMenu(root, model_name_var, "")
model_menu.grid(row=2, column=1, padx=10, pady=10)
update_model_options()

tk.Label(root, text="Translate to:").grid(row=3, column=0, padx=10, pady=10)
to_lang_var = tk.StringVar(value="en")
tk.OptionMenu(root, to_lang_var, "en", "ko", "ja", "zh", "zh-Hant", "th").grid(row=3, column=1, padx=10, pady=10)

translate_button = tk.Button(root, text="Translate", command=translate)
translate_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

tk.Label(root, text="Translated Text:").grid(row=5, column=0, padx=10, pady=10)
result_text = tk.Text(root, height=10, width=50)
result_text.grid(row=5, column=1, padx=10, pady=10)

tk.Label(root, text="Progress:").grid(row=6, column=0, padx=10, pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=6, column=1, padx=10, pady=10)

root.mainloop()