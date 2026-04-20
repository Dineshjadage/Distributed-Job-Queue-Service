import socket
import threading
import time
import hashlib
import uuid

# Auth: store only the hash of the secret
RAW_KEY = "SECRET123"
AUTH_HASH = hashlib.sha256(RAW_KEY.encode()).hexdigest()

HOST = "0.0.0.0"
PORT = 5000

# Each job: {"id": uuid, "name": str, "submitted_at": float}
jobs = []
in_progress_jobs = {}   # job_id -> {"name", "started_at", "submitted_at"}
lock = threading.Lock()
job_completion_log = []  # list of dicts for completed jobs

JOB_TIMEOUT = 30  # seconds


# ── helpers ──────────────────────────────────────────────────────────────────

def send_msg(conn, text: str):
    conn.send(text.encode())


def recv_msg(conn) -> str:
    return conn.recv(4096).decode().strip()


def job_list_text():
    if not jobs:
        return "EMPTY"
    lines = [f"{job['id']}|{job['name']}" for job in jobs]
    return "\n".join(lines)


# ── client handler ────────────────────────────────────────────────────────────

def handle_client(conn, addr):
    print(f"[CLIENT] connected: {addr}")
    try:
        while True:
            data = recv_msg(conn)
            if not data:
                break

            if data.startswith("SUBMIT "):
                job_name = data[7:].strip()
                job_id = str(uuid.uuid4())[:8]  # short unique ID
                job = {"id": job_id, "name": job_name, "submitted_at": time.time()}
                with lock:
                    jobs.append(job)
                print(f"[CLIENT] Job added: [{job_id}] {job_name}")
                send_msg(conn, f"OK {job_id}")

            else:
                send_msg(conn, "UNKNOWN COMMAND")
    except Exception as e:
        print(f"[CLIENT] error: {e}")
    finally:
        conn.close()
        print(f"[CLIENT] disconnected: {addr}")


# ── worker handler ────────────────────────────────────────────────────────────

def handle_worker(conn, addr):
    print(f"[WORKER] connected: {addr}")
    try:
        while True:
            command = recv_msg(conn)
            if not command:
                break

            if command == "LIST":
                with lock:
                    send_msg(conn, job_list_text())

            elif command == "GETJOB":
                # Atomic: list + claim in one step — fixes race condition
                with lock:
                    if not jobs:
                        send_msg(conn, "NO_JOBS")
                    else:
                        job = jobs.pop(0)
                        in_progress_jobs[job["id"]] = {
                            "name": job["name"],
                            "started_at": time.time(),
                            "submitted_at": job["submitted_at"],
                        }
                        send_msg(conn, f"JOB {job['id']} {job['name']}")
                        print(f"[WORKER] claimed: [{job['id']}] {job['name']}")

            elif command.startswith("ACCEPT "):
                # Accept by specific ID
                job_id = command.split()[1]
                with lock:
                    idx = next((i for i, j in enumerate(jobs) if j["id"] == job_id), None)
                    if idx is not None:
                        job = jobs.pop(idx)
                        in_progress_jobs[job_id] = {
                            "name": job["name"],
                            "started_at": time.time(),
                            "submitted_at": job["submitted_at"],
                        }
                        send_msg(conn, f"JOB {job_id} {job['name']}")
                        print(f"[WORKER] accepted: [{job_id}] {job['name']}")
                    else:
                        send_msg(conn, "NOT_FOUND")

            elif command.startswith("DONE "):
                job_id = command.split()[1]
                with lock:
                    if job_id in in_progress_jobs:
                        info = in_progress_jobs.pop(job_id)
                        elapsed = round(time.time() - info["submitted_at"], 4)
                        job_completion_log.append({
                            "id": job_id,
                            "name": info["name"],
                            "elapsed": elapsed,
                        })
                        send_msg(conn, f"COMPLETED {job_id} {elapsed}s")
                        print(f"[WORKER] done: [{job_id}] {info['name']} in {elapsed}s")
                    else:
                        send_msg(conn, "NOT_FOUND")

            elif command == "STATUS":
                with lock:
                    pending = len(jobs)
                    in_prog = len(in_progress_jobs)
                    done = len(job_completion_log)
                send_msg(conn, f"PENDING:{pending} IN_PROGRESS:{in_prog} DONE:{done}")

            else:
                send_msg(conn, "UNKNOWN COMMAND")

    except Exception as e:
        print(f"[WORKER] error: {e}")
    finally:
        conn.close()
        print(f"[WORKER] disconnected: {addr}")


# ── timeout monitor ───────────────────────────────────────────────────────────

def monitor_jobs():
    while True:
        time.sleep(5)
        with lock:
            now = time.time()
            to_requeue = [
                jid for jid, info in in_progress_jobs.items()
                if now - info["started_at"] > JOB_TIMEOUT
            ]
            for jid in to_requeue:
                info = in_progress_jobs.pop(jid)
                jobs.append({"id": jid, "name": info["name"], "submitted_at": info["submitted_at"]})
                print(f"[MONITOR] timeout re-queued: [{jid}] {info['name']}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] running on port {PORT}")

    threading.Thread(target=monitor_jobs, daemon=True).start()

    while True:
        conn, addr = s.accept()
        try:
            data = recv_msg(conn)
            parts = data.split()
            if len(parts) != 2:
                send_msg(conn, "BAD HANDSHAKE")
                conn.close()
                continue

            role, key_hash = parts

            # Compare hashes — fixes plaintext auth
            if key_hash != AUTH_HASH:
                send_msg(conn, "AUTH FAILED")
                conn.close()
                print(f"[SERVER] auth failed from {addr}")
                continue

            send_msg(conn, "AUTH OK")

            if role == "CLIENT":
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            elif role == "WORKER":
                threading.Thread(target=handle_worker, args=(conn, addr), daemon=True).start()
            else:
                send_msg(conn, "INVALID ROLE")
                conn.close()

        except Exception as e:
            print(f"[SERVER] handshake error: {e}")
            conn.close()


if __name__ == "__main__":
    main()
