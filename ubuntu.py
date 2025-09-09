import requests
import os
import hashlib
from urllib.parse import urlparse
from PIL import Image

# Allowed extensions and max size
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
DOWNLOAD_DIR = "Fetched_Images"

# Track downloaded image hashes to prevent duplicates
downloaded_hashes = set()

def sanitize_filename(filename, url):
    """Ensure safe filename with extension fallback."""
    if not filename or "." not in filename:
        filename = f"downloaded_{hash(url)}.jpg"
    return filename

def get_file_hash(filepath):
    """Generate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def is_safe_image(filepath):
    """Check if file is a valid image using Pillow."""
    try:
        with Image.open(filepath) as img:
            img.verify()  # Verify the image integrity
        return True
    except (OSError):
        return False

def fetch_image(url):
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # Request with streaming
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        # --- Security checks via headers ---
        content_type = response.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            print(f"✗ Skipped (not an image): {url}")
            return

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            print(f"✗ Skipped (file too large): {url}")
            return

        # Extract and sanitize filename
        parsed_url = urlparse(url)
        filename = sanitize_filename(os.path.basename(parsed_url.path), url)
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # Download file with size check
        size = 0
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    f.close()
                    os.remove(filepath)
                    print(f"✗ Skipped (exceeded size limit): {filename}")
                    return
                f.write(chunk)

        # Validate as real image
        if not is_safe_image(filepath):
            os.remove(filepath)
            print(f"✗ Skipped (invalid or corrupted image): {filename}")
            return

        # Check duplicates (hash comparison)
        file_hash = get_file_hash(filepath)
        if file_hash in downloaded_hashes:
            os.remove(filepath)
            print(f"✗ Skipped (duplicate image): {filename}")
            return
        downloaded_hashes.add(file_hash)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except Exception as e:
        print(f"✗ Error for {url}: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for safely collecting images from the web\n")

    urls = input("Please enter image URLs (separate with spaces): ").split()

    if not urls:
        print("✗ No URLs provided. Exiting.")
        return

    for url in urls:
        fetch_image(url)

    print("\n✓ All tasks completed. Stay safe online.")

if __name__ == "__main__":
    main()






# import requests
# import os
# import hashlib
# from PIL import Image
# from urllib.parse import urlparse

# # Allowed extensions and max size
# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
# MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
# DOWNLOAD_DIR = "Fetched_Images"

# # Keep track of downloaded file hashes to prevent duplicates
# downloaded_hashes = set()

# def get_filename(filename, url):
#     """Ensure safe filename with extension fallback."""
#     if not filename or "." not in filename:
#         filename = f"downloaded_{hash(url)}.jpg"
#     return filename

# def get_hash(filepath):
#     """Generate SHA256 hash of a file."""
#     sha256 = hashlib.sha256()
#     with open(filepath, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             sha256.update(chunk)
#     return sha256.hexdigest()

# def is_safe_image(filepath):
#     """Check if file is actually a valid image."""
#     try:
#         with Image.open(filepath) as img:
#             return img.format.lower() in {"jpeg", "png", "gif"}
#     except Exception:
#         return False

# def fetch_image(url):
#     try:
#         os.makedirs(DOWNLOAD_DIR, exist_ok=True)

#         # Request with streaming
#         response = requests.get(url, timeout=10, stream=True)
#         response.raise_for_status()

#         # --- Security checks via headers ---
#         content_type = response.headers.get("Content-Type", "").lower()
#         if not content_type.startswith("image/"):
#             print(f"✗ Skipped (not an image): {url}")
#             return

#         content_length = response.headers.get("Content-Length")
#         if content_length and int(content_length) > MAX_FILE_SIZE:
#             print(f"✗ Skipped (file too large): {url}")
#             return

#         # Extract and sanitize filename
#         parsed_url = urlparse(url)
#         filename = get_filename(os.path.basename(parsed_url.path), url)
#         filepath = os.path.join(DOWNLOAD_DIR, filename)

#         # Download file with size check
#         size = 0
#         with open(filepath, "wb") as f:
#             for chunk in response.iter_content(1024):
#                 size += len(chunk)
#                 if size > MAX_FILE_SIZE:
#                     f.close()
#                     os.remove(filepath)
#                     print(f"✗ Skipped (exceeded size limit): {filename}")
#                     return
#                 f.write(chunk)

#         # Validate as image
#         if not is_safe_image(filepath):
#             os.remove(filepath)
#             print(f"✗ Skipped (invalid image format): {filename}")
#             return

#         # Check duplicates (hash comparison)
#         file_hash = get_hash(filepath)
#         if file_hash in downloaded_hashes:
#             os.remove(filepath)
#             print(f"✗ Skipped (duplicate image): {filename}")
#             return
#         downloaded_hashes.add(file_hash)

#         print(f"✓ Successfully fetched: {filename}")
#         print(f"✓ Image saved to {filepath}")

#     except requests.exceptions.RequestException as e:
#         print(f"✗ Connection error for {url}: {e}")
#     except Exception as e:
#         print(f"✗ Error for {url}: {e}")

# def main():
#     print("Welcome to the Ubuntu Image Fetcher")
#     print("A tool for safely collecting images from the web\n")

#     urls = input("Please enter image URLs (separate with spaces): ").split()

#     if not urls:
#         print("✗ No URLs provided. Exiting.")
#         return

#     for url in urls:
#         fetch_image(url)

#     print("\n✓ All tasks completed. Stay safe online.")

# if __name__ == "__main__":
#     main()
