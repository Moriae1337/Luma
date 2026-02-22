import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton, QButtonGroup,
    QScrollArea, QFileDialog, QMessageBox, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt
from PIL import Image as PILImage

from core.config_manager import ConfigManager
from core.processing_thread import ProcessingThread
from ui.image_preview import ImagePreviewWidget
from constants import IMAGE_FILTER


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luma")
        self.setGeometry(100, 100, 750, 900)
        
        # Initialize variables
        self.image_paths = []
        self.image_custom_prompts = {}
        self.processing_thread = None
        
        # Initialize managers
        self.config_manager = ConfigManager()
        
        # Initialize image preview widget
        self.image_preview = None
        
        # Create UI
        self.create_ui()
        
        # Load configuration
        self.load_config()
    
    def create_ui(self):
        """Create the user interface."""
        # Central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content_widget = QWidget()
        self.content_layout = QGridLayout(content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setColumnStretch(1, 1)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        self.content_widget = content_widget
        row = 0
        
        # Student Name
        self.content_layout.addWidget(QLabel("Student:"), row, 0)
        self.student_name_edit = QLineEdit()
        self.content_layout.addWidget(self.student_name_edit, row, 1)
        row += 1
        
        # Group
        self.content_layout.addWidget(QLabel("Group:"), row, 0)
        self.group_edit = QLineEdit()
        self.content_layout.addWidget(self.group_edit, row, 1)
        row += 1
        
        # Output filename
        self.content_layout.addWidget(QLabel("Output Filename:"), row, 0)
        filename_layout = QVBoxLayout()
        self.output_filename_edit = QLineEdit()
        filename_layout.addWidget(self.output_filename_edit)
        hint_label = QLabel("(leave empty for Name_Group)")
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        filename_layout.addWidget(hint_label)
        filename_widget = QWidget()
        filename_widget.setLayout(filename_layout)
        self.content_layout.addWidget(filename_widget, row, 1)
        row += 1
        
        # API Key
        self.content_layout.addWidget(QLabel("Gemini API Key:"), row, 0)
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(self.api_key_edit)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        api_key_layout.addWidget(save_btn)
        api_key_widget = QWidget()
        api_key_widget.setLayout(api_key_layout)
        self.content_layout.addWidget(api_key_widget, row, 1)
        row += 1
        
        # Image selection
        self.content_layout.addWidget(QLabel("Exercise Images:"), row, 0)
        image_layout = QHBoxLayout()
        self.select_images_btn = QPushButton("Select Images")
        self.select_images_btn.clicked.connect(self.select_images)
        image_layout.addWidget(self.select_images_btn)
        self.image_label = QLabel("No images selected")
        image_layout.addWidget(self.image_label)
        image_widget = QWidget()
        image_widget.setLayout(image_layout)
        self.content_layout.addWidget(image_widget, row, 1)
        row += 1
        
        # Initialize image preview widget
        self.image_preview = ImagePreviewWidget(
            self, self.content_layout, self.show_full_image, self.remove_image
        )
        
        # Image prompts (will be added dynamically)
        self.image_prompts_group = None
        self.image_prompt_widgets = {}
        
        # Store row positions
        self.format_row = row
        self.custom_prompt_row = row + 1
        
        # Output format
        self.format_label = QLabel("Output Format:")
        self.content_layout.addWidget(self.format_label, self.format_row, 0)
        format_layout = QHBoxLayout()
        self.output_format_group = QButtonGroup()
        pdf_radio = QRadioButton("PDF")
        pdf_radio.setChecked(True)
        word_radio = QRadioButton("Word")
        self.output_format_group.addButton(pdf_radio, 0)
        self.output_format_group.addButton(word_radio, 1)
        format_layout.addWidget(pdf_radio)
        format_layout.addWidget(word_radio)
        self.format_widget = QWidget()
        self.format_widget.setLayout(format_layout)
        self.content_layout.addWidget(self.format_widget, self.format_row, 1)
        
        # Custom prompt
        self.custom_prompt_label = QLabel("Custom Prompt (All):")
        self.content_layout.addWidget(self.custom_prompt_label, self.custom_prompt_row, 0, Qt.AlignmentFlag.AlignTop)
        prompt_layout = QVBoxLayout()
        self.custom_prompt_text = QTextEdit()
        self.custom_prompt_text.setMaximumHeight(60)
        prompt_layout.addWidget(self.custom_prompt_text)
        hint_label2 = QLabel("(Optional: Applies to all images if no per-image prompt)")
        hint_label2.setStyleSheet("color: gray; font-size: 9pt;")
        prompt_layout.addWidget(hint_label2)
        self.prompt_widget = QWidget()
        self.prompt_widget.setLayout(prompt_layout)
        self.content_layout.addWidget(self.prompt_widget, self.custom_prompt_row, 1)
        
        row = self.custom_prompt_row + 1
        
        # Process button
        self.process_btn = QPushButton("Process and Generate Document")
        self.process_btn.clicked.connect(self.process_exercises)
        self.process_btn_row = row
        self.content_layout.addWidget(self.process_btn, self.process_btn_row, 0, 1, 2)
        row += 1
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress_row = row
        self.content_layout.addWidget(self.progress, self.progress_row, 0, 1, 2)
        row += 1
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_row = row
        self.content_layout.addWidget(self.status_label, self.status_row, 0, 1, 2)
    
    def select_images(self):
        """Open file dialog to select exercise images."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Exercise Images", "", IMAGE_FILTER
        )
        if files:
            new_files = [f for f in files if f not in self.image_paths]
            self.image_paths.extend(new_files)
            self._update_image_ui(len(self.image_paths))
            self.image_preview.create_preview(self.image_paths)
            self.create_image_prompt_fields()
    
    def _update_image_ui(self, count: int):
        """Update UI elements based on image count."""
        self.image_label.setText(f"{count} image(s) selected")
        self.select_images_btn.setText("Add More Images" if count > 0 else "Select Images")
    
    def remove_image(self, image_path: str):
        """Remove an image from the selection."""
        if image_path in self.image_paths:
            self.image_paths.remove(image_path)
            if image_path in self.image_custom_prompts:
                del self.image_custom_prompts[image_path]
            
            self._update_image_ui(len(self.image_paths))
            self.image_preview.create_preview(self.image_paths)
            self.create_image_prompt_fields()
            
            # Reset widget positions if no images
            if not self.image_paths:
                self._reset_widget_positions()
    
    def _reset_widget_positions(self):
        """Reset widget positions when no images are present."""
        widgets_to_move = [
            (self.format_label, self.format_widget),
            (self.custom_prompt_label, self.prompt_widget),
            (self.process_btn,),
            (self.progress,),
            (self.status_label,)
        ]
        
        for widget_group in widgets_to_move:
            for widget in widget_group:
                self.content_layout.removeWidget(widget)
        
        self.format_row = 5
        self.custom_prompt_row = 6
        self.process_btn_row = 7
        self.progress_row = 8
        self.status_row = 9
        
        self.content_layout.addWidget(self.format_label, self.format_row, 0)
        self.content_layout.addWidget(self.format_widget, self.format_row, 1)
        self.content_layout.addWidget(self.custom_prompt_label, self.custom_prompt_row, 0, Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(self.prompt_widget, self.custom_prompt_row, 1)
        self.content_layout.addWidget(self.process_btn, self.process_btn_row, 0, 1, 2)
        self.content_layout.addWidget(self.progress, self.progress_row, 0, 1, 2)
        self.content_layout.addWidget(self.status_label, self.status_row, 0, 1, 2)
    
    def create_image_prompt_fields(self):
        """Create custom prompt fields for each selected image."""
        # Remove old group if it exists
        if self.image_prompts_group is not None:
            self.content_layout.removeWidget(self.image_prompts_group)
            self.image_prompts_group.deleteLater()
            self.image_prompts_group = None
        
        if not self.image_paths:
            return
        
        # Create new group box
        self.image_prompts_group = QGroupBox("Custom Prompts per Image (Optional)")
        prompts_layout = QGridLayout()
        prompts_layout.setColumnStretch(1, 1)
        
        self.image_prompt_widgets = {}
        
        for idx, image_path in enumerate(self.image_paths):
            filename = os.path.basename(image_path)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            
            label = QLabel(f"Image {idx+1} ({filename}):")
            label.setStyleSheet("font-size: 9pt;")
            prompts_layout.addWidget(label, idx, 0)
            
            text_edit = QTextEdit()
            text_edit.setMaximumHeight(50)
            
            saved_prompt = self.image_custom_prompts.get(image_path, "")
            if saved_prompt:
                text_edit.setPlainText(saved_prompt)
            
            prompts_layout.addWidget(text_edit, idx, 1)
            self.image_prompt_widgets[image_path] = (label, text_edit)
        
        self.image_prompts_group.setLayout(prompts_layout)
        
        # Calculate row positions
        prompts_row = 6 if self.image_preview.image_preview_group else 5
        new_format_row = prompts_row + 1
        new_prompt_row = new_format_row + 1
        new_process_row = new_prompt_row + 1
        new_progress_row = new_process_row + 1
        new_status_row = new_progress_row + 1
        
        # Remove widgets temporarily
        widgets_to_remove = [
            self.format_label, self.format_widget,
            self.custom_prompt_label, self.prompt_widget,
            self.process_btn, self.progress, self.status_label
        ]
        for widget in widgets_to_remove:
            self.content_layout.removeWidget(widget)
        
        # Re-add preview if it exists
        if self.image_preview.image_preview_group is not None:
            self.content_layout.removeWidget(self.image_preview.image_preview_group)
            self.content_layout.addWidget(self.image_preview.image_preview_group, 5, 0, 1, 2)
        
        # Add prompts group
        self.content_layout.addWidget(self.image_prompts_group, prompts_row, 0, 1, 2)
        
        # Re-add widgets at new positions
        self.content_layout.addWidget(self.format_label, new_format_row, 0)
        self.content_layout.addWidget(self.format_widget, new_format_row, 1)
        self.content_layout.addWidget(self.custom_prompt_label, new_prompt_row, 0, Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(self.prompt_widget, new_prompt_row, 1)
        self.content_layout.addWidget(self.process_btn, new_process_row, 0, 1, 2)
        self.content_layout.addWidget(self.progress, new_progress_row, 0, 1, 2)
        self.content_layout.addWidget(self.status_label, new_status_row, 0, 1, 2)
        
        # Update stored row numbers
        self.format_row = new_format_row
        self.custom_prompt_row = new_prompt_row
        self.process_btn_row = new_process_row
        self.progress_row = new_progress_row
        self.status_row = new_status_row
    
    def show_full_image(self, image_path: str):
        """Show full-size image in a new window."""
        try:
            from PyQt6.QtWidgets import QMainWindow as QImgWindow
            from PyQt6.QtGui import QPixmap, QImage
            
            img = PILImage.open(image_path)
            
            # Create new window
            img_window = QImgWindow(self)
            img_window.setWindowTitle(f"Preview: {os.path.basename(image_path)}")
            
            # Resize if needed
            screen = self.screen().geometry()
            max_width = screen.width() - 100
            max_height = screen.height() - 100
            
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
            
            # Convert to QPixmap
            img_rgb = img.convert('RGB')
            width, height = img_rgb.size
            img_bytes = img_rgb.tobytes("raw", "RGB")
            q_image = QImage(img_bytes, width, height, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Create label with image
            from PyQt6.QtWidgets import QLabel as QImgLabel
            label = QImgLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Create layout
            layout = QVBoxLayout()
            layout.addWidget(label)
            
            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(img_window.close)
            layout.addWidget(close_btn)
            
            central = QWidget()
            central.setLayout(layout)
            img_window.setCentralWidget(central)
            
            img_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not display image: {str(e)}")
    
    def save_config(self):
        """Save settings to config file."""
        # Collect custom prompts from UI
        for image_path in self.image_paths:
            if image_path in self.image_prompt_widgets:
                _, text_edit = self.image_prompt_widgets[image_path]
                custom_prompt = text_edit.toPlainText().strip()
                if custom_prompt:
                    self.image_custom_prompts[image_path] = custom_prompt
        
        config = {
            "api_key": self.api_key_edit.text(),
            "output_format": self.output_format_group.checkedButton().text().lower(),
            "student_name": self.student_name_edit.text(),
            "group": self.group_edit.text(),
            "output_filename": self.output_filename_edit.text(),
            "custom_prompt": self.custom_prompt_text.toPlainText().strip(),
            "image_custom_prompts": self.image_custom_prompts
        }
        
        if self.config_manager.save(config):
            QMessageBox.information(self, "Success", "Settings saved!")
        else:
            QMessageBox.critical(self, "Error", "Failed to save config")
    
    def load_config(self):
        """Load settings from config file."""
        config = self.config_manager.load()
        
        self.api_key_edit.setText(config.get("api_key", ""))
        output_format = config.get("output_format", "pdf")
        if output_format == "word":
            self.output_format_group.button(1).setChecked(True)
        else:
            self.output_format_group.button(0).setChecked(True)
        
        self.student_name_edit.setText(config.get("student_name", ""))
        self.group_edit.setText(config.get("group", ""))
        self.output_filename_edit.setText(config.get("output_filename", ""))
        
        custom_prompt = config.get("custom_prompt", "")
        if custom_prompt:
            self.custom_prompt_text.setPlainText(custom_prompt)
        
        self.image_custom_prompts = config.get("image_custom_prompts", {})
    
    def process_exercises(self):
        """Process exercises in a separate thread."""
        # Validate inputs
        if not self.student_name_edit.text().strip():
            QMessageBox.critical(self, "Error", "Please enter student name")
            return
        if not self.group_edit.text().strip():
            QMessageBox.critical(self, "Error", "Please enter group")
            return
        if not self.api_key_edit.text().strip():
            QMessageBox.critical(self, "Error", "Please enter API key")
            return
        if not self.image_paths:
            QMessageBox.critical(self, "Error", "Please select at least one image")
            return
        
        # Auto-save config
        self.save_config()
        
        # Disable button and start progress
        self.process_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("Processing...")
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(self)
        self.processing_thread.status_update.connect(self.status_label.setText)
        self.processing_thread.finished.connect(self.processing_complete)
        self.processing_thread.error.connect(self.processing_error)
        
        print(f"Starting processing thread with {len(self.image_paths)} images")
        self.processing_thread.start()
        
        # Verify thread started
        if not self.processing_thread.isRunning():
            self.status_label.setText("Failed to start processing thread")
            self.process_btn.setEnabled(True)
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", "Failed to start processing thread")
    
    def processing_complete(self, output_path: str):
        """Called when processing is complete."""
        self.progress.setVisible(False)
        self.process_btn.setEnabled(True)
        self.status_label.setText("Complete!")
        format_name = "Word document" if self.output_format_group.checkedButton().text().lower() == "word" else "PDF"
        QMessageBox.information(
            self,
            "Success",
            f"{format_name} generated successfully!\n\nSaved to:\n{output_path}"
        )
    
    def processing_error(self, error_message: str):
        """Called when processing encounters an error."""
        self.progress.setVisible(False)
        self.process_btn.setEnabled(True)
        self.status_label.setText("Error occurred")
        QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_message}")

