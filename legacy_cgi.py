"""Backwards-compatible cgi module.

This is a stand-in for the cgi module, which was deprecated in Python 3.11
and removed in Python 3.13.

This is not a full and complete replacement for the cgi module, but it
provides enough functionality for the googletrans library to work.
"""
import re

def parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type and a dictionary of options.

    """
    parts = line.split(';')
    maintype = parts[0].lower()
    plist = []
    for part in parts[1:]:
        i = part.find('=')
        if i >= 0:
            name = part[:i].strip().lower()
            value = part[i+1:].strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            plist.append((name, value))
    return maintype, dict(plist)