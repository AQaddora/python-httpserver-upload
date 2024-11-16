# FileDrop - Simple File Sharing Server

**FileDrop** is a simple server that allows users on the same local network to easily upload and download files through a web interface. It also generates a QR code for quick access to the server URL from any device on the same network.

### Key Features:
- **File Sharing**: Upload and download files through a simple web interface.
- **QR Code Generation**: Dynamically generates a QR code for easy access to the server.
- **Local Network Only**: Works across multiple devices connected to the same local network.
- **Cross-Platform**: Use on **macOS**, **Linux**, and **iOS** via **A-Shell Mini** or **A-Shell**.

### Requirements:
- Python 3.x
- **Install via pip**:
   ```bash
   pip install filedrop
   ```

   This will install all required dependencies, including the **qrcode** library for QR code generation.

### Usage on iOS (A-Shell Mini):

1. **Install A-Shell Mini**: Install **A-Shell Mini** or **A-Shell** from the App Store.
2. **Install the Python Package**:
   - Open **A-Shell** or **A-Shell Mini**.
   - Install **FileDrop** by running:
     ```bash
     pip install filedrop
     ```
3. **Run the Server**:
   - After installation, run the server with:
     ```bash
     python3 -m filedrop
     ```
4. **Access the Server**: Open **Safari** on your iOS device and go to `http://localhost:8000`.

### Usage on macOS/Linux:

1. **Install FileDrop**:
   - Install **FileDrop** via pip:
     ```bash
     pip install filedrop
     ```

2. **Run the Server**:
   - After installation, run the server with:
     ```bash
     python3 -m filedrop
     ```
3. **Access the Server**: Open your browser and go to `http://localhost:8000`.

4. **Optional: Create a Shortcut (for macOS)**:
   - You can create a shortcut to automatically run the server and open the browser.
   - A **Shortcuts app** shortcut may be provided in future updates.

### How it Works:
- Once the server is running, you can access the web interface at `http://localhost:8000`.
- You can upload files through the web interface.
- Files are stored in a shared directory, and anyone on the same local network can download them.
- The server generates a QR code that you can scan to easily open the server's web interface on another device.

### Important Notes:
- **Local Network**: All devices must be connected to the same **local network**.
- **Recommendation**: Use a **5G network** for faster file transfers between devices.

### Contribution:

We welcome contributions to improve this project! If you’d like to contribute, you can help with:

- Improving the codebase.
- Enhancing cross-platform support (especially Windows support).
- Creating a shortcut for automatic setup and execution on iOS.
- Adding features or improving documentation.

To contribute, please fork this repository, make your changes, and submit a pull request. We appreciate your contributions!

### TODO:
- **Windows Support**: Currently, the server does not support Windows. Contributions to support Windows are welcome.
- **Automatic Shortcut**: A shortcut that automatically downloads the bundled server and opens it when the app is launched.
- **Other Enhancements**: Feel free to propose new features or improvements.

### Troubleshooting:
- Ensure that all devices are connected to the **same local network** for proper communication.

### Future Updates:
- Additional features and fixes may be added based on feedback and contributions from the community.

Feel free to use this simple file-sharing server as needed. Enjoy sharing files easily across your local network!