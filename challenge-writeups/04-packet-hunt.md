# Challenge 04 Writeup: Packet Hunt

## Category
Networking

## Difficulty
Medium (200 Points)

## Learning Objective
Learn to analyze packet captures using Wireshark, apply HTTP filters, follow TCP streams, and locate sensitive parameters inside application headers.

## Tools Required
- Wireshark (Windows / macOS / Linux) or Python (`pyshark`/`scapy`/raw binary string search)

## Challenge Resource
`traffic.pcapng`

## Intended Solution Steps

### Option A: Wireshark (GUI)
1. Download `traffic.pcapng` and open it in Wireshark.
2. Type display filter `http` into the Wireshark filter bar and press Enter.
3. Observe the HTTP GET request to `/api/v1/telemetry?auth_token=session_98241&flag=FLAG{follow_the_network_story}`.
4. Right-click the HTTP packet, select **Follow** -> **TCP Stream** or **HTTP Stream**.
5. Examine the request query parameters and headers to reveal:
   - URL parameter: `flag=FLAG{follow_the_network_story}`
   - HTTP Header: `X-Secret-Flag: FLAG{follow_the_network_story}`

### Option B: Python String Search (Windows Friendly)
```powershell
python -c "with open('traffic.pcapng', 'rb') as f: data = f.read(); import re; print(re.findall(rb'FLAG\{[^}]+\}', data))"
```

## Expected Observations
- Captured packet contains HTTP traffic between client `192.168.1.105` and server `10.0.0.50`.
- HTTP GET parameters and custom header contain `FLAG{follow_the_network_story}`.

## Final Flag
`FLAG{follow_the_network_story}`
