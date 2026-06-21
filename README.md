

https://github.com/user-attachments/assets/11835740-0650-4f9e-9c06-961ce1c7d0e8


# NetFileTransfer

A simple file transfer protocol implemented in Python using **two separate TCP channels**: a control channel for sending commands and a reverse-connection data channel (callback) for the actual file bytes.

The project includes a real-time protocol visualizer that prints a colour-coded sequence diagram in the terminal as the transfer happens.

---

## Protocol architecture

```
  CLIENT (127.0.0.1)                      SERVER (127.0.0.1:9999)
        |                                          |
        |===[ TCP CONNECT :9999 ]================>|   Control channel
        |                                          |
        |---os.listdir()---------------------------->|   Text commands
        |<---['OFFBOUNDS', 'file.txt'] ------------|   Server responses
        |                                          |
        |---upload(OFFBOUNDS\file.txt)------------->|
        |                                          |
  [CLIENT opens listener on port 9998]             |
        |                                          |
        |<========[ DATA CHANNEL :9998 ]==========|   Data channel (callback)
        |<---bytes... bytes... bytes... -----------|   Binary transfer
        |                                          |
```

### Key concepts demonstrated

| Concept | Where |
|---|---|
| TCP client socket | `cftp.py` / `dcftp.py` connecting to port 9999 |
| Text protocol over TCP | Commands like `os.listdir()`, `upload(...)` sent as strings |
| Reverse connection (callback) | Client listens on 9998; server connects back |
| Two independent channels | Control (9999) and data (9998) on separate sockets |
| Binary transfer in chunks | `Upload()` / `Download()` reading 1000 bytes at a time |

---

## Files

```
NetFileTransfer/
├── sftps.py            # Server (control channel + data channel handler)
├── cftp.py             # Upload client
├── dcftp.py            # Download client
├── protocol_logger.py  # Real-time protocol visualizer (sequence diagram)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Installation

### Requirements
- Python 3.8+
- `pip`

### Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `colorama` — terminal colours (Windows / Linux / macOS)
- `tqdm` — progress bar during file transfer

---

## How to run

### 1. Start the server

In one terminal, from inside the `NetFileTransfer/` folder:

```bash
python sftps.py
```

The server listens on port `9999` and handles multiple clients via threads.

### 2. Upload a file

In another terminal, from inside the `NetFileTransfer/` folder:

```bash
python cftp.py
```

The program will:
1. Connect to the server (control channel)
2. Check whether the `OFFBOUNDS` directory exists on the server (and create it if not)
3. Ask for the name of a local file to send
4. Open port `9998` as a listener
5. Send the file to the server through the data channel

### 3. Download a file

```bash
python dcftp.py
```

The program will:
1. Connect to the server (control channel)
2. Ask for a local destination folder
3. Browse the remote files and pick one
4. Open port `9998` as a listener
5. Receive the file from the server through the data channel

---

## Protocol visualizer

When you run either client, the terminal shows a **live sequence diagram**:

```
══════════════════════════════════════════════════════════════════════
      NetFileTransfer  —  Protocol Visualizer  [UPLOAD]
══════════════════════════════════════════════════════════════════════

         CLIENT (127.0.0.1)                    SERVER (127.0.0.1:9999)
        |                                               |
  [+0.001s]  Connecting to 127.0.0.1:9999 ...
        |===[ TCP CONNECT :9999 ]==================>|
        |                                               |
  [+0.002s]  SEND    14B  →  'os.listdir()'
        |---os.listdir()                    ------->|
        |                                               |
  [+2.103s]  RECV    32B  ←  "['OFFBOUNDS']"
        |<--['OFFBOUNDS']                   --------|
        |                                               |
  [+2.104s]  *** Directory 'OFFBOUNDS' found ***
        ...
  [+6.210s]  *** Server connected on data channel :9998 ***
        |<==[ DATA CHANNEL :9998 ]=================|
        |                                               |
  Uploading: 100%|████████████| 4.2kB/4.2kB [00:00<00:00, 5.1kB/s]
```

### Colour guide

| Colour | Meaning |
|---|---|
| Cyan | TCP connection events / phase labels |
| Yellow | Commands sent to the server |
| Green | Responses received from the server |
| Blue | Data channel established |
| Magenta | General phase annotations |

---

## Ports used

| Port | Channel | Direction |
|---|---|---|
| `9999` | Control | Client → Server |
| `9998` | Data (callback) | Server → Client |

Port `9998` uses a **reverse connection**: the client opens the listener and the server connects back to it. This is the opposite of the usual flow and is one of the main concepts this project illustrates.

---

## Course context

This project is part of the **Connectivity and Cyber-Physical Systems** course and is the third hands-on activity in the sequence:

| Activity | Protocol | Main concept |
|---|---|---|
| Assignment 1 | TCP | Stream socket, multiple clients, threads |
| Assignment 2 | UDP | Datagrams, broadcast, connectionless registration |
| Assignment 3 (this) | TCP (two channels) | Control channel + data channel, reverse connection |
