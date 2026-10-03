# Challenge 01 Writeup: Hidden in Plain Sight

## Category
Web Security

## Difficulty
Easy (50 Points)

## Learning Objective
Understand client-side source code inspection and recognize that comments left in rendered HTML markups are public and accessible to anyone.

## Tools Required
- Modern Web Browser (Chrome, Firefox, Edge, Brave)
- Developer Tools / Page Source Viewer

## Intended Solution Steps
1. Navigate to the challenge target URL: `http://localhost:5000/api/challenges/target/hidden-source`
2. Right-click anywhere on the webpage and select **"View Page Source"** or press `Ctrl + U` (`Cmd + Option + U` on macOS).
3. Search for HTML comments starting with `<!--`.
4. Locate the developer note comment at the bottom of the document:
   ```html
   <!-- 
     DEVELOPER NOTE:
     Remember to delete debug credentials before production deploy!
     Secret Flag: FLAG{source_code_reveals_secrets}
   -->
   ```
5. Copy the flag `FLAG{source_code_reveals_secrets}` and submit it on the CyberQuest challenge page.

## Expected Observations
- The rendered web page appears normal with status "Secure".
- The sensitive information is omitted from the visible DOM layout but remains visible in the raw source code response.

## Final Flag
`FLAG{source_code_reveals_secrets}`
