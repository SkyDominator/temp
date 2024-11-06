import tkinter as tk
from tkinter import scrolledtext
import process

# 빌드 커맨드:
#& "C:\Users\raykim\Documents\workspace\personal\dev\Scripts\pyinstaller.exe" --onefile --windowed 'workspace/toolbox/html-to-md/v7/converter.py'
# pyinstaller --onefile --windowed --add-data "workspace/toolbox/html-to-md/v7/process.py;." 'workspace/toolbox/html-to-md/v7/converter.py'

def convert_html_to_markdown():
    html_input = input_text.get("1.0", tk.END).strip()
    if html_input:
        markdown_output = process.convert(html_input)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, markdown_output)

# Create the main window
root = tk.Tk()
root.title("HTML to Markdown Converter")

# Create and place the input text box
input_label = tk.Label(root, text="Input HTML:")
input_label.pack()
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
input_text.pack()

# Create and place the convert button
convert_button = tk.Button(root, text="Convert", command=convert_html_to_markdown)
convert_button.pack()

# Create and place the result text box
result_label = tk.Label(root, text="Markdown Output:")
result_label.pack()
result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
result_text.pack()

# Run the Tkinter main loop
root.mainloop()