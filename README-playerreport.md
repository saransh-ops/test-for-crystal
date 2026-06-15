# PlayerReportManager 🛡️
**Crystalfbft — Staff Report Management System**

A full-stack player reporting system: web form for players, CLI tool for staff, Google Sheets backend, Discord alerts.

---

## Stack
| Part | What it is |
|------|-----------|
| `main.py` | Staff CLI — view, filter, update reports |
| `report-web.html` | Player-facing web form + public status tracker |
| `google_apps_script.js` | Backend — paste into Google Apps Script |
| `launcher.bat` | Windows launcher, auto-installs deps |

---

## Setup

### 1. Google Apps Script
1. Go to [script.google.com](https://script.google.com) → New Project
2. Paste contents of `google_apps_script.js`
3. Deploy → New Deployment → Web App
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Copy the deployment URL

### 2. Web Form
- Open `report-web.html`
- Replace `YOUR_GOOGLE_APPS_SCRIPT_URL_HERE` with your URL

### 3. CLI
```bash
launcher.bat
# First run sets your staff password and Script URL
```

---

## CLI Features
- `[1]` View open reports
- `[2]` View all reports  
- `[3]` Filter by status (Open / Investigating / Resolved / Rejected)
- `[4]` Search by accused player name
- `[5]` View report by ID → change status, add staff notes
- `[6]` Settings — update URLs, change password

## Web Features
- **Report tab** — username, accused, reason picker (with priority badge), description, evidence link
- **Track tab** — paste Report ID, see full status + staff notes in chat-style UI, add follow-ups, live refresh every 10s

## Discord
Set your webhook in Settings `[6]` in the CLI. Pings on every new report with player head, priority color, and all details.

---

## Requirements
```
Python 3.10+
requests
colorama
```
