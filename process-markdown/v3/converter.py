import tkinter as tk
from tkinter import scrolledtext
import process

# 빌드 커맨드:
# pyinstaller --onefile --windowed --name=md_modifier 'workspace/toolbox/process-markdown/gui/converter.py'

def modify_markdown():
    md_input = input_text.get("1.0", tk.END).strip()
    if md_input:
        markdown_output = process.convert(md_input)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, markdown_output)

# Create the main window
root = tk.Tk()
root.title("Markdown Modifier")

# Create and place the input text box
input_label = tk.Label(root, text="Original Markdown:")
input_label.pack()
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
input_text.pack()

# Create and place the convert button
convert_button = tk.Button(root, text="Convert", command=modify_markdown)
convert_button.pack()

# Create and place the result text box
result_label = tk.Label(root, text="Output:")
result_label.pack()
result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
result_text.pack()

# Run the Tkinter main loop
root.mainloop()