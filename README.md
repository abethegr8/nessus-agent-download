# Python Nessus Agent Downloader

A Python script that queries the Tenable Downloads API to automatically discover the latest Windows x64 Nessus Agent and generate its direct download URL.

Instead of manually browsing the Tenable Downloads page and updating deployment scripts whenever a new version is released, this script retrieves the latest release directly from the Tenable public API.

---

# Project Overview

Many organizations deploy the Nessus Agent across hundreds or thousands of servers.

Rather than hardcoding a specific installer version, this script dynamically retrieves the most recent Windows x64 installer by:

1. Querying the Tenable Downloads API
2. Parsing the JSON response
3. Identifying the newest Nessus Agent version
4. Finding the Windows x64 MSI installer
5. Building the direct download URL

This approach allows deployment scripts and automation pipelines to always use the latest available release.

---

# Features

* Uses only Python's standard library
* No external packages required
* Queries the official Tenable Downloads API
* Automatically identifies the newest agent version
* Ignores older releases
* Filters only the Windows x64 MSI installer
* Returns download metadata
* Builds a direct download URL
* Includes error handling for network failures
* Well documented and heavily commented

---

# Technologies Used

* Python 3
* REST APIs
* JSON
* urllib.request
* Azure/Linux compatible
* Bash automation friendly

---

# API Used

Official Tenable Downloads API

```text
https://www.tenable.com/downloads/api/v1/public/pages/nessus-agents
```

The API returns a JSON document containing every supported Nessus Agent release for:

* Windows
* Linux
* macOS
* ARM
* x64

This script filters the response to return only the latest Windows Server x64 installer.

---

# How It Works

The script follows this workflow:

```text
Call Tenable API
        │
        ▼
Receive JSON Response
        │
        ▼
Parse Products Dictionary
        │
        ▼
Locate Latest Nessus Agent Version
        │
        ▼
Find Windows x64 MSI
        │
        ▼
Generate Download URL
        │
        ▼
Display Results
```

---

# Example Output

```text
Nessus Agent v11.1.2

File:
NessusAgent-11.1.2-x64.msi

ID:
27830

Size:
61,743,104 bytes

SHA256:
<hash>

OS:
Windows Server (x86 64-bit)

Download URL:

https://www.tenable.com/downloads/api/v1/public/pages/nessus-agents/downloads/27830/download?i_agree_to_tenable_license_agreement=true
```

---

# Running the Script

Clone the repository:

```bash
git clone https://github.com/<username>/python-nessus-agent-downloader.git
```

Run:

```bash
python3 get_nessus_agent_url.py
```

---

# Error Handling

The script gracefully handles:

* Network failures
* HTTP errors
* Missing API fields
* Missing product versions
* Missing Windows x64 installers
* Invalid API responses

Instead of producing a Python stack trace, meaningful error messages are displayed.

Example:

```text
[ERROR] Failed to reach Tenable API
```

---

# Skills Demonstrated

This project demonstrates:

* Python programming
* REST API integration
* JSON parsing
* Dictionaries and lists
* Functions
* Loops
* Conditional logic
* Exception handling
* Version comparison
* String formatting
* URL construction
* Infrastructure automation

---

# Real-World Use Case

This script was developed to support infrastructure automation.

Instead of manually downloading the latest Nessus Agent whenever a new release becomes available, deployment scripts can execute this utility to retrieve the newest Windows x64 installer automatically.

This removes manual maintenance from deployment workflows and ensures new server builds always install the latest supported agent.

---

# Microsoft Copilot Usage

Microsoft Copilot assisted during development by helping generate portions of the Python code and documentation.

All generated code was manually reviewed, tested, and validated against the Tenable API before being incorporated into the final solution.

Copilot was used as an engineering productivity tool while design decisions, troubleshooting, testing, and validation remained the responsibility of the developer.

---

# Future Improvements

Potential enhancements include:

* Download the installer automatically
* Verify the SHA256 checksum after download
* Support Linux RPM packages
* Support Debian packages
* Support macOS installers
* Export results as JSON
* Add logging
* Add unit tests
* Package as a reusable Python module
* Integrate with Azure DevOps or GitHub Actions
* Automatically deploy the latest agent to target servers

---

# Lessons Learned

While building this project I gained hands-on experience with:

* Consuming REST APIs using Python
* Parsing nested JSON structures
* Working with dictionaries and lists
* Comparing software versions programmatically
* Constructing URLs dynamically
* Implementing robust exception handling
* Writing maintainable, well-documented Python code

This project reinforced how infrastructure engineers can combine scripting and APIs to automate repetitive operational tasks and eliminate manual processes.
