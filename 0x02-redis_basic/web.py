#!/usr/bin/env python3
"""
web.py

This module provides a function to fetch and cache web pages,
with an expiration time, and track the number of accesses.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
cache = redis.Redis(host='localhost', port=6379, db=0)

def cache_page(func: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to cache a web page and track access counts.

    Args:
        func (Callable[[str], str]): The function to wrap.

    Returns:
        Callable[[str], str]: The wrapped function.
    """
    @wraps(func)
    def wrapper(url: str) -> str:
        """
        Wrapper function to handle caching and tracking.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The content of the web page.
        """
        # Check if the URL is in cache
        cached_page = cache.get(f'cached:{url}')
        if cached_page:
            # Increment the access count for the URL
            cache.incr(f'count:{url}')
            return cached_page.decode('utf-8')

        # Fetch the page if not in cache
        page_content = func(url)

        # Store the page content in cache with an expiration time of 10 seconds
        cache.setex(f'cached:{url}', 10, page_content)

        # Increment the access count for the URL
        cache.incr(f'count:{url}')

        return page_content
    return wrapper

@cache_page
def get_page(url: str) -> str:
    """
    Fetch the content of a web page.

    Args:
        url (str): The URL of the web page.

    Returns:
        str: The content of the web page.
    """
    response = requests.get(url)
    return response.text
