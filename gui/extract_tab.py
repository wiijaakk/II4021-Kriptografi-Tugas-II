import customtkinter as ctk
from tkinter import filedialog, messagebox

class ExtractTab:
    def __init__(self, parent):
        self.section_font = ctk.CTkFont(size=14, weight="bold")
        self.small_font = ctk.CTkFont(size=14)

        root = ctk.CTkFrame(parent, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=10, pady=10)
        root.grid_columnconfigure(0, weight=4)
        root.grid_columnconfigure(1, weight=5)
        root.grid_rowconfigure(0, weight=1)

        self.video_path = ctk.StringVar()
        self.encrypt_enabled = ctk.IntVar(value=0)
        self.mode = ctk.StringVar(value="sequential")
        self.scheme = ctk.StringVar(value="3-3-2")
        self.last_binary_payload = None
        self.last_filename = "extracted_payload.bin"

        left = ctk.CTkFrame(root, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(root, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self._build_controls(left)
        self._build_output_panel(right)

        self.update_encryption_state()
        self.update_seed_state()

    def _build_controls(self, parent):
        self.form = ctk.CTkFrame(parent, fg_color="transparent")
        self.form.grid(row=0, column=0, sticky="nsew", padx=14, pady=(10, 10))
        self.form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.form, text="Stego Video", font=self.section_font).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        video_row = ctk.CTkFrame(self.form)
        video_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        video_row.grid_columnconfigure(0, weight=1)
        self.video_entry = ctk.CTkEntry(video_row, textvariable=self.video_path, state="readonly")
        self.video_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(video_row, text="Browse", width=90, command=self.browse).grid(row=0, column=1)

        options = ctk.CTkFrame(self.form, corner_radius=10)
        options.grid(row=2, column=0, sticky="ew", pady=(8, 2))
        options.grid_columnconfigure(0, weight=1)

        settings_col = ctk.CTkFrame(options, fg_color="transparent")
        settings_col.grid(row=0, column=0, sticky="ew", padx=0, pady=8)
        settings_col.grid_columnconfigure(0, weight=1)

        self.encryption_checkbox = ctk.CTkCheckBox(
            settings_col,
            text="Use Encryption (A5/1)",
            font=self.small_font,
            variable=self.encrypt_enabled,
            onvalue=1,
            offvalue=0,
            command=self.update_encryption_state,
        )
        self.encryption_checkbox.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.encryption_key_frame = ctk.CTkFrame(settings_col, fg_color="transparent")
        self.encryption_key_frame.grid_columnconfigure(0, weight=1)
        self.key_entry = ctk.CTkEntry(self.encryption_key_frame, placeholder_text="A5/1 key (integer)")
        self.key_entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(settings_col, text="Mode", font=self.section_font).grid(row=2, column=0, sticky="w", pady=(8, 0))
        mode_row = ctk.CTkFrame(settings_col, fg_color="transparent")
        mode_row.grid(row=3, column=0, sticky="ew", pady=(2, 4))
        ctk.CTkRadioButton(
            mode_row,
            text="Sequential",
            font=self.small_font,
            variable=self.mode,
            value="sequential",
            command=self.update_seed_state,
        ).pack(side="left")
        ctk.CTkRadioButton(
            mode_row,
            text="Random",
            font=self.small_font,
            variable=self.mode,
            value="random",
            command=self.update_seed_state,
        ).pack(side="left", padx=(8, 0))

        self.seed_frame = ctk.CTkFrame(settings_col, fg_color="transparent")
        self.seed_frame.grid_columnconfigure(0, weight=1)
        self.seed_entry = ctk.CTkEntry(self.seed_frame, placeholder_text="Stego key")
        self.seed_entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(settings_col, text="LSB Scheme", font=self.section_font).grid(row=5, column=0, sticky="w", pady=(8, 0))
        ctk.CTkOptionMenu(
            settings_col,
            values=["1-1-1", "3-3-2", "4-4-4", "mp4-robust"],
            font=self.small_font,
            dropdown_font=self.small_font,
            variable=self.scheme,
        ).grid(row=6, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkButton(parent, text="EXTRACT", height=40, command=self.run_extract).grid(
            row=1, column=0, sticky="ew", padx=12, pady=(0, 8)
        )

    def _build_output_panel(self, parent):
        self.status_label = ctk.CTkLabel(parent, text="", anchor="w", justify="left", font=self.small_font)
        self.status_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        output_card = ctk.CTkFrame(parent)
        output_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        output_card.grid_columnconfigure(0, weight=1)
        output_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(output_card, text="Output", font=self.section_font).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 2)
        )

        self.output_box = ctk.CTkTextbox(output_card, height=200)
        self.output_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.output_box.configure(state="disabled")

        self.save_button = ctk.CTkButton(
            output_card,
            text="Save Extracted File",
            height=32,
            command=self.save_extracted_file,
        )
        self.save_button.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.avi *.mp4")])
        if path:
            self.video_path.set(path)

    def _is_encryption_enabled(self):
        """Parse encryption checkbox state robustly."""
        raw = self.encryption_checkbox.get()
        if isinstance(raw, str):
            return raw.strip().lower() in ("1", "true", "on", "yes")
        return bool(raw)

    def run_extract(self):
        video = self.video_path.get()

        try:
            from gui.stego_service import extract_payload

            result = extract_payload(
                stego_video=video,
                a51_key=self.key_entry.get() if self._is_encryption_enabled() else "",
                stego_key=self.seed_entry.get(),
                mode=self.mode.get(),
                scheme=self.scheme.get(),
            )
            meta = result["meta"]

            if result["is_text"]:
                self.last_binary_payload = None
                self.last_filename = "extracted_payload.txt"
                self._set_output_text(result.get("text", ""))
                self.status_label.configure(
                    text=f"✓ Text extracted | encrypted={meta.get('is_encrypted')}"
                )
                self.save_button.configure(state="disabled")
                messagebox.showinfo("Extract Sukses", "Payload teks berhasil diekstrak.")
            else:
                self.last_binary_payload = result["payload"]
                self.last_filename = result.get("default_filename") or "extracted_payload.bin"
                self._set_output_text(
                    f"File extracted: {self.last_filename}\n"
                    "Klik 'Save Extracted File' untuk menyimpan."
                )
                self.status_label.configure(
                    text=f"✓ File extracted | encrypted={meta.get('is_encrypted')}"
                )
                self.save_button.configure(state="normal")
                messagebox.showinfo(
                    "Extract Sukses",
                    "Payload file berhasil diekstrak. Pilih lokasi simpan file.",
                )
        except Exception as exc:
            if "Key A5/1 wajib diisi" in str(exc) and not self._is_encryption_enabled():
                self.status_label.configure(text="✗ Error: Payload terenkripsi, aktifkan Use Encryption (A5/1).")
                messagebox.showerror(
                    "Extract Gagal",
                    "Payload terdeteksi terenkripsi. Centang 'Use Encryption (A5/1)' lalu isi key yang benar.",
                )
                return

            self.status_label.configure(text=f"✗ Error: {exc}")
            messagebox.showerror("Extract Gagal", str(exc))

    def _set_output_text(self, text):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.configure(state="disabled")

    def update_encryption_state(self):
        encrypt_enabled = self._is_encryption_enabled()
        if encrypt_enabled:
            self.encryption_key_frame.grid(row=1, column=0, sticky="ew")
        else:
            self.encryption_key_frame.grid_remove()
            self.key_entry.delete(0, "end")

    def update_seed_state(self):
        if self.mode.get() == "random":
            self.seed_entry.configure(placeholder_text="Stego key (required)")
            self.seed_frame.grid(row=4, column=0, sticky="ew", pady=(0, 2))
        else:
            self.seed_entry.delete(0, "end")
            self.seed_frame.grid_forget()

    def save_extracted_file(self):
        if self.last_binary_payload is None:
            messagebox.showwarning("Belum Ada File", "Belum ada payload file yang bisa disimpan.")
            return

        initial_name = self.last_filename or "extracted_payload.bin"
        extension = ""
        if "." in initial_name:
            extension = "." + initial_name.split(".")[-1]

        output_path = filedialog.asksaveasfilename(
            initialfile=initial_name,
            defaultextension=extension,
        )
        if not output_path:
            return

        with open(output_path, "wb") as out_file:
            out_file.write(self.last_binary_payload)

        messagebox.showinfo("File Tersimpan", f"File berhasil disimpan di:\n{output_path}")