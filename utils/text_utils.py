import re


def convert_markdown_bold_to_html(text: str) -> str:
    """Convert markdown bold (**text**) to HTML bold (<b>text</b>)."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text


def split_markdown_bold(text: str) -> list[str]:
    """Split text by markdown bold markers, preserving the markers."""
    return re.split(r'(\*\*.+?\*\*)', text)


def is_essay_assignment(text: str) -> bool:
    """Check if the exercise is an essay assignment."""
    essay_keywords = ['essay', 'composition', 'write a', 'write an', 'paragraph', 'paragraphs']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in essay_keywords)

