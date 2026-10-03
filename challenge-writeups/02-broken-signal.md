# Challenge 02 Writeup: Broken Signal

## Category
Cryptography

## Difficulty
Easy (75 Points)

## Learning Objective
Understand multi-stage data encoding pipelines (Hexadecimal and Base64) and practice decoding using CyberChef, Python, or shell command line tools.

## Tools Required
- CyberChef / Python 3 / PowerShell / Online Decoders
- File downloader or text editor

## Challenge Resource
`signal.txt` containing the encoded payload:
```
526b784252337462586c65636e63466f5a665a57356a62325270626d633d
```

## Intended Solution Steps

### Option A: CyberChef
1. Drag `signal.txt` or paste `526b784252337462586c65636e63466f5a665a57356a62325270626d633d` into CyberChef.
2. Add the **"From Hex"** operation to the recipe pipeline.
3. Output reveals intermediate Base64 payload: `RkxBR3tsYXllcnNfb2ZfZW5jb2Rpbmc=`
4. Add the **"From Base64"** operation to the recipe pipeline.
5. Final decoded output: `FLAG{layers_of_encoding}`

### Option B: Python Command
Run the following PowerShell / Python snippet:
```powershell
python -c "import base64; hex_data = '526b784252337462586c65636e63466f5a665a57356a62325270626d633d'; b64_data = bytes.fromhex(hex_data).decode('utf-8'); flag = base64.b64decode(b64_data).decode('utf-8'); print(flag)"
```

## Expected Observations
- Step 1 Hex Decode -> `RkxBR3tsYXllcnNfb2ZfZW5jb2Rpbmc=`
- Step 2 Base64 Decode -> `FLAG{layers_of_encoding}`

## Final Flag
`FLAG{layers_of_encoding}`
