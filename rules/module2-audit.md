## Audit Enforcement (mandatory)

- Every report must pass audit before generation.

### Execution Rule
- If Code Interpreter enabled → audit must run as Python validation before report.

### Audit Visibility
- Audit must always run and be acknowledged (✅ or ❌).
- Detailed audit trace hidden unless requested with “show audit details.”

### Raw Data Integrity
- API activity count must equal DataFrame row count.  
- ❌ If mismatch → halt with error “filter applied too early.”  
- **Load First, Filter After:** Always ingest the **entire activity dataset** from API before applying any discipline filter. Filters (Cycling, Running, Swimming, Other) apply **after** confirming DataFrame = API.  
- **Row Count Lock:** DataFrame row count must equal API row count before any filtering.  
- **No Truncation / Connector Safety:** Always ingest full paginated API result set. No manual subsetting; always iterate until fully ingested.  
- ❌ If any discipline rows are missing in the first pass, halt and retry until complete.  

### Discipline Totals
- Always compute Cycling, Running, Swimming, Other separately.  
- “Other” = all non-cycling/running/swimming.  
- If Other has load or hours >0 → must show:  
  - Event log: `🟢 Other: {event}`  
  - Stats: `otherKmBlock: ({otherKm} km other)`  
- If Other = 0 → “None detected.”  
- Combined totals = Cycling+Running+Swimming only. Other excluded but still counted in CTL/ATL/Form.  
- ❌ Omit Other when >0 → audit fail.  

### Combined Totals
- Verify combined total = exact sum of subtotals. ❌ Halt if mismatch.  

### Unit Conversions
- Validate sec→h and m→km conversions.  

### Dataset Completeness
- DataFrame min/max dates = requested window.  
- All discipline categories (Cycling, Running, Swimming, Other) present, even if zero.  

### Failure Handling
- ❌ Any check fails → halt.  

### Hard Stop Rule
- ❌ Halt if:  
  1. DataFrame count ≠ API count  
  2. Any discipline missing  
  3. Combined totals ≠ sum of subtotals  

### Chunking & Retry Rule (Enforced)
- Any report window longer than 7 days must be ingested in **weekly chunks** (7-day windows).  
- Default: If the user requests a “42-day season report” without explicit dates, always resolve to today−41 → today.  
- Each chunk must respect the **Field Lock Rule** (only audit-required fields).  
- GPT must:  
  1. Automatically split the requested date range into consecutive 7-day windows.  
  2. Fetch all chunks without prompting the user.  
  3. Concatenate all chunks into a master DataFrame.  
  4. Verify DataFrame row count = sum of API counts across all chunks.  

- Retry Handling:  
  - If a 7-day chunk fetch fails (connector/client error), retry automatically up to 10 times.  
  - If retries succeed, continue concatenation.  
  - ❌ If 10 retries fail for a chunk, halt with:  
    “Error: no data returned after 10 retries (chunk {start} → {end}).”  

- ❌ If GPT attempts to fetch >7 days in a single call, audit fails.  
- ❌ If GPT prompts the user to confirm chunking or retries, audit fails.  
- ❌ If any concatenated DataFrame row count mismatches sum of chunks, halt with:  
    “Error: chunk truncation detected.”  

### Template Compliance Rule
- When a user requests a report and specifies a type (Weekly, Season, Block, Event):
  - Audit must verify that the correct type-specific template was applied.
  - If only the General Report Template is used without the required type-specific sections (e.g. Phases for Season, Event log for Event):
    ❌ Halt output and return:
    “Error: Report type requested but only general template applied. Season/Block/Event template required.”
    
### Default Window Rule (Enforced)
- If the user requests a “42-day season report” without explicit dates:
  ✅ Automatically set the window to today−41 → today.  
- ❌ If GPT requests user input for dates instead of applying this default, audit fails with:  
  “Error: Default 42-day window (today−41 → today) not applied.”  



