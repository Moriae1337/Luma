import os
from functools import partial
from PyQt6.QtWidgets import (
    QGroupBox, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from utils.image_utils import load_image_as_pixmap, get_image_filename
from constants import PREVIEW_MIN_HEIGHT


class ImagePreviewWidget:
    """Manages image preview display."""
    
    def __init__(self, parent_widget, content_layout, on_image_click, on_remove_image):
        self.parent = parent_widget
        self.content_layout = content_layout
        self.on_image_click = on_image_click
        self.on_remove_image = on_remove_image
        self.image_preview_group = None
        self.image_preview_widgets = {}
        self._pixmap_cache = []
    
    def create_preview(self, image_paths: list):
        """Create preview thumbnails for selected images."""
        if self.image_preview_group is not None:
            try:
                self.content_layout.removeWidget(self.image_preview_group)
                self.image_preview_widgets.clear()
                self._pixmap_cache.clear()
                QApplication.processEvents()
                self.image_preview_group.deleteLater()
                self.image_preview_group = None
                QApplication.processEvents()
            except Exception as e:
                print(f"Error cleaning up preview: {e}")
                self.image_preview_group = None
        
        if not image_paths:
            return
        
        self.image_preview_group = QGroupBox("Image Preview")
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(5)
        
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setMinimumHeight(PREVIEW_MIN_HEIGHT)
        preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        preview_content = QWidget()
        preview_content_layout = QHBoxLayout(preview_content)
        preview_content_layout.setSpacing(5)
        
        self.image_preview_widgets = {}
        self._pixmap_cache.clear()
        
        for idx, image_path in enumerate(image_paths):
            try:
                pixmap = load_image_as_pixmap(image_path)
                self._pixmap_cache.append(pixmap)
                
                preview_frame = QFrame()
                preview_frame.setFrameStyle(QFrame.Shape.Box)
                preview_frame.setLineWidth(1)
                frame_layout = QVBoxLayout(preview_frame)
                frame_layout.setSpacing(2)
                frame_layout.setContentsMargins(5, 5, 5, 5)
                
                label_img = QLabel()
                label_img.setPixmap(pixmap)
                label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_img.setScaledContents(False)
                frame_layout.addWidget(label_img)
                
                filename = get_image_filename(image_path)
                label_text = QLabel(f"{idx+1}. {filename}")
                label_text.setStyleSheet("font-size: 9pt;")
                label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
                frame_layout.addWidget(label_text)
                
                remove_btn = QPushButton("Remove")
                remove_btn.setStyleSheet(
                    "QPushButton { background-color: #ff4444; color: white; font-weight: bold; "
                    "padding: 3px 8px; border: none; border-radius: 3px; }"
                    "QPushButton:hover { background-color: #cc0000; }"
                    "QPushButton:pressed { background-color: #990000; }"
                )
                remove_btn.clicked.connect(partial(self.on_remove_image, image_path))
                frame_layout.addWidget(remove_btn)
                
                label_img.mousePressEvent = partial(self._on_image_click, image_path)
                label_text.mousePressEvent = partial(self._on_image_click, image_path)
                
                self.image_preview_widgets[image_path] = (
                    preview_frame, pixmap, label_img, label_text, remove_btn
                )
                preview_content_layout.addWidget(preview_frame)
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                preview_frame = QFrame()
                preview_frame.setFrameStyle(QFrame.Shape.Box)
                preview_frame.setLineWidth(1)
                frame_layout = QVBoxLayout(preview_frame)
                frame_layout.setSpacing(2)
                frame_layout.setContentsMargins(5, 5, 5, 5)
                
                error_label = QLabel(f"Error loading\n{os.path.basename(image_path)}")
                error_label.setStyleSheet("color: red; font-size: 9pt;")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                frame_layout.addWidget(error_label)
                
                remove_btn = QPushButton("Remove")
                remove_btn.setStyleSheet(
                    "QPushButton { background-color: #ff4444; color: white; font-weight: bold; "
                    "padding: 3px 8px; border: none; border-radius: 3px; }"
                    "QPushButton:hover { background-color: #cc0000; }"
                )
                remove_btn.clicked.connect(partial(self.on_remove_image, image_path))
                frame_layout.addWidget(remove_btn)
                
                self.image_preview_widgets[image_path] = (
                    preview_frame, None, None, error_label, remove_btn
                )
                preview_content_layout.addWidget(preview_frame)
        
        preview_scroll.setWidget(preview_content)
        preview_layout.addWidget(preview_scroll)
        self.image_preview_group.setLayout(preview_layout)
        
        self.content_layout.addWidget(self.image_preview_group, 5, 0, 1, 2)
    
    def _on_image_click(self, image_path, event):
        """Handle image click event safely."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_image_click(image_path)
    
    def clear(self):
        """Clear the preview."""
        if self.image_preview_group is not None:
            try:
                self.content_layout.removeWidget(self.image_preview_group)
                self.image_preview_group.deleteLater()
                self.image_preview_group = None
                self.image_preview_widgets.clear()
                self._pixmap_cache.clear()
            except Exception:
                pass

