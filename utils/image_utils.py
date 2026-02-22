import os
from PIL import Image as PILImage
from PyQt6.QtGui import QPixmap, QImage
from constants import THUMBNAIL_SIZE


def load_image_as_pixmap(image_path: str, thumbnail_size: tuple = None) -> QPixmap:
    """
    Load an image file and convert it to QPixmap.
    
    Args:
        image_path: Path to the image file
        thumbnail_size: Optional tuple (width, height) to resize image
        
    Returns:
        QPixmap object
    """
    if thumbnail_size is None:
        thumbnail_size = THUMBNAIL_SIZE
    
    # Open and resize image to thumbnail
    img = PILImage.open(image_path)
    img.thumbnail(thumbnail_size, PILImage.Resampling.LANCZOS)
    
    # Convert PIL Image to QPixmap
    img_rgb = img.convert('RGB')
    width, height = img_rgb.size
    img_bytes = img_rgb.tobytes("raw", "RGB")
    q_image = QImage(img_bytes, width, height, QImage.Format.Format_RGB888)
    pixmap = QPixmap.fromImage(q_image)
    
    return pixmap


def get_image_filename(image_path: str, max_length: int = 20) -> str:
    """Get formatted filename for display."""
    filename = os.path.basename(image_path)
    if len(filename) > max_length:
        filename = filename[:max_length - 3] + "..."
    return filename

