import os
import tkinter as tk
from tkinter import filedialog, messagebox
from translate import Model, translate_file

def open_path():
    if path_type_var.get() == "directory":
        path = filedialog.askdirectory()
    else:
        path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
    
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def update_model_options(*args):
    platform = platform_var.get()
    model_menu['menu'].delete(0, 'end')
    
    if platform == "google":
        models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    elif platform == "groq":
        models = ["llama-3.1-70b-versatile"]
    else:
        models = []
    
    for model in models:
        model_menu['menu'].add_command(label=model, command=tk._setit(model_name_var, model))
    model_name_var.set(models[0] if models else "")

def translate():
    path = path_entry.get()
    if not path:
        messagebox.showerror("Error", "Please select a file or directory.")
        return
    
    model_platform = platform_var.get()
    model_name = model_name_var.get()
    if not model_platform or not model_name:
        messagebox.showerror("Error", "Please select a model platform and name.")
        return
    
    try:
        model = Model(model_platform, model_name)
        if path_type_var.get() == "directory":
            for filename in os.listdir(path):
                if filename.endswith(".md"):
                    file_path = os.path.join(path, filename)
                    translate_file(file_path, model, en=en_var.get(), ja=ja_var.get(), zh=zh_var.get(), zh_Hant=zh_Hant_var.get(), th=th_var.get())
        else:
            translate_file(path, model, en=en_var.get(), ja=ja_var.get(), zh=zh_var.get(), zh_Hant=zh_Hant_var.get(), th=th_var.get())
        messagebox.showinfo("Success", "Translation completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Markdown Translator")

path_type_var = tk.StringVar(value="directory")
tk.Radiobutton(root, text="Directory", variable=path_type_var, value="directory").grid(row=0, column=0, padx=10, pady=10)
tk.Radiobutton(root, text="File", variable=path_type_var, value="file").grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Select Path:").grid(row=1, column=0, padx=10, pady=10)
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=open_path).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Model Platform:").grid(row=2, column=0, padx=10, pady=10)
platform_var = tk.StringVar(value="google")
platform_var.trace("w", update_model_options)
platform_menu = tk.OptionMenu(root, platform_var, "google", "groq")
platform_menu.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Model Name:").grid(row=3, column=0, padx=10, pady=10)
model_name_var = tk.StringVar()
model_menu = tk.OptionMenu(root, model_name_var, "")
model_menu.grid(row=3, column=1, padx=10, pady=10)
update_model_options()

en_var = tk.BooleanVar()
ja_var = tk.BooleanVar()
zh_var = tk.BooleanVar()
zh_Hant_var = tk.BooleanVar()
th_var = tk.BooleanVar()

tk.Checkbutton(root, text="Translate to English", variable=en_var).grid(row=4, column=0, padx=10, pady=10)
tk.Checkbutton(root, text="Translate to Japanese", variable=ja_var).grid(row=4, column=1, padx=10, pady=10)
tk.Checkbutton(root, text="Translate to Simplified Chinese", variable=zh_var).grid(row=5, column=0, padx=10, pady=10)
tk.Checkbutton(root, text="Translate to Traditional Chinese", variable=zh_Hant_var).grid(row=5, column=1, padx=10, pady=10)
tk.Checkbutton(root, text="Translate to Thai", variable=th_var).grid(row=6, column=0, padx=10, pady=10)

tk.Button(root, text="Translate", command=translate).grid(row=7, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()