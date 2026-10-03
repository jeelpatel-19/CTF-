# Challenge 03 Writeup: Metadata Mystery

## Category
Forensics

## Difficulty
Medium (150 Points)

## Learning Objective
Learn digital forensics techniques for examining JPEG file headers and EXIF comment fields embedded within media artifacts.

## Tools Required
- ExifTool / Python PIL / PowerShell / Online EXIF Viewer / `strings`

## Challenge Resource
`evidence.jpg`

## Intended Solution Steps

### Option A: Python PIL / EXIF Inspection (Windows Friendly)
Run the following Python script:
```python
from PIL import Image, ExifTags

img = Image.open('evidence.jpg')
exif_data = img._getexif()

if exif_data:
    for tag_id, value in exif_data.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
        print(f"{tag}: {value}")
```
Or check raw string comments in binary:
```powershell
python -c "with open('evidence.jpg', 'rb') as f: content = f.read(); print([line for line in content.split(b'\n') if b'FLAG' in line])"
```

### Option B: ExifTool
```bash
exiftool evidence.jpg
```
Look for `UserComment` or `Comment` tag:
`EXIF UserComment: FLAG{metadata_is_evidence}`

### Option C: Strings / Grep
```bash
strings evidence.jpg | grep FLAG
```

## Expected Observations
- The visual image shows evidence file graphic.
- Embedded EXIF COM segment holds `FLAG{metadata_is_evidence}`.

## Final Flag
`FLAG{metadata_is_evidence}`
