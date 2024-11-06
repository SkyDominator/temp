import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QShortcut
from PyQt5.QtGui import QKeySequence, QTextCursor, QTextDocument, QFont, QKeyEvent
from PyQt5.QtCore import Qt
from collections import Counter
from datetime import datetime


# 빌드 커맨드:
# pyinstaller --onefile --add-data "C:/Users/khy/Documents/workspace/concordance_search/data/full_parsed_records.json;." --add-data "C:/Users/khy/Documents/workspace/concordance_search/data/korean_inverted_index.json;." --add-data "C:/Users/khy/Documents/workspace/concordance_search/data/english_inverted_index.json;." .\py\concordance.py

# .py version
# json_tu_file_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/full_parsed_records.json'
# korean_index_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/korean_inverted_index.json'
# english_index_path = 'C:/Users/khy/Documents/workspace/concordance_search/data/english_inverted_index.json'

# executable version
# Define a function to get the correct path
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Use the function to get the paths of your data files
json_tu_file_path = resource_path('full_parsed_records.json')
korean_index_path = resource_path('korean_inverted_index.json')
english_index_path = resource_path('english_inverted_index.json')


# Load the JSON files
with open(json_tu_file_path, 'r', encoding='utf-8') as file:
    translations = json.load(file)

with open(korean_index_path, 'r', encoding='utf-8') as file:
    korean_index = json.load(file)

with open(english_index_path, 'r', encoding='utf-8') as file:
    english_index = json.load(file)


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Return and e.modifiers() & Qt.ShiftModifier:
            self.parent().findPrevious()
        else:
            super().keyPressEvent(e)
            
def human_readable_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")

def search_translations(input_text, language_index):
    tokens = input_text.split()
    token_count = len(tokens)
    matching_keys = Counter()
    for token in tokens:
        if token in language_index:
            matching_keys.update(language_index[token])
    match_rates = {key: count / token_count for key, count in matching_keys.items() if count >= token_count / 2}
    return match_rates

def format_results(results, match_rates):
    formatted_text = ""
    for key in results:
        creation_date = human_readable_date(translations[key]["CreationDate"])
        change_date = human_readable_date(translations[key]["ChangeDate"])
        korean = translations[key]["Korean"]
        english = translations[key]["English"]
        match_rate = f"{match_rates[key]*100:.2f}%"
        
        formatted_text += f"Creation Date: {creation_date} | Change Date: {change_date} | Match Rate: {match_rate}\n\n"
        formatted_text += f"Korean Text:\n{korean}\n\n"
        formatted_text += f"English Text:\n{english}\n"
        formatted_text += "=" * 100 + "\n\n\n"  # Increased spacing between entries
    return formatted_text.strip()

class TranslationSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.layout = QVBoxLayout()
        self.setupInputArea()
        self.setupResultsArea()
        self.setupSearchPanel()
        self.setLayout(self.layout)
        self.setWindowTitle("Translation Search")

    def setupInputArea(self):
        input_layout = QHBoxLayout()
        label = QLabel("Enter terms or sentence to search:")
        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self.on_search)
        input_layout.addWidget(label)
        input_layout.addWidget(self.entry)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)

        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.search_button)

    def setupResultsArea(self):
            self.results_box = CustomTextEdit(self)
            self.results_box.setReadOnly(False)
            self.results_box.setStyleSheet("""
                QTextEdit {
                    selection-background-color: #007bff;  /* Deeper blue for highlighted text */
                    selection-color: white;
                    font-family: Arial;
                    font-size: 12pt;
                    color: #333333;
                }
            """)
            self.results_box.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            self.layout.addWidget(self.results_box)

    def setupSearchPanel(self):
        self.search_panel_widget = QWidget()
        self.search_panel = QHBoxLayout(self.search_panel_widget)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search term...")
        self.search_field.returnPressed.connect(self.findNext)  # Enter triggers findNext
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.findNext)
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.findPrevious)

        self.search_panel.addWidget(self.search_field)
        self.search_panel.addWidget(self.next_button)
        self.search_panel.addWidget(self.prev_button)
        self.layout.addWidget(self.search_panel_widget)
        self.search_panel_widget.hide()

        # Shortcut for Ctrl+F to focus on the search field
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focusOnSearchField)

        # Shortcut for Shift+Enter to find the previous occurrence
        self.previous_shortcut = QShortcut(QKeySequence("Shift+Enter"), self)
        self.previous_shortcut.activated.connect(self.findPrevious)

    def on_search(self):
        user_input = self.entry.text()
        language_index = korean_index if any(char > '\u1100' and char < '\uffff' for char in user_input) else english_index
        match_rates = search_translations(user_input, language_index)
        if match_rates:
            sorted_keys = sorted(match_rates, key=match_rates.get, reverse=True)
            results_text = format_results(sorted_keys, match_rates)
        else:
            results_text = "No result found."
        self.results_box.setText(results_text)

    def focusOnSearchField(self):
        self.search_panel_widget.show()
        self.search_field.setFocus()

    def findNext(self):
        if not self.results_box.find(self.search_field.text()):
            self.results_box.moveCursor(QTextCursor.Start)

    def findPrevious(self):
        if not self.results_box.find(self.search_field.text(), QTextDocument.FindBackward):
            self.results_box.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranslationSearchApp()
    ex.show()
    sys.exit(app.exec_())