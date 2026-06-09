import requests
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 5
print_lock = threading.Lock()
write_lock = threading.Lock()


def tsprint(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def append_output(path, line):
    with write_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def check_server(server, verbose=False):
    base = f"http://{server}"

    if verbose:
        tsprint(f"[*] {server}   connecting to root...")

    try:
        requests.get(base, timeout=TIMEOUT)
    except Exception as e:
        if verbose:
            tsprint(f"[-] {server}   root check FAILED   ({e})")
        return None

    if verbose:
        tsprint(f"[+] {server}   root OK,  fetching /api/tags...")

    try:
        r = requests.get(f"{base}/api/tags", timeout=TIMEOUT)
        if r.ok:
            models = [m["name"] for m in r.json().get("models", [])]
            if models:
                if verbose:
                    tsprint(f"[✓] {server}   found {len(models)} model(s):  {', '.join(models)}")
            else:
                if verbose:
                    tsprint(f"[-] {server}   /api/tags returned 0 models")
                return None
        else:
            if verbose:
                tsprint(f"[-] {server}   /api/tags returned HTTP {r.status_code}")
            return None
    except Exception as e:
        if verbose:
            tsprint(f"[-] {server}   /api/tags FAILED   ({e})")
        return None

    if verbose:
        tsprint(f"[*] {server}   testing generation (auth check)...")

    auth_free_models = []
    for model in models:
        try:
            gr = requests.post(
                f"{base}/api/generate",
                json={"model": model, "prompt": "hi", "stream": False},
                timeout=TIMEOUT + 5,
            )
            if gr.status_code == 401 or gr.status_code == 403:
                if verbose:
                    tsprint(f"[-] {server}   model '{model}' requires auth (HTTP {gr.status_code})")
                continue
            if not gr.ok:
                if verbose:
                    tsprint(f"[-] {server}   model '{model}' generation failed (HTTP {gr.status_code})")
                continue
            auth_free_models.append(model)
            if verbose:
                tsprint(f"[✓] {server}   model '{model}' passed auth check")
        except Exception as e:
            if verbose:
                tsprint(f"[-] {server}   model '{model}' generation FAILED ({e})")
            continue

    if auth_free_models:
        return auth_free_models

    if verbose:
        tsprint(f"[-] {server}   no auth-free models")
    return None


def main():
    parser = argparse.ArgumentParser(description="Ollama server scanner")
    parser.add_argument("-i", "--input", required=True, help="Input file with ip:port per line")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Thread count")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show checking process step-by-step")
    args = parser.parse_args()

    with open(args.input) as f:
        servers = [line.strip() for line in f if line.strip()]

    total = len(servers)
    found_count = 0
    checked_count = 0

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check_server, s, args.verbose): s for s in servers}
        for future in as_completed(futures):
            server = futures[future]
            models = future.result()
            checked_count += 1

            if models:
                found_count += 1
                line = f"{server} -> {', '.join(models)}"
                append_output(args.output, line)
                tsprint(f"[{checked_count}/{total}] {server} -> {', '.join(models)}")
            else:
                if not args.verbose:
                    tsprint(f"[{checked_count}/{total}] [-] {server}")
                else:
                    tsprint(f"[{checked_count}/{total}] [-] {server}   no models")

    print(f"\nDone. {found_count} server(s) with models found out of {total} checked.")


if __name__ == "__main__":
    main()

