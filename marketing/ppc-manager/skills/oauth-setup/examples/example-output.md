# OAuth Setup — Example Output

Sample of what the `oauth-setup` skill produces after a user connects Google (GTM, GA4, Google Ads) and Meta Ads.

---

## Connection summary

**Workspace:** acme-au
**Date:** 2026-04-25
**Connected platforms:** Google (GTM, GA4, Google Ads), Meta Ads

| Platform | Status | Scopes | Token expiry | Vault key |
|---|---|---|---|---|
| Google GTM | connected | `tagmanager.edit.containers`, `tagmanager.publish` | 2026-05-25 | `vault://ppc/google/gtm/acme-au` |
| Google GA4 | connected | `analytics.edit`, `analytics.manage.users.readonly` | 2026-05-25 | `vault://ppc/google/ga4/acme-au` |
| Google Ads | connected | `adwords` | 2026-05-25 | `vault://ppc/google/ads/acme-au` |
| Meta Ads | connected | `ads_management`, `business_management`, `pages_show_list` | 2026-06-23 (60d) | `vault://ppc/meta/ads/acme-au` |

---

## Google Cloud Console — what was created

- **Project:** `acme-ppc-manager` (existing — reused)
- **OAuth consent screen:** External, in production, verified
- **OAuth client:** Desktop app (`ppc-manager — acme`)
- **Enabled APIs:** Tag Manager API, Google Analytics Admin API, Google Ads API

## Meta App — what was created

- **App name:** `ppc-manager — acme`
- **App type:** Business
- **Permissions added:** `ads_management`, `business_management`, `pages_show_list`
- **System user:** `ppc-manager-bot` with assigned ad accounts

---

## Token storage

All tokens are encrypted at rest using the plugin vault (libsodium sealed box). Refresh tokens are rotated automatically; access tokens are refreshed on use.

To revoke a connection:

```bash
ppc-manager auth revoke --workspace acme-au --platform google
```

## Next steps

1. Run the `gtm-setup` skill to baseline the GTM container.
2. Run the `ga4-setup` skill to align GA4 retention/links.
3. Run the `meta-pixel-setup` skill if the Meta Pixel is not yet installed.
