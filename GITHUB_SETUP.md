# Publishing TerraDesk to GitHub

Follow these steps to publish the source code AND the compiled EXE.

## Step 1 — Create the GitHub Repository

1. Go to https://github.com/new
2. Repository name: `terradesk`
3. Description: `🏡 Open-source isometric village simulation for Windows desktop`
4. Make it **Public**
5. Do NOT add README (we have one)
6. Click **Create repository**

## Step 2 — Push the Source Code

Open a terminal in the `C:\bireysel projeler\tetradesk` folder and run:

```powershell
git init
git add .
git commit -m "Initial release: TerraDesk v1.0.0 - full village simulation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/terradesk.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3 — Create a GitHub Release with the EXE

```powershell
# Tag the release
git tag v1.0.0
git push origin v1.0.0
```

Then:
1. Go to your repository on GitHub
2. Click **Releases** → **Create a new release**
3. Tag: `v1.0.0`
4. Title: `TerraDesk v1.0.0 — Village Simulation`
5. Description:
   ```
   ## 🏡 TerraDesk v1.0.0

   Full isometric village simulation with:
   - 14 building types
   - Autonomous citizen AI
   - Economy system (taxes, salaries, trading)
   - Day/night cycles, 4 seasons, weather
   - God Mode panel
   - Desktop integration (always-on-top, wallpaper mode)
   - Save/load system

   ## Download
   - **TerraDesk.exe** — Windows (no install needed, just run!)
   - **Source code** — Run with Python 3.11+ and `pip install -r requirements.txt`
   ```
6. Drag and drop `dist\TerraDesk.exe` into the **Attach binaries** area
7. Click **Publish release**

## Step 4 — Add a .gitignore (already done)

The `.gitignore` already excludes `dist/`, `build/`, `__pycache__/`, `*.spec`, etc.

## Done! 🎉

Your game is now live at:
- Source: `https://github.com/YOUR_USERNAME/terradesk`
- EXE download: In the Releases page