from datetime import date
from enum import Enum
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import requests

URL = "https://www.nh.gov/index.htm"
MARKER_1 = "icon-flag"
MARKER_2 = "full"
HTML_COMMENT = "<!--"


class Status(Enum):
    FULLMAST = 1
    HALFMAST = 2
    UNDEFINED = 3


status_context = {
    Status.FULLMAST: ("resources/images/fullmast.png", " - Full Mast"),
    Status.HALFMAST: ("resources/images/halfmast.png", " - Half Mast"),
}


def get_page(url: str) -> str:
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError:
        return ""

    return request.text


def find_status_line(text: str) -> str:
    def is_html_comment() -> bool:
        return line.strip().startswith(HTML_COMMENT)

    for line in text.split("\r\n"):
        if MARKER_1 in line and not is_html_comment():
            return line

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
