from datetime import date
from enum import Enum
from tkinter import *
from tkinter import ttk

import requests
from PIL import Image, ImageTk

from tkinter_helpers import center

URL = "https://www.nh.gov/index.htm"
MARKER_1 = "icon-flag"
MARKER_2 = "full"
HTML_COMMENT_START = "<!--"
HTML_COMMENT_END = "-->"

# date format e.g., Sunday, January 01, 2022
DATE_FORMAT = '%A, %B %d, %Y'


class Status(Enum):
    FULLMAST = 1
    HALFMAST = 2
    UNDETERMINED = 3


status_context = {
    Status.FULLMAST: ("resources/images/flag_full.png", " - Full Mast"),
    Status.HALFMAST: ("resources/images/flag_half.png", " - Half Mast"),
    Status.UNDETERMINED: ("resources/images/undetermined.png", " - Unable to determine"),
}


def _get_page(url: str) -> str:
    """"Return the webpage text of 'url' if successful, or else an empty string"""
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError:
        return ""

    return request.text


def _is_comment_start(line: str):
    return line.lstrip().startswith(HTML_COMMENT_START)


def _is_comment_end(line: str):
    return line.rstrip().endswith(HTML_COMMENT_END)


def _is_single_line_comment(line: str):
    return _is_comment_start(line) and _is_comment_end(line)


def _is_start_multiline_comment(line: str):
    return _is_comment_start(line) and not _is_comment_end(line)


def _skip_html_comments(text):
    def _skip_intervening_comment_lines():
        while not _is_comment_end(next(document)):
            continue
        next(document)  # position iterator at line right after the closing comment line

    # explicitly create iterator as it will be manually manipulated
    document = iter(text.split("\r\n"))
    for line in document:
        if not line.strip():
            continue
        if _is_single_line_comment(line):
            continue  # allows skipping consecutive comment lines
        if _is_start_multiline_comment(line):
            _skip_intervening_comment_lines()
            continue

        yield line


def _find_status_line(text: str) -> str:
    for line in _skip_html_comments(text):
        if MARKER_1 in line:
            return line

    return ""


def get_status() -> Status:
    status_line = _find_status_line(_get_page(URL))
    if not status_line:
        return Status.UNDETERMINED
    if MARKER_2 in status_line:
        return Status.FULLMAST

    return Status.HALFMAST


def main():
    status = get_status()

    root = Tk()
    window_title = f"Flag Status for {date.today().strftime(DATE_FORMAT)}"
    file_name, title_suffix = status_context[status]
    status_image = ImageTk.PhotoImage(Image.open(file_name))
    label = ttk.Label(root, image=status_image)
    root.title("".join([window_title, title_suffix]))
    label.pack()
    center(root)

    root.mainloop()


if __name__ == '__main__':
    main()
