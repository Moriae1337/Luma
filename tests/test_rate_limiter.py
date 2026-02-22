import time
import threading
import pytest
from core.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter."""
    
    def test_initialization(self):
        """Test RateLimiter initialization with default values."""
        limiter = RateLimiter()
        assert limiter.max_requests == 15
        assert limiter.time_window == 60.0
        assert len(limiter.requests) == 0
    
    def test_initialization_custom_values(self):
        """Test RateLimiter initialization with custom values."""
        limiter = RateLimiter(max_requests=10, time_window=30.0)
        assert limiter.max_requests == 10
        assert limiter.time_window == 30.0
    
    def test_acquire_single_request(self):
        """Test acquiring a single request slot."""
        limiter = RateLimiter(max_requests=5, time_window=60.0)
        result = limiter.acquire()
        assert result is True
        assert len(limiter.requests) == 1
    
    def test_acquire_multiple_requests(self):
        """Test acquiring multiple request slots."""
        limiter = RateLimiter(max_requests=5, time_window=60.0)
        for i in range(5):
            result = limiter.acquire()
            assert result is True
        assert len(limiter.requests) == 5
    
    def test_acquire_exceeds_limit(self):
        """Test that acquiring more than max_requests blocks."""
        limiter = RateLimiter(max_requests=2, time_window=1.0)
        
        assert limiter.acquire() is True
        assert limiter.acquire() is True
        
        start_time = time.time()
        result = limiter.acquire(timeout=0.5)
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.4
        assert result is False
    
    def test_get_available_slots(self):
        """Test getting available slots."""
        limiter = RateLimiter(max_requests=5, time_window=60.0)
        assert limiter.get_available_slots() == 5
        
        limiter.acquire()
        assert limiter.get_available_slots() == 4
        
        limiter.acquire()
        limiter.acquire()
        assert limiter.get_available_slots() == 2
    
    def test_get_available_slots_at_limit(self):
        """Test available slots when at limit."""
        limiter = RateLimiter(max_requests=3, time_window=60.0)
        for _ in range(3):
            limiter.acquire()
        assert limiter.get_available_slots() == 0
    
    def test_reset(self):
        """Test resetting the rate limiter."""
        limiter = RateLimiter(max_requests=5, time_window=60.0)
        for _ in range(3):
            limiter.acquire()
        assert len(limiter.requests) == 3
        
        limiter.reset()
        assert len(limiter.requests) == 0
        assert limiter.get_available_slots() == 5
    
    def test_time_window_expiration(self):
        """Test that old requests expire after time window."""
        limiter = RateLimiter(max_requests=2, time_window=0.5)
        
        limiter.acquire()
        limiter.acquire()
        assert limiter.get_available_slots() == 0
        
        time.sleep(0.6)
        
        assert limiter.get_available_slots() == 2
    
    def test_thread_safety(self):
        """Test that RateLimiter is thread-safe."""
        limiter = RateLimiter(max_requests=10, time_window=60.0)
        results = []
        
        def acquire_request():
            result = limiter.acquire()
            results.append(result)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=acquire_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        assert all(results)
        assert limiter.get_available_slots() == 0
    
    def test_acquire_timeout_none(self):
        """Test acquire with timeout=None waits indefinitely."""
        limiter = RateLimiter(max_requests=1, time_window=0.1)
        limiter.acquire()
        
        start_time = time.time()
        result = limiter.acquire(timeout=None)
        elapsed = time.time() - start_time
        
        assert result is True
        assert elapsed >= 0.1 
    
    def test_acquire_timeout_expires(self):
        """Test acquire with timeout that expires."""
        limiter = RateLimiter(max_requests=1, time_window=2.0)
        limiter.acquire()
        
        result = limiter.acquire(timeout=0.1)
        assert result is False

