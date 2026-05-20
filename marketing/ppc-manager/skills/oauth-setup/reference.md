# OAuth Setup — Reference

Step-by-step walkthroughs for every external platform the `oauth-setup` skill touches. Referenced by phase number from `SKILL.md`.

---

## Section 1. Google Cloud Console — one-time project setup

Everything in this section is done at [console.cloud.google.com](https://console.cloud.google.com). Allow ~15 minutes the first time.

### 1.1 Create or pick a project

1. Click the project picker in the top bar.
2. Click **New project** if you don't have one.
3. Name it e.g. `ppc-manager-personal`.
4. Leave the organisation empty unless your company requires one.
5. Click **Create** and wait ~20 seconds.

### 1.2 Enable the required APIs

From the left nav: **APIs & Services → Library**. Search and enable each of:

- **Tag Manager API**
- **Google Analytics Admin API**
- **Google Analytics Data API**
- **Google Ads API**

Each takes 10–20 seconds to enable. You will be billed $0 unless you exceed the free tier, which is very high for these APIs.

### 1.3 Configure the OAuth consent screen

From the left nav: **APIs & Services → OAuth consent screen**.

1. **User type:** External. Click Create.
2. **App information:**
   - App name: `ppc-manager` (or your preferred label)
   - User support email: your email
   - Developer contact information: your email
3. Click **Save and continue**.
4. **Scopes:** click **Add or remove scopes** and paste these (one per line) into the filter box:
   - `https://www.googleapis.com/auth/tagmanager.edit.containers`
   - `https://www.googleapis.com/auth/tagmanager.readonly`
   - `https://www.googleapis.com/auth/analytics.readonly`
   - `https://www.googleapis.com/auth/analytics.edit`
   - `https://www.googleapis.com/auth/adwords`
5. Tick the checkbox on each matching result. Click **Update** then **Save and continue**.
6. **Test users:** add your own email (and any team members who will use the plugin). Click **Save and continue**.
7. **Summary:** review and click **Back to dashboard**.

At this point the app is in **testing mode**. That is fine — it stays in testing mode forever if you only use it yourself. Going to production requires Google app verification which is not needed.

### 1.4 Create an OAuth Desktop client

From the left nav: **APIs & Services → Credentials**.

1. Click **+ Create credentials → OAuth client ID**.
2. **Application type:** **Desktop app** (important — not Web).
3. **Name:** `ppc-manager`.
4. Click **Create**.
5. A dialog appears showing your new client ID. Click **Download JSON**.
6. Save the file somewhere outside any git repo — e.g. `~/.config/ppc-manager/client_secret.json`.

That file is the input to `/ppc-manager:oauth-setup`. Keep it private but you do not need to encrypt it — the actual OAuth tokens derived from it are what matter, and those go straight into the ppc-manager vault.

### 1.5 Find your Google Ads developer token

1. Sign in to [ads.google.com](https://ads.google.com).
2. From any account, open the top-right menu → **Tools** → **Setup / API Center**.
3. If you have never been there, you will be asked to apply for a token.
4. **Basic access** is approved instantly and is enough for test accounts.
5. **Standard access** is required for production accounts and takes several business days to approve. You can start with Basic.
6. Copy the developer token (~22 characters).

---

## Section 2. Meta Business Developer App — one-time setup

Done at [developers.facebook.com](https://developers.facebook.com). Allow ~10 minutes.

### 2.1 Create the app

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps).
2. Click **Create app**.
3. **Use case:** **Other** → **Next**.
4. **App type:** **Business** → **Next**.
5. **Display name:** `ppc-manager`.
6. **App contact email:** your email.
7. **Business Account:** pick your Meta Business Manager (create one first at [business.facebook.com](https://business.facebook.com) if you don't have one).
8. Click **Create app**.

### 2.2 Add the Marketing API product

1. From the left nav: **Add Product**.
2. Find **Marketing API** → **Set up**.
3. No extra configuration needed — the product is added.

### 2.3 Configure app settings

1. From the left nav: **App settings → Basic**.
2. Copy the **App ID** (numeric, public).
3. Click **Show** next to **App secret** and copy it (sensitive).
4. Under **App Domains**, leave empty — the OAuth loopback does not need a registered domain.
5. Under **Privacy Policy URL**, put any placeholder URL (required by Meta; the app will stay in development mode so this is not enforced).
6. Click **Save changes**.

### 2.4 Permissions & OAuth redirect

1. From the left nav: **Use cases → Customize**.
2. For `ads_management`, `ads_read`, `business_management`, `pages_read_engagement`, `pages_manage_metadata` — verify each is in the **Permissions** list. If not, add them.
3. While the app is in **development mode**, you (as an app admin) have all these scopes without review. Don't promote the app to **Live** unless you need other users.

### 2.5 Find your Meta ad account IDs

The OAuth flow will list them automatically, but you can also verify in [business.facebook.com/settings/ad-accounts](https://business.facebook.com/settings/ad-accounts). The IDs look like `act_1234567890`.

---

## Section 3. Combined OAuth scope list (for reference)

| Platform | Scope | Purpose |
|---|---|---|
| Google Tag Manager | `tagmanager.edit.containers` | Create/update tags, triggers, variables, versions |
| Google Tag Manager | `tagmanager.readonly` | List containers, read existing items |
| Google Analytics 4 | `analytics.readonly` | Run reports, read property metadata |
| Google Analytics 4 | `analytics.edit` | Create conversion events, custom dimensions/metrics |
| Google Ads | `adwords` | Everything Google Ads API |
| Meta | `ads_management` | Create/update campaigns, ad sets, ads |
| Meta | `ads_read` | Read performance data |
| Meta | `business_management` | List ad accounts, pages, pixels |
| Meta | `pages_read_engagement` | Read Page events |
| Meta | `pages_manage_metadata` | Update Page settings if the user needs it |

---

## Section 4. Top 10 OAuth errors and how to fix them

### 1. `invalid_grant: Bad Request`

The refresh token has been revoked or the clock on your machine is skewed. Fix: revoke the app at [myaccount.google.com/permissions](https://myaccount.google.com/permissions), run `oauth-setup` again, and ensure your system clock is within a minute of real time (`sudo ntpdate pool.ntp.org` or the Windows equivalent).

### 2. `Google hasn't verified this app`

Expected during Testing mode. Click **Advanced → Go to ppc-manager (unsafe)**. This only means the app is not yet verified, not that it is compromised. It is verified against your own GCP project.

### 3. `This app's developer needs to verify that it complies...`

You did not add your own email to the **Test users** list in the OAuth consent screen (Section 1.3 step 6). Go add it, then retry.

### 4. `Access blocked: Google Ads API requires...`

Your developer token does not match the refresh token's account. Ensure the Google account you consented with has Google Ads API access (applied for at Section 1.5). For Basic access this is immediate.

### 5. Missing refresh token

You consented before but Google only returns a refresh token on first consent unless `prompt=consent` is set. The `oauth_google.py` script sets `prompt=consent` by default, so this should not happen — but if it does, revoke the app at `myaccount.google.com/permissions` and retry.

### 6. Meta `OAuthException: (#100) The parameter redirect_uri is required`

The loopback server did not bind to the port the OAuth dialog is redirecting to. This typically means another process stole the port between `oauth_meta.py` picking it and the browser redirecting. Retry — the script picks a fresh port each run.

### 7. Meta `Invalid platform app`

The Meta app is not in Development mode or does not have Marketing API added. See Section 2.2.

### 8. Meta `Error validating access token: Session has expired`

The long-lived token has passed its 60-day window. Run `/ppc-manager:oauth-setup refresh meta default`.

### 9. `ModuleNotFoundError: No module named 'fastmcp'`

The venv bootstrap hook has not yet run, or it failed. Check `${CLAUDE_PLUGIN_DATA}/install.log` and run `make install` from the plugin directory to force a fresh install.

### 10. Script appears to hang after opening browser

The loopback server is waiting for the redirect, but your browser is blocked on a popup, or you closed the tab. Close the terminal (Ctrl+C), reopen, and retry. Add `--port 8765` if you want a deterministic port for firewall rules.

---

## Section 5. Revoking access and starting over

1. Delete `${CLAUDE_PLUGIN_DATA}/tokens.enc`.
2. Revoke the app at:
   - Google: [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
   - Meta: [business.facebook.com/settings/system-users](https://business.facebook.com/settings/system-users) → remove the app
3. Disable the plugin in Claude Code.
4. Enable the plugin — this re-prompts for the vault passphrase.
5. Run `/ppc-manager:oauth-setup`.

Note that Meta tokens that have already been re-exchanged cannot be re-derived without fresh browser consent, so expect to see a new browser OAuth dialog after a full revoke.
