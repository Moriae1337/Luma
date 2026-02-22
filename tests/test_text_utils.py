import pytest
from utils.text_utils import (
    convert_markdown_bold_to_html,
    split_markdown_bold,
    is_essay_assignment
)


class TestConvertMarkdownBoldToHTML:
    """Test cases for convert_markdown_bold_to_html."""
    
    def test_single_bold(self):
        """Test converting single bold markdown."""
        text = "This is **bold** text"
        result = convert_markdown_bold_to_html(text)
        assert result == "This is <b>bold</b> text"
    
    def test_multiple_bold(self):
        """Test converting multiple bold markdown."""
        text = "**First** and **second** bold"
        result = convert_markdown_bold_to_html(text)
        assert result == "<b>First</b> and <b>second</b> bold"
    
    def test_no_bold(self):
        """Test text with no bold markers."""
        text = "This is plain text"
        result = convert_markdown_bold_to_html(text)
        assert result == "This is plain text"
    
    def test_only_bold(self):
        """Test text that is only bold."""
        text = "**Bold only**"
        result = convert_markdown_bold_to_html(text)
        assert result == "<b>Bold only</b>"
    
    def test_nested_asterisks(self):
        """Test text with asterisks that aren't bold markers."""
        text = "Price: $**50**"
        result = convert_markdown_bold_to_html(text)
        assert result == "Price: $<b>50</b>"
    
    def test_bold_at_start(self):
        """Test bold at the start of text."""
        text = "**Start** of text"
        result = convert_markdown_bold_to_html(text)
        assert result == "<b>Start</b> of text"
    
    def test_bold_at_end(self):
        """Test bold at the end of text."""
        text = "End of **text**"
        result = convert_markdown_bold_to_html(text)
        assert result == "End of <b>text</b>"
    
    def test_empty_string(self):
        """Test empty string."""
        result = convert_markdown_bold_to_html("")
        assert result == ""


class TestSplitMarkdownBold:
    """Test cases for split_markdown_bold."""
    
    def test_single_bold(self):
        """Test splitting text with single bold."""
        text = "This is **bold** text"
        result = split_markdown_bold(text)
        assert result == ["This is ", "**bold**", " text"]
    
    def test_multiple_bold(self):
        """Test splitting text with multiple bold."""
        text = "**First** and **second**"
        result = split_markdown_bold(text)
        assert len(result) == 5
        assert result[0] == ""
        assert result[1] == "**First**"
        assert result[2] == " and "
        assert result[3] == "**second**"
        assert result[4] == ""
    
    def test_no_bold(self):
        """Test splitting text with no bold."""
        text = "This is plain text"
        result = split_markdown_bold(text)
        assert result == ["This is plain text"]
    
    def test_only_bold(self):
        """Test splitting text that is only bold."""
        text = "**Bold only**"
        result = split_markdown_bold(text)
        assert result == ["", "**Bold only**", ""]
    
    def test_empty_string(self):
        """Test empty string."""
        result = split_markdown_bold("")
        assert result == [""]


class TestIsEssayAssignment:
    """Test cases for is_essay_assignment."""
    
    def test_essay_keyword(self):
        """Test detection of essay keyword."""
        assert is_essay_assignment("Write an essay about...") is True
        assert is_essay_assignment("This is an essay assignment") is True
    
    def test_composition_keyword(self):
        """Test detection of composition keyword."""
        assert is_essay_assignment("Write a composition") is True
        assert is_essay_assignment("This composition should...") is True
    
    def test_write_a_keyword(self):
        """Test detection of 'write a' keyword."""
        assert is_essay_assignment("Write a paragraph about...") is True
        assert is_essay_assignment("Please write a story") is True
    
    def test_write_an_keyword(self):
        """Test detection of 'write an' keyword."""
        assert is_essay_assignment("Write an article") is True
    
    def test_paragraph_keyword(self):
        """Test detection of paragraph keyword."""
        assert is_essay_assignment("Write a paragraph") is True
        assert is_essay_assignment("Write paragraphs about...") is True
    
    def test_case_insensitive(self):
        """Test that detection is case insensitive."""
        assert is_essay_assignment("ESSAY about...") is True
        assert is_essay_assignment("Write An Essay") is True
        assert is_essay_assignment("COMPOSITION") is True
    
    def test_not_essay(self):
        """Test that regular exercises are not detected as essays."""
        assert is_essay_assignment("Answer the following questions") is False
        assert is_essay_assignment("Fill in the blanks") is False
        assert is_essay_assignment("Choose the correct answer") is False
        assert is_essay_assignment("Match the words") is False
    
    def test_empty_string(self):
        """Test empty string."""
        assert is_essay_assignment("") is False
    
    def test_keyword_in_middle(self):
        """Test keyword appearing in the middle of text."""
        assert is_essay_assignment("The task is to write an essay") is True
        assert is_essay_assignment("Please complete this essay assignment") is True

