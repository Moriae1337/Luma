import time
import threading
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Rate limiter that enforces a maximum number of requests per time window.
    Uses a sliding window approach.
    """
    
    def __init__(self, max_requests: int = 15, time_window: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds (default 60 for per-minute limit)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()  # Store timestamps of requests
        self.lock = threading.Lock()
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.
        Blocks if necessary until a request slot is available.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
            
        Returns:
            True if permission granted, False if timeout
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                now = time.time()
                
                # Remove old requests outside the time window
                while self.requests and self.requests[0] < now - self.time_window:
                    self.requests.popleft()
                
                # Check if we can make a request
                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return True
                
                # Calculate wait time until oldest request expires
                if self.requests:
                    oldest_request = self.requests[0]
                    wait_time = (oldest_request + self.time_window) - now + 0.1  # Small buffer
                    if wait_time > 0:
                        if timeout is not None:
                            elapsed = time.time() - start_time
                            remaining_timeout = timeout - elapsed
                            if remaining_timeout <= 0:
                                return False
                            time.sleep(min(wait_time, remaining_timeout))
                        else:
                            time.sleep(wait_time)
                        continue
            
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
    
    def get_available_slots(self) -> int:
        """Get number of available request slots."""
        with self.lock:
            now = time.time()
            # Remove old requests
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            return max(0, self.max_requests - len(self.requests))
    
    def reset(self):
        """Reset the rate limiter (clear all requests)."""
        with self.lock:
            self.requests.clear()

