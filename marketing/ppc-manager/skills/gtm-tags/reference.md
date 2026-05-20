# GTM Tags — Reference

Recipe-style reference for the tag patterns this skill installs. Each recipe is a complete, ready-to-use specification.

## Contents

1. [GA4 Event tag (generic)](#1-ga4-event-tag-generic)
2. [Meta Pixel base tag](#2-meta-pixel-base-tag)
3. [Meta Pixel event tag](#3-meta-pixel-event-tag)
4. [Google Ads conversion tag](#4-google-ads-conversion-tag)
5. [Google Ads Conversion Linker](#5-google-ads-conversion-linker)
6. [LinkedIn Insight Tag](#6-linkedin-insight-tag)
7. [TikTok Pixel](#7-tiktok-pixel)
8. [Scroll Depth tracking](#8-scroll-depth-tracking)
9. [Form Submission tracking](#9-form-submission-tracking)
10. [Conversion-tracking audit checklist](#10-conversion-tracking-audit-checklist)

---

## 1. GA4 Event tag (generic)

**Tag type:** `gaawe` (GA4 Event)

**Parameters:**
```json
{
  "measurementIdOverride": "{{CONST - GA4 Measurement ID}}",
  "eventName": "purchase",
  "eventSettingsVariable": "{{CONST - GA4 Event Settings}}",
  "eventParameters": [
    { "name": "currency", "value": "{{DL - currency}}" },
    { "name": "value", "value": "{{DL - value}}" },
    { "name": "transaction_id", "value": "{{DL - transaction_id}}" },
    { "name": "items", "value": "{{DL - items}}" }
  ]
}
```

**Firing trigger:** Custom Event matching `event equals purchase`.

**Name:** `Con - GA4 - Event - purchase`

---

## 2. Meta Pixel base tag

**Tag type:** `html` (Custom HTML)

**HTML body:**

```html
<script>
!function(f,b,e,v,n,t,s){
  if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{{CONST - Meta Pixel ID}}');
fbq('track', 'PageView');
</script>
```

**Firing trigger:** `All Pages - Page View`

**Name:** `Con - Meta - Pixel Base`

---

## 3. Meta Pixel event tag

**Tag type:** `html` (Custom HTML)

**HTML body (example: Purchase):**

```html
<script>
fbq('track', 'Purchase', {
  value: {{DL - value}},
  currency: '{{DL - currency}}',
  content_ids: {{JS - items to content_ids}},
  content_type: 'product',
  num_items: {{JS - items length}}
}, { eventID: '{{DL - event_id}}' });
</script>
```

**Firing trigger:** Custom Event matching `event equals purchase`

**Name:** `Con - Meta - Event - Purchase`

**Notes:**
- `eventID` is critical — it matches Meta Pixel browser events to Meta CAPI server events for deduplication.
- The `JS - items to content_ids` variable is a small Custom JS variable:

```js
function() {
  var items = {{DL - items}} || [];
  return items.map(function(i) { return i.item_id; });
}
```

---

## 4. Google Ads conversion tag

**Tag type:** `awct` (Google Ads Conversion Tracking)

**Parameters:**
```json
{
  "conversionId": "AW-1234567890",
  "conversionLabel": "abc_def_ghi",
  "conversionValue": "{{DL - value}}",
  "currencyCode": "{{DL - currency}}",
  "orderId": "{{DL - transaction_id}}",
  "enableConversionLinker": "true"
}
```

**Firing trigger:** Custom Event matching `event equals purchase`

**Name:** `Con - Google Ads - Purchase`

**Prerequisite:** `Con - Google Ads - Conversion Linker` must exist (see Recipe 5).

---

## 5. Google Ads Conversion Linker

**Tag type:** `cl` (Conversion Linker)

**Parameters:**
```json
{
  "enableCrossDomain": "true",
  "conversionCookiePrefix": "_gcl"
}
```

**Firing trigger:** `All Pages - Page View`

**Name:** `Con - Google Ads - Conversion Linker`

**Notes:** Required by every Google Ads tag that needs cross-domain conversion tracking. Install once, never touch again.

---

## 6. LinkedIn Insight Tag

**Tag type:** `html` (Custom HTML)

**HTML body:**

```html
<script type="text/javascript">
_linkedin_partner_id = "{{CONST - LinkedIn Partner ID}}";
window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
window._linkedin_data_partner_ids.push(_linkedin_partner_id);
</script>
<script type="text/javascript">
(function(l) {
  if (!l) { window.lintrk = function(a,b){window.lintrk.q.push([a,b])};
  window.lintrk.q=[]}
  var s = document.getElementsByTagName("script")[0];
  var b = document.createElement("script");
  b.type = "text/javascript"; b.async = true;
  b.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
  s.parentNode.insertBefore(b, s);
})(window.lintrk);
</script>
```

**Firing trigger:** `All Pages - Page View`

**Name:** `Con - LinkedIn - Insight Tag`

---

## 7. TikTok Pixel

**Tag type:** `html` (Custom HTML)

**HTML body:**

```html
<script>
!function (w, d, t) {
  w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e},ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=i,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};var o=document.createElement("script");o.type="text/javascript",o.async=!0,o.src=i+"?sdkid="+e+"&lib="+t;var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};
  ttq.load('{{CONST - TikTok Pixel Code}}');
  ttq.page();
}(window, document, 'ttq');
</script>
```

**Firing trigger:** `All Pages - Page View`

**Name:** `Con - TikTok - Pixel Base`

---

## 8. Scroll Depth tracking

**Built-in trigger type:** Scroll Depth (`scrollDepth`)

**Trigger params:**
```json
{
  "verticalThresholdsPercentagesEnabled": "true",
  "verticalThresholdsPercentages": "25,50,75,90",
  "triggerConditions": "all pages"
}
```

**Tag type:** `gaawe` (GA4 Event)

**Tag params:**
```json
{
  "measurementIdOverride": "{{CONST - GA4 Measurement ID}}",
  "eventName": "scroll_depth",
  "eventParameters": [
    { "name": "percent_scrolled", "value": "{{Scroll Depth Threshold}}" }
  ]
}
```

**Firing trigger:** the Scroll Depth trigger above

**Name:** `Mkt - GA4 - Scroll Depth`

---

## 9. Form Submission tracking

**Trigger type:** Form Submit (`formSubmission`)

**Trigger params:**
```json
{
  "waitForTags": "true",
  "waitForTagsTimeout": "2000",
  "triggerConditions": [
    { "name": "Form ID", "condition": "equals", "value": "contact-form" }
  ]
}
```

**Tag type:** `gaawe`

**Tag params:**
```json
{
  "measurementIdOverride": "{{CONST - GA4 Measurement ID}}",
  "eventName": "form_submit",
  "eventParameters": [
    { "name": "form_id", "value": "{{Form ID}}" },
    { "name": "form_name", "value": "{{Form Element}}" }
  ]
}
```

**Name:** `Con - GA4 - Event - form_submit`

---

## 10. Conversion-tracking audit checklist

Use this list in audit mode to diff against an existing container:

| Item | Expected | Remediation if missing |
|---|---|---|
| GA4 Config tag on All Pages | exactly 1 | run `gtm-setup` |
| Conversion Linker tag on All Pages | exactly 1 | install Recipe 5 |
| GA4 Event tag per conversion event | one per `purchase`/`generate_lead`/`sign_up` | install Recipe 1 per event |
| Meta Pixel base on All Pages | 1 (if running Meta Ads) | install Recipe 2 |
| Meta Pixel event tag per conversion | one per matching GA4 event | install Recipe 3 |
| Google Ads conversion tag per conversion | one per conversion action in Google Ads | install Recipe 4 |
| `eventID` on Meta Pixel events | must use `{{DL - event_id}}` | update the tag |
| Legacy UA tags | zero | delete |
| Tags with no firing trigger | zero | delete or attach trigger |
| Tags not following naming convention | zero | rename via `update_tag` |
