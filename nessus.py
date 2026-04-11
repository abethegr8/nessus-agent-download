#!/usr/bin/env python3
"""
Query the Tenable Downloads API v1 to find the latest
Nessus Agent download URL for Windows Server (x64).

API endpoint:
  https://www.tenable.com/downloads/api/v1/public/pages/nessus-agents

The JSON response structure looks like this (simplified):
{
    "id": 61,
    "title": "Tenable Nessus Agent",
    "products": {
        "plugins-archive": { ... },          <-- not a versioned agent, skip
        "signing-keys": { ... },             <-- not a versioned agent, skip
        "nessus-agents-11.1.2": {            <-- latest version (what we want)
            "product_name": "Nessus Agents - 11.1.2",
            "version": "11.1.2",
            "downloads": [
                {
                    "id": 27831,             <-- unique download ID (used to build URL)
                    "file": "NessusAgent-11.1.2-arm64.msi",   <-- ARM, skip
                    "description": "Windows 11 (Arm 64-bit)",
                    "meta_data": { "sha256": "...", "version": "11.1.2", ... }
                },
                {
                    "id": 27830,
                    "file": "NessusAgent-11.1.2-x64.msi",     <-- this is what we want
                    "description": "Windows Server 2012, ... (x86 64-bit)",
                    "meta_data": { "sha256": "...", "version": "11.1.2", ... }
                },
                { ... more downloads for Linux, macOS, etc. }
            ]
        },
        "nessus-agents-11.0.4": { ... }      <-- older version, skip
    }
}
"""

# ── Imports ──────────────────────────────────────────────────────────
# json          - parse the JSON response body into a Python dictionary
# sys           - lets us exit with an error code and write to stderr
# urllib.request - make HTTP requests (built into Python, no pip install needed)
# urllib.error   - catch HTTP errors like timeouts or 404s
import json
import sys
import urllib.request
import urllib.error

# ── Constants ────────────────────────────────────────────────────────
# The base API URL that returns the full JSON listing of all Nessus Agent downloads.
API_URL = "https://www.tenable.com/downloads/api/v1/public/pages/nessus-agents"

# The download URL template.  We plug in the download ID we find from the API.
# The {download_id} placeholder gets replaced with the actual numeric ID
# using Python's str.format() method later in the script.
#
# Example final URL:
#   https://www.tenable.com/.../downloads/27830/download?i_agree_to_tenable_license_agreement=true
DOWNLOAD_TEMPLATE = (
    "https://www.tenable.com/downloads/api/v1/public/pages/nessus-agents"
    "/downloads/{download_id}/download?i_agree_to_tenable_license_agreement=true"
)


def get_latest_windows_x64_agent():
    """
    Main logic:
      1. Call the Tenable API
      2. Parse the JSON response
      3. Find the latest version of Nessus Agent
      4. Find the Windows x64 MSI download within that version
      5. Build and return the download URL
    """

    # ── Step 1: Make the HTTP GET request to the API ─────────────────
    # We wrap this in a try/except so if the network is down or the URL
    # is wrong, we get a clean error message instead of a stack trace.
    try:
        # Create a Request object so we can add headers.
        # The "Accept" header tells the server we want JSON back.
        # The "User-Agent" header identifies who is making the request.
        # Some servers (including Tenable) block requests that use Python's
        # default user agent ("Python-urllib/3.x") because it looks like
        # bot traffic.  Setting a real-looking User-Agent fixes the 403 error.
        req = urllib.request.Request(API_URL, headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        })

        # urlopen sends the request and gives us a response object.
        # The "with" statement ensures the connection gets closed when we're done.
        with urllib.request.urlopen(req) as resp:
            # resp.read() returns raw bytes, .decode() converts to a string,
            # and json.loads() parses that string into a Python dictionary.
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"[ERROR] Failed to reach Tenable API: {e}", file=sys.stderr)
        sys.exit(1)

    # ── Step 2: Get the "products" dictionary from the response ──────
    # .get() is safer than data["products"] because it returns an empty
    # dict {} instead of crashing if the key doesn't exist.
    products = data.get("products", {})

    # ── Step 3: Loop through products to find the latest version ─────
    # Product keys in the JSON look like:
    #   "plugins-archive"        -> not a versioned agent release, skip
    #   "signing-keys"           -> not a versioned agent release, skip
    #   "nessus-agents-11.1.2"   -> version 11.1.2
    #   "nessus-agents-11.0.4"   -> version 11.0.4
    #
    # We need to compare version numbers to find the highest one.
    # We'll track the winner in these two variables:
    latest_key = None       # the product dictionary key (e.g. "nessus-agents-11.1.2")
    latest_version = ()     # version as a tuple for comparison, e.g. (11, 1, 2)

    # .items() gives us both the key and value for each entry in the dict.
    # key   = "nessus-agents-11.1.2"  (the dictionary key, a string)
    # product = { "product_name": ..., "version": ..., "downloads": [...] }
    for key, product in products.items():
        # Skip anything that isn't a versioned agent product.
        # startswith() checks if the key begins with the string we expect.
        if not key.startswith("nessus-agents-"):
            continue

        # Grab the version string from the product data (e.g. "11.1.2").
        version_str = product.get("version")
        if not version_str:
            continue  # skip if there's no version (shouldn't happen, but be safe)

        # Convert "11.1.2" into a tuple (11, 1, 2) so we can compare numerically.
        # Here's how this one-liner works, broken down:
        #
        #   version_str.split(".")     "11.1.2"  ->  ["11", "1", "2"]
        #   int(x) for x in ...        converts each string to an integer
        #   tuple(...)                  wraps the result into (11, 1, 2)
        #
        # Why tuples?  Python compares tuples element by element:
        #   (11, 1, 2) > (11, 0, 4)  →  True   (because 1 > 0 at index 1)
        #   (10, 9, 9) > (11, 0, 0)  →  False  (because 10 < 11 at index 0)
        version_tuple = tuple(int(x) for x in version_str.split("."))

        # If this version is higher than our current best, update the winner.
        if version_tuple > latest_version:
            latest_version = version_tuple
            latest_key = key

    # If we looped through everything and found nothing, bail out.
    if latest_key is None:
        print("[ERROR] No Nessus Agent product versions found.", file=sys.stderr)
        sys.exit(1)

    # ── Step 4: Get the downloads list for the latest version ────────
    # Now that we know the key (e.g. "nessus-agents-11.1.2"), pull out
    # that product's data and its list of download entries.
    product = products[latest_key]
    version = product["version"]              # e.g. "11.1.2"
    downloads = product.get("downloads", [])  # list of download entry dicts

    # ── Step 5: Find the Windows Server x64 MSI in the downloads ─────
    # Each download entry has a "file" field like:
    #   "NessusAgent-11.1.2-x64.msi"          <- Windows x64 (WANT THIS)
    #   "NessusAgent-11.1.2-arm64.msi"         <- Windows ARM (skip)
    #   "NessusAgent-11.1.2.dmg"               <- macOS (skip)
    #   "NessusAgent-11.1.2-el8.x86_64.rpm"    <- Linux RPM (skip)
    #   "NessusAgent-11.1.2-debian10_amd64.deb" <- Linux DEB (skip)
    #
    # Checking endswith("-x64.msi") uniquely matches the Windows Server
    # 64-bit installer and excludes ARM64 and every non-Windows file.
    for dl in downloads:
        filename = dl.get("file", "")

        if filename.endswith("-x64.msi"):
            # ── Step 6: Build the download URL ───────────────────────
            # .format() replaces {download_id} in the template string
            # with the actual numeric ID from this download entry.
            download_url = DOWNLOAD_TEMPLATE.format(download_id=dl["id"])

            # Return a dictionary with all the useful info.
            # We use .get() with a default to avoid KeyError crashes
            # if a field is missing.  For the nested "meta_data" dict,
            # we chain two .get() calls:
            #   dl.get("meta_data", {})     -> get meta_data or empty dict
            #   .get("sha256")              -> get sha256 from that dict
            return {
                "version": version,
                "file": filename,
                "id": dl["id"],
                "size": dl.get("size"),
                "sha256": dl.get("meta_data", {}).get("sha256"),
                "description": dl.get("description"),
                "download_url": download_url,
            }

    # If we got here, we found the latest version but there was no x64 MSI in it.
    print("[ERROR] Windows x64 MSI not found in the latest release.", file=sys.stderr)
    sys.exit(1)


# ── Entry point ──────────────────────────────────────────────────────
# __name__ == "__main__" is a Python pattern that means:
#   "only run this block when the script is executed directly"
#   (e.g. python3 get_nessus_agent_url.py)
#
# It does NOT run if another script imports this file as a module:
#   from get_nessus_agent_url import get_latest_windows_x64_agent
#
# This is useful because it lets you reuse the function in other scripts
# without it automatically printing output.
if __name__ == "__main__":
    # Call our function which does all the work and returns a dictionary.
    result = get_latest_windows_x64_agent()

    # Print the results in a readable format.
    # f-strings (the f"..." syntax) let us embed variables directly in strings.
    # The :, in {result['size']:,} adds commas to large numbers (61,743,104).
    print(f"Nessus Agent v{result['version']}")
    print(f"File:     {result['file']}")
    print(f"ID:       {result['id']}")
    print(f"Size:     {result['size']:,} bytes")
    print(f"SHA256:   {result['sha256']}")
    print(f"OS:       {result['description']}")
    print()
    print(f"Download URL:")
    print(f"  {result['download_url']}")