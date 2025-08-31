import argparse
import json
import re
from typing import Tuple

URL_PATTERN = re.compile(r"(?i)\b((?:https?:\/\/|www\.)[^\s\"\)\]]+)")
PHONE_CANDIDATE = re.compile(r"(?<![A-Za-z0-9])(\+?\d[\d\s\-\.\(\)]{6,}?\d)(?![A-Za-z0-9])")
EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")

def replace_phones_strict(text: str) -> Tuple[str, bool]:
    replaced = False
    def _sub(m: re.Match) -> str:
        nonlocal replaced
        val = m.group(0)
        digits = len(re.sub(r"[^0-9]", "", val))
        if 8 <= digits <= 15:
            replaced = True
            return "<phone>"
        return val
    out = PHONE_CANDIDATE.sub(_sub, text)
    return out, replaced

def redact_text(text: str) -> Tuple[str, bool]:
    if not isinstance(text, str):
        return text, False
    changed = False
    # redact emails
    new_text, email_count = EMAIL_PATTERN.subn("<email>", text)
    if email_count:
        changed = True
    # redact urls
    new_text2, url_count = URL_PATTERN.subn("<url>", new_text)
    if url_count:
        changed = True
    # redact phones (strict digit counting)
    new_text3, phone_changed = replace_phones_strict(new_text2)
    if phone_changed:
        changed = True
    return new_text3, changed

def process_file(input_path: str, output_path: str, modified_rows_path: str) -> int:
    modified = 0
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8", newline="\n") as fout, \
         open(modified_rows_path, "w", encoding="utf-8", newline="\n") as fmod:
        for line in fin:
            line = line.rstrip("\n\r")
            out_line = line
            try:
                obj = json.loads(line)
                if "text" in obj and obj["text"] is not None:
                    new_text, changed = redact_text(obj["text"])
                    if changed:
                        obj["text"] = new_text
                        out_line = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                        fmod.write(out_line + "\n")
                        modified += 1
            except Exception:
                pass
            fout.write(out_line + "\n")
    return modified

def main():
    parser = argparse.ArgumentParser(description="Redact emails, URLs, and phone numbers in JSONL text field.")
    parser.add_argument("--input", dest="input_path", default="review-Alaska_10.filtered.json")
    parser.add_argument("--output", dest="output_path", default="review-Alaska_10.filtered.redacted.strict.json")
    parser.add_argument("--modified", dest="modified_rows_path", default="review-Alaska_10.filtered.modified_rows.strict.json")
    args = parser.parse_args()
    modified = process_file(args.input_path, args.output_path, args.modified_rows_path)
    print(f"modified_rows_strict={modified}")

if __name__ == "__main__":
    main()