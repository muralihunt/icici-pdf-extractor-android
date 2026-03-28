import os
import pandas as pd
import fitz
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
        super().__init__(orientation="vertical", padding=40, spacing=20, **kwargs)
        
        self.add_widget(Label(text="PDF Searcher Pro", font_size='24sp', size_hint_y=None, height=100))

        self.password_input = TextInput(hint_text="PDF Password (optional)", multiline=False, password=True, size_hint_y=None, height=100)
        self.add_widget(self.password_input)

        self.search_input = TextInput(hint_text="Search keyword (e.g. Amazon)", multiline=False, size_hint_y=None, height=100)
        self.add_widget(self.search_input)

        self.status = Label(text="Step 1: Select a PDF file", color=(0.7, 0.7, 0.7, 1))
        self.add_widget(self.status)

        self.btn_select = Button(text="📂 SELECT PDF", size_hint_y=None, height=120, background_color=(0.2, 0.5, 0.9, 1))
        self.btn_select.bind(on_press=self.open_file_picker)
        self.add_widget(self.btn_select)

        self.btn_run = Button(text="📊 GENERATE EXCEL", size_hint_y=None, height=120, background_color=(0.1, 0.7, 0.3, 1))
        self.btn_run.bind(on_press=self.process_pdf)
        self.add_widget(self.btn_run)
        
        self.selected_path = None

    def open_file_picker(self, instance):
        filechooser.open_file(on_selection=self.on_file_selected)

    def on_file_selected(self, selection):
        if selection:
            self.selected_path = selection[0]
            self.status.text = f"Selected: {os.path.basename(self.selected_path)}"

    def process_pdf(self, instance):
        keyword = self.search_input.text.strip().lower()
        if not self.selected_path or not keyword:
            self.status.text = "Error: File and Keyword required!"
            return

        # Request Android Permissions at runtime
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        try:
            doc = fitz.open(self.selected_path)
            if doc.is_encrypted:
                if not doc.authenticate(self.password_input.text):
                    self.status.text = "Error: Wrong Password"
                    return

            extracted_data = []
            for page in doc:
                blocks = page.get_text("blocks")
                for b in blocks:
                    line_text = b[4].strip()
                    if keyword in line_text.lower():
                        clean_text = " ".join(line_text.split())
                        extracted_data.append({"Page": page.number + 1, "Data": clean_text})

            if not extracted_data:
                self.status.text = f"No matches found for '{keyword}'"
                return

            # File naming logic
            timestamp = datetime.now().strftime("%H%M%S")
            fname = f"Search_{keyword}_{timestamp}.xlsx"

            if platform == 'android':
                from android.storage import primary_external_storage_path
                # Save to /sdcard/Download/ for easy access
                download_path = os.path.join(primary_external_storage_path(), 'Download')
                if not os.path.exists(download_path):
                    os.makedirs(download_path)
                final_path = os.path.join(download_path, fname)
            else:
                final_path = fname

            pd.DataFrame(extracted_data).to_excel(final_path, index=False)
            self.status.text = f"✅ SUCCESS!\nSaved to Downloads/{fname}"

        except Exception as e:
            self.status.text = f"Error: {str(e)}"

class MainApp(App):
    def build(self): return UI()

if __name__ == "__main__":
    MainApp().run()
