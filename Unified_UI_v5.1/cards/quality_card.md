## 🎯 Training Quality

| Day | Session | RPE | Feel | IF | Compliance |
|:--|:--|:--:|:--:|--:|--:|
{{#each quality}}
| {{this.date}} | {{this.name}} | {{this.rpe}} | {{this.feel}} | {{this.if}} | {{this.compliance}} |
{{/each}}

**Interpretation**  
Average RPE = {{avg_rpe}} Mean Feel = {{avg_feel}}  
Execution Quality = {{execution_score}} / 100  
→ {{execution_comment}}
