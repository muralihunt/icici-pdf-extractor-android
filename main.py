import os
import re
import pandas as pd
import fitz  # PyMuPDF
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from plyer import filechooser

# ICICI Specific Patterns
# Date: DD-MM-YYYY or DD/MM/YYYY
date_pattern = r'\d{2}[-/]\d{2}[-/]\d{4}'
# Amount: Matches numbers like 1,234.00 or 500.00
amount_pattern = r'[\d,]+\.\d{2}'

class UI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)
        self.label = Label(text="ICICI PDF Extractor", font_size='20sp')
        self.add_widget(self.label)

        self.btn = Button(text="Select ICICI Statement", size_hint_y=None, height=120)
        self.btn.bind(on_press=self.pick_file)
        self.add_widget(self.btn)

        self.run_btn = Button(text="Extract to CSV", size_hint_y=None, height=120, background_color=(0, 0.7, 0, 1))
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
        if not self.file_path:
            self.label.text = "Please select a file first!"
            return

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        try:
            doc = fitz.open(self.file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text("text") + "\n"

            # ICICI Regex: Date -> Description -> Amount
            # We look for a date, then any text (non-greedy), then an amount.
            matches = re.findall(f'({date_pattern})\s+(.*?)\s+({amount_pattern})', full_text, re.DOTALL)

            if not matches:
                self.label.text = "No transactions found.\nCheck if PDF is password protected."
                return

            df = pd.DataFrame(matches, columns=["Date", "Description", "Amount"])
            
            # Clean up descriptions (remove newlines inside descriptions)
            df['Description'] = df['Description'].str.replace('\n', ' ').str.strip()

            if platform == 'android':
                from android.storage import primary_external_storage_path
                path = os.path.join(primary_external_storage_path(), "Download", "ICICI_Extracted.csv")
            else:
                path = "ICICI_Extracted.csv"

            df.to_csv(path, index=False)
            self.label.text = f"✅ Success! {len(df)} rows\nSaved to Downloads folder"

        except Exception as e:
            self.label.text = f"Error: {str(e)}"

class ICICIApp(App):
    def build(self):
        return UI()

if __name__ == "__main__":
    ICICIApp().run()
