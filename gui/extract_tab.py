import customtkinter as ctk
from tkinter import filedialog, messagebox

class ExtractTab:
    def __init__(self, parent):
        self.section_font = ctk.CTkFont(size=18, weight="bold")

        self.video_path = ctk.StringVar()
        self.encrypt_enabled = ctk.BooleanVar(value=False)
        self.mode = ctk.StringVar(value="sequential")
        self.scheme = ctk.StringVar(value="3-3-2")
        self.last_binary_payload = None
        self.last_filename = "extracted_payload.bin"

        ctk.CTkLabel(parent, text="Stego Video", font=self.section_font).pack(anchor="w", padx=10, pady=(8, 2))
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkEntry(row, textvariable=self.video_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", command=self.browse).pack(side="left")

        self.encryption_checkbox = ctk.CTkCheckBox(
            parent,
            text="Use Encryption (A5/1)",
            variable=self.encrypt_enabled,
            command=self.update_encryption_state,
        )
        self.encryption_checkbox.pack(anchor="w", padx=10, pady=(2, 10))

        self.key_frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(self.key_frame, text="Key A5/1").pack(anchor="w")
        self.key_entry = ctk.CTkEntry(self.key_frame, placeholder_text="Key (integer)")
        self.key_entry.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(parent, text="Mode", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
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

        ctk.CTkLabel(parent, text="LSB Scheme", font=self.section_font).pack(anchor="w", padx=10, pady=(2, 2))
        ctk.CTkOptionMenu(parent, values=["1-1-1", "3-3-2", "4-4-4"], variable=self.scheme).pack(
            padx=10, pady=(0, 10)
        )

        ctk.CTkButton(parent, text="EXTRACT", command=self.run_extract).pack(pady=10)

        self.result_section = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(self.result_section, text="Output", font=self.section_font).pack(anchor="w", pady=(2, 2))
        self.output_box = ctk.CTkTextbox(self.result_section, height=150)
        self.output_box.pack(fill="x")
        self.output_box.configure(state="disabled")

        self.save_button = ctk.CTkButton(
            self.result_section,
            text="Save Extracted File",
            command=self.save_extracted_file,
        )
        self.save_button.pack(pady=(8, 8))

        self.status_label = ctk.CTkLabel(parent, text="")
        self.status_label.pack(pady=(6, 0))

        self.update_encryption_state()
        self.update_seed_state()

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("AVI", "*.avi")])
        if path:
            self.video_path.set(path)

    def run_extract(self):
        video = self.video_path.get()

        try:
            from gui.stego_service import extract_payload

            result = extract_payload(
                stego_video=video,
                a51_key=self.key_entry.get() if self.encrypt_enabled.get() else "",
                stego_key=self.seed_entry.get(),
                mode=self.mode.get(),
                scheme=self.scheme.get(),
            )
            meta = result["meta"]

            if result["is_text"]:
                self.last_binary_payload = None
                self.last_filename = "extracted_payload.txt"
                self._show_result_section()
                self._set_save_button_visibility(False)
                self._set_output_text(result.get("text", ""))
                self.status_label.configure(
                    text=f"Text extracted | encrypted={meta.get('is_encrypted')}"
                )
                messagebox.showinfo("Extract Sukses", "Payload teks berhasil diekstrak.")
            else:
                self.last_binary_payload = result["payload"]
                self.last_filename = result.get("default_filename") or "extracted_payload.bin"
                self._show_result_section()
                self._set_save_button_visibility(True)
                self._set_output_text(
                    f"File extracted: {self.last_filename}\n"
                    "Klik 'Save Extracted File' untuk menyimpan."
                )
                self.status_label.configure(
                    text=f"File extracted | encrypted={meta.get('is_encrypted')}"
                )
                messagebox.showinfo(
                    "Extract Sukses",
                    "Payload file berhasil diekstrak. Pilih lokasi simpan file.",
                )
        except Exception as exc:
            if "Key A5/1 wajib diisi" in str(exc) and not self.encrypt_enabled.get():
                self.status_label.configure(text="Error: Payload terenkripsi, aktifkan Use Encryption (A5/1).")
                messagebox.showerror(
                    "Extract Gagal",
                    "Payload terdeteksi terenkripsi. Centang 'Use Encryption (A5/1)' lalu isi key yang benar.",
                )
                return

            self.status_label.configure(text=f"Error: {exc}")
            messagebox.showerror("Extract Gagal", str(exc))

    def _show_result_section(self):
        if not self.result_section.winfo_manager():
            self.result_section.pack(fill="x", padx=10, pady=(0, 0))

    def _set_save_button_visibility(self, can_save):
        if can_save:
            if not self.save_button.winfo_manager():
                self.save_button.pack(pady=(8, 8))
        else:
            self.save_button.pack_forget()

    def _set_output_text(self, text):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.configure(state="disabled")

    def update_encryption_state(self):
        if self.encrypt_enabled.get():
            self.key_frame.pack(fill="x", padx=10, pady=(0, 10), after=self.encryption_checkbox)
        else:
            self.key_frame.pack_forget()
            self.key_entry.delete(0, "end")

    def update_seed_state(self):
        if self.mode.get() == "random":
            self.seed_entry.configure(placeholder_text="Stego Key (required for random)")
            self.seed_frame.pack(fill="x", padx=10, pady=(0, 10), after=self.random_radio)
        else:
            self.seed_entry.delete(0, "end")
            self.seed_frame.pack_forget()

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