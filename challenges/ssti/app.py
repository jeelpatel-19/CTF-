import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Ensure flag file exists
FLAG_PATH = os.path.join(os.path.dirname(__file__), 'flag.txt')
if not os.path.exists(FLAG_PATH):
    with open(FLAG_PATH, 'w') as f:
        f.write('FLAG{template_injection}\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.values.get('name', 'Guest')
    
    # Intentionally vulnerable Jinja2 template string formatting
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Template Trouble — CyberQuest</title>
        <style>
            body {{
                background-color: #0b0f19;
                color: #e2e8f0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .card {{
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 30px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            }}
            h1 {{ color: #10b981; margin-top: 0; font-size: 1.6rem; }}
            .greeting {{
                background: #1e293b;
                border-left: 4px solid #10b981;
                padding: 15px;
                border-radius: 6px;
                margin: 20px 0;
                font-size: 1.1rem;
            }}
            form {{ display: flex; gap: 10px; margin-top: 20px; }}
            input[type="text"] {{
                flex: 1;
                background: #0b0f19;
                border: 1px solid #374151;
                color: #e2e8f0;
                padding: 10px 14px;
                border-radius: 6px;
                font-size: 0.95rem;
            }}
            button {{
                background: #10b981;
                color: #000;
                font-weight: 600;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
            }}
            button:hover {{ background: #34d399; }}
            .subtext {{ font-size: 0.85rem; color: #64748b; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎨 Custom Profile Banner Generator</h1>
            <p>Enter your display name below to render a customized dynamic greeting!</p>
            
            <form method="GET" action="/">
                <input type="text" name="name" placeholder="Enter your name (e.g. Alice)" value="{name}">
                <button type="submit">Render</button>
            </form>

            <div class="greeting">
                Hello, {name}! Welcome to the platform.
            </div>

            <div class="subtext">
                Powered by Python Flask & Jinja2 Template Engine.
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    print("Starting SSTI Vulnerable Challenge on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
