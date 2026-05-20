---
name: health-disclaimer
description: Print the standard health-wellness disclaimer block (not medical advice; consult a clinician). Reference text for all health skills.
argument-hint: [no-args]
---

# Health Disclaimer (Reference)

When invoked, output the following block verbatim. Every skill in this plugin must include this disclaimer at the top of its output.

---

> **Important — read first.** The information produced by this plugin is general guidance based on publicly available literature. It is **not personal medical, dietary, or fitness advice** and is not a substitute for assessment by a qualified clinician.
>
> Before making changes to your diet, training, sleep, or supplement intake, please consult a GP, accredited practising dietitian (APD), accredited exercise physiologist (AEP), sleep physician, or pharmacist as relevant. People with pre-existing conditions, those who are pregnant or breastfeeding, on prescription medications, or under 18 should always seek individualised professional advice.
>
> In Australia, the Therapeutic Goods Administration (TGA) regulates therapeutic claims; this plugin does not make therapeutic claims and does not recommend specific brands or products.

---

This skill exists so other skills (e.g. `smart-supplement-stack`, `week-of-meals`) can reference it. It is not intended to be invoked directly by end users.
