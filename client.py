import socket
import threading
import hashlib
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

RAW_KEY = "SECRET123"
AUTH_HASH = hashlib.sha256(RAW_KEY.encode()).hexdigest()


class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Job Queue — Client")
        self.geometry("680x560")
        self.resizable(False, False)
        self.configure(bg="#0f1117")

        self.sock = None
        self.connected = False
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── fonts & colours ──
        BG      = "#0f1117"
        CARD    = "#1a1d27"
        ACCENT  = "#4f8ef7"
        SUCCESS = "#3ecf8e"
        DANGER  = "#f76f6f"
        FG      = "#e8eaf0"
        MUTED   = "#6b7280"

        self.configure(bg=BG)

        title = tk.Label(self, text="JOB QUEUE  /  CLIENT", bg=BG,
                         fg=ACCENT, font=("Courier New", 13, "bold"))
        title.pack(pady=(18, 4))

        sub = tk.Label(self, text="submit jobs to the server", bg=BG,
                       fg=MUTED, font=("Courier New", 9))
        sub.pack(pady=(0, 14))

        # ── connection card ──
        conn_frame = tk.Frame(self, bg=CARD, bd=0, padx=20, pady=14)
        conn_frame.pack(fill="x", padx=24)

        tk.Label(conn_frame, text="HOST", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).grid(row=0, column=0, sticky="w")
        tk.Label(conn_frame, text="PORT", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).grid(row=0, column=2, sticky="w", padx=(16, 0))

        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="5000")

        host_e = tk.Entry(conn_frame, textvariable=self.host_var, bg="#252836",
                          fg=FG, insertbackground=FG, relief="flat",
                          font=("Courier New", 10), width=20)
        host_e.grid(row=1, column=0, sticky="w", pady=(2, 0))

        port_e = tk.Entry(conn_frame, textvariable=self.port_var, bg="#252836",
                          fg=FG, insertbackground=FG, relief="flat",
                          font=("Courier New", 10), width=8)
        port_e.grid(row=1, column=2, sticky="w", padx=(16, 0), pady=(2, 0))

        self.conn_btn = tk.Button(conn_frame, text="CONNECT", command=self._connect,
                                  bg=ACCENT, fg="#fff", relief="flat",
                                  font=("Courier New", 9, "bold"), padx=14, pady=4,
                                  cursor="hand2", activebackground="#3a7de0")
        self.conn_btn.grid(row=1, column=4, padx=(20, 0))

        self.status_dot = tk.Label(conn_frame, text="●", bg=CARD, fg=DANGER,
                                   font=("Courier New", 14))
        self.status_dot.grid(row=1, column=5, padx=(10, 0))

        # ── job submission ──
        job_frame = tk.Frame(self, bg=CARD, padx=20, pady=14)
        job_frame.pack(fill="x", padx=24, pady=(10, 0))

        tk.Label(job_frame, text="JOB NAME", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")

        entry_row = tk.Frame(job_frame, bg=CARD)
        entry_row.pack(fill="x", pady=(3, 0))

        self.job_var = tk.StringVar()
        self.job_entry = tk.Entry(entry_row, textvariable=self.job_var, bg="#252836",
                                  fg=FG, insertbackground=FG, relief="flat",
                                  font=("Courier New", 11), width=36)
        self.job_entry.pack(side="left")
        self.job_entry.bind("<Return>", lambda e: self._submit_job())

        self.submit_btn = tk.Button(entry_row, text="SUBMIT", command=self._submit_job,
                                    bg=SUCCESS, fg="#0f1117", relief="flat",
                                    font=("Courier New", 9, "bold"), padx=14, pady=4,
                                    cursor="hand2", state="disabled",
                                    activebackground="#2bb87a")
        self.submit_btn.pack(side="left", padx=(10, 0))

        bulk_btn = tk.Button(entry_row, text="BULK 100", command=self._bulk_submit,
                             bg="#2d3148", fg=FG, relief="flat",
                             font=("Courier New", 9, "bold"), padx=10, pady=4,
                             cursor="hand2", activebackground="#3a3f5c")
        bulk_btn.pack(side="left", padx=(8, 0))
        self.bulk_btn = bulk_btn

        # ── log ──
        log_frame = tk.Frame(self, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=24, pady=12)

        tk.Label(log_frame, text="LOG", bg=BG, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")

        self.log = scrolledtext.ScrolledText(log_frame, bg=CARD, fg=FG,
                                             font=("Courier New", 9),
                                             relief="flat", state="disabled",
                                             wrap="word")
        self.log.pack(fill="both", expand=True, pady=(3, 0))
        self.log.tag_config("ok",      foreground=SUCCESS)
        self.log.tag_config("err",     foreground=DANGER)
        self.log.tag_config("info",    foreground=ACCENT)
        self.log.tag_config("muted",   foreground=MUTED)

    # ── networking ────────────────────────────────────────────────────────────

    def _connect(self):
        if self.connected:
            return
        host = self.host_var.get().strip()
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return

        threading.Thread(target=self._do_connect, args=(host, port), daemon=True).start()

    def _do_connect(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.sock.send(f"CLIENT {AUTH_HASH}".encode())
            resp = self.sock.recv(1024).decode()
            if resp != "AUTH OK":
                self._log(f"Auth failed: {resp}", "err")
                self.sock.close()
                return
            self.connected = True
            self._log(f"Connected to {host}:{port}", "ok")
            self.after(0, self._on_connected)
        except Exception as e:
            self._log(f"Connection error: {e}", "err")

    def _on_connected(self):
        self.status_dot.config(fg="#3ecf8e")
        self.conn_btn.config(state="disabled")
        self.submit_btn.config(state="normal")
        self.bulk_btn.config(state="normal")

    def _submit_job(self):
        name = self.job_var.get().strip()
        if not name:
            return
        if not self.connected:
            self._log("Not connected.", "err")
            return
        threading.Thread(target=self._do_submit, args=(name,), daemon=True).start()
        self.job_var.set("")

    def _do_submit(self, name):
        try:
            self.sock.send(f"SUBMIT {name}".encode())
            resp = self.sock.recv(1024).decode()
            if resp.startswith("OK"):
                job_id = resp.split()[1]
                self._log(f"Submitted: {name}  →  ID [{job_id}]", "ok")
            else:
                self._log(f"Server: {resp}", "err")
        except Exception as e:
            self._log(f"Error: {e}", "err")

    def _bulk_submit(self):
        if not self.connected:
            self._log("Not connected.", "err")
            return
        threading.Thread(target=self._do_bulk, daemon=True).start()

    def _do_bulk(self):
        self._log("Submitting 100 jobs...", "info")
        start = time.time()
        for i in range(1, 101):
            try:
                self.sock.send(f"SUBMIT BULK_JOB_{i}".encode())
                self.sock.recv(1024)
            except Exception as e:
                self._log(f"Bulk error at {i}: {e}", "err")
                return
        elapsed = round(time.time() - start, 4)
        self._log(f"100 jobs submitted in {elapsed}s", "ok")

    # ── log helper ────────────────────────────────────────────────────────────

    def _log(self, msg, tag="muted"):
        def _write():
            self.log.config(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.log.insert("end", f"[{ts}] {msg}\n", tag)
            self.log.see("end")
            self.log.config(state="disabled")
        self.after(0, _write)


if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
