import customtkinter as ctk
from tkinter import filedialog, messagebox

class ExtractTab:
    def __init__(self, parent):
        self.video_path = ctk.StringVar()
        self.mode = ctk.StringVar(value="sequential")
        self.scheme = ctk.StringVar(value="3-3-2")
        self.last_binary_payload = None
        self.last_filename = "extracted_payload.bin"

        ctk.CTkLabel(parent, text="Stego Video").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", padx=10)

        ctk.CTkEntry(row, textvariable=self.video_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse", command=self.browse).pack(side="left")

        self.key_entry = ctk.CTkEntry(parent, placeholder_text="Key A5/1")
        self.key_entry.pack(fill="x", padx=10)

        ctk.CTkLabel(parent, text="Mode").pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkRadioButton(
            parent,
            text="Sequential",
            variable=self.mode,
            value="sequential",
            command=self.update_seed_state,
        ).pack(anchor="w", padx=10)
        ctk.CTkRadioButton(
            parent,
            text="Random",
            variable=self.mode,
            value="random",
            command=self.update_seed_state,
        ).pack(anchor="w", padx=10)

        self.seed_entry = ctk.CTkEntry(parent, placeholder_text="Stego Key")
        self.seed_entry.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(parent, text="LSB Scheme").pack(anchor="w", padx=10)
        ctk.CTkOptionMenu(parent, values=["1-1-1", "3-3-2", "4-4-4"], variable=self.scheme).pack(
            padx=10, pady=(0, 6)
        )

        ctk.CTkButton(parent, text="EXTRACT", command=self.run_extract).pack(pady=10)
        ctk.CTkButton(parent, text="Save Extracted File", command=self.save_extracted_file).pack(pady=(0, 8))

        self.output_box = ctk.CTkTextbox(parent, height=150)
        self.output_box.pack(fill="x", padx=10)

        self.status_label = ctk.CTkLabel(parent, text="")
        self.status_label.pack(pady=(6, 0))

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
                a51_key=self.key_entry.get(),
                stego_key=self.seed_entry.get(),
                mode=self.mode.get(),
                scheme=self.scheme.get(),
            )
            meta = result["meta"]

            self.output_box.delete("1.0", "end")
            if result["is_text"]:
                self.last_binary_payload = None
                self.last_filename = "extracted_payload.txt"
                self.output_box.insert("1.0", result.get("text", ""))
                self.status_label.configure(
                    text=f"Text extracted | encrypted={meta.get('is_encrypted')}"
                )
                messagebox.showinfo("Extract Sukses", "Payload teks berhasil diekstrak.")
            else:
                self.last_binary_payload = result["payload"]
                self.last_filename = result.get("default_filename") or "extracted_payload.bin"
                self.output_box.insert(
                    "1.0",
                    f"File extracted: {self.last_filename}\n"
                    "Klik 'Save Extracted File' untuk menyimpan.",
                )
                self.status_label.configure(
                    text=f"File extracted | encrypted={meta.get('is_encrypted')}"
                )
                messagebox.showinfo(
                    "Extract Sukses",
                    "Payload file berhasil diekstrak. Pilih lokasi simpan file.",
                )
        except ModuleNotFoundError:
            self.status_label.configure(text="Error: Dependency opencv-python belum terpasang.")
            messagebox.showerror(
                "Dependency Missing",
                "Modul 'cv2' belum terpasang. Install dengan: pip install opencv-python",
            )
        except Exception as exc:
            self.status_label.configure(text=f"Error: {exc}")
            messagebox.showerror("Extract Gagal", str(exc))

    def update_seed_state(self):
        if self.mode.get() == "random":
            self.seed_entry.configure(state="normal", placeholder_text="Stego Key (required for random)")
        else:
            self.seed_entry.configure(state="normal", placeholder_text="Stego Key (optional for sequential)")

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