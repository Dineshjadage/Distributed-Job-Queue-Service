import socket
import time

HOST = "10.63.228.68"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.send("CLIENT SECRET123".encode())

print("Connected to server")

choice = input("1. Manual Jobs\n2. Generate 100 Jobs\nSelect: ")

if choice == "1":

    while True:

        job = input("Enter Job (or exit): ")

        if job.lower() == "exit":
            break

        s.send(job.encode())

        response = s.recv(1024).decode()

        print("Server:", response)

elif choice == "2":

    start = time.time()

    for i in range(1, 101):

        job = f"JOB_{i}"

        s.send(job.encode())

        s.recv(1024)

    end = time.time()

    print("\n100 Jobs submitted")

    print("Submission Time:", round(end - start, 4), "seconds")

s.close()