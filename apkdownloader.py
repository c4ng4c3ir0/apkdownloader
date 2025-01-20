import os
import sys
import argparse
import requests

def download_apk(package_name, saveinfo, path):
    url = "https://api-apk.evozi.com/download"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://apps.evozi.com",
        "Referer": "https://apps.evozi.com/",
    }
    data = {
        "caabcbcdfabcaffac": "1737348414",
        "bbdeafcaaeeddfd": package_name,
        "badcbcacacaadc": "UBQGe7U86onw2D22x37HjQ",
        "fetch": "false",
    }

    print(f"Fetching download link for {package_name}...")
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"Failed to fetch APK information for {package_name}: HTTP {response.status_code}")
        return False

    response_data = response.json()
    if response_data.get("status") != "success" or not response_data.get("url"):
        print(f"Error: Unable to download APK for {package_name}. The link was not provided.")
        return False

    apk_url = "https:" + response_data["url"].replace("\\", "")
    app_info = {
        "packagename": response_data.get("packagename"),
        "filesize": response_data.get("filesize"),
        "sha1": response_data.get("sha1"),
        "version": response_data.get("version"),
        "fetched_at": response_data.get("fetched_at"),
    }

    package_dir = path if path else package_name
    os.makedirs(package_dir, exist_ok=True)

    apk_path = os.path.join(package_dir, f"{package_name}.apk")

    print(f"Downloading APK to {apk_path}...")
    apk_response = requests.get(apk_url, stream=True)
    if apk_response.status_code == 200:
        with open(apk_path, "wb") as apk_file:
            for chunk in apk_response.iter_content(chunk_size=1024):
                apk_file.write(chunk)
        print(f"APK downloaded successfully to {apk_path}")
    else:
        print(f"Error: Failed to download APK for {package_name}.")
        return False

    if saveinfo:
        info_path = os.path.join(package_dir, "info.txt")
        print(f"Saving app information to {info_path}...")
        with open(info_path, "w") as info_file:
            for key, value in app_info.items():
                info_file.write(f"{key}: {value}\n")
        print("App information saved successfully.")

    return True

def process_package_list(file_path, saveinfo, path):
    if not os.path.isfile(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    with open(file_path, "r") as f:
        packages = [line.strip() for line in f if line.strip()]

    for package_name in packages:
        print(f"Processing package: {package_name}")
        success = download_apk(package_name, saveinfo, path)
        if not success:
            print(f"Failed to process package: {package_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APK Downloader Script")
    parser.add_argument("package_name", nargs="?", help="Package name of the app (e.g., com.example)")
    parser.add_argument("-list", help="Path to a file containing a list of package names, one per line")
    parser.add_argument("-saveinfo", action="store_true", help="Save app information to a file")
    parser.add_argument("-path", help="Base path to save the APK and app information", default=None)

    args = parser.parse_args()

    if args.list:
        process_package_list(args.list, args.saveinfo, args.path)
    elif args.package_name:
        download_apk(args.package_name, args.saveinfo, args.path)
    else:
        print("Error: You must provide either a package name or a list of package names.")
        sys.exit(1)
