# GTM Setup — Reference

Dense reference material for the `gtm-setup` skill: tag type constants, trigger type constants, variable type constants, the baseline naming convention, and the GA4 Configuration tag parameter shape.

---

## 1. Naming convention (mandatory)

All tags, triggers, and variables created by ppc-manager follow this convention. Audit any container that doesn't.

### Tags

Format: `{Category} - {Platform} - {Descriptor}`

| Example | Meaning |
|---|---|
| `Con - GA4 - Config` | GA4 Configuration tag (one per container) |
| `Con - GA4 - Event - purchase` | GA4 Event tag for the `purchase` event |
| `Con - Meta - Pixel Base` | Meta pixel base install |
| `Con - Meta - Event - Purchase` | Meta pixel event |
| `Con - LinkedIn - Insight Tag` | LinkedIn Insight base |
| `Util - HTML - Consent Mode Init` | Consent mode default init |

Categories: `Con` (conversion tracking), `Util` (utility), `Mkt` (non-conversion marketing), `Test` (test tags). Platforms: `GA4`, `Meta`, `LinkedIn`, `TikTok`, `Google Ads`, `Microsoft`.

### Triggers

Format: `{Scope} - {Event}`

| Example | Meaning |
|---|---|
| `All Pages - Page View` | Default built-in Page View trigger |
| `Form Submit - Contact Us` | Form submit for one specific form |
| `Custom Event - purchase` | DataLayer custom event |
| `Click - CTA Button` | Element visibility / click |

### Variables

Format: `{Type prefix} - {Name}`

| Prefix | Meaning |
|---|---|
| `DL - ` | Data Layer Variable |
| `CONST - ` | Constant |
| `URL - ` | URL variable |
| `COOKIE - ` | First-party cookie |
| `JS - ` | Custom JavaScript |
| `LOOK - ` | Lookup table |

Example: `DL - purchase.value`, `CONST - GA4 Measurement ID`, `URL - Hostname`.

---

## 2. Tag type constants (the GTM API shorthand)

Passed as `tag_type` to `ppc-gtm:create_tag`.

| Constant | Tag | Most common parameters |
|---|---|---|
| `gaawc` | GA4 Configuration | `measurementId` (e.g. G-XXXXXXXXXX), `sendPageView` (bool) |
| `gaawe` | GA4 Event | `eventName`, `measurementIdOverride`, `eventParameters` (list) |
| `html` | Custom HTML | `html` (string), `supportDocumentWrite` (bool) |
| `img` | Custom Image | `url` (template string) |
| `awct` | Google Ads Conversion | `conversionId`, `conversionLabel`, `conversionValue`, `currencyCode` |
| `sp` | Google Ads Remarketing | `conversionId`, `conversionLabel` |
| `cl` | Conversion Linker | `enableCrossDomain` (bool), `domains` (list) |
| `flc` | Floodlight Counter | `activityGroupTagString`, `activityTagString` |
| `ua` | Universal Analytics (legacy) | **DO NOT CREATE. Propose deletion only.** |

---

## 3. Trigger type constants

Passed as `trigger_type` to `ppc-gtm:create_trigger`.

| Constant | Trigger | Notes |
|---|---|---|
| `pageview` | Page View | Fires as early as possible |
| `domReady` | DOM Ready | Fires when HTML is parsed |
| `windowLoaded` | Window Loaded | Fires when the load event completes |
| `click` | All Element Click | Element click (not just links) |
| `linkClick` | Link Click | Only `<a>` elements; supports outbound link tracking |
| `formSubmission` | Form Submit | Native form submit event |
| `customEvent` | Custom Event | Requires `custom_event_filter` pointing at a dataLayer event name |
| `timer` | Timer | Fires every N milliseconds |
| `historyChange` | History Change | SPA route changes |
| `elementVisibility` | Element Visibility | `sentinel` selector |
| `scrollDepth` | Scroll Depth | `horizontalThresholds` / `verticalThresholds` |
| `youTubeVideo` | YouTube Video | Play/pause/progress |

---

## 4. Variable type constants

Passed as `variable_type` to `ppc-gtm:create_variable`.

| Constant | Variable type | Key parameters |
|---|---|---|
| `v` | Data Layer Variable | `name` = dataLayer key, `dataLayerVersion` = `2` |
| `c` | Constant | `value` |
| `k` | First-Party Cookie | `name` |
| `u` | URL | `component` (e.g. `HOST`, `PATH`), `defaultValue` |
| `jsm` | Custom JavaScript | `javascript` (function body returning a value) |
| `smm` | Lookup Table | `input` (variable ref), `map` (list of `{key, value}`) |
| `e` | Custom Event | `event` |
| `remm` | RegEx Table | `input`, `map`, `fullMatch` |

---

## 5. Baseline change plan (what gtm-setup installs by default)

Use this as the starting point when the user has not customised anything.

### Variables to create

| Name | Type | Parameter |
|---|---|---|
| `CONST - GA4 Measurement ID` | `c` (Constant) | `value = G-XXXXXXXXXX` (from Phase 2) |
| `DL - event` | `v` (Data Layer) | `name = event` |

### Triggers to create

| Name | Type | Notes |
|---|---|---|
| `All Pages - Page View` | `pageview` | No filters; built-in |

### Tags to create

| Name | Type | Firing trigger | Parameters |
|---|---|---|---|
| `Con - GA4 - Config` | `gaawc` | `All Pages - Page View` | `measurementId = {{CONST - GA4 Measurement ID}}`, `sendPageView = true` |

### Optional additions (ask the user)

- `Util - HTML - Consent Mode Init` (`html` tag firing on `All Pages - Page View` with priority 100) if no third-party CMP detected.
- `Con - Meta - Pixel Base` if `meta-pixel-setup` has been run.

---

## 6. Consent Mode v2 stub (AU/NZ default)

Place in a Custom HTML tag named `Util - HTML - Consent Mode Init` firing on `All Pages - Page View` with **Tag firing priority = 100**:

```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('consent', 'default', {
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied',
    'functionality_storage': 'granted',
    'security_storage': 'granted',
    'wait_for_update': 500
  });
  gtag('set', 'ads_data_redaction', true);
</script>
```

This is a default-deny stub. The user's CMP is expected to call `gtag('consent', 'update', {...})` when the user accepts.

---

## 7. Common container audit findings

Use these as the starting point for the diff in Phase 3. Any of these should appear on the change plan:

| Finding | Action |
|---|---|
| Universal Analytics `ua` tag | Propose deletion |
| Tag with no firing trigger | Flag for user review |
| GA4 Config tag on anything except All Pages | Propose moving to All Pages |
| Multiple GA4 Config tags with different measurement IDs | Ask user which is correct |
| Tag names not matching the convention | Propose rename |
| More than one Custom HTML tag firing on All Pages | Audit each for consent / performance impact |
| Floodlight tags without Conversion Linker | Propose adding Conversion Linker |
| `gtm.dom` or `gtm.load` triggers used instead of `All Pages - Page View` | Check that downstream tags still fire correctly |
