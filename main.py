import os
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from plyer import filechooser

class UI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=30, spacing=15, **kwargs)
        
        self.add_widget(Label(text="Advanced PDF Extractor", font_size='22sp', size_hint_y=None, height=100))

        # Inputs
        self.add_widget(Label(text="PDF Password (leave blank if none):", size_hint_y=None, height=40))
        self.password_input = TextInput(multiline=False, password=True, size_hint_y=None, height=80)
        self.add_widget(self.password_input)

        self.add_widget(Label(text="Text to Search:", size_hint_y=None, height=40))
        self.search_input = TextInput(multiline=False, hint_text="e.g. Amazon, Salary, Rent", size_hint_y=None, height=80)
        self.add_widget(self.search_input)

        self.label = Label(text="Select a PDF to begin", halign="center")
        self.add_widget(self.label)

        # Action Buttons
        self.btn = Button(text="📂 SELECT PDF", size_hint_y=None, height=120, background_color=(0.1, 0.5, 0.8, 1))
        self.btn.bind(on_press=self.pick_file)
        self.add_widget(self.btn)

        self.run_btn = Button(text="📊 SEARCH & EXPORT", size_hint_y=None, height=120, background_color=(0.1, 0.7, 0.3, 1))
        self.run_btn.bind(on_press=self.extract)
        self.add_widget(self.run_btn)
        
        self.file_path = None

    def pick_file(self, instance):
        filechooser.open_file(on_selection=self.set_file)

    def set_file(self, selection):
        if selection:
            self.file_path = selection[0]
            self.label.text = f"Selected: {os.path.basename(self.file_path)}"

    def extract(self, instance):
        query = self.search_input.text.strip().lower()
        if not self.file_path or not query:
            self.label.text = "Error: Select file and enter search text"
            return

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        try:
            doc = fitz.open(self.file_path)
            if doc.is_encrypted:
                if not doc.authenticate(self.password_input.text):
                    self.label.text = "Error: Invalid PDF Password"
                    return

            results = []
            for page in doc:
                # blocks capture full lines or paragraphs containing the text
                blocks = page.get_text("blocks")
                for b in blocks:
                    content = b[4].strip()
                    if query in content.lower():
                        # Standardize line format
                        clean_line = " ".join(content.split())
                        results.append({"Page": page.number + 1, "Extracted Line": clean_line})

            if not results:
                self.label.text = f"No matches found for '{query}'"
                return

            # Generate Unique Excel Name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PDF_Search_{query}_{timestamp}.xlsx"

            if platform == 'android':
                from android.storage import primary_external_storage_path
                save_path = os.path.join(primary_external_storage_path(), "Download", filename)
            else:
                save_path = filename

            pd.DataFrame(results).to_excel(save_path, index=False, engine='openpyxl')
            self.label.text = f"✅ Extracted {len(results)} lines!\nFile: {filename}"

        except Exception as e:
            self.label.text = f"Error: {str(e)}"

class PDFSearchApp(App):
    def build(self): return UI()

if __name__ == "__main__":
    PDFSearchApp().run()
