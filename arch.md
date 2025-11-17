        ┌──────────────────────────┐
        │        ChatGPT App       │
        │ (User interface + logic) │
        └────────────┬─────────────┘
                     │ HTTPS (Tool call)
                     ▼
        ┌──────────────────────────┐
        │    Render Container      │
        │  (FastAPI + LangServe)   │
        │    ┌────────────────┐    │
        │    │  LangChain     │    │
        │    │  + your repo   │    │
        │    └────────────────┘    │
        │ Executes Python code     │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │     Intervals.icu API    │
        │ (External Data Provider) │
        └──────────────────────────┘


| Component            | Runs code?     | Stores data?     | Controlled by |
| -------------------- | -------------- | ---------------- | ------------- |
| **GitHub**           | ❌              | ✅ (code only)    | You           |
| **Render container** | ✅              | ❌                | You           |
| **LangServe**        | ✅              | ❌                | You           |
| **LangChain**        | ✅ (in-process) | ❌                | You           |
| **ChatGPT**          | ❌              | transient        | OpenAI        |
| **Intervals.icu**    | ✅ (remote API) | ✅ (athlete data) | intervals.icu |
