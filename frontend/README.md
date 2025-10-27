# HealthLLM - Next.js + Tailwind Starter

This project was generated automatically and includes:
- Next.js pages for Login/Signup, Dashboard, Upload
- Tailwind CSS configured
- Header and Footer components
- API route stubs for auth, LLM queries and upload

## Downloaded files location inside the zip:
- All project files are inside this folder.

## Setup instructions for macOS (Apple Silicon - M1/M2/M5)

1. Install Homebrew if you don't have it:  
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Install Node.js (recommended LTS). Using nvm is optional:
   - Install Node via Homebrew:
     ```
     brew install node
     ```
     Confirm with `node -v` (should be >= 18).

3. Unzip the downloaded project and open a terminal in the project folder.

4. Install dependencies:
   ```
   npm install
   ```

5. Initialize Tailwind (already configured) — if you need to rebuild CSS after changes:
   ```
   npx tailwindcss -i ./styles/globals.css -o ./public/output.css --watch
   ```
   Not required for development; Next will pick up Tailwind classes.

6. Run the dev server:
   ```
   npm run dev
   ```
   Then open http://localhost:3000 in your browser.

## Notes
- API routes are stubs for demonstration. Replace with proper auth, database, and real LLM integration.
- The upload endpoint uses `formidable` (already referenced). On some Node versions you may need to `npm install formidable`.
- To integrate with a real LLM, replace `/pages/api/llm.js` with a server-side call to your provider (OpenAI, etc.) and secure API keys in environment variables.

Happy hacking!
