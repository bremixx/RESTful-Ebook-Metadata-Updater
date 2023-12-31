from typing import List, Union, Tuple
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from glob import glob
from shutil import copy


def launch() -> None:
    '''Deploys the preview image window'''
    root = tk.Tk()
    root.resizable(False, False)

    app = MainWindow(root)
    app.viewer_frame()
    app.create_widgets()

    root.mainloop()


class MainWindow(tk.Frame):

    def __init__(self, main=None):

        tk.Frame.__init__(self, main)
        self.index = 1
        self.main = main
        self.pack(fill=tk.BOTH, expand=1)
        self.rarrow = tk.PhotoImage(file=r'static\arrow-right-solid.png')
        self.larrow = tk.PhotoImage(file=r'static\arrow-left-solid.png')
        self.darrow = tk.PhotoImage(file=r'static\arrow-down-solid.png')
        self.img = None

    def click_forward(self) -> None:
        '''Navigate forward to new image in viewer frame'''
        files = glob('cover_page*.jpg')
        self.index += 1
        if f'cover_page{self.index}.jpg' not in files:
            self.index = 1
        self.viewer_frame()

    def click_back(self) -> None:
        '''Navigate back to previous image in viewer frame'''
        files = glob('cover_page*.jpg')
        self.index -= 1
        if f'cover_page{self.index}.jpg' not in files:
            self.index = len(files)
        self.viewer_frame()

    def save_image(self) -> None:
        '''Save image to eBook cover page'''
        copy(f'cover_page{self.index}.jpg', 'convert.jpg')

        self.main.destroy()

    def dimensions(self) -> List[Union[Tuple, float]]:
        '''Gets the cover_page.jpg image dimensions'''
        files = [file for file in glob('cover_page*.jpg')]
        return [(Image.open(file).size) for file in files]

    def resize_image(self) -> None:
        '''Resize cover page image for viewer window'''
        dim = min(self.dimensions())
        if dim[1] >= 900:
            dim = (dim[0] * .5, dim[1] * .5)
        width, height = self.load.size
        aspect_ratio = width / height
        new = (round(dim[0] * aspect_ratio), round(dim[1] * aspect_ratio))
        self.adjusted_image = self.load.resize(new)

    def viewer_frame(self) -> None:
        '''Renders image in main window'''
        if self.img is not None:
            self.img.destroy()

        self.load = Image.open(f'cover_page{self.index}.jpg')
        self.resize_image()

        render = ImageTk.PhotoImage(self.adjusted_image)
        self.img = tk.Label(self, image=render, borderwidth=0)
        self.img.image = render
        self.img.pack(side=tk.TOP)

    def create_widgets(self) -> None:
        '''Creates button frame for viewer navigation'''
        style = ttk.Style()
        style.configure('TButton', background='#333333')

        button_frame = tk.Frame(self, bg='#333333')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        button1 = ttk.Button(button_frame, text='Previous',
            image=self.larrow, compound='image', command=self.click_back)
        button2 = ttk.Button(button_frame, text='Next',
            image=self.rarrow, compound='image', command=self.click_forward)
        button3 = ttk.Button(button_frame, text='Download',
            image=self.darrow, compound='image', command=self.save_image)

        button1.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        button2.grid(row=0, column=2, padx=10, pady=10, sticky='w')
        button3.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(2, weight=1)
