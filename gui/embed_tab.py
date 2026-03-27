import customtkinter as ctk
from tkinter import filedialog
from core.stego import embed
from gui.crypto_util import encrypt_bytes
from gui.metrics import calculate_mse, calculate_psnr

class EmbedTab:
    def __init__(self, parent):
        self.parent = parent

        self.video_path = ctk.StringVar()
        self.output_path = ctk.StringVar()

        # VIDEO INPUT
        ctk.CTkLabel(parent, text="Cover Video").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=10, pady=5)

        ctk.CTkEntry(row, textvariable=self.video_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", command=self.browse_video).pack(side="left")

        # MESSAGE
        ctk.CTkLabel(parent, text="Message").pack(anchor="w", padx=10)
        self.textbox = ctk.CTkTextbox(parent, height=80)
        self.textbox.pack(fill="x", padx=10, pady=5)

        # ENCRYPTION
        self.use_encrypt = ctk.BooleanVar()
        ctk.CTkCheckBox(parent, text="Use Encryption", variable=self.use_encrypt).pack(anchor="w", padx=10)
        self.key_entry = ctk.CTkEntry(parent, placeholder_text="Key (integer)")
        self.key_entry.pack(fill="x", padx=10)

        # MODE
        self.mode = ctk.StringVar(value="sequential")
        ctk.CTkRadioButton(parent, text="Sequential", variable=self.mode, value="sequential").pack(anchor="w", padx=10)
        ctk.CTkRadioButton(parent, text="Random", variable=self.mode, value="random").pack(anchor="w", padx=10)

        self.seed_entry = ctk.CTkEntry(parent, placeholder_text="Stego Key")
        self.seed_entry.pack(fill="x", padx=10)

        # SCHEME
        self.scheme = ctk.StringVar(value="3-3-2")
        ctk.CTkOptionMenu(parent, values=["1-1-1", "3-3-2", "4-4-4"], variable=self.scheme).pack(padx=10)

        # OUTPUT
        ctk.CTkLabel(parent, text="Output").pack(anchor="w", padx=10)
        row2 = ctk.CTkFrame(parent)
        row2.pack(fill="x", padx=10)

        ctk.CTkEntry(row2, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row2, text="Save", command=self.save_file).pack(side="left")

        # BUTTON
        ctk.CTkButton(parent, text="EMBED", command=self.run_embed).pack(pady=10)

        self.result = ctk.CTkLabel(parent, text="")
        self.result.pack()

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("AVI", "*.avi")])
        if path:
            self.video_path.set(path)

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".avi")
        if path:
            self.output_path.set(path)

    def run_embed(self):
        video = self.video_path.get()
        output = self.output_path.get()
        message = self.textbox.get("1.0", "end").strip()

        data = message.encode()

        if self.use_encrypt.get():
            key = int(self.key_entry.get())
            data = encrypt_bytes(data, key)

        payload_info = {
            'payload': data,
            'ukuran': len(data),
            'nama_file': '',
            'extension': '',
            'is_encrypted': self.use_encrypt.get(),
            'is_text': True
        }

        embed(video, payload_info, output, self.scheme.get(), self.mode.get(), self.seed_entry.get())

        mse = calculate_mse(video, output)
        psnr = calculate_psnr(mse)

        self.result.configure(text=f"Done | PSNR={psnr:.2f} | MSE={mse:.5f}")