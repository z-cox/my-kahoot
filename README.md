# Name That Bar: CT-scanned chocolate bar quiz

A live quiz. Players guess which chocolate bar is in each CT scan on their phones; you project the host screen.

## Put it online (about 5 minutes, free)
1. Create a new **public** GitHub repo and upload everything in this folder (drag and drop works; keep the `images`, `.streamlit` folders).
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**, pick your repo, set the main file to `app.py`, and click **Deploy**.
3. In the app's **Settings > Secrets**, add: `HOST_PASSWORD = "pick-something-here"`.
4. Open `https://<your-app>.streamlit.app/?host=1` and enter the password. The QR code on the lobby screen is filled in for you.

Before the event: free apps go to sleep after a while without visitors, so open the URL a few minutes beforehand to wake it. Press **Reset game** in the host sidebar before you start.

## Other ways to run it
- **GitHub Codespaces:** Code > Codespaces > Create. It installs and starts automatically. In the Ports tab, set port 8501 to Public so others can join.
- **Your laptop:** `pip install -r requirements.txt` then `streamlit run app.py` (players: `localhost:8501`, host: `localhost:8501/?host=1`, default password `ctscan`).

## Customize
Edit `QUESTIONS` at the top of `app.py`: image path, correct answer, and the four options. Replace the GIFs in `images/` with your own.

## Limits
Game state lives in server memory (one running instance). Don't redeploy or reboot mid-quiz.
