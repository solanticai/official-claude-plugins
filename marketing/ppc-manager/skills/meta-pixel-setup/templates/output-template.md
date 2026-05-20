# Meta Pixel Setup — {{site_name}}

**Pixel ID:** {{pixel_id}}
**Container:** {{container_public_id}}
**Date:** {{DD_MM_YYYY}}

---

## Events installed

| Event | Trigger | Params | eventID used |
|---|---|---|---|
{{#events}}
| {{name}} | {{trigger}} | {{params}} | {{event_id_source}} |
{{/events}}

---

## AEM priority ranking (top 8)

1. {{aem_1}}
2. {{aem_2}}
3. {{aem_3}}
4. {{aem_4}}
5. {{aem_5}}
6. {{aem_6}}
7. {{aem_7}}
8. {{aem_8}}

---

## Verification

- [{{verify_base}}] Base pixel fires on All Pages
- [{{verify_events}}] All event tags fire in GTM preview
- [{{verify_ids}}] Every event has `eventID` populated
- [{{verify_em}}] Events appear in Meta Events Manager Test Events

---

## Next steps

1. Run `/ppc-manager:meta-capi-setup` for server-side tracking.
2. Run `/ppc-manager:meta-events-mapping` to reconcile with GA4.
3. Rank events for AEM priority in Events Manager.
