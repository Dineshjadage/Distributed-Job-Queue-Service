# 🚀 Distributed Job Queue System (TCP-Based)

**Developed by: Dinesh Jadage**

A multi-client, multi-worker distributed job queue system built using Python sockets and threading. This project simulates how job scheduling and processing systems work in real-world distributed environments.

---

## 📌 Features

- 🔐 Secure authentication using SHA-256 hashing  
- 🧑‍💻 Multiple clients can submit jobs concurrently  
- ⚙️ Multiple workers can process jobs in parallel  
- 📊 Real-time job status tracking (Pending / In Progress / Completed)  
- ⏱ Automatic job timeout handling & re-queuing  
- 🖥 GUI-based Client and Worker applications (Tkinter)  
- 🚀 Bulk job submission support  

---

## 🏗 System Architecture

        +-----------+        +-----------+
        |  Client   | -----> |           |
        | (GUI App) |        |           |
        +-----------+        |           |
                             |  Server   | -----> Workers
        +-----------+        |           |        (GUI Apps)
        |  Client   | -----> |           |
        +-----------+        +-----------+

---

## 📂 Project Structure

├── server.py        # Central job queue server  
├── client.py        # GUI client for submitting jobs  
├── worker.py        # GUI worker for processing jobs  

---

## ⚙️ Technologies Used

- Python 3  
- Socket Programming (TCP)  
- Multithreading  
- Tkinter (GUI)  
- UUID (Job IDs)  
- Hashlib (Authentication Security)  

---

## 🔐 Authentication

- Uses SHA-256 hashing  
- Shared secret key: `SECRET123`  
- Both client and worker must authenticate before communication  

---

## 🚀 How to Run the Project

### 1️⃣ Clone Repository

git clone https://github.com/your-username/job-queue-system.git  
cd job-queue-system  

---

### 2️⃣ Start Server

python server.py  

---

### 3️⃣ Run Client (Job Submission)

python client.py  

- Host: 127.0.0.1  
- Port: 5000  

---

### 4️⃣ Run Worker (Job Processing)

python worker.py  

---

## 🔄 Workflow

1. Client submits job → Server stores it  
2. Worker requests job → Server assigns job  
3. Worker processes job → Marks DONE  
4. Server logs completion time  

---

## 🧠 Key Concepts

- Producer-Consumer Model  
- Distributed Systems  
- Thread Synchronization  
- Socket Communication  
- Fault Tolerance  

---

## 👨‍💻 Author

Dinesh Jadage  
GitHub: https://github.com/Dineshjadage  
LinkedIn: https://www.linkedin.com/in/dinesh-jadage-b4ba5a320/
