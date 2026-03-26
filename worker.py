import socket
import time

HOST = "10.63.228.68"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.send("WORKER SECRET123".encode())

while True:

    print("\n1. Show Jobs")
    print("2. Accept Job")
    print("3. Exit")

    choice = input("Select: ")

    if choice == "1":

        start = time.time()

        s.send("LIST".encode())

        jobs = s.recv(4096).decode()

        end = time.time()

        print("\nAvailable Jobs:")
        print(jobs)

        print("Time to fetch jobs:", round(end - start, 4), "seconds")

    elif choice == "2":

        job_id = input("Enter job number: ")

        start = time.time()

        s.send(f"ACCEPT {job_id}".encode())

        response = s.recv(1024).decode()

        end = time.time()

        print(response)

        print("Job selection time:", round(end - start, 4), "seconds")

    elif choice == "3":
        break

s.close()