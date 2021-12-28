"""
    >>> find_status_line('First line\\r\\n<!-- Comment Line\\r\\nNext line in comment\\r\\nLast line in comment-->\\r\\nLast line of text icon-flag')
    'Last line of text icon-flag'
"""

from datetime import date
from enum import Enum
from tkinter import *
from tkinter import ttk
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


def find_status_line(text: str) -> str:
    def skip_html_comment(a_line):
        if a_line.lstrip().startswith(HTML_COMMENT_START):
            if not a_line.rstrip().endswith(HTML_COMMENT_END):
                while not next(line_iterator).rstrip().endswith(HTML_COMMENT_END):
                    continue

        return a_line

    line_iterator = iter(text.split("\r\n"))

    for line in line_iterator:
        b_line = skip_html_comment(line)
        if MARKER_1 in b_line:
            return b_line

    return ""


def get_status(status_line: str) -> Status:
    if not status_line:
        return Status.UNDEFINED

    if MARKER_2 in status_line:
        return Status.FULLMAST

    return Status.HALFMAST


if __name__ == '__main__':
    status = get_status(find_status_line(get_page(URL)))

    root = Tk()
    window_title = f"Flag Status {date.today()}"

    if status != Status.UNDEFINED:
        file_name, title_suffix = status_context[status]
        status_image = ImageTk.PhotoImage(Image.open(file_name))
        label = ttk.Label(root, image=status_image)
        root.title("".join([window_title, title_suffix]))
    else:
        label = ttk.Label(root, text="Unable to determine status.")
    label.pack()

    root.mainloop()
