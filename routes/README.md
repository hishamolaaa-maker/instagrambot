# 📲 Instagram DM Automation Tool

Automate Instagram comment replies and DMs based on keywords — like ManyChat, but self-hosted and free.

**How it works:** When someone comments a keyword (e.g. "link") on your post, the bot automatically replies to the comment AND sends them a private DM.

---

## 🚀 Quick Deploy on Railway (Free, No Coding Needed)

### Step 1 — Upload to GitHub

1. Download this project folder
2. Go to [github.com](https://github.com) → sign up or log in
3. Click **New repository** → name it `instagram-dm-bot` → Create
4. Upload all the files from this folder to the repo

### Step 2 — Deploy on Railway

1. Go to [railway.app](https://railway.app) → sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `instagram-dm-bot` repository
4. Railway will auto-detect the Dockerfile and start building

### Step 3 — Add Environment Variables on Railway

In your Railway project → **Variables** tab, add:

| Variable | Value |
|----------|-------|
| `INSTAGRAM_ACCESS_TOKEN` | Your long-lived token (see below) |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Your IG business account ID |
| `FACEBOOK_APP_SECRET` | Your Facebook app secret |
| `WEBHOOK_VERIFY_TOKEN` | Any random string (e.g. `mysecrettoken123`) |
| `DATABASE_URL` | Leave empty (uses SQLite by default) |

### Step 4 — Get your public URL

Railway gives you a URL like `https://instagram-dm-bot-production.up.railway.app`
That's your webhook URL: `https://YOUR-URL/webhook/instagram`

---

## 🔧 Instagram / Facebook Setup (Step by Step)

### 1. Convert Instagram to Business/Creator Account

- Instagram app → Profile → ⚙️ Settings → Account → **Switch to Professional Account**
- Choose **Business** or **Creator**

### 2. Create a Facebook Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps** → **Create App**
3. Choose **Business** type
4. Fill in App Name and email → Create

### 3. Add Instagram Graph API

1. In your app dashboard → **Add a Product**
2. Find **Instagram Graph API** → click **Set up**

### 4. Add Required Permissions

Go to **App Review** → **Permissions and Features**, request:
- `instagram_manage_comments` — to reply to comments
- `instagram_manage_messages` — to send DMs
- `pages_read_engagement` — to read page data

> **Note about DMs:** Instagram's DM API requires that the user has previously messaged your business, OR you have approved `instagram_manage_messages` permission. Apply for this permission in App Review with a use case like "customer engagement automation."

### 5. Generate a Long-lived Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Add permissions: `instagram_manage_comments`, `instagram_manage_messages`, `pages_manage_posts`
4. Click **Generate Access Token** and authorize
5. Exchange for a long-lived token (valid 60 days):
   ```
   GET https://graph.facebook.com/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={YOUR_APP_ID}
     &client_secret={YOUR_APP_SECRET}
     &fb_exchange_token={SHORT_LIVED_TOKEN}
   ```
6. Copy the returned `access_token`

> **Token expires in 60 days!** Set a calendar reminder to refresh it. You can re-run the exchange above with the same long-lived token to get a new 60-day one.

### 6. Get Your Page ID and Instagram Account ID

In Graph API Explorer:
```
GET /me/accounts
```
Copy the `id` of your Facebook Page.

Then:
```
GET /{page-id}?fields=instagram_business_account
```
Copy the `id` inside `instagram_business_account` — that's your Instagram Account ID.

### 7. Configure the Webhook

1. In Facebook Developer App → **Webhooks** (left menu)
2. Click **Add Subscriptions** → select **Instagram**
3. Callback URL: `https://YOUR-RAILWAY-URL/webhook/instagram`
4. Verify Token: whatever you set as `WEBHOOK_VERIFY_TOKEN`
5. Subscribe to field: **comments**

---

## 📦 Get a Post ID

In Graph API Explorer:
```
GET /{instagram-account-id}/media?fields=id,caption,timestamp&limit=10
```

Copy the `id` of the post you want to track. Use this as the **Post ID** when creating a campaign.

---

## 🖥️ Using the Dashboard

Visit `https://YOUR-RAILWAY-URL/dashboard`

1. **Settings** → Enter your Access Token, Page ID, Instagram Account ID → Save
2. **Campaigns** → Click "New Campaign"
   - Paste the Post ID
   - Add trigger keywords (comma-separated): `link, price, info, send me`
   - Write your comment reply: `Hey! Check your DMs 📩`
   - Write your DM message: `Hi! Here's the link: https://...`
3. Campaign goes active immediately ✅

---

## 🛡️ Security

- Webhook signature is validated via `X-Hub-Signature-256` on every request
- Credentials stored in environment variables, never exposed to frontend
- Duplicate comment processing prevented via database deduplication

---

## 🏗️ Project Structure

```
├── main.py              # FastAPI entry point
├── instagram.py         # Instagram Graph API client
├── models.py            # SQLAlchemy DB models
├── database.py          # DB session setup
├── routes/
│   ├── webhook.py       # Webhook endpoints
│   ├── dashboard.py     # HTML page routes
│   └── api.py           # REST API (campaigns/config)
├── templates/
│   └── dashboard.html   # Full dashboard UI
├── static/              # CSS/JS assets
├── Dockerfile
├── railway.toml
├── requirements.txt
└── env.example          # Environment variables template
```

---

## ❓ Troubleshooting

**Webhook not verifying?**
- Make sure `WEBHOOK_VERIFY_TOKEN` in Railway matches exactly what you put in Facebook webhook settings

**Comments not triggering?**
- Check that the Post ID in the campaign matches the actual post
- Make sure the campaign is Active
- View Railway logs for webhook events

**DMs not sending?**
- Instagram requires the user to have messaged your account first (unless you have approved DM permission)
- Apply for `instagram_manage_messages` in Facebook App Review

**Token expired?**
- Re-generate a long-lived token and update it in Settings dashboard
