import traceback
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QThread, pyqtSignal

from core.gemini_client import GeminiClient
from core.rate_limiter import RateLimiter
from constants import MAX_REQUESTS_PER_WINDOW, RATE_LIMIT_WINDOW, MAX_CONCURRENT_WORKERS


class ProcessingThread(QThread):
    """Thread for processing exercises in the background."""
    
    status_update = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
    
    def run(self):
        """Run the processing in background thread."""
        try:
            self.status_update.emit("Starting processing...")
            
            if not self.app.image_paths:
                self.error.emit("No images selected")
                return
            
            self.status_update.emit(f"Processing {len(self.app.image_paths)} images with Gemini Vision...")
            exercises_with_answers = self._process_images()
            
            if not exercises_with_answers:
                self.error.emit("No results generated from images")
                return
            
            # Check for errors in results
            error_count = sum(1 for _, answer in exercises_with_answers if answer.startswith("Error:"))
            if error_count > 0:
                self.status_update.emit(f"Completed with {error_count} error(s). Generating document...")
            else:
                self.status_update.emit("All images processed successfully. Generating document...")
            
            # Generate document (PDF or Word)
            output_path = self._generate_document(exercises_with_answers)
            
            self.finished.emit(output_path)
        except Exception as e:
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"
            print(f"Processing error: {error_details}")
            self.error.emit(str(e))
    
    def _process_images(self) -> list[tuple[str, str]]:
        """Process all images in parallel with rate limiting."""
        api_key = self.app.api_key_edit.text()
        if not api_key:
            raise Exception("API key is empty")
        
        if not self.app.image_paths:
            raise Exception("No images selected")
        
        # Collect custom prompts from UI
        image_custom_prompts = {}
        for image_path in self.app.image_paths:
            if image_path in self.app.image_prompt_widgets:
                _, text_edit = self.app.image_prompt_widgets[image_path]
                custom_prompt = text_edit.toPlainText().strip()
                if custom_prompt:
                    image_custom_prompts[image_path] = custom_prompt
        
        total_images = len(self.app.image_paths)
        
        rate_limiter = RateLimiter(MAX_REQUESTS_PER_WINDOW, RATE_LIMIT_WINDOW)
        
        available_slots = rate_limiter.get_available_slots()
        max_workers = min(
            MAX_CONCURRENT_WORKERS,
            max(available_slots, 1),
            total_images
        )
        
        self.status_update.emit(
            f"Processing {total_images} images in parallel "
            f"({max_workers} concurrent workers, {MAX_REQUESTS_PER_WINDOW} requests/{RATE_LIMIT_WINDOW}s limit)..."
        )
        
        exercises_with_answers = [None] * total_images
        completed = 0
        completed_lock = threading.Lock()
        
        def process_single_image(idx: int, image_path: str) -> tuple[int, tuple[str, str]]:
            """Process a single image with rate limiting."""
            nonlocal completed
            
            if not rate_limiter.acquire(timeout=300):  # 5 minute timeout
                return (idx, ("", "Error: Rate limit timeout"))
            
            try:
                self.status_update.emit(
                    f"Processing image {idx + 1} of {total_images}: {os.path.basename(image_path)}"
                )
                
                # Create a new client instance for this thread
                client = GeminiClient(api_key)
                answer = client.generate_answer_from_image(
                    image_path,
                    image_custom_prompts.get(image_path, "")
                )
                
                with completed_lock:
                    completed += 1
                    self.status_update.emit(
                        f"✓ Completed {completed}/{total_images} images "
                        f"({rate_limiter.get_available_slots()} slots remaining)"
                    )
                
                return (idx, ("", answer))
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing image {idx + 1}: {error_msg}")
                
                # Check if it's an API key error
                if 'api key' in error_msg.lower() or 'API_KEY' in error_msg:
                    raise Exception(error_msg)
                
                with completed_lock:
                    completed += 1
                    self.status_update.emit(
                        f"✗ Error processing image {idx + 1}: {error_msg[:80]}"
                    )
                
                return (idx, ("", f"Error: {error_msg}"))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_single_image, idx, path): idx
                for idx, path in enumerate(self.app.image_paths)
            }
            
            for future in as_completed(futures):
                try:
                    idx, result = future.result()
                    exercises_with_answers[idx] = result
                except Exception as e:
                    idx = futures[future]
                    error_msg = str(e)
                    exercises_with_answers[idx] = ("", f"Error: {error_msg}")
                    
                    # API key error, cancel remaining tasks and raise
                    if 'api key' in error_msg.lower() or 'API_KEY' in error_msg:
                        for f in futures:
                            f.cancel()
                        raise Exception(error_msg)
        
        self.status_update.emit(f"Finished processing all {total_images} images")
        return exercises_with_answers
    
    def _generate_document(self, exercises_with_answers: list[tuple[str, str]]) -> str:
        """Generate PDF or Word document."""
        from core.document_generator import DocumentGenerator
        
        student_name = self.app.student_name_edit.text().strip()
        group = self.app.group_edit.text().strip()
        custom_filename = self.app.output_filename_edit.text().strip()
        
        output_filename = DocumentGenerator.generate_output_filename(
            student_name, group, custom_filename
        )
        
        output_format = self.app.output_format_group.checkedButton().text().lower()
        
        if output_format == "word":
            self.status_update.emit("Generating Word document...")
            output_path = DocumentGenerator.generate_word(
                exercises_with_answers, student_name, group, output_filename
            )
        else:
            self.status_update.emit("Generating PDF...")
            output_path = DocumentGenerator.generate_pdf(
                exercises_with_answers, student_name, group, output_filename
            )
        
        return output_path

