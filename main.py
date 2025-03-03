# Author: Scott Grivner
# Website: scottgrivner.dev
# Abstract: Scrape a web page for PDF files and download them all locally.

# Import Modules
import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Define your URL
url = "https://yourWebsiteURL"

# If there is no such folder, the script will create one automatically
folder_location = r'./downloads'
if not os.path.exists(folder_location):
    os.mkdir(folder_location)

# Fetch page content
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# List to store downloaded PDF filenames
downloaded_pdfs = []
pdf_count = 1  # Counter for unnamed PDFs

def get_unique_filename(folder, filename):
    """Ensures filename is unique by appending a number if the file already exists."""
    base, ext = os.path.splitext(filename)
    counter = 2  # Start numbering at (2) if a duplicate is found

    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base} ({counter}){ext}"
        counter += 1

    return os.path.join(folder, new_filename)

def get_pdf_filename(pdf_url):
    """Extracts filename from URL or generates a default one if missing."""
    global pdf_count
    parsed_url = urlparse(pdf_url)
    filename = os.path.basename(parsed_url.path)
    
    # Assign a default name if the filename is missing
    if not filename or "." not in filename:
        filename = f"Downloaded_PDF_{pdf_count}.pdf"
        pdf_count += 1
    
    return get_unique_filename(folder_location, filename)

# Find all <a> links ending in .pdf
for link in soup.select("a[href$='.pdf']"):
    pdf_url = urljoin(url, link['href'])
    filename = get_pdf_filename(pdf_url)

    try:
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            downloaded_pdfs.append(filename)
            print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")

# Find PDFs embedded in `data-pdf` attributes inside <main> tags
for main_tag in soup.find_all("main", class_="pdf-document"):
    pdf_url = main_tag.get("data-pdf")
    if pdf_url:
        pdf_url = urljoin(url, pdf_url)  # Ensure full URL
        filename = get_pdf_filename(pdf_url)

        try:
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(pdf_response.content)
                downloaded_pdfs.append(filename)
                print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download {pdf_url}: {e}")

# Summary Output
if downloaded_pdfs:
    print(f"\n{len(downloaded_pdfs)} PDF file(s) downloaded.")
else:
    print("\nNo PDF files downloaded.")
