## 🧩 Audit Summary

{{#if athlete}}
**Athlete:** {{athlete.name}} ({{athlete.country}})  
**Location:** {{athlete.city}}, {{athlete.state}}  
**Timezone:** {{athlete.timezone}}  
![Profile Image]({{athlete.profile_medium}}){width=72 height=72}
{{/if}}

✅ Tier 0–2 checks passed.  
Source = {{data_source}} (verified).  
No event duplication or gap detected.  
Discipline = {{discipline}}.  
Variance < 2 %.
