import customtkinter as ctk
from tkinter import filedialog
from core.stego import extract
from gui.crypto_util import decrypt_bytes

class ExtractTab:
    def __init__(self, parent):
        self.video_path = ctk.StringVar()

        ctk.CTkLabel(parent, text="Stego Video").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=10)

        ctk.CTkEntry(row, textvariable=self.video_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", command=self.browse).pack(side="left")

        self.key_entry = ctk.CTkEntry(parent, placeholder_text="Key (optional)")
        self.key_entry.pack(fill="x", padx=10)

        self.mode = ctk.StringVar(value="sequential")
        self.scheme = ctk.StringVar(value="3-3-2")

        ctk.CTkButton(parent, text="EXTRACT", command=self.run_extract).pack(pady=10)

        self.output_box = ctk.CTkTextbox(parent, height=150)
        self.output_box.pack(fill="x", padx=10)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("AVI", "*.avi")])
        if path:
            self.video_path.set(path)

    def run_extract(self):
        video = self.video_path.get()

        payload, meta = extract(video, self.scheme.get(), self.mode.get())

        if meta['is_encrypted']:
            key = int(self.key_entry.get())
            payload = decrypt_bytes(payload, key)

        try:
            text = payload.decode()
        except:
            text = str(payload)

        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)