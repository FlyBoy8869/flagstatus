"""
    >>> find_status_line('First line\\r\\n<!-- Comment Line\\r\\nNext line in comment\\r\\nLast line in comment-->\\r\\nLast line of text icon-flag')
    'Last line of text icon-flag'
"""

from datetime import date
from enum import Enum
from tkinter import *
from tkinter import ttk
from typing import Iterable, Iterator

from PIL import ImageTk, Image
import requests

URL = "https://www.nh.gov/index.htm"
MARKER_1 = "icon-flag"
MARKER_2 = "full"
HTML_COMMENT_START = "<!--"
HTML_COMMENT_END = "-->"


class Status(Enum):
    FULLMAST = 1
    HALFMAST = 2
    UNDEFINED = 3


status_context = {
    Status.FULLMAST: ("resources/images/flag_full.png", " - Full Mast"),
    Status.HALFMAST: ("resources/images/flag_half.png", " - Half Mast"),
}


def get_page(url: str) -> str:
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


def _skip_intervening_comment_lines(it: Iterator[str]):
    while not _is_comment_end(next(it)):
        continue


def _skip_html_comments(text):
    # explicitly create iterator as it will be manually manipulated
    document = iter(text.split("\r\n"))
    for line in document:
        if _is_single_line_comment(line):
            continue
        if _is_start_multiline_comment(line):
            _skip_intervening_comment_lines(document)

        yield line


def find_status_line(text: str) -> str:
    for line in _skip_html_comments(text):
        if MARKER_1 in line:
            return line

    return ""


def get_status() -> Status:
    status_line = find_status_line(get_page(URL))
    if not status_line:
        return Status.UNDEFINED
    if MARKER_2 in status_line:
        return Status.FULLMAST

    return Status.HALFMAST


if __name__ == '__main__':
    status = get_status()

    root = Tk()
    window_title = f"Flag Status {date.today()}"

    if status != Status.UNDEFINED:
        file_name, title_suffix = status_context[status]
        status_image = ImageTk.PhotoImage(Image.open(file_name))
        label = ttk.Label(root, image=status_image)
        root.title("".join([window_title, title_suffix]))
    else:
        label = ttk.Label(root, text="\nUnable to determine status.\n\n")
    label.pack()

    root.mainloop()
