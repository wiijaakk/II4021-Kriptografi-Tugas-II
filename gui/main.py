import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from gui.embed_tab import EmbedTab
from gui.extract_tab import ExtractTab


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Steganography")
        self.geometry("1260x760")
        self.minsize(1160, 700)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        embed_tab = self.tabview.add("Embed")
        extract_tab = self.tabview.add("Extract")

        EmbedTab(embed_tab)
        ExtractTab(extract_tab)

if __name__ == "__main__":
    app = App()
    app.mainloop()