import argparse
import os
import requests
import re
import warnings

# Ignorar avisos relacionados a SSL não verificado
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def fetch_response(url, proxy=None):
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.get(url, proxies=proxies, verify=False)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error: Unable to fetch data from {url}: {e}")
        exit(1)

def extract_tokens(response):
    ca_token = re.search(r'caabcbcdfabcaffac\s*:\s*(\d+)', response)
    bad_token_key = re.search(r'badcbcacacaadc\s*:\s*([\w]+)', response)
    if not ca_token or not bad_token_key:
        print("Error: Unable to extract session tokens.")
        exit(1)

    bad_token_key = bad_token_key.group(1)
    bad_token_value_match = re.search(rf'var\s+{bad_token_key}\s*=\s*\'(.*?)\'', response)
    if not bad_token_value_match:
        print(f"Error: Unable to extract value for {bad_token_key}.")
        exit(1)

    bad_token_value = bad_token_value_match.group(1)
    return ca_token.group(1), bad_token_value

def post_request(url, data, proxy=None):
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.post(url, data=data, proxies=proxies, headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error: Unable to send POST request: {e}")
        exit(1)

def download_file(url, output_path, proxy=None):
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.get(url, proxies=proxies, stream=True, verify=False)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"APK downloaded successfully to: {output_path}")
    except requests.RequestException as e:
        print(f"Error: Failed to download APK: {e}")
        exit(1)

def save_info(info, output_path):
    try:
        with open(output_path, 'w') as f:
            for key, value in info.items():
                f.write(f"{key}: {value}\n")
        print(f"App information saved to: {output_path}")
    except IOError as e:
        print(f"Error: Unable to save app information: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="APK Downloader Script")
    parser.add_argument("-pkg", required=True, help="Package name")
    parser.add_argument("-saveinfo", action="store_true", help="Save app information")
    parser.add_argument("-path", help="Output path for APK and info file")
    parser.add_argument("-proxy", help="Proxy URL (http://proxy:port)")

    args = parser.parse_args()

    base_url = f"https://apps.evozi.com/apk-downloader/?id={args.pkg}"
    response = fetch_response(base_url, args.proxy)

    ca_token, bad_token = extract_tokens(response)

    post_url = "https://api-apk.evozi.com/download"
    post_data = {
        "caabcbcdfabcaffac": ca_token,
        "bbdeafcaaeeddfd": args.pkg,
        "badcbcacacaadc": bad_token,
        "fetch": "false"
    }

    download_response = post_request(post_url, post_data, args.proxy)

    apk_url = download_response.get("url")
    if not apk_url:
        print("Error: Unable to retrieve APK download link.")
        exit(1)

    apk_url = f"https:{apk_url.replace('\\', '')}"

    package_name = download_response.get("packagename", "unknown")
    file_size = download_response.get("filesize", "unknown")
    sha1 = download_response.get("sha1", "unknown")
    version = download_response.get("version", "unknown")
    fetched_at = download_response.get("fetched_at", "unknown")

    # Define a pasta de saída com o nome do pacote
    output_dir = args.path if args.path else "."
    package_dir = os.path.join(output_dir, package_name)
    os.makedirs(package_dir, exist_ok=True)

    # Caminho para salvar o APK e as informações
    apk_output = os.path.join(package_dir, f"{package_name}.apk")
    download_file(apk_url, apk_output, args.proxy)

    if args.saveinfo:
        info_output = os.path.join(package_dir, "info.txt")
        save_info({
            "Package Name": package_name,
            "File Size": file_size,
            "SHA1": sha1,
            "Version": version,
            "Fetched At": fetched_at
        }, info_output)

if __name__ == "__main__":
    main()
