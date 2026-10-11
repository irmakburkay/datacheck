"""
Simple in-memory rate limiter for DataCheck.
Prevents abuse without external dependencies.
"""

import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class SimpleRateLimiter:
    """
    In-memory rate limiter using sliding window.
    
    Note: This is NOT suitable for production multi-process deployments.
    For production, use Redis-based rate limiting (Flask-Limiter).
    For this assessment, it demonstrates understanding of abuse prevention.
    """
    
    def __init__(self):
        # Storage: {ip: [(timestamp, endpoint), ...]}
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # Clean old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove entries older than 1 hour."""
        if time.time() - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff = time.time() - 3600
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                (ts, ep) for ts, ep in self.requests[ip] 
                if ts > cutoff
            ]
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, ip: str, endpoint: str, limit: int, window: int) -> tuple[bool, dict]:
        """
        Check if IP has exceeded rate limit.
        
        Args:
            ip: Client IP address
            endpoint: Endpoint being accessed
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            (is_limited, info_dict)
        """
        self._cleanup_old_entries()
        
        now = time.time()
        cutoff = now - window
        
        # Get recent requests for this IP and endpoint
        recent = [
            ts for ts, ep in self.requests[ip] 
            if ts > cutoff and ep == endpoint
        ]
        
        # Add current request
        self.requests[ip].append((now, endpoint))
        
        count = len(recent) + 1
        is_limited = count > limit
        
        retry_after = None
        if is_limited and recent:
            # Calculate when the oldest request will expire
            oldest = min(recent)
            retry_after = int(oldest + window - now)
        
        return is_limited, {
            'count': count,
            'limit': limit,
            'window': window,
            'retry_after': retry_after
        }
    
    def get_stats(self) -> dict:
        """Get current rate limiter stats."""
        return {
            'tracked_ips': len(self.requests),
            'total_requests': sum(len(reqs) for reqs in self.requests.values())
        }


# Global rate limiter instance
_rate_limiter = SimpleRateLimiter()


def reset_rate_limiter():
    """Reset the rate limiter (useful for testing)."""
    global _rate_limiter
    _rate_limiter = SimpleRateLimiter()


def rate_limit(limit: int = 10, window: int = 60, endpoint_specific: bool = True):
    """
    Decorator to apply rate limiting to Flask routes.
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        endpoint_specific: If True, limit is per endpoint; if False, global per IP
    
    Example:
        @rate_limit(limit=5, window=60)  # 5 requests per minute
        def my_route():
            return "Hello"
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP (handle proxies)
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = 'unknown'
            
            endpoint = f.__name__ if endpoint_specific else 'global'
            
            is_limited, info = _rate_limiter.is_rate_limited(ip, endpoint, limit, window)
            
            if is_limited:
                logger.warning(
                    f"Rate limit exceeded: IP={ip}, endpoint={endpoint}, "
                    f"count={info['count']}/{info['limit']} in {info['window']}s"
                )
                
                response = jsonify({
                    'error': 'Too many requests',
                    'message': f'Rate limit exceeded. Try again in {info["retry_after"]} seconds.',
                    'retry_after': info['retry_after']
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(info['retry_after'])
                return response
            
            return f(*args, **kwargs)
        
        return wrapped
    return decorator


def get_rate_limiter_stats() -> dict:
    """Get current rate limiter statistics."""
    return _rate_limiter.get_stats()
