import socket
import threading
import hashlib
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

RAW_KEY = "SECRET123"
AUTH_HASH = hashlib.sha256(RAW_KEY.encode()).hexdigest()


class WorkerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Job Queue — Worker")
        self.geometry("720x620")
        self.resizable(False, False)

        self.sock = None
        self.connected = False
        self.current_job = None   # (id, name)
        self.auto_mode = False

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        BG      = "#0f1117"
        CARD    = "#1a1d27"
        ACCENT  = "#f5a623"
        SUCCESS = "#3ecf8e"
        DANGER  = "#f76f6f"
        FG      = "#e8eaf0"
        MUTED   = "#6b7280"
        PURPLE  = "#a78bfa"

        self.configure(bg=BG)

        tk.Label(self, text="JOB QUEUE  /  WORKER", bg=BG,
                 fg=ACCENT, font=("Courier New", 13, "bold")).pack(pady=(18, 4))
        tk.Label(self, text="claim and process jobs from the server", bg=BG,
                 fg=MUTED, font=("Courier New", 9)).pack(pady=(0, 14))

        # ── connection card ──
        conn_frame = tk.Frame(self, bg=CARD, padx=20, pady=14)
        conn_frame.pack(fill="x", padx=24)

        tk.Label(conn_frame, text="HOST", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).grid(row=0, column=0, sticky="w")
        tk.Label(conn_frame, text="PORT", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).grid(row=0, column=2, sticky="w", padx=(16, 0))

        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="5000")

        tk.Entry(conn_frame, textvariable=self.host_var, bg="#252836",
                 fg=FG, insertbackground=FG, relief="flat",
                 font=("Courier New", 10), width=20).grid(row=1, column=0, sticky="w", pady=(2,0))

        tk.Entry(conn_frame, textvariable=self.port_var, bg="#252836",
                 fg=FG, insertbackground=FG, relief="flat",
                 font=("Courier New", 10), width=8).grid(row=1, column=2, sticky="w",
                                                          padx=(16,0), pady=(2,0))

        self.conn_btn = tk.Button(conn_frame, text="CONNECT", command=self._connect,
                                  bg=ACCENT, fg="#0f1117", relief="flat",
                                  font=("Courier New", 9, "bold"), padx=14, pady=4,
                                  cursor="hand2", activebackground="#d4901e")
        self.conn_btn.grid(row=1, column=4, padx=(20, 0))

        self.status_dot = tk.Label(conn_frame, text="●", bg=CARD, fg=DANGER,
                                   font=("Courier New", 14))
        self.status_dot.grid(row=1, column=5, padx=(10, 0))

        # ── job list ──
        list_frame = tk.Frame(self, bg=CARD, padx=20, pady=14)
        list_frame.pack(fill="x", padx=24, pady=(10, 0))

        top_row = tk.Frame(list_frame, bg=CARD)
        top_row.pack(fill="x")

        tk.Label(top_row, text="AVAILABLE JOBS", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(side="left")

        self.refresh_btn = tk.Button(top_row, text="⟳ REFRESH", command=self._refresh,
                                     bg="#252836", fg=FG, relief="flat",
                                     font=("Courier New", 8), padx=8, pady=2,
                                     cursor="hand2", state="disabled")
        self.refresh_btn.pack(side="right")

        self.getjob_btn = tk.Button(top_row, text="⚡ GET NEXT JOB", command=self._get_next_job,
                                    bg=PURPLE, fg="#fff", relief="flat",
                                    font=("Courier New", 8, "bold"), padx=10, pady=2,
                                    cursor="hand2", state="disabled")
        self.getjob_btn.pack(side="right", padx=(0, 8))

        # job listbox
        lb_frame = tk.Frame(list_frame, bg=CARD)
        lb_frame.pack(fill="x", pady=(6, 0))

        self.job_listbox = tk.Listbox(lb_frame, bg="#252836", fg=FG,
                                      selectbackground=ACCENT, selectforeground="#0f1117",
                                      font=("Courier New", 9), relief="flat",
                                      height=5, activestyle="none")
        self.job_listbox.pack(side="left", fill="x", expand=True)

        sb = tk.Scrollbar(lb_frame, command=self.job_listbox.yview, bg=CARD)
        sb.pack(side="right", fill="y")
        self.job_listbox.config(yscrollcommand=sb.set)

        self.accept_btn = tk.Button(list_frame, text="ACCEPT SELECTED",
                                    command=self._accept_selected,
                                    bg=SUCCESS, fg="#0f1117", relief="flat",
                                    font=("Courier New", 9, "bold"), padx=14, pady=4,
                                    cursor="hand2", state="disabled")
        self.accept_btn.pack(anchor="e", pady=(8, 0))

        # ── current job card ──
        cj_frame = tk.Frame(self, bg=CARD, padx=20, pady=14)
        cj_frame.pack(fill="x", padx=24, pady=(10, 0))

        tk.Label(cj_frame, text="CURRENT JOB", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")

        self.current_job_label = tk.Label(cj_frame, text="— none —", bg=CARD, fg=MUTED,
                                          font=("Courier New", 11))
        self.current_job_label.pack(anchor="w", pady=(4, 6))

        prog_row = tk.Frame(cj_frame, bg=CARD)
        prog_row.pack(fill="x")

        self.progress = ttk.Progressbar(prog_row, mode="determinate", length=400)
        self.progress.pack(side="left")

        self.done_btn = tk.Button(prog_row, text="MARK DONE", command=self._mark_done,
                                  bg=DANGER, fg="#fff", relief="flat",
                                  font=("Courier New", 9, "bold"), padx=12, pady=3,
                                  cursor="hand2", state="disabled")
        self.done_btn.pack(side="left", padx=(12, 0))

        # ── log ──
        log_frame = tk.Frame(self, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=24, pady=12)

        tk.Label(log_frame, text="LOG", bg=BG, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")

        self.log = scrolledtext.ScrolledText(log_frame, bg=CARD, fg=FG,
                                             font=("Courier New", 9), relief="flat",
                                             state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True, pady=(3, 0))
        self.log.tag_config("ok",   foreground=SUCCESS)
        self.log.tag_config("err",  foreground=DANGER)
        self.log.tag_config("info", foreground=ACCENT)
        self.log.tag_config("muted", foreground=MUTED)

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
            self.sock.send(f"WORKER {AUTH_HASH}".encode())
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
        self.refresh_btn.config(state="normal")
        self.getjob_btn.config(state="normal")
        self._refresh()

    def _refresh(self):
        if not self.connected:
            return
        threading.Thread(target=self._do_list, daemon=True).start()

    def _do_list(self):
        try:
            self.sock.send("LIST".encode())
            data = self.sock.recv(4096).decode()
            self.after(0, lambda: self._populate_list(data))
        except Exception as e:
            self._log(f"List error: {e}", "err")

    def _populate_list(self, data):
        self.job_listbox.delete(0, "end")
        if data == "EMPTY":
            self.job_listbox.insert("end", "  (no jobs available)")
            self.accept_btn.config(state="disabled")
        else:
            for line in data.strip().split("\n"):
                parts = line.split("|", 1)
                if len(parts) == 2:
                    self.job_listbox.insert("end", f"  [{parts[0]}]  {parts[1]}")
            self.accept_btn.config(state="normal")

    def _get_next_job(self):
        """Atomic claim — no race condition."""
        if not self.connected or self.current_job:
            return
        threading.Thread(target=self._do_getjob, daemon=True).start()

    def _do_getjob(self):
        try:
            self.sock.send("GETJOB".encode())
            resp = self.sock.recv(1024).decode()
            if resp == "NO_JOBS":
                self._log("No jobs available.", "muted")
            elif resp.startswith("JOB "):
                parts = resp.split(" ", 2)
                job_id, job_name = parts[1], parts[2]
                self.after(0, lambda: self._start_job(job_id, job_name))
            else:
                self._log(f"Unexpected: {resp}", "err")
        except Exception as e:
            self._log(f"GetJob error: {e}", "err")

    def _accept_selected(self):
        sel = self.job_listbox.curselection()
        if not sel or self.current_job:
            return
        line = self.job_listbox.get(sel[0])
        # parse "[job_id]  job_name"
        import re
        m = re.match(r'\s*\[([^\]]+)\]', line)
        if not m:
            return
        job_id = m.group(1)
        threading.Thread(target=self._do_accept, args=(job_id,), daemon=True).start()

    def _do_accept(self, job_id):
        try:
            self.sock.send(f"ACCEPT {job_id}".encode())
            resp = self.sock.recv(1024).decode()
            if resp.startswith("JOB "):
                parts = resp.split(" ", 2)
                jid, jname = parts[1], parts[2]
                self.after(0, lambda: self._start_job(jid, jname))
            else:
                self._log(f"Accept failed: {resp}", "err")
        except Exception as e:
            self._log(f"Accept error: {e}", "err")

    def _start_job(self, job_id, job_name):
        self.current_job = (job_id, job_name)
        self.current_job_label.config(text=f"[{job_id}]  {job_name}", fg="#e8eaf0")
        self.done_btn.config(state="normal")
        self.accept_btn.config(state="disabled")
        self._log(f"Working on: [{job_id}] {job_name}", "info")
        self._animate_progress()

    def _animate_progress(self):
        self.progress["value"] = 0
        self._progress_step()

    def _progress_step(self):
        if not self.current_job:
            return
        val = self.progress["value"]
        if val < 95:
            self.progress["value"] = val + 1
            self.after(50, self._progress_step)

    def _mark_done(self):
        if not self.current_job or not self.connected:
            return
        job_id, job_name = self.current_job
        threading.Thread(target=self._do_done, args=(job_id, job_name), daemon=True).start()

    def _do_done(self, job_id, job_name):
        try:
            self.sock.send(f"DONE {job_id}".encode())
            resp = self.sock.recv(1024).decode()
            if resp.startswith("COMPLETED"):
                elapsed = resp.split()[-1]
                self._log(f"Completed [{job_id}] {job_name} — total time {elapsed}", "ok")
                self.after(0, self._clear_job)
                self.after(0, self._refresh)
            else:
                self._log(f"Done response: {resp}", "err")
        except Exception as e:
            self._log(f"Done error: {e}", "err")

    def _clear_job(self):
        self.current_job = None
        self.current_job_label.config(text="— none —", fg="#6b7280")
        self.progress["value"] = 100
        self.after(600, lambda: self.progress.config(value=0))
        self.done_btn.config(state="disabled")

    # ── log ──────────────────────────────────────────────────────────────────

    def _log(self, msg, tag="muted"):
        def _write():
            self.log.config(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.log.insert("end", f"[{ts}] {msg}\n", tag)
            self.log.see("end")
            self.log.config(state="disabled")
        self.after(0, _write)


if __name__ == "__main__":
    app = WorkerApp()
    app.mainloop()
