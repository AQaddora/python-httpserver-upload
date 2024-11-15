#!/usr/bin/env python3

import cgitb
cgitb.enable()

import cgi
import os
import socket
import glob
from urllib.parse import quote

REQUEST_METHOD = os.environ.get('REQUEST_METHOD', 'GET')
REQUEST_PORT = os.environ.get("SERVER_PORT", '8000')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, '../uploads')
HTML_TEMPLATE = os.path.join(BASE_DIR, '../static', 'index.html')


# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_file_links():
    """Get a list of downloadable file links."""
    files = glob.glob(f"{UPLOAD_DIR}/*")
    return [
        f'<li><a href="/uploads/{quote(os.path.basename(file))}" download>{os.path.basename(file)}</a></li>'
        for file in files
    ]

def render_page(success_filenames=None):
    """Render the HTML page with the dynamic content."""
    with open(HTML_TEMPLATE, 'r') as f:
        html_content = f.read()

    # Generate links for uploaded files
    file_links = get_file_links()
    file_links_html = "\n".join(file_links) if file_links else "<p>No files uploaded yet.</p>"

    # # Insert the file upload success message if applicable
    # success_message = ""
    # if success_filenames:
    #     uploaded_files = "".join(f"<li>{fname}</li>" for fname in success_filenames)
    #     success_message = f"<h3>Files uploaded successfully:</h3><ul>{uploaded_files}</ul><hr>"

    # Generate QR code
    qr_html = ""
    try:
        import qrcode
        import qrcode.image.svg

        hostname = socket.gethostname().lower()    
        url = f'http://{hostname}:{REQUEST_PORT}/cgi-bin/pyupload.cgi'
        qr = qrcode.make(url)
        qr.save("url-qr.png")
        qr_html = f"""
            <hr>
            <p>Scan to access on another device: <a href="{url}">{url}</a></p>
            <div class="qr-container">
                <img src="../url-qr.png" />
            </div>
        """
    except ImportError:
        qr_html = "<p>QR code generation is not available. Install the `qrcode` library to enable this feature.</p>"

    # Replace placeholders in the template
    # html_content = html_content.replace("{{SUCCESS_MESSAGE}}", success_message)
    html_content = html_content.replace("{{FILE_LINKS}}", file_links_html)
    html_content = html_content.replace("{{QR_CODE}}", qr_html)

    print("Content-Type: text/html")
    print()
    print(html_content)



if REQUEST_METHOD == 'POST':
    # Handle file upload
    form = cgi.FieldStorage()
    files = form['uploadedfile'] if isinstance(form['uploadedfile'], list) else [form['uploadedfile']]

    filenames = []
    for file in files:
        filename = os.path.basename(file.filename)  # Sanitize the filename
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, 'wb') as f:
            f.write(file.file.read())
        filenames.append(filename)

    render_page(success_filenames=filenames)

else:
    # Handle GET request
    render_page()
