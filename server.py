import socket
import threading
import time

AUTH_KEY = "SECRET123"

HOST = "0.0.0.0"
PORT = 5000

jobs = []
lock = threading.Lock()

job_submission_times = {}
job_completion_times = {}


def send_job_list(conn):
    job_text = "\n".join([f"{i+1}. {job}" for i, job in enumerate(jobs)])

    if job_text == "":
        job_text = "No Jobs Available"

    conn.send(job_text.encode())


def handle_client(conn, addr):

    print("Client connected:", addr)

    while True:
        try:
            job = conn.recv(1024).decode()

            if not job:
                break

            with lock:
                jobs.append(job)
                job_submission_times[job] = time.time()

            print("\nNew Job Added:", job)
            print_jobs()

            conn.send("JOB ADDED".encode())

        except:
            break

    conn.close()
    print("Client disconnected:", addr)


def handle_worker(conn, addr):

    print("Worker connected:", addr)

    while True:
        try:
            command = conn.recv(1024).decode()

            if not command:
                break

            if command == "LIST":

                with lock:
                    send_job_list(conn)

            elif command.startswith("ACCEPT"):

                job_id = int(command.split()[1]) - 1

                with lock:

                    if 0 <= job_id < len(jobs):

                        job = jobs.pop(job_id)

                        start_time = job_submission_times[job]
                        end_time = time.time()

                        completion_time = end_time - start_time
                        job_completion_times[job] = completion_time

                        conn.send(f"JOB ACCEPTED: {job}".encode())

                        print("\nWorker accepted job:", job)
                        print("Completion time:", round(completion_time, 4), "seconds")

                        print_jobs()

                    else:
                        conn.send("INVALID JOB ID".encode())

        except:
            break

    conn.close()
    print("Worker disconnected:", addr)


def print_jobs():

    print("\nCurrent Job List:")

    for i, job in enumerate(jobs):
        print(f"{i+1}. {job}")

    if not jobs:
        print("No Jobs")


def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((HOST, PORT))
    s.listen()

    print("Server running on port", PORT)

    while True:

        conn, addr = s.accept()

        try:
            data = conn.recv(1024).decode()

            role, key = data.split()

            if key != AUTH_KEY:

                conn.send("AUTH FAILED".encode())
                conn.close()

                print("Unauthorized connection from:", addr)

                continue

            if role == "CLIENT":

                threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()

            elif role == "WORKER":

                threading.Thread(
                    target=handle_worker,
                    args=(conn, addr),
                    daemon=True
                ).start()

            else:

                conn.send("INVALID ROLE".encode())
                conn.close()

        except:
            conn.close()


main()