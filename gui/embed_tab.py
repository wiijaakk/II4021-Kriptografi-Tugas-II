import customtkinter as ctk
from tkinter import filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.video_io import calculate_capacity
from gui.metrics import calculate_mse, calculate_psnr, sample_rgb_histogram
from gui.stego_service import embed_payload

class EmbedTab:
    def __init__(self, parent):
        self.section_font = ctk.CTkFont(size=14, weight="bold")
        self.small_font = ctk.CTkFont(size=14)

        root = ctk.CTkFrame(parent, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=10, pady=10)
        root.grid_columnconfigure(0, weight=4)
        root.grid_columnconfigure(1, weight=5)
        root.grid_rowconfigure(0, weight=1)

        self.video_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.payload_file_path = ctk.StringVar()
        self.payload_type = ctk.StringVar(value="text")
        self.encrypt_enabled = ctk.IntVar(value=0)
        self.mode = ctk.StringVar(value="sequential")
        self.scheme = ctk.StringVar(value="3-3-2")

        left = ctk.CTkFrame(root, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(root, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self._build_controls(left)
        self._build_metrics_panel(right)
        self._build_histogram_panel(right)

        self.encrypt_enabled.set(0)
        self.encryption_checkbox.deselect()
        self.encryption_key_frame.grid_remove()

        self.update_payload_input()
        self.update_encryption_state()
        self.update_seed_state()
        self._refresh_capacity_hint()
        self._draw_empty_histogram("Pilih cover video untuk melihat RGB histogram")

    def _build_controls(self, parent):
        self.form = ctk.CTkFrame(parent, fg_color="transparent")
        self.form.grid(row=0, column=0, sticky="nsew", padx=14, pady=(10, 10))
        self.form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.form, text="Cover Video", font=self.section_font).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        video_row = ctk.CTkFrame(self.form)
        video_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        video_row.grid_columnconfigure(0, weight=1)
        self.video_entry = ctk.CTkEntry(video_row, textvariable=self.video_path, state="readonly")
        self.video_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(video_row, text="Browse", width=90, command=self.browse_video).grid(row=0, column=1)

        ctk.CTkLabel(self.form, text="Payload", font=self.section_font).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.payload_switch = ctk.CTkSegmentedButton(
            self.form,
            values=["text", "file"],
            variable=self.payload_type,
            font=self.small_font,
            command=lambda _: self.update_payload_input(),
        )
        self.payload_switch.grid(row=3, column=0, sticky="ew", pady=(0, 6))

        self.text_payload_frame = ctk.CTkFrame(self.form)
        self.text_payload_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.text_payload_frame, text="Message", font=self.small_font).grid(row=0, column=0, sticky="w")
        self.textbox = ctk.CTkTextbox(self.text_payload_frame, height=88)
        self.textbox.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.file_payload_frame = ctk.CTkFrame(self.form)
        self.file_payload_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.file_payload_frame, text="Payload File", font=self.small_font).grid(
            row=0, column=0, sticky="w", columnspan=2
        )
        self.payload_file_entry = ctk.CTkEntry(
            self.file_payload_frame,
            textvariable=self.payload_file_path,
            state="readonly",
        )
        self.payload_file_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0), padx=(0, 6))
        ctk.CTkButton(self.file_payload_frame, text="Browse", width=90, command=self.browse_payload_file).grid(
            row=1, column=1, pady=(4, 0)
        )

        options = ctk.CTkFrame(self.form, corner_radius=10)
        options.grid(row=6, column=0, sticky="ew", pady=(8, 2))
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

        ctk.CTkLabel(settings_col, text="Insertion Mode", font=self.section_font).grid(row=2, column=0, sticky="w", pady=(8, 0))
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
            values=["1-1-1", "3-3-2", "4-4-4"],
            font=self.small_font,
            dropdown_font=self.small_font,
            variable=self.scheme,
            command=lambda _: self._refresh_capacity_hint(),
        ).grid(row=6, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(self.form, text="Output", font=self.section_font).grid(row=7, column=0, sticky="w", pady=(6, 2))
        out_row = ctk.CTkFrame(self.form, fg_color="transparent")
        out_row.grid(row=8, column=0, sticky="ew")
        out_row.grid_columnconfigure(0, weight=1)
        self.output_entry = ctk.CTkEntry(out_row, textvariable=self.output_path, state="readonly", height=28)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(out_row, text="Save As", width=90, height=28, command=self.save_file).grid(row=0, column=1)

        ctk.CTkButton(parent, text="EMBED", height=40, command=self.run_embed).grid(
            row=1, column=0, sticky="ew", padx=12, pady=(0, 8)
        )

    def _build_metrics_panel(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=10)
        panel.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.metric_mse = ctk.CTkLabel(panel, text="MSE: -", font=self.small_font)
        self.metric_mse.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.metric_psnr = ctk.CTkLabel(panel, text="PSNR: -", font=self.small_font)
        self.metric_psnr.grid(row=0, column=1, sticky="w", padx=8, pady=8)

        self.metric_capacity = ctk.CTkLabel(panel, text="Capacity: -", font=self.small_font)
        self.metric_capacity.grid(row=0, column=2, sticky="w", padx=8, pady=8)

        self.metric_scheme = ctk.CTkLabel(panel, text="Scheme: 3-3-2", font=self.small_font)
        self.metric_scheme.grid(row=0, column=3, sticky="w", padx=8, pady=8)

        self.result = ctk.CTkLabel(parent, text="", anchor="w", justify="left")
        self.result.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))

    def _build_histogram_panel(self, parent):
        hist_card = ctk.CTkFrame(parent)
        hist_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        hist_card.grid_columnconfigure(0, weight=1)
        hist_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(hist_card, text="RGB Histogram", font=self.section_font).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 2)
        )
        ctk.CTkLabel(
            hist_card,
            text="Cover vs stego comparison",
            font=self.small_font,
            text_color="#8CB5D9",
        ).grid(row=0, column=0, sticky="e", padx=10, pady=(8, 2))

        self.hist_container = ctk.CTkFrame(hist_card, fg_color="#0F1D3A")
        self.hist_container.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.hist_container.grid_rowconfigure(0, weight=1)
        self.hist_container.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(6.8, 2.9), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.hist_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("AVI", "*.avi")])
        if path:
            self.video_path.set(path)
            self._refresh_capacity_hint()
            self._update_histograms(cover_video=path)

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
            self.file_payload_frame.grid_forget()
            self.text_payload_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        else:
            self.text_payload_frame.grid_forget()
            self.file_payload_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))

    def update_encryption_state(self):
        encrypt_enabled_raw = self.encryption_checkbox.get()
        if isinstance(encrypt_enabled_raw, str):
            encrypt_enabled = encrypt_enabled_raw.strip().lower() in ("1", "true", "on", "yes")
        else:
            encrypt_enabled = bool(encrypt_enabled_raw)

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

    def _refresh_capacity_hint(self):
        self.metric_scheme.configure(text=f"Scheme: {self.scheme.get()}")
        cover_video = (self.video_path.get() or "").strip()
        if not cover_video:
            self.metric_capacity.configure(text="Capacity: -")
            return

        try:
            cap_bytes = calculate_capacity(cover_video, self.scheme.get())
            self.metric_capacity.configure(text=f"Capacity: {cap_bytes} B")
        except Exception:
            self.metric_capacity.configure(text="Capacity: n/a")

    def _draw_empty_histogram(self, info_text):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#0F1D3A")
        self.figure.set_facecolor("#0F1D3A")
        ax.text(0.5, 0.5, info_text, color="#9FC4E3", ha="center", va="center", fontsize=11)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#2A4B74")
        self.canvas.draw()

    def _update_histograms(self, cover_video=None, stego_video=None):
        cover_video = (cover_video or "").strip()
        stego_video = (stego_video or "").strip()

        if not cover_video and not stego_video:
            self._draw_empty_histogram("Belum ada video untuk dihitung")
            return

        self.figure.clear()
        self.figure.set_facecolor("#0F1D3A")

        plots = [("b", "#65A9FF", "Blue"), ("g", "#49D17D", "Green"), ("r", "#FF6B7A", "Red")]

        cover_hist = None
        stego_hist = None
        try:
            if cover_video:
                cover_hist = sample_rgb_histogram(cover_video)
            if stego_video:
                stego_hist = sample_rgb_histogram(stego_video)
        except Exception as exc:
            self._draw_empty_histogram(f"Gagal render histogram: {exc}")
            return

        for idx, (key, line_color, label) in enumerate(plots, start=1):
            ax = self.figure.add_subplot(1, 3, idx)
            ax.set_facecolor("#0F1D3A")
            ax.set_title(label, color="#C2D5F0", fontsize=9)
            ax.tick_params(colors="#6E8CB2", labelsize=7)
            ax.grid(alpha=0.12, color="#2F4C73", linewidth=0.5)

            if cover_hist is not None:
                ax.plot(cover_hist["bins"], cover_hist[key], color=line_color, linewidth=1.2, label="Cover")
            if stego_hist is not None:
                ax.plot(
                    stego_hist["bins"],
                    stego_hist[key],
                    color="#F6B73C",
                    linewidth=1.0,
                    linestyle="--",
                    label="Stego",
                )

            if idx == 3 and (cover_hist is not None or stego_hist is not None):
                ax.legend(facecolor="#0F1D3A", edgecolor="#2F4C73", fontsize=7, labelcolor="#BCD3EE")

        self.figure.tight_layout(pad=1.1)
        self.canvas.draw()

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
                encrypt_enabled=(
                    self.encryption_checkbox.get().strip().lower() in ("1", "true", "on", "yes")
                    if isinstance(self.encryption_checkbox.get(), str)
                    else bool(self.encryption_checkbox.get())
                ),
            )

            mse = calculate_mse(video, output)
            psnr = calculate_psnr(mse)

            self.metric_mse.configure(text=f"MSE: {mse:.5f}")
            self.metric_psnr.configure(text=f"PSNR: {psnr:.2f} dB")
            self.metric_capacity.configure(
                text=f"Capacity: {flow_result['needed_bytes']}/{flow_result['available_bytes']} B"
            )


            self._update_histograms(cover_video=video, stego_video=output)
            messagebox.showinfo("Embed Sukses", "Payload berhasil disisipkan ke video.")
        except Exception as exc:
            self.result.configure(text=f"Error: {exc}")
            messagebox.showerror("Embed Gagal", str(exc))
