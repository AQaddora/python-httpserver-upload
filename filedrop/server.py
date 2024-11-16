import os
import socket
import subprocess
import json
import qrcode
from qrcode.image.pure import PyPNGImage
from http.server import SimpleHTTPRequestHandler, HTTPServer


# Directory where files will be uploaded
UPLOAD_DIR = 'uploads'
STATIC_DIR = 'static'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Ensure the uploads directory exists
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def get_local_ip():
    """Get the local IP address of the server."""
    if os.name == 'nt':  # If the system is Windows
        try:
            # Run ipconfig command to get network information
            result = subprocess.run('ipconfig', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout

            # Look for 'IPv4 Address' in the output and return the corresponding IP
            for line in output.splitlines():
                if 'IPv4 Address' in line:
                    local_ip = line.split(':')[1].strip()
                    return local_ip
            return "NONE"
        except Exception:
            return "NONE"
    
    else:  # For Linux/macOS/iOS and other Unix-based systems
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))  # This doesn't connect to anything, just to get the local IP address
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "NONE"  # Fallback message
        finally:
            s.close()
        return local_ip


class SimpleHTTPRequestHandlerWithUpload(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to serve the HTML form"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Serve HTML content directly
            html_content = self.get_index_html()
            self.wfile.write(html_content.encode())

        elif self.path == '/style.css':
            # Serve CSS content directly
            css_content = self.get_style_css()
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(css_content.encode())

        elif self.path.startswith('/uploads/'):
            super().do_GET()
        elif self.path == '/get_files':
            # Serve the list of uploaded files as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = os.listdir(UPLOAD_DIR)
            self.wfile.write(json.dumps(files).encode())
        elif self.path == '/get_hostname':
            # Serve the local IP of the server
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            ip_address = get_local_ip()
            self.wfile.write(ip_address.encode())
        elif self.path == '/qr_code.png':
            # Check if QR code was generated successfully
            qr_path = self.generate_qr_code()
            if qr_path and os.path.exists(qr_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(qr_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                # Handle error if QR code wasn't generated
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Error: Failed to generate QR code.")
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to handle file uploads"""
        if self.path == '/upload':
            # Parse the form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Check for the boundary in the form data
            boundary = self.headers.get('Content-Type').split('=')[-1].encode()
            if boundary not in post_data:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Invalid file data")
                return

            files_uploaded = []
            parts = post_data.split(boundary)
            for part in parts:
                if b'filename="' in part:
                    file_data = part.split(b'\r\n\r\n')[1]  # Extract file data after boundary
                    filename = self.get_filename_from_content(part)  # Extract filename
                    if filename:
                        save_path = os.path.join(UPLOAD_DIR, filename)
                        with open(save_path, 'wb') as f:
                            f.write(file_data)
                        files_uploaded.append(filename)

            if files_uploaded:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"{files_uploaded} uploaded successfully!".encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("No file uploaded.".encode())

    def get_filename_from_content(self, content):
        """Extract filename from the uploaded content"""
        boundary = self.headers.get('Content-Type').split('=')[-1]
        filename = None
        if f'filename="' in str(content):
            filename = content.split(b'filename="')[1].split(b'"')[0].decode('utf-8')
        return filename

    def get_index_html(self):
        """Return the HTML content for the index page"""
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FileDrop</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <h1>File Drop</h1>
                <div id="urlContainer">
                    <!-- URL and QR code will be dynamically inserted here -->
                </div>
                <div class="upload-form">
                    <form id="uploadForm" action="/upload" method="POST" enctype="multipart/form-data">
                        <!-- Hidden file input -->
                        <input type="file" name="uploadedfile" id="fileInput" multiple />
                        <!-- Custom button to trigger file input -->
                        <button type="button" id="customUploadButton">Choose Files</button>
                        <input type="submit" value="Upload File" style="display:none;" />
                    </form>
                </div>
                <hr>
                <h2>Available Files</h2>
                <ol id="fileList">
                    <!-- List of uploaded files will be dynamically updated here -->
                </ol>
            </div>

            <script>
                function getServerUrl() {
                    // Fetch the hostname from the server-side response
                    fetch('/get_hostname')
                        .then(response => response.text())
                        .then(hostname => {
                            // Check if a valid hostname is retrieved
                            if (hostname && hostname !== '127.0.0.1' && hostname !== 'NONE') {
                                document.getElementById('urlContainer').style.color = "black";
                                const url = `http://${hostname}:8000`;
                                document.getElementById('urlContainer').innerHTML = `<p>Scan this to access on another device or visit: <a href="#" id="app-url">URL</a></p>
                                    <p>Make sure all devices are on the same network.</p>
                                    <div class="qr-container" id="qr-code">
                                        <!-- QR code will be dynamically inserted here -->
                                    </div>`;
                                // Update the link and QR code
                                document.getElementById('app-url').href = url;
                                document.getElementById('app-url').textContent = url;

                                // Generate QR code for the URL
                                const qrContainer = document.getElementById('qr-code');
                                qrContainer.innerHTML = `<img src="/qr_code.png" alt="QR Code">`;
                            }else{
                                document.getElementById('urlContainer').style.color = "red";
                                document.getElementById('urlContainer').innerHTML = "Error: Could not get the IP address, Go to device's settings";
                            }
                        })
                        .catch(error => {
                            document.getElementById('urlContainer').style.color = "red";
                            document.getElementById('urlContainer').innerHTML = "Error: Could not get the IP address, Go to device's settings";
                        });
                }
                // Fetch the list of uploaded files when the page loads
                window.onload = function () {
                    // Generate the QR code and set the app URL
                    getServerUrl();

                    // Fetch the list of files from the server
                    fetch('/get_files')
                        .then(response => response.json())
                        .then(files => {
                            const fileList = document.getElementById('fileList');
                            files.forEach(file => {
                                let li = document.createElement('li');
                                li.innerHTML = `<a href="/uploads/${file}" download>${file}</a>`;
                                fileList.appendChild(li);
                            });
                        });
                };

                // Handle form submission with AJAX
                document.getElementById('customUploadButton').onclick = function () {
                    // Trigger file input click to select a file
                    document.getElementById('fileInput').click();
                };

                document.getElementById('fileInput').onchange = function (event) {
                    // Automatically submit the form after a file is selected
                    let formData = new FormData(document.getElementById('uploadForm'));
                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                        .then(response => response.text())
                        .then(data => {
                            alert('File uploaded successfully!');
                            // Re-fetch the file list to display the new file
                            fetch('/get_files')
                                .then(response => response.json())
                                .then(files => {
                                    const fileList = document.getElementById('fileList');
                                    fileList.innerHTML = ''; // Clear the existing list
                                    files.forEach(file => {
                                        let li = document.createElement('li');
                                        li.innerHTML = `<a href="/uploads/${file}" download>${file}</a>`;
                                        fileList.appendChild(li);
                                    });
                                });
                        })
                        .catch(error => {
                            alert('File upload failed!');
                        });
                };
            </script>
        </body>
        </html>
        '''

    def get_style_css(self):
        """Return the CSS content for the page"""
        return '''
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f4f4f4;
            color: #333;
        }

        .upload-form {
            width: 100%;
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .upload-form button {
            width: 80%;
            max-width: 300px;
            min-width: 250px;
            margin-bottom: 30px;
        }
        .container {
            max-width: 800px;
            margin: 30px auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        h1, h2, h3 {
            color: #333;
        }

        input[type="file"] {
            display: none; /* Hide the file input */
        }

        .file-input-button {
            background: #007BFF;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            text-align: center;
        }

        .file-input-button:hover {
            background: #0056b3;
        }

        input[type="submit"], button {
            background: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 4px;
        }

        input[type="submit"]:hover, button:hover {
            background: #0056b3;
        }

        a {
            color: #007BFF;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .qr-container {
            align-items: center;
            justify-content: center;
            display: flex;
        }

        img {
            width: 80%;
            max-width: 250px;
        }
        '''

    def generate_qr_code(self):
        """Generate a QR code for the server URL and save it to the root folder as SVG"""
        try:
            url = f"http://{get_local_ip()}:8000"
            img = qrcode.make(url, image_factory=PyPNGImage)
            qr_path = os.path.join(STATIC_DIR, 'qr_code.png')
            img.save(qr_path)
            print(f"QR code generated and saved as SVG at {qr_path}")  # Debugging output
            return qr_path

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None    
# Run the server
def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandlerWithUpload)
    print("Welcome to FileDrop! (v1.0.7)")
    print("Server running on http://localhost:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    main()
