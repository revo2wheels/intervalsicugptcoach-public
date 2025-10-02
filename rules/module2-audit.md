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

### Chunking Rule
- All season (42-day) requests must be ingested in **weekly chunks** (6 windows).  
- Each chunk must respect the **Field Lock Rule** (only audit-required fields).  
- After chunk retrieval:  
  - Concatenate all chunks.  
  - Verify DataFrame row count = sum of API counts per chunk.  
- ❌ If any chunk mismatch → halt with error “chunk truncation detected.”  
