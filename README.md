# Horror Channel Auto-Uploader (100% Free Stack)

Daily automatically: script likhta hai -> narration banata hai -> video assemble
karta hai -> YouTube pe upload karta hai. Sab GitHub Actions pe free mein chalta hai,
tera PC/laptop 24/7 on rakhne ki zaroorat nahi.

## ⚠️ Read this first
- Voice thoda TTS-ish sound karega (edge-tts), cinematic AI video nahi milega free tier mein.
- YouTube's policy "reused/repetitive content" ko demonetize kar sakti hai -- isliye
  script ko topic pool se vary karo, aur time-to-time khud commentary/intro add karne
  ki koshish karo taaki channel "authentic" lage.
- Ek baar OAuth setup manual hoga (30 min), uske baad fully automatic.
- Token kabhi kabhi expire ho sakta hai (rare) -- 2 min ka manual refresh lagega.

## Step 1 — Get free API keys

### Gemini API key (script generation, free tier)
1. Go to https://aistudio.google.com/apikey
2. "Create API key" click karo, copy karo.

### Pexels API key (stock video, free)
1. Go to https://www.pexels.com/api/
2. Sign up, "Your API Key" copy karo.

## Step 2 — YouTube API setup (one-time, ~30 min)
1. Go to https://console.cloud.google.com/ -> naya project banao.
2. "APIs & Services" -> "Library" -> "YouTube Data API v3" -> Enable.
3. "APIs & Services" -> "Credentials" -> "Create Credentials" -> "OAuth client ID"
   -> Application type: **Desktop app**.
4. Download the JSON, rename it to `client_secret.json`, isi folder mein rakho.
5. "OAuth consent screen" mein apni Gmail ko "Test user" add karo (varna auth fail hoga).
6. Apne laptop pe locally ek baar chalao (yahi ek step hai jo tera involvement maangta hai):
   ```
   pip install -r requirements.txt
   python upload_youtube.py
   ```
   Ye browser kholega, apne YouTube channel wale Google account se login karo, allow karo.
   Isse `token.pickle` file ban jayegi -- ye hi file GitHub Actions use karega daily.

## Step 3 — Put this on GitHub
1. Naya **private** repo banao GitHub pe.
2. Ye poora folder push karo.
3. `client_secret.json` aur `token.pickle` ko **commit MAT karo directly** -- inhe
   base64 encode karke GitHub Secrets mein daalo (next step).

## Step 4 — Add GitHub Secrets
Repo -> Settings -> Secrets and variables -> Actions -> "New repository secret".
Add these 4 secrets:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | tera Gemini key |
| `PEXELS_API_KEY` | tera Pexels key |
| `YT_TOKEN_PICKLE_B64` | `base64 token.pickle` ka output (terminal mein: `base64 -w0 token.pickle`) |
| `YT_CLIENT_SECRET_B64` | `base64 -w0 client_secret.json` ka output |

## Step 5 — Test it
GitHub repo -> "Actions" tab -> "Daily Horror Video Upload" -> "Run workflow" button
(manual trigger) -> dekh ki pipeline pass hoti hai. Agar fail ho toh "debug-output"
artifact download karke error dekh sakta hai.

## Step 6 — Let it run
Ab ye daily 7:30 PM IST (cron schedule, `.github/workflows/daily_upload.yml` mein
change kar sakta hai) automatically chalega. Tera involvement ab bas:
- Occasionally naye topics `config.py` ke `TOPIC_POOL` mein add karna
- Kabhi kabhi upload check karna ki sab theek gaya

## Customization
- **More topics**: `config.py` -> `TOPIC_POOL` list mein add karo.
- **Voice**: `config.py` -> `VOICE` change karo (`hi-IN-SwaraNeural` for female voice).
- **Upload time**: `.github/workflows/daily_upload.yml` -> cron line change karo.
- **Private review before publish**: `config.py` -> `YOUTUBE_PRIVACY_STATUS = "private"`
  then manually publish from YouTube Studio after checking quality.

## Local testing (before pushing to GitHub)
```bash
pip install -r requirements.txt
echo "GEMINI_API_KEY=xxx" > .env
echo "PEXELS_API_KEY=xxx" >> .env
python main.py
```
