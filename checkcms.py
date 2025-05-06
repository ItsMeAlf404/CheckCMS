import requests
from colorama import Fore, init
import concurrent.futures
import threading
import os

init(autoreset=True)

# Lock untuk akses aman file di thread
lock = threading.Lock()

# Fungsi untuk memeriksa CMS
def check_cms(url):
    url = url.strip()
    if not url:
        return  # Lewati jika domain kosong

    if not url.startswith("http"):
        url = "http://" + url

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=6)
        html = response.text.lower()

        # Cek CMS
        cms = identify_cms(html, url)

        if cms:
            print(Fore.GREEN + f"[{cms}] {url}")
            with lock:
                with open(f"{cms}.txt", "a") as f:
                    f.write(url + "\n")
        else:
            print(Fore.RED + f"[Not Detected] {url}")
            with lock:
                with open("not_detected.txt", "a") as f:
                    f.write(url + "\n")

    except requests.exceptions.RequestException as e:
        with lock:
            print(Fore.YELLOW + f"[Error] {url} => {e}")
            with open("not_detected.txt", "a") as f:
                f.write(f"{url} # Error: {e}\n")

# Fungsi untuk mengidentifikasi CMS berdasarkan HTML
def identify_cms(html, url):
    # Cek WordPress
    if "wp-content" in html or "wp-includes" in html or "/wp-json/" in html:
        return "WordPress"

    # Cek Joomla
    if "joomla" in html or "com_content" in html:
        return "Joomla"

    # Cek Drupal
    if "drupal.js" in html or "/sites/all/modules/" in html:
        return "Drupal"

    # Cek Laravel
    if "/vendor/" in html or "/storage/" in html or "/public/" in html:
        return "Unknown CMS"

    # Cek Magento
    if "magento.js" in html or "/catalog/product/view/" in html:
        return "Magento"

    return None  # Tidak terdeteksi CMS tertentu

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "=== CMS Checker (WordPress, Joomla, Drupal, Laravel, Magento, dll.) ===\n")

    file_name = input(Fore.BLUE + "--> Masukkan nama file list domain: ").strip()

    try:
        with open(file_name, "r") as file:
            domain_list = file.read().splitlines()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(check_cms, domain_list)

    except FileNotFoundError:
        print(Fore.RED + f"File '{file_name}' tidak ditemukan.")
    except Exception as e:
        print(Fore.RED + f"Terjadi kesalahan: {e}")
