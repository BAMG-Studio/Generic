#!/usr/bin/env python3
"""
Main application file
Author: John Doe <john@example.com>
License: MIT
"""

import os
import sys
import requests  # Third-party dependency


def fetch_data(url: str) -> dict:
    """Fetch data from API endpoint"""
    response = requests.get(url)
    return response.json()


def process_data(data: dict) -> list:
    """Process the fetched data"""
    results = []
    for item in data.get('items', []):
        if item.get('active'):
            results.append(item)
    return results


def main():
    """Main entry point"""
    api_url = "https://api.example.com/data"
    # API_KEY = "sk_test_1234567890abcdef"  # Secret key
    
    data = fetch_data(api_url)
    results = process_data(data)
    print(f"Processed {len(results)} items")


if __name__ == "__main__":
    main()
