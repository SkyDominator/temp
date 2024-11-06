# 빌드: pyinstaller --onefile --windowed 'workspace/toolbox/번역 API 미번역 처리/python/v6/skipTranslationV6.py'

import tkinter as tk
from tkinter import filedialog, Label, Button, StringVar, messagebox
import os
import re

# Assuming necessary functions are defined in the provided scripts. This might need adjustment.
from createSkipListV7 import extract_english_words
from applySkipListsFromDirV7 import wrap_words_with_span

class SkipTranslationApp:    
    def __init__(self, root):
        self.root = root
        root.title('Skip Translation Tool')

        # Setting up the layout
        self.label = Label(root, text='Select a directory or a file to create skip lists.')
        self.label.pack()

        self.input_path_label = Label(root, text='Input Path:')
        self.input_path_label.pack()

        self.start_button = Button(root, text='Select Input Path', command=self.select_input_path)
        self.start_button.pack()

        self.create_button = Button(root, text='Create Skip List', command=self.create_skip_list, state='disabled')
        self.create_button.pack()

        self.open_results_button = Button(root, text='Open Results', command=self.open_results, state='disabled')
        self.open_results_button.pack()

        self.apply_button = Button(root, text='Apply Skip Lists', command=self.apply_skip_lists, state='disabled')
        self.apply_button.pack()

        self.status = StringVar()
        self.status.set('Waiting for user input...')
        self.status_label = Label(root, textvariable=self.status)
        self.status_label.pack()
        self.selected_input_path = ''

    def select_input_path(self):
        user_choice = messagebox.askyesno("Choose Input", "Would you like to select a directory? (No for file)")
        path = ''
        if user_choice:
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()

        if path:
            self.input_path_label.config(text='Selected Input Path: ' + path)
            assert path.endswith(".html") or os.path.isdir(path), "HTML 파일 또는 HTML 파일이 포함된 폴더를 선택해주세요."
            self.selected_input_path = path
            self.create_button['state'] = 'normal'

    def create_skip_list(self):
        self.status.set('Creating skip lists...')
        try:
            self.skiplist_path = extract_english_words(self.selected_input_path)
            self.status.set('Skip lists created successfully!')
            messagebox.showinfo("Success", "Skip lists created successfully!")
            self.open_results_button['state'] = 'normal'
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status.set('An error occurred.')

    def open_results(self):
        if isinstance(self.skiplist_path, list) and len(self.skiplist_path) > 0:
            for path in self.skiplist_path:
                try:
                    os.startfile(path)
                except Exception as e:
                    messagebox.showerror("Error", f"Unable to open results: {e}")
        elif isinstance(self.skiplist_path, str):
            try:
                os.startfile(self.skiplist_path)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open results: {e}")
        else:
            messagebox.showerror("Error", f"Unable to open results: Invalid skiplist path type.")
        
        # 생성한 스킵리스트 파일을 열어서 결과를 모두 확인한 후에야 스킵 적용 버튼을 활성화한다.
        self.apply_button['state'] = 'normal'
        # 스킵 적용할 영문 파일 경로를 지정한다.

    def apply_skip_lists(self):
        self.status.set('Applying skip lists to HTML files...')
        try:
            # 국문 HTML 파일 경로를 인자로 넘겨주고, wrap_words_with_span에서 당하는 영문 파일을 처리한다.
            wrap_words_with_span(self.selected_input_path)
            self.status.set('Process completed successfully!')
            messagebox.showinfo("Success", "HTML files processed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status.set('An error occurred.')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Skip Translation Tool')  # Set the window title here
    root.geometry('600x400')  # Set the window size here
    app = SkipTranslationApp(root)
    root.mainloop()
