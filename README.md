# 📱 **Local Chat - A Modern Socket-Based Chat Application**

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/language-Python-blue) 
![Platforms](https://img.shields.io/badge/platform-Linux%2C%20Windows%2C%20macOS-orange)
![CustomTkinter](https://img.shields.io/badge/library-CustomTkinter-green)
![Socket](https://img.shields.io/badge/networking-Socket-red)
![Repo Size](https://img.shields.io/github/repo-size/gtrZync/local-chat?color=pink)
![Last Commit](https://img.shields.io/github/last-commit/gtrZync/local-chat?color=ff69b4)

**A school project for Human-Computer Interaction course**  
*Creating a beautiful, modern chat application for local network communication*

</div>

---

## 📖 **About**

**Local Chat** is a desktop chat application designed for two users to communicate over a local network (same PC or LAN). Built as a school project, this application demonstrates socket programming, modern GUI design, and client-server architecture.

The application features a **phone-inspired UI design** using CustomTkinter, providing a modern and intuitive user experience. While functional for educational purposes, this is **non-production ready code** - perfect for learning and experimentation!

---

## **Features**

- 🔐 **User Authentication** - Login/signup system with phone number and username
- 💬 **Real-time Messaging** - Socket-based communication between clients with instant delivery
- 📱 **Modern UI** - Phone-inspired design with CustomTkinter
- 🎨 **Beautiful Interface** - Clean, modern aesthetic with custom fonts and icons
- 🔄 **Multi-threaded** - Non-blocking UI with background network operations
- 💾 **Message Persistence** - All messages saved to JSON database with timestamps
- 📜 **Conversation History** - Load and display past messages when opening chats
- 👥 **Auto-Contact Discovery** - Connected users automatically appear in each other's contact lists
- 🖱️ **Draggable App Icon** - Drag the app icon on the home screen for a playful experience
- 🎯 **GUI Event System** - Thread-safe UI updates via server-sent GUI events
- 🌐 **Local Network Support** - Works on same PC or local network

---

## 🛠️ **Tech Stack**

| Component | Technology |
|-----------|-----------|
| **GUI Framework** | CustomTkinter |
| **Networking** | Python Sockets (TCP/IP) |
| **Data Storage** | JSON (local database) |
| **Console Output** | Rich (beautiful terminal output) |
| **Language** | Python 3.x |

---

##  **Installation**

### Prerequisites

- Python 3.8 or higher
- pip 

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/gtRZync/local-chat.git
   cd local-chat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python --version
   pip list
   ```

---

##  **Usage**

### **Step 1: Start the Server**

The server must be running before clients can connect. Open a terminal and run:

```bash
# From the project root directory
python -m local_chat.server.server
```

**Or alternatively:**
```bash
python local_chat/server/server.py
```

You should see:
```
╭─────────────────────────────────╮
│ SERVER                          │
├─────────────────────────────────┤
│ Server started                  │
│ 0.0.0.0:5423                    │
╰─────────────────────────────────╯
```

>[!NOTE] 
>The server runs on `localhost:5423` by default. Keep this terminal open while using the application.
---

### **Step 2: Launch the Client Application**

Open a **new terminal** (keep the server running) and start the client:

```bash
# From the project root directory
python main.py
```

A window with a phone-like interface will appear!

---

### **Step 3: Using the Application**

#### **First Time Setup**

1. **Click the Chat icon** on the home screen
2. **Enter your details:**
   - Phone number (10 digits) (I chose my country's format: **0694 XXX XXX**)
   - Username (minimum 3 characters)
3. **Click Continue**
   - If you're a new user, an account will be created automatically
   - If you're an existing user, you'll be logged in

#### **Chatting**

1. After login, you'll see the **Chat List** view
   - Connected users automatically appear in your contact list
   - Contacts are loaded from your conversation history
2. **Select a contact** to open the conversation
   - Past messages are automatically loaded and displayed
   - Messages are sorted chronologically
3. **Type your message** and click the send button
   - Messages appear in real-time!
   - Sent messages appear on the right (blue), received on the left (gray)
   - All messages are automatically saved to the database
4. **Navigate back** using the back arrow to return to the chat list

#### **Home Screen Features**

- **Drag the Chat icon** - Click and drag the app icon around the home screen
- **Click the icon** - Tap (without dragging) to launch the chat app
- **Live clock** - Real-time clock display on the home screen

---

## 📸 **Screenshots**

### **Home Screen**
<div align="center">

*Screenshot placeholder - Beautiful phone-inspired home screen with clock and app icon*

</div>

---

### **Login View**
<div align="center">

*Screenshot placeholder - Clean login interface with phone number and username fields*

</div>

---

### **Chat List View**
<div align="center">

*Screenshot placeholder - Chat list showing available contacts*

</div>

---

### **Conversation View**
<div align="center">

*Screenshot placeholder - Active chat conversation interface*

</div>

---

## 📁 **Project Structure**

```
local-chat/
├── assets/                 # UI assets (images, fonts, icons)
│   ├── background/        # Background images
│   ├── font/             # Custom fonts (SF Pro)
│   ├── icon/             # Application icons
│   └── model/            # UI mockups/screenshots
├── data/                  # Data storage
│   └── database.json     # User accounts, conversations, and message history
├── local_chat/
│   ├── app/              # Main application (client GUI)
│   │   └── app.py       # Entry point for client
│   ├── server/           # Server implementation
│   │   └── server.py     # Entry point for server
│   ├── client/           # Client networking
│   ├── command/          # Business logic (auth, data)
│   ├── config/           # Configuration files
│   ├── gui/              # GUI components
│   │   ├── views/        # Different UI views
│   │   └── widgets/      # Reusable UI widgets
│   └── utils/            # Utility functions
├── main.py               # (Optional entry point)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🔧 **Configuration**

### **Server Configuration**

Default server settings (in `local_chat/server/server.py`):
- **Host:** `0.0.0.0` (accepts connections from any interface)
- **Port:** `5423`

To change these, modify the `Server` class initialization:
```python
server = Server(host='localhost', port=5423)
```

### **Client Configuration**

Default client settings (in `local_chat/app/app.py`):
- **Host:** `localhost`
- **Port:** `5423`

To connect to a different server, modify the `Address` in `__on_login_success()`:
```python
address=Address(host='192.168.1.100', port=5423)  # Example: different PC on LAN
```
---

## 🎓 **Educational Purpose**

This project was created for a **Human-Computer Interaction** course assignment. It demonstrates:

- [x] Socket programming (TCP/IP)
- [x] Client-server architecture
- [x] Multi-threaded applications
- [x] Modern GUI design principles
- [x] User authentication systems
- [x] Real-time communication
- [x] Data persistence (JSON database)
- [x] Thread-safe GUI updates
- [x] Event-driven architecture

---

## ⚠️ **Important Notes**

### **Non-Production Ready**

This code is **NOT production-ready** and is intended for educational purposes:

- ❌ No encryption or security measures
- ❌ No error recovery mechanisms
- ❌ Limited scalability (designed for 2 users)
- ❌ Basic error handling
- ❌ No input validation in many areas
- ❌ No message encryption
- ❌ No user blocking/reporting features

### **Known Limitations**

- Server must be running before clients connect
- Only supports 2 users chatting at a time
- No file sharing capabilities
- No emoji/sticker support (yet (if im not lazy))
- Basic authentication (no password)
- Messages are saved but not encrypted
- No message search functionality
- No group chats (1-on-1 only)

---

## **Troubleshooting**

### **Server won't start**
- Check if port `5423` is already in use
- Try changing the port in server configuration
- Ensure you have proper network permissions

### **Client can't connect**
- Verify server is running
- Check firewall settings
- Ensure correct host/port configuration
- Try `localhost` instead of IP address

### **UI freezes**
- Check console for error messages

### **Messages not appearing**
- Verify both users are logged in
- Check server console for connection status
- Ensure correct `receiver_user_id` is used
- Check if messages are being saved to `data/database.json`

### **Contacts not showing up**
- Ensure both users are connected to the server
- Contacts appear automatically when users connect
- Check `data/database.json` for conversation entries
- Try refreshing the chat list view

### **Message history not loading**
- Verify conversation exists in `data/database.json`
- Check that messages array contains message objects
- Ensure timestamps are in correct format: `YYYY-MM-DDTHH:MM:SS`

---

## 📝 **Development**

### **Adding Features**

The codebase is structured for easy extension:
- Add new views in `local_chat/gui/views/`
- Modify server logic in `local_chat/server/server.py`
- Update client behavior in `local_chat/client/client.py`

---

## 👥 **Contributors**

- **Developer:** Myson Dio
- **Course:** Human-Computer Interaction
- **Institution:** University of French Guiana

---

## **Acknowledgments**

- **CustomTkinter** - For the beautiful modern UI framework
- **Rich** - For elegant terminal output
- **SF Pro Font** - For the iOS-inspired typography
- **Python Socket Library** - For networking capabilities

---

<div align="center">

*"Connecting people, one socket at a time"*

</div>

<p align="center"><a href="https://github.com/catppuccin/catppuccin/blob/main/LICENSE"><img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=MIT&colorA=363a4f&colorB=b7bdf8"/></a></p>
