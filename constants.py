# Processing delays (in seconds)
DELAY_BETWEEN_IMAGES = 2
BASE_RETRY_DELAY = 15
MAX_RETRIES = 2

# Rate limiting settings
MAX_REQUESTS_PER_WINDOW = 15  # Maximum requests per time window
RATE_LIMIT_WINDOW = 60.0  # Time window in seconds
MAX_CONCURRENT_WORKERS = 5  # Maximum parallel workers

# Image preview settings
THUMBNAIL_SIZE = (100, 100)
PREVIEW_MIN_HEIGHT = 220

# document settings
DOCUMENT_FONTS = ['Helvetica']
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 14

# Gemini API prompts
BASE_PROMPT = """Look at this exercise image from an English textbook and solve it completely.

IMPORTANT FORMATTING:
- Start your answer with the exercise name/title in BOLD (e.g., **Exercise A** or **Task 1** or whatever the exercise is called in the image)
- Format the exercise name as bold text at the very beginning of your response
- If you can see a page number in the image, include it in your answer (e.g., **Page 45, Exercise A** or **Exercise A (Page 45)**)

If this is asking for an essay, composition, or to write paragraphs:
- Write a complete, well-structured essay with introduction, body paragraphs, and conclusion
- Follow any length requirements specified
- Do NOT include numbers or bullet points
- Write in continuous prose
- Start with the bold exercise name (and page number if visible) first

If this is a regular exercise with questions:
- Start with the bold exercise name (and page number if visible) first
- Provide ALL numbered answers completely
- Answer EVERY question in the exercise
- Number each answer clearly (1., 2., 3., etc.)
- Do NOT stop after a few answers
- Output ONLY the final words. No explanations, no "Answer:" labels.

Please solve the exercise and provide your answer now, starting with the bold exercise name (and page number if you can see it in the image)."""

# File filters
IMAGE_FILTER = "Image files (*.png *.jpg *.jpeg *.bmp *.tiff);;All files (*.*)"

# Config file
CONFIG_FILE = "config.json"

