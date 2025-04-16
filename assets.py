"""
Assets Module - Handles ASCII art and other assets
"""
import os
import json
from data.ascii_art import ASCII_ART

def get_ascii_art(art_name):
    """Get ASCII art by name"""
    return ASCII_ART.get(art_name, "")
