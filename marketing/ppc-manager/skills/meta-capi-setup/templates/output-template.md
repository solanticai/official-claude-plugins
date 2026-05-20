# Meta CAPI Setup — {{site_name}}

**Pixel ID:** {{pixel_id}}
**Backend:** {{backend_type}}
**Date:** {{DD_MM_YYYY}}

---

## Dedup strategy

- `event_id` source: {{event_id_source}}
- Browser events: {{browser_event_count}}
- Server events: {{server_event_count}}
- Dedup method: matching `event_name` + `event_id`

---

## Events forwarded server-side

| Event | Params | `user_data` fields | EMQ target |
|---|---|---|---|
{{#capi_events}}
| {{name}} | {{params}} | {{user_data_fields}} | ≥{{emq_target}} |
{{/capi_events}}

---

## Implementation

- **Backend:** {{backend_type}}
- **File path:** `{{file_path}}`
- **Deploy target:** {{deploy_target}}
- **Code:** see `scripts/capi_example_server.py` adapted for {{backend_type}}.

---

## Test Events validation

- Test code used: `{{test_code}}`
- Events sent: {{test_events_sent}}
- Events received in Test Events: {{test_events_received}}
- Current EMQ: {{current_emq}}
- Target EMQ: 7.0+

---

## Production checklist

- [{{prod_hash}}] PII hashed (SHA-256, lowercased, trimmed)
- [{{prod_eventid}}] `event_id` matches browser counterpart
- [{{prod_actionsource}}] `action_source = "website"`
- [{{prod_ipua}}] IP and user_agent included
- [{{prod_fbcfbp}}] `fbc` and `fbp` cookies forwarded
- [{{prod_testcode}}] Test event code removed from production
- [{{prod_secrets}}] Access token stored in env vars, not source

---

## Next steps

1. Deploy to production.
2. Monitor Events Manager → Overview for 24 hours.
3. Run `/ppc-manager:meta-events-mapping` to reconcile.
