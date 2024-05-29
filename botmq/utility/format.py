import re

def format_to_title_case(s: str) -> str:
    return re.sub(r'_([a-z])', lambda x: ' ' + x.group(1).upper(), s).title()