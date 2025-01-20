# APK Downloader

A Python script for automating the download of APK files using the Evozi API, with support for saving metadata and organizing downloads into structured directories.

## Features

- Download a single APK by specifying the package name (e.g., `com.example`).
- Process multiple APK downloads from a file containing a list of package names.
- Save app metadata (`packagename`, `filesize`, `sha1`, `version`, `fetched_at`) to a text file.
- Organize APKs and metadata into package-specific directories.

## Requirements

- Python 3.6 or later
- Install the required library:
  ```
  pip install requests
  ```
## Usage

This script allows you to download APKs from the Evozi API, either individually or in bulk, and optionally save metadata about the downloaded apps.

### Download a Single APK
To download an APK by providing its package name:
```
python3 apk_downloader.py com.example
```
To also save the app's metadata (e.g., packagename, filesize, sha1, version, fetched_at) in a text file:
```
python3 apk_downloader.py com.example -saveinfo
```
Download Multiple APKs
To download multiple APKs, create a file (e.g., packages.txt) with one package name per line:
```
python3 apk_downloader.py -list packages.txt -saveinfo
```
