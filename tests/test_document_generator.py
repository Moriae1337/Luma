import os
import pytest
from core.document_generator import DocumentGenerator


class TestGenerateOutputFilename:
    """Test cases for generate_output_filename."""
    
    def test_with_custom_filename(self):
        """Test with custom filename provided."""
        result = DocumentGenerator.generate_output_filename(
            "John Doe", "Group A", "custom_output"
        )
        assert result == "custom_output"
    
    def test_without_custom_filename(self):
        """Test generating filename from student name and group."""
        result = DocumentGenerator.generate_output_filename(
            "John Doe", "Group A", ""
        )
        assert result == "John_Doe_Group_A"
    
    def test_spaces_replaced(self):
        """Test that spaces are replaced with underscores."""
        result = DocumentGenerator.generate_output_filename(
            "Mary Jane", "Class 1", ""
        )
        assert result == "Mary_Jane_Class_1"
    
    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        result = DocumentGenerator.generate_output_filename(
            "John  Doe", "Group  A", ""
        )
        assert result == "John__Doe_Group__A"
    
    def test_empty_student_name(self):
        """Test with empty student name."""
        result = DocumentGenerator.generate_output_filename(
            "", "Group A", ""
        )
        assert result == "_Group_A"
    
    def test_empty_group(self):
        """Test with empty group."""
        result = DocumentGenerator.generate_output_filename(
            "John Doe", "", ""
        )
        assert result == "John_Doe_"
    
    def test_both_empty(self):
        """Test with both empty."""
        result = DocumentGenerator.generate_output_filename("", "", "")
        assert result == "_"


class TestGeneratePDF:
    """Test cases for generate_pdf."""
    
    @pytest.fixture
    def sample_exercises(self):
        """Sample exercises for testing."""
        return [
            ("Exercise A", "**Exercise A**\n1. Answer one\n2. Answer two"),
            ("Exercise B", "**Exercise B**\n1. Answer three")
        ]
    
    def test_generate_pdf_empty_exercises(self, tmp_path):
        """Test PDF generation with empty exercises list."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            output_path = DocumentGenerator.generate_pdf(
                [],
                "Test Student",
                "Test Group",
                "empty_test"
            )
            
            assert os.path.exists(output_path)
        finally:
            os.chdir(original_cwd)


class TestGenerateWord:
    """Test cases for generate_word."""
    
    @pytest.fixture
    def sample_exercises(self):
        """Sample exercises for testing."""
        return [
            ("Exercise A", "**Exercise A**\n1. Answer one\n2. Answer two"),
            ("Exercise B", "**Exercise B**\n1. Answer three")
        ]
    
    def test_generate_word_basic(self, sample_exercises, tmp_path):
        """Test basic Word document generation."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            output_path = DocumentGenerator.generate_word(
                sample_exercises,
                "Test Student",
                "Test Group",
                "test_output"
            )
            
            assert os.path.exists(output_path)
            assert output_path.endswith(".docx")
            assert "test_output.docx" in output_path
        finally:
            os.chdir(original_cwd)
    
    def test_generate_word_with_extension(self, sample_exercises, tmp_path):
        """Test Word generation when filename already has .docx extension."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            output_path = DocumentGenerator.generate_word(
                sample_exercises,
                "Test Student",
                "Test Group",
                "test_output.docx"
            )
            
            assert os.path.exists(output_path)
            assert output_path.endswith(".docx")
            assert output_path.count(".docx") == 1
        finally:
            os.chdir(original_cwd)
    
    def test_generate_word_empty_exercises(self, tmp_path):
        """Test Word generation with empty exercises list."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            output_path = DocumentGenerator.generate_word(
                [],
                "Test Student",
                "Test Group",
                "empty_test"
            )
            
            assert os.path.exists(output_path)
        finally:
            os.chdir(original_cwd)
    
    def test_generate_word_student_info(self, sample_exercises, tmp_path):
        """Test that Word document contains student information."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            output_path = DocumentGenerator.generate_word(
                sample_exercises,
                "Jane Smith",
                "Class 3B",
                "info_test"
            )
            
            assert os.path.exists(output_path)
        finally:
            os.chdir(original_cwd)

