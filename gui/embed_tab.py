import customtkinter as ctk
from tkinter import filedialog, messagebox
from gui.metrics import calculate_mse, calculate_psnr
from gui.stego_service import embed_payload

class EmbedTab:
    def __init__(self, parent):
        self.parent = parent
        self.section_font = ctk.CTkFont(size=18, weight="bold")

        self.video_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.payload_file_path = ctk.StringVar()
        self.payload_type = ctk.StringVar(value="text")
        self.encrypt_enabled = ctk.BooleanVar(value=False)

        # pilih video
        ctk.CTkLabel(parent, text="Cover Video", font=self.section_font).pack(anchor="w", padx=10, pady=(8, 2))
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkEntry(row, textvariable=self.video_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", command=self.browse_video).pack(side="left")

        # pilih payload
        ctk.CTkLabel(parent, text="Payload Source", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
        self.payload_type_row = ctk.CTkFrame(parent)
        self.payload_type_row.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkRadioButton(
            self.payload_type_row,
            text="Text",
            variable=self.payload_type,
            value="text",
            command=self.update_payload_input,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(
            self.payload_type_row,
            text="File",
            variable=self.payload_type,
            value="file",
            command=self.update_payload_input,
        ).pack(side="left")

        self.text_payload_frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(self.text_payload_frame, text="Text Payload").pack(anchor="w")
        self.textbox = ctk.CTkTextbox(self.text_payload_frame, height=90)
        self.textbox.pack(fill="x", pady=(4, 0))

        self.file_payload_frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(self.file_payload_frame, text="File Payload").pack(anchor="w")
        payload_file_row = ctk.CTkFrame(self.file_payload_frame)
        payload_file_row.pack(fill="x", pady=(4, 0))
        ctk.CTkEntry(payload_file_row, textvariable=self.payload_file_path).pack(
            side="left", fill="x", expand=True
        )
        ctk.CTkButton(payload_file_row, text="Browse", command=self.browse_payload_file).pack(
            side="left"
        )

        # pilih encryption
        self.encryption_checkbox = ctk.CTkCheckBox(
            parent,
            text="Use Encryption (A5/1)",
            variable=self.encrypt_enabled,
            command=self.update_encryption_state,
        )
        self.encryption_checkbox.pack(anchor="w", padx=10, pady=(2, 10))

        self.encryption_key_frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(self.encryption_key_frame, text="Key A5/1").pack(anchor="w")
        self.key_entry = ctk.CTkEntry(self.encryption_key_frame, placeholder_text="Key (integer)")
        self.key_entry.pack(fill="x", pady=(4, 0))

        # seq or random
        ctk.CTkLabel(parent, text="Insertion Mode", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
        self.mode = ctk.StringVar(value="sequential")
        self.sequential_radio = ctk.CTkRadioButton(
            parent,
            text="Sequential",
            variable=self.mode,
            value="sequential",
            command=self.update_seed_state,
        )
        self.sequential_radio.pack(anchor="w", padx=10, pady=(0, 2))
        self.random_radio = ctk.CTkRadioButton(
            parent,
            text="Random",
            variable=self.mode,
            value="random",
            command=self.update_seed_state,
        )
        self.random_radio.pack(anchor="w", padx=10, pady=(0, 10))

        self.seed_frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(self.seed_frame, text="Stego Key").pack(anchor="w")
        self.seed_entry = ctk.CTkEntry(self.seed_frame, placeholder_text="Stego Key")
        self.seed_entry.pack(fill="x", pady=(4, 0))

        # pilih lsb scheme
        ctk.CTkLabel(parent, text="LSB Scheme", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
        self.scheme = ctk.StringVar(value="3-3-2")
        ctk.CTkOptionMenu(parent, values=["1-1-1", "3-3-2", "4-4-4"], variable=self.scheme).pack(padx=10, pady=(0, 10))

        # file output
        ctk.CTkLabel(parent, text="Output", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
        row2 = ctk.CTkFrame(parent)
        row2.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkEntry(row2, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row2, text="Save", command=self.save_file).pack(side="left")

        # embed button
        ctk.CTkButton(parent, text="EMBED", command=self.run_embed).pack(pady=10)

        self.result = ctk.CTkLabel(parent, text="")
        self.result.pack()

        self.update_payload_input()
        self.update_encryption_state()
        self.update_seed_state()

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("AVI", "*.avi")])
        if path:
            self.video_path.set(path)

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".avi")
        if path:
            self.output_path.set(path)

    def browse_payload_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.payload_file_path.set(path)

    def update_payload_input(self):
        if self.payload_type.get() == "text":
            self.file_payload_frame.pack_forget()
            self.text_payload_frame.pack(fill="x", padx=10, pady=(0, 6), after=self.payload_type_row)
        else:
            self.text_payload_frame.pack_forget()
            self.file_payload_frame.pack(fill="x", padx=10, pady=(0, 6), after=self.payload_type_row)

    def update_encryption_state(self):
        if self.encrypt_enabled.get():
            self.encryption_key_frame.pack(
                fill="x",
                padx=10,
                pady=(0, 6),
                after=self.encryption_checkbox,
            )
        else:
            self.encryption_key_frame.pack_forget()
            self.key_entry.delete(0, "end")

    def update_seed_state(self):
        if self.mode.get() == "random":
            self.seed_entry.configure(placeholder_text="Stego Key (required for random)")
            self.seed_frame.pack(fill="x", padx=10, pady=(0, 6), after=self.random_radio)
        else:
            self.seed_entry.delete(0, "end")
            self.seed_frame.pack_forget()

    def run_embed(self):
        video = self.video_path.get()
        output = self.output_path.get()
        text_payload = self.textbox.get("1.0", "end").strip()

        try:
            flow_result = embed_payload(
                cover_video=video,
                output_video=output,
                payload_type=self.payload_type.get(),
                text_payload=text_payload,
                file_payload_path=self.payload_file_path.get(),
                a51_key=self.key_entry.get(),
                mode=self.mode.get(),
                scheme=self.scheme.get(),
                stego_key=self.seed_entry.get(),
                encrypt_enabled=self.encrypt_enabled.get(),
            )

            mse = calculate_mse(video, output)
            psnr = calculate_psnr(mse)
            self.result.configure(
                text=(
                    f"Done | PSNR={psnr:.2f} | MSE={mse:.5f} | "
                    f"Capacity {flow_result['needed_bytes']}/{flow_result['available_bytes']} bytes"
                )
            )
            messagebox.showinfo("Embed Sukses", "Payload berhasil disisipkan ke video.")
        except Exception as exc:
            self.result.configure(text=f"Error: {exc}")
            messagebox.showerror("Embed Gagal", str(exc))