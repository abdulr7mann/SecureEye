import sys
import re

def find_sql_injection(file_path):
    pattern = r'\$_(GET|POST|REQUEST)\[[\"\'"]?\w+[\"\'"]?\]\s*\.\s*\$?\w*\s*(\.\s*\$_(GET|POST|REQUEST)\[[\"\'"]?\w+[\"\'"]?\]\s*)*\s*(=|!=|<>|>|<|>=|<=|LIKE|REGEXP|BETWEEN)\s*(\$_(GET|POST|REQUEST)\[[\"\'"]?\w+[\"\'"]?\]|\?)'

    with open(file_path) as f:
        for line_number, line in enumerate(f, start=1):
            if re.search(pattern, line):
                print(f"{line_number}: {line.strip()}")

if __name__ == '__main__':
    file_path = sys.argv[1]
    find_sql_injection(file_path)
