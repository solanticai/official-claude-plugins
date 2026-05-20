# Plain-Language Questionnaire

Use these questions via `AskUserQuestion` when repo signals are missing. Ask **at most seven**. Skip any question already answered by the stack fingerprint or by `$ARGUMENTS`.

---

### Q1 — Who uses this app?

| Option | Interpretation |
|---|---|
| Nobody yet — I'm still building it | Pre-launch |
| Just me | Personal tool |
| A small team (under 100 people) | Internal tool |
| Some paying customers (100–10,000) | Early stage |
| Many users (10,000+) | Growth stage |

### Q2 — Where does it run?

| Option | Interpretation |
|---|---|
| Vercel / Netlify / Cloudflare Pages | Edge PaaS |
| Heroku / Fly / Render | Container PaaS |
| A cloud VM I set up (EC2, Droplet) | Self-managed VM |
| Kubernetes (EKS, GKE, AKS, self-hosted) | Kubernetes |
| My own laptop — I haven't deployed it | Pre-launch |
| I'm not sure | Unknown |

### Q3 — How do you ship a change today?

| Option | Interpretation |
|---|---|
| I push to main and my host auto-deploys | PaaS auto-deploy |
| I run a script in my terminal | Manual scripted deploy |
| CI runs tests and deploys for me | Full CI/CD |
| Someone else handles it | Delegated |
| I haven't deployed anything yet | Pre-deploy |

### Q4 — Has the app ever gone down in a way users noticed?

| Option | Interpretation |
|---|---|
| Never | Either low stakes or well-run |
| Once or twice | Normal for an early-stage app |
| Every few weeks | Reliability debt |
| Every week or more often | Urgent reliability work |

### Q5 — If something breaks at 3am, who fixes it and how?

| Option | Interpretation |
|---|---|
| Me — I'll see it in the morning | Best-effort |
| Me — I have alerts set up | On-call of one |
| We have an on-call rotation | Team on-call |
| Nothing breaks at 3am (hope) | Pre-production maturity |

### Q6 — How many people can deploy to production?

| Option | Interpretation |
|---|---|
| Just me | Solo |
| 2–5 people | Small team |
| A whole team with approval gates | Formal process |
| Everyone with GitHub access can | Loose |

### Q7 — If the person who knows this app best left tomorrow, how long would recovery take?

| Option | Interpretation |
|---|---|
| A few hours — the docs are good | Well-documented |
| A few days — the setup is mostly standard | OK |
| A week or two — there's tribal knowledge | Docs debt |
| Months — nobody else knows how it works | Urgent docs work |

### Q8 — Is there anything you worry about breaking?

Free-text. Used verbatim in the report's "What you worry about" section.

### Q9 — What's the goal of this assessment?

| Option | Interpretation |
|---|---|
| I'm pre-launch and want to know what to set up | Greenfield |
| I'm live and want to know what's most broken | Reactive |
| I'm hiring and want to know what work is needed | Hiring |
| A customer / investor asked | External pressure |
