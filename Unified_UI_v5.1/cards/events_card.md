
## 🗓️ Events

**Training Timeline**

| Date | Type | Session | Duration | TSS | IF | Notes |
|:--|:--|:--|--:|--:|--:|:--|
{% for e in events %}
| {{e.date}} | {{e.type}} | {{e.name}} | {{e.duration}} | {{e.tss}} | {{e.if}} | {{e.comment}} |
{% endfor %}

**Highlights**
- 🧩 {{weekly_summary}}
- 🛌 Rest Days: {{rest_days}}
- ⏳ Current Day: {{pending_sessions}}
- 🎯 Best Session: {{best_session.name}} ({{best_session.load}} AU)
