# scraper/utils.py
import re
import json5

def extract_js_courses_array(html):
    """
    Find the 'courses: [' ... ']' block inside embedded JS and parse it using json5.
    Uses bracket-matching to capture the array text safely.
    Returns Python list of dicts or [] on failure.
    """
    idx = html.find("courses:")
    if idx == -1:
        return []
    # find the first '[' after 'courses:'
    start = html.find("[", idx)
    if start == -1:
        return []
    # bracket matching to find the closing ']' that matches the first '['
    depth = 0
    end = start
    for i in range(start, len(html)):
        ch = html[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    array_text = html[start:end+1]
    try:
        # json5 handles unquoted keys, trailing commas, etc.
        parsed = json5.loads(array_text)
        if isinstance(parsed, list):
            return parsed
    except Exception as e:
        # fallback: try to find a smaller object like 'data:{...courses:[...]}'
        try:
            m = re.search(r"data:\s*({.*})\s*\)\s*;", html, re.S)
            if m:
                obj = json5.loads(m.group(1))
                return obj.get("courses", []) or []
        except Exception:
            pass
    return []

def split_concepts(text):
    """
    Clean and split the 'Concepts Covered' text into list of tags.
    Splits on commas, semicolons, pipes, 'and', dashes, bullets.
    Lowercases and strips whitespace.
    """
    if not text:
        return []
    parts = re.split(r'[;,|••–—\-\u2022]|\band\b|\&', text)
    res = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # remove trailing punctuation
        p = re.sub(r'^[\W_]+|[\W_]+$', '', p)
        if p:
            res.append(p.lower())
    return res
