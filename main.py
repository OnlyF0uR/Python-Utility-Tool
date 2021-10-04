# External imports
import tkinter as tk
from tkinter import ttk

# Internal imports
from encryption import Encryption
from generation import Generation
from scraping import Scraping
from calculator import Calculator


# Should be instantiated once
class WindowHandler:
    def __init__(self):
        # Instantiate classes
        window = tk.Tk()

        window.title('Utility')
        window.geometry('500x300')

        # Notebook
        tab_control = ttk.Notebook(window)
        # Individual tab frames
        gen_tab = tk.Frame(tab_control)
        crypt_tab = tk.Frame(tab_control)
        scrape_tab = tk.Frame(tab_control)
        calc_tab = tk.Frame(tab_control)

        # Adding the actual tabs
        tab_control.add(gen_tab, text='Genereren')
        tab_control.add(crypt_tab, text='Versluiteling')
        tab_control.add(scrape_tab, text='Scraping')
        tab_control.add(calc_tab, text='Mathematiek')

        tab_control.pack(expand=1, fill='both')

        # Set all tabs
        Generation(gen_tab).set_text()
        Encryption(crypt_tab).set_text()
        Scraping(scrape_tab).set_text()
        Calculator(scrape_tab).set_text()

        # Window loop
        window.mainloop()


if __name__ == "__main__":
    WindowHandler()
