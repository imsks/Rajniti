"""
Middleware for request validation, logging, and rate limiting
"""
import logging
import time
from functools import wraps
from flask import request, jsonify
from typing import Callable, Dict, Any
import re

logger = logging.getLogger(__name__)


class RequestValidator:
    """Validates and sanitizes incoming requests"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input - remove dangerous characters"""
        if not isinstance(value, str):
            return ""
        # Remove null bytes and limit length
        sanitized = value.replace('\x00', '').strip()[:max_length]
        return sanitized
    
    @staticmethod
    def validate_politician_id(politician_id: str) -> bool:
        """Validate politician ID format"""
        # IDs should be alphanumeric with hyphens/underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, politician_id)) and len(politician_id) <= 100
    
    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, str]:
        """Validate search query"""
        if not query or len(query.strip()) == 0:
            return False, "Query cannot be empty"
        if len(query) > 200:
            return False, "Query too long (max 200 characters)"
        # Check for SQL injection patterns
        dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE', 'INSERT']
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                return False, f"Invalid characters in query"
        return True, ""


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.max_requests = 100  # per minute
        self.window = 60  # seconds
    
    def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is allowed
        Returns: (allowed, remaining_requests)
        """
        now = time.time()
        
        # Clean old entries
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier]
                if now - ts < self.window
            ]
        else:
            self.requests[identifier] = []
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False, 0
        
        # Add current request
        self.requests[identifier].append(now)
        remaining = self.max_requests - len(self.requests[identifier])
        return True, remaining


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(func: Callable) -> Callable:
    """Decorator for rate limiting endpoints"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        identifier = request.remote_addr or 'unknown'
        allowed, remaining = _rate_limiter.is_allowed(identifier)
        
        if not allowed:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        # Add rate limit headers
        response = func(*args, **kwargs)
        if isinstance(response, tuple):
            response_obj, status = response
        else:
            response_obj = response
            status = 200
        
        # Add headers if it's a Flask response
        if hasattr(response_obj, 'headers'):
            response_obj.headers['X-RateLimit-Limit'] = str(_rate_limiter.max_requests)
            response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response_obj if not isinstance(response, tuple) else (response_obj, status)
    
    return wrapper


def log_request(func: Callable) -> Callable:
    """Decorator to log API requests with timing"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        method = request.method
        path = request.path
        ip = request.remote_addr
        
        logger.info(f"Request: {method} {path} from {ip}")
        
        try:
            response = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract status code
            status = 200
            if isinstance(response, tuple):
                if len(response) > 1:
                    status = response[1]
            
            logger.info(f"Response: {method} {path} - {status} ({duration:.3f}s)")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error: {method} {path} - {str(e)} ({duration:.3f}s)")
            raise
    
    return wrapper


def validate_pagination():
    """Validate pagination parameters"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    # Enforce limits
    page = max(1, min(page, 1000))  # Max 1000 pages
    limit = max(1, min(limit, 100))  # Max 100 items per page
    
    offset = (page - 1) * limit
    
    return page, limit, offset
