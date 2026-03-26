# 🚀 Distributed Job Queue Service (TCP-Based)

## 📌 Overview

This project implements a **Distributed Job Queue Service** using **TCP sockets in Python**.
It follows a **Client–Server–Worker architecture**, where:

* **Clients** submit jobs to the server
* **Server** manages the job queue and distributes tasks
* **Workers** fetch and execute jobs

The system also measures **performance metrics** like:

* Job submission time
* Job selection time
* Job completion time

---

## 🏗️ Architecture

```
Client(s)  --->  Server  --->  Worker(s)
                (Queue Manager)
```

---

## 📂 Project Structure

* `server.py` → Main server handling clients & workers 
* `client.py` → Client for submitting jobs 
* `worker.py` → Worker for fetching and processing jobs 

---

## ⚙️ Features

* Multi-client job submission
* Multi-worker job processing
* Thread-safe job queue (using locks)
* Authentication system (`SECRET123`)
* Performance evaluation (time tracking)
* TCP socket-based communication

---

## 🛠️ Requirements

* Python 3.x
* No external libraries required (uses built-in modules)

---

## 💻 Installation & Setup

### 🔹 Step 1: Clone the Repository

```bash
git clone https://github.com/Dineshjadage/Distributed-Job-Queue-Service.git
cd Distributed-Job-Queue-Service
```

---

### 🔹 Step 2: Update IP Address

In all files (`server.py`, `client.py`, `worker.py`), update:

```python
HOST = "YOUR_IP_ADDRESS"
```

👉 For same system:

```python
HOST = "127.0.0.1"
```

---

## 🚀 How to Run (Windows / Mac)

### 🖥️ 1. Start Server

```bash
python server.py
```

Output:

```
Server running on port 5000
```

---

### 👤 2. Run Client

```bash
python client.py
```

Options:

* Manual job entry
* Auto-generate 100 jobs

---

### ⚙️ 3. Run Worker(s)

```bash
python worker.py
```

Menu:

```
1. Show Jobs
2. Accept Job
3. Exit
```

👉 You can run multiple workers in different terminals

---

## 📊 Performance Metrics

The system measures:

* ⏱️ Job submission time (client side)
* ⏱️ Job fetching time (worker side)
* ⏱️ Job completion time (server side)

Example output:

```
Time to fetch jobs: 0.0023 seconds
Job selection time: 0.0018 seconds
Completion time: 0.0045 seconds
```

---

## 🔐 Authentication

* Clients and workers must send:

```
CLIENT SECRET123
WORKER SECRET123
```

* Unauthorized access is rejected

---

## ⚠️ Notes

* Ensure server is running before client/worker
* Use same IP & port across all files
* Firewall/network settings may affect connectivity

---

## 🎯 Future Improvements

* Job priority scheduling
* Load balancing
* Fault tolerance
* Distributed deployment across multiple machines

---

## 👨‍💻 Author

**Dinesh Ashok Jadage**

---

## 📜 License

This project is for academic and learning purposes.
