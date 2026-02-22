import re
import time
from PIL import Image as PILImage
from constants import BASE_PROMPT, BASE_RETRY_DELAY, MAX_RETRIES


class GeminiClient:
    """Client for interacting with Google Gemini Vision API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._configured = False
    
    def _configure(self):
        """Configure the Gemini API."""
        if self._configured:
            return
        
        try:
            import google.generativeai as genai
            import warnings
            warnings.filterwarnings('ignore', category=FutureWarning)
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self._configured = True
        except ImportError:
            raise Exception("Google Generative AI library not installed. Install with: pip install google-generativeai")
    
    def generate_answer_from_image(
        self, 
        image_path: str, 
        custom_prompt: str = ""
    ) -> str:
        """
        Generate answer from an image using Gemini Vision API.
        
        Args:
            image_path: Path to the image file
            custom_prompt: Optional custom prompt to append
            
        Returns:
            Generated answer text
        """
        self._configure()
        
        # Read image file
        img = PILImage.open(image_path)
        
        # Build prompt
        prompt = BASE_PROMPT
        if custom_prompt:
            prompt += f"\n\nAdditional instructions:\n{custom_prompt}"
        
        # Get available models
        available_models = self._get_available_vision_models()
        
        if not available_models:
            raise Exception("No Gemini vision models found. Please check your API key and ensure you have access to Gemini models.")
        
        # Try each available model
        last_error = None
        
        for model_name in available_models:
            for attempt in range(MAX_RETRIES):
                try:
                    model = self.genai.GenerativeModel(model_name)
                    response = model.generate_content([prompt, img])
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    last_error = error_str
                    
                    # rate limit errors
                    is_rate_limit = (
                        '429' in error_str or 
                        'quota' in error_str.lower() or 
                        'rate limit' in error_str.lower() or
                        'exceeded' in error_str.lower()
                    )
                    
                    if is_rate_limit:
                        if attempt < MAX_RETRIES - 1:
                            delay = BASE_RETRY_DELAY
                            delay_match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                            if delay_match:
                                delay = float(delay_match.group(1)) + 2  # Add 2 second buffer
                            
                            time.sleep(delay)
                            continue  # same model
                        else:
                            # Max retries reached, try next model
                            break
                    
                    # Skip 404/not found errors and continue to next model
                    if '404' in error_str or 'not found' in error_str.lower() or 'not supported' in error_str.lower():
                        break  # Try next model
                    
                    # next model
                    break
        
        error_msg = f"All Gemini vision models failed. Last error: {last_error}"
        if available_models:
            error_msg += f"\n\nTried models: {', '.join(available_models)}"
        raise Exception(error_msg)
    
    def _get_available_vision_models(self) -> list:
        """Get list of available Gemini vision models."""
        available_models = []
        try:
            for model in self.genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name
                    # Filter for Gemini models that support vision (1.5+, 2.0+, or flash models)
                    model_name_lower = model_name.lower()
                    if 'gemini' in model_name_lower:
                        # Check if it's a vision-capable model
                        if any(x in model_name_lower for x in ['1.5', '2.0', 'flash', 'pro']):
                            available_models.append(model_name)
        except Exception as e:
            error_str = str(e)
            # Check for API key errors
            if 'api key' in error_str.lower() or 'api_key' in error_str.lower() or 'API_KEY_INVALID' in error_str:
                raise Exception(
                    f"API Key Error: Your API key is invalid or expired. "
                    f"Please check your API key in the settings.\n\nDetails: {error_str}"
                )
            raise Exception(f"Failed to list available models: {error_str}")
        
        return available_models

