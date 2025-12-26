// ================================================================
// CLOUDFLARE WORKER V17 INTERVALS ICU RAILWAY
// ================================================================
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    // ================================================================
    // 🟢 PUBLIC OAUTH ROUTES — HARD EXIT, NO AUTH, NO HELPERS
    // ================================================================
    if (pathname.startsWith("/oauth/authorize")) {
      const target = new URL(
        request.url.replace(
          /^https:\/\/intervalsicugptcoach\.clive-a5a\.workers\.dev/,
          "https://intervals.icu"
        )
      );
      target.searchParams.set(
        "redirect_uri",
        "https://chat.openai.com/aip/g-3b0244cf708774fb9151458671c462eb5460f41e/oauth/callback"
      );
      return Response.redirect(target.toString(), 302);
    }

    if (pathname.startsWith("/oauth/callback")) {
      return Response.redirect(
        "https://chat.openai.com/aip/g-3b0244cf708774fb9151458671c462eb5460f41e/oauth/callback" +
          new URL(request.url).search,
        302
      );
    }

    if (pathname.startsWith("/api/oauth/token")) {
      const resp = await fetch("https://intervals.icu/api/oauth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: await request.text()
      });

      const json = await resp.json();

      return new Response(JSON.stringify(json), {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // ================================================================
    // 🌐 CORS preflight support
    // ================================================================
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, POST, OPTIONS"
        }
      });
    }

    // ================================================================
    // 🚦 ROUTE TO RAILWAY (PROD OR STAGING)
    // ================================================================
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    let RAILWAY_BASE = "https://intervalsicugptcoach-public-production.up.railway.app";
    let ENVIRONMENT = "production"; // default

    // Extract parameters
    const stagingParam = url.searchParams.get("staging");
    const ownerParam = url.searchParams.get("owner");
    const userAgent = request.headers.get("User-Agent") || "unknown";
    const referer = request.headers.get("Referer") || "none";
    const ip = request.headers.get("CF-Connecting-IP") || "n/a";
    const authHeader = request.headers.get("Authorization");

    // ----------------------------------------------------------------
    // 🔐 OWNER-BASED STAGING ACCESS (for ChatGPT & manual tests)
    // ----------------------------------------------------------------
    if (stagingParam === "1" && ownerParam === "clive") {
      RAILWAY_BASE = "https://intervalsicugptcoach-public-staging.up.railway.app";
      ENVIRONMENT = "staging-owner";
    }
    // Unauthorized attempts to staging → strip parameter, stay prod
    else if (stagingParam === "1") {
      url.searchParams.delete("staging");
      ENVIRONMENT = "blocked-staging";
    }

    // ----------------------------------------------------------------
    // 🧭 Debug Logging
    // ----------------------------------------------------------------
    console.log(
      `[ROUTE → ${ENVIRONMENT.toUpperCase()}] ${url.pathname}${url.search}` +
      ` | Target=${RAILWAY_BASE}` +
      ` | UA=${userAgent}` +
      ` | Ref=${referer}` +
      ` | IP=${ip}` +
      ` | Auth=${authHeader ? "✅" : "❌"}` +
      (ownerParam ? ` | Owner=${ownerParam}` : "")
    );


    // ================================================================
    // Helpers
    // ================================================================
    const getDate = (daysAgo) => {
      const d = new Date();
      d.setUTCDate(d.getUTCDate() - daysAgo);
      return d.toISOString().split("T")[0];
    };

    const normaliseDateParams = (params, defaultDays) => {
      const oldest = params.get("oldest");
      const newest = params.get("newest");
      const isDate = (x) => /^\d{4}-\d{2}-\d{2}$/.test(x);
      return {
        oldest: isDate(oldest) ? oldest : getDate(defaultDays),
        newest: isDate(newest) ? newest : getDate(0)
      };
    };
    // ================================================================
    // 📆 DEFAULT DATA WINDOWS (centralized config)
    // ================================================================
    // These define how far back/forward each dataset should go.
    // All durations are in days.
    const DATA_WINDOWS = {
      LIGHT_DAYS: 90,    // historical light summary range
      FULL_DAYS: 7,      // detailed full activity window
      WELLNESS_DAYS: 42, // wellness tracking window
      CALENDAR_DAYS: 14  // future planned event lookahead
    };
    // ================================================================
    // 📅 FUTURE CALENDAR RANGE HELPER
    // ================================================================
    const getFutureDateRange = (daysAhead = DATA_WINDOWS.CALENDAR_DAYS) => {
      const today = new Date();
      const start = today.toISOString().slice(0, 10);
      const end = new Date(today.getTime() + daysAhead * 86400000)
        .toISOString()
        .slice(0, 10);
      return { start, end };
    };
    // ================================================================
    // 📅 Fetch calendar for explicit start → end range (quiet, production-safe)
    // ================================================================
    const fetchFutureCalendarFromRange = async (start, end) => {
      try {
        // 1️⃣ WORKOUTS
        const workoutsReq = fetch(
          `${INTERVALS_API_BASE}/athlete/0/events?oldest=${start}&newest=${end}&category=WORKOUT`,
          { headers: buildAuthHeaders() }
        );

        // 2️⃣ RACES (RACE, A/B/C RACE — parallelized)
        const raceCats = ["RACE", "A RACE", "B RACE", "C RACE"];
        const raceReqs = raceCats.map(cat =>
          fetch(
            `${INTERVALS_API_BASE}/athlete/0/events?oldest=${start}&newest=${end}&category=${encodeURIComponent(cat)}`,
            { headers: buildAuthHeaders() }
          )
        );

        // 3️⃣ EVERYTHING ELSE (no category filter)
        const allReq = fetch(
          `${INTERVALS_API_BASE}/athlete/0/events?oldest=${start}&newest=${end}`,
          { headers: buildAuthHeaders() }
        );

        // Wait for all in parallel
        const [workoutsRes, raceResList, allRes] = await Promise.all([
          workoutsReq,
          Promise.all(raceReqs),
          allReq
        ]);

        // Parse safely — handle any non-200s gracefully
        const workoutsTxt = workoutsRes.ok ? await workoutsRes.text() : "[]";
        const raceTxts = await Promise.all(
          raceResList.map(r => (r.ok ? r.text() : "[]"))
        );
        const allTxt = allRes.ok ? await allRes.text() : "[]";

        // Safely parse each block
        const workouts = safeParse(workoutsTxt, "array");
        const races = raceTxts.flatMap(txt => safeParse(txt, "array"));
        const all = safeParse(allTxt, "array");

        // Exclude duplicates and known categories
        const others = all.filter(
          e => !["WORKOUT", "RACE", "A RACE", "B RACE", "C RACE"].includes(e.category)
        );

        // Merge all quietly (even if any group is empty)
        const calendar = [...workouts, ...races, ...others].sort(
          (a, b) => new Date(a.start_date_local) - new Date(b.start_date_local)
        );

        // Compact summary
        console.log(
          `[CALENDAR RANGE] ✅ ${calendar.length} total (${workouts.length} workouts, ${races.length} races, ${others.length} others) for ${start} → ${end}`
        );

        return calendar;
      } catch (err) {
        // Contextual error log — minimal noise
        console.error("[CALENDAR RANGE] ❌", err.message, { start, end });
        return [];
      }
    };

    // ================================================================
    // 📏 JSON size helpers (byte-accurate)
    // ================================================================
    const jsonSize = (obj) => {
      try {
        return new TextEncoder().encode(JSON.stringify(obj)).length;
      } catch {
        return -1;
      }
    };
    // ================================================================
    // 🔒 CANONICAL ATHLETE EXTRACTION (NO SAFE PARSE)
    // ================================================================
    const extractAthlete = (profTxt) => {
      const athlete = JSON.parse(profTxt);

      if (!athlete || typeof athlete !== "object") {
        throw new Error("[FATAL] Athlete profile is not an object");
      }

      if (!athlete.timezone) {
        throw new Error(
          "[FATAL] Athlete missing timezone — refusing to continue"
        );
      }

      return athlete;
    };
    // ================================================================
    // 🔥 Correct safeParse with expected type
    // ================================================================
    const safeParse = (txt, type = "array") => {
      if (!txt || txt.trim() === "") {
        return type === "array" ? [] : {};
      }
      try {
        const parsed = JSON.parse(txt);
        if (parsed === null) return type === "array" ? [] : {};
        if (Array.isArray(parsed)) return parsed;
        if (typeof parsed === "object") return parsed;
      } catch (_) {}
      return type === "array" ? [] : {};
    };

    // ================================================================
    // 🔥 Unified payload logger (ENVIRONMENT-aware + color-coded)
    // ================================================================
    const logPayload = (tag, payload, athleteRawText = "", routeTarget) => {
      // Auto-fill the route target if missing
      if (!routeTarget) routeTarget = ENVIRONMENT || "unknown";

      let envTag = "⚪️";
      if (routeTarget.includes("prod")) envTag = "🟢";
      else if (routeTarget.includes("staging")) envTag = "🟣";
      else if (routeTarget.includes("blocked")) envTag = "🔒";

      // === Byte size accounting ===
      const sizes = {
        athlete: jsonSize(payload.athlete),
        activities_light: jsonSize(payload.activities_light),
        activities_full: jsonSize(payload.activities_full),
        wellness: jsonSize(payload.wellness),
        calendar: jsonSize(payload.calendar), // 👈 added
        total: jsonSize(payload),
      };

      // === Row counts ===
      const rows = {
        athlete: payload.athlete ? 1 : 0,
        light: Array.isArray(payload.activities_light)
          ? payload.activities_light.length
          : 0,
        full: Array.isArray(payload.activities_full)
          ? payload.activities_full.length
          : 0,
        wellness: Array.isArray(payload.wellness)
          ? payload.wellness.length
          : 0,
        calendar: Array.isArray(payload.calendar)
          ? payload.calendar.length
          : 0, // 👈 added
      };

      // === Compact summary ===
      const rowSummary = `rows(light=${rows.light}, full=${rows.full}, well=${rows.wellness}, cal=${rows.calendar})`;

      // === Emit structured log ===
      console.log(
        JSON.stringify({
          message: `${envTag} [${tag}] ${routeTarget} | ${rowSummary}`,
          range: payload.range,
          athlete_id: payload.athlete?.id ?? "<missing>",
          sizes,
          rows,
          athlete_raw_preview: athleteRawText
            ? athleteRawText.slice(0, 200)
            : "<no raw>",
        })
      );
    };


    // ================================================================
    // 🔥 callRailway — passes ENVIRONMENT automatically
    // ================================================================
    const callRailway = async (payload, tag, athleteRawText = "") => {
      logPayload(tag, payload, athleteRawText, ENVIRONMENT);

      const resp = await fetch(`${RAILWAY_BASE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const text = await resp.text();
      const envTag =
        ENVIRONMENT.includes("prod")
          ? "🟢"
          : ENVIRONMENT.includes("staging")
          ? "🟣"
          : "🔒";

      console.log(`${envTag} [${tag}] Railway returned ${resp.status} (${text.length} bytes)`);

      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    };

    // ================================================================
    // 🧠 UNIFIED AUTH HANDLING (Corrected)
    // ================================================================
    let bearerToken = null;

    // 1️⃣ Always prefer the Worker-stored secret token
    if (env.ICU_OAUTH && env.ICU_OAUTH.trim() !== "") {
      bearerToken = `Bearer ${env.ICU_OAUTH.trim()}`;
      console.log("[AUTH] Using ICU_OAUTH from Worker environment");
    }

    // 2️⃣ If ChatGPT or local Python sends an Authorization header, override
    if (authHeader && authHeader.startsWith("Bearer ")) {
      bearerToken = authHeader.trim();
      console.log("[AUTH] Overriding with inbound Authorization header");
    }

    // 3️⃣ If still nothing → fail explicitly (should never happen)
    if (!bearerToken) {
      console.log("[AUTH] ERROR — No Authorization token available");
      return new Response(
        JSON.stringify({ error: "No OAuth token available for Intervals.icu" }),
        { status: 401 }
      );
    }

    // ================================================================
    // Helpers
    // ================================================================
    const buildAuthHeaders = () => {
      const h = new Headers();
      h.set("Authorization", bearerToken);
      h.set("Accept", "application/json");
      return h;
    };

    // ================================================================
    // 📅 Unified calendar fetch — pulls WORKOUT + RACE + OTHER (quiet, production-safe)
    // ================================================================
    const fetchFutureCalendar = async (daysAhead = DATA_WINDOWS.CALENDAR_DAYS) => {
      const { start: calStart, end: calEnd } = getFutureDateRange(daysAhead);

      try {
        // 1️⃣ WORKOUTS (single category)
        const workoutsReq = fetch(
          `${INTERVALS_API_BASE}/athlete/0/events?oldest=${calStart}&newest=${calEnd}&category=WORKOUT`,
          { headers: buildAuthHeaders() }
        );

        // 2️⃣ RACES (RACE, A/B/C RACE — parallelized)
        const raceCats = ["RACE", "A RACE", "B RACE", "C RACE"];
        const raceReqs = raceCats.map(cat =>
          fetch(
            `${INTERVALS_API_BASE}/athlete/0/events?oldest=${calStart}&newest=${calEnd}&category=${encodeURIComponent(cat)}`,
            { headers: buildAuthHeaders() }
          )
        );

        // 3️⃣ EVERYTHING ELSE (no category filter)
        const allReq = fetch(
          `${INTERVALS_API_BASE}/athlete/0/events?oldest=${calStart}&newest=${calEnd}`,
          { headers: buildAuthHeaders() }
        );

        // Wait for all in parallel
        const [workoutsRes, raceResList, allRes] = await Promise.all([
          workoutsReq,
          Promise.all(raceReqs),
          allReq
        ]);

        // Parse safely — handle any non-200s gracefully
        const workoutsTxt = workoutsRes.ok ? await workoutsRes.text() : "[]";
        const raceTxts = await Promise.all(
          raceResList.map(r => (r.ok ? r.text() : "[]"))
        );
        const allTxt = allRes.ok ? await allRes.text() : "[]";

        // Safely parse each block
        const workouts = safeParse(workoutsTxt, "array");
        const races = raceTxts.flatMap(txt => safeParse(txt, "array"));
        const all = safeParse(allTxt, "array");

        // Filter out duplicates and known categories
        const others = all.filter(
          e => !["WORKOUT", "RACE", "A RACE", "B RACE", "C RACE"].includes(e.category)
        );

        // Merge all and sort chronologically
        const calendar = [...workouts, ...races, ...others].sort(
          (a, b) => new Date(a.start_date_local) - new Date(b.start_date_local)
        );

        // Compact success log — one per call
        console.log(
          `[CALENDAR] ✅ ${calendar.length} total (${workouts.length} workouts, ${races.length} races, ${others.length} others) for ${calStart} → ${calEnd}`
        );

        return calendar;
      } catch (err) {
        console.error("[CALENDAR] ❌ fetchFutureCalendar failed:", err.message, { calStart, calEnd });
        return [];
      }
    };


    // ================================================================
    // INTERNAL DATA ROUTES — UPDATED TO USE /events API
    // ================================================================
    const athleteIdMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteIdMatch ? athleteIdMatch[1] : "0";

    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      // --- 1️⃣ Parse query or JSON body for overrides ---
      let bodyOverrides = {};
      if (request.method === "POST") {
        try {
          bodyOverrides = await request.json();
        } catch {
          bodyOverrides = {};
        }
      }

      const queryOldest = url.searchParams.get("oldest");
      const queryNewest = url.searchParams.get("newest");
      const queryFields = url.searchParams.get("fields");

      // --- 2️⃣ Default date range ---
      const { oldest: defaultOldest, newest: defaultNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);

      const oldest = bodyOverrides.oldest || queryOldest || defaultOldest;
      const newest = bodyOverrides.newest || queryNewest || defaultNewest;

      // --- 3️⃣ Canonical field whitelist (Intervals.icu-supported) ---
      const validFieldSet = new Set([
        "id","start_date_local","name","type","sport_type",
        "distance","moving_time","icu_training_load","IF",
        "average_heartrate","average_cadence","icu_average_watts",
        "strain_score","trimp","hr_load",
        "icu_efficiency_factor","icu_intensity","icu_power_hr",
        "decoupling","icu_pm_w_prime","icu_w_prime",
        "icu_max_wbal_depletion","icu_joules_above_ftp",
        "total_elevation_gain","calories","VO2MaxGarmin", "VO2MaxWhoop", "HRTLNDLT1",
        "source","device_name"
      ]);

      // --- 4️⃣ Field alias map (handles ChatGPT and API variances) ---
      const fieldAliases = {
        // ───── Core training metrics ─────
        "tss": "icu_training_load",
        "load": "icu_training_load",
        "training_load": "icu_training_load",
        "stress": "icu_training_load",

        // ───── Duration variants ─────
        "duration": "moving_time",
        "time": "moving_time",
        "elapsed": "moving_time",
        "moving_time": "moving_time",
        "duration_seconds": "moving_time",
        "duration_minutes": "moving_time",   // convert /60 in code

        // ───── Heart-rate variants ─────
        "hr": "average_heartrate",
        "heartrate": "average_heartrate",
        "avg_hr": "average_heartrate",
        "average_hr": "average_heartrate",
        "hr_avg": "average_heartrate",
        "heart_rate": "average_heartrate",

        // ───── Power / Watts ─────
        "watts": "icu_average_watts",
        "power": "icu_average_watts",
        "avg_power": "icu_average_watts",
        "average_power": "icu_average_watts",
        "power_avg": "icu_average_watts",

        // ───── Cadence ─────
        "cadence": "average_cadence",
        "cad": "average_cadence",
        "avg_cadence": "average_cadence",
        "cadence_avg": "average_cadence",

        // ───── Distance ─────
        "distance": "distance",
        "distance_m": "distance",
        "distance_km": "distance",   // divide by 1000
        "dist": "distance",

        // ───── Elevation / Climb ─────
        "elevation": "total_elevation_gain",
        "elevation_gain": "total_elevation_gain",
        "elev_gain": "total_elevation_gain",
        "climb": "total_elevation_gain",

        // ───── Intensity / Efficiency ─────
        "if": "IF",
        "intensity_factor": "IF",
        "efficiency": "icu_efficiency_factor",
        "efficiency_factor": "icu_efficiency_factor",
        "decoupling": "decoupling",

        // ───── Metadata ─────
        "title": "name",
        "name": "name",
        "activity": "name",
        "date": "start_date_local",
        "start": "start_date_local",
        "sport": "type",
        "type": "type",
        "source": "source",
        "platform": "source",
        "device": "device_name",

        // ───── Energy / Calories ─────
        "calories": "calories",
        "kcal": "calories",
        "energy": "calories",

        // ───── TRIMP / Strain / HR Load ─────
        "trimp": "trimp",
        "strain": "strain_score",
        "strain_score": "strain_score",
        "hr_load": "hr_load",

        // ───── VO₂-related ─────
        "vo2max": "VO2MaxGarmin",
        "vo2_max": "VO2MaxGarmin",
        "vo2maxgarmin": "VO2MaxGarmin",
        "vo2max_garmin": "VO2MaxGarmin",
        "vo2max_garmin_connect": "VO2MaxGarmin",

        // ───── W′ (anaerobic work capacity) ─────
        "wprime": "icu_w_prime",
        "w_prime": "icu_w_prime",

        // ───── Optional Tier-1 / extended ─────
        "notes": "notes",              // full dataset only
        "comment": "notes",
        "description": "notes"
      };

      const defaultFields = Array.from(validFieldSet).join(",");

      // --- 5️⃣ Resolve requested fields ---
      let requestedFields = (bodyOverrides.fields || queryFields || defaultFields)
        .split(",")
        .map(f => f.trim().toLowerCase())
        .filter(Boolean)
        .map(f => fieldAliases[f] || f);

      // --- 6️⃣ Filter to valid ones only ---
      const filteredFields = requestedFields.filter(f => validFieldSet.has(f));
      const invalidFields = requestedFields.filter(f => !validFieldSet.has(f));

      // --- 7️⃣ Log alias usage & dropped fields ---
      if (invalidFields.length > 0) {
        console.warn(`[T0-LIGHT] ⚠️ Dropping invalid fields: ${invalidFields.join(", ")}`);
      }

      const appliedAliases = Object.entries(fieldAliases)
        .filter(([alias, canonical]) => requestedFields.includes(canonical))
        .map(([alias]) => alias);
      if (appliedAliases.length > 0) {
        console.log(`[T0-LIGHT] 🧩 Applied alias mappings for: ${appliedAliases.join(", ")}`);
      }

      // --- 8️⃣ Always include essential fields for consistency ---
      const essentialFields = ["id", "start_date_local", "type", "name"];
      for (const f of essentialFields) {
        if (!filteredFields.includes(f)) filteredFields.push(f);
      }

      // --- 9️⃣ Finalize safe field string ---
      const fields = filteredFields.join(",");

      // --- 🔟 Build & call API ---
      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${encodeURIComponent(oldest)}` +
        `&newest=${encodeURIComponent(newest)}` +
        `&fields=${encodeURIComponent(fields)}`;

      const r = await fetch(target, { headers: buildAuthHeaders() });
      const text = await r.text();
      const sizeKB = (new TextEncoder().encode(text).length / 1024).toFixed(1);

      console.log(`[T0-LIGHT] → ${target} (${sizeKB} KB)`);

      return new Response(text, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }


    // === FULL ACTIVITIES ===
    if (pathname.startsWith(`/athlete/${athleteId}/activities`) && !pathname.includes("t0light")) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${oldest}&newest=${newest}`;

      const r = await fetch(target, { headers: buildAuthHeaders() });
      const text = await r.text();
      const sizeKB = (new TextEncoder().encode(text).length / 1024).toFixed(1);

      console.log(`[FULL] → ${target} (${sizeKB} KB)`);

      return new Response(text, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // === WELLNESS ===
    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, DATA_WINDOWS.WELLNESS_DAYS);
      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness` +
        `?oldest=${oldest}&newest=${newest}`;

      const r = await fetch(target, { headers: buildAuthHeaders() });
      const text = await r.text();
      const sizeKB = (new TextEncoder().encode(text).length / 1024).toFixed(1);

      console.log(`[WELLNESS] → ${target} (${sizeKB} KB)`);

      return new Response(text, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // === CALENDAR (planned workouts) → EVENTS API ===
    if (pathname.startsWith(`/athlete/${athleteId}/calendar`)) {
      const calendar = await fetchFutureCalendar(DATA_WINDOWS.CALENDAR_DAYS);
      const sizeKB = (JSON.stringify(calendar).length / 1024).toFixed(1);
      console.log(`[CALENDAR] → (payload=${sizeKB} KB)`);

      return new Response(JSON.stringify(calendar), {
        status: 200,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // === PROFILE ===
    if (pathname.startsWith(`/athlete/${athleteId}`)) {
      const target = `${INTERVALS_API_BASE}${pathname}`;
      const r = await fetch(target, { headers: buildAuthHeaders() });
      const text = await r.text();
      const sizeKB = (new TextEncoder().encode(text).length / 1024).toFixed(1);

      console.log(`[PROFILE] → ${target} (${sizeKB} KB)`);

      return new Response(text, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }



    // ================================================================
    // REPORT ROUTES — UPDATED TO USE /events API (planned workouts)
    // ================================================================
    const runWeekly = async () => {
      console.log("[RUN_WEEKLY] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.WELLNESS_DAYS);
      const { start: calStart, end: calEnd } = getFutureDateRange(DATA_WINDOWS.CALENDAR_DAYS);

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        // 90d light
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${lightOldest}&newest=${lightNewest}` +
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin,HRTLNDLT1`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        // 7d full
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${fullOldest}&newest=${fullNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        // 42d wellness
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/wellness?oldest=${wellOldest}&newest=${wellNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        // Profile
        fetch(`${INTERVALS_API_BASE}/athlete/0`, {
          headers: buildAuthHeaders()
        }).then((r) => r.text()),
      ]);
      // Calendar → Events (planned workouts)
      const calendar = await fetchFutureCalendar(DATA_WINDOWS.CALENDAR_DAYS);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "weekly",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        calendar,
        athlete
      };

      return await callRailway(payload, "WEEKLY", profTxt);
    };

    if (pathname === "/run_weekly" && request.method === "GET") {
      return runWeekly();
    }

    // ================================================================
    // SEASON
    // ================================================================
    if (pathname === "/run_season" && request.method === "GET") {
      console.log("[RUN_SEASON] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams,DATA_WINDOWS.WELLNESS_DAYS);
      const { start: calStart, end: calEnd } = getFutureDateRange(DATA_WINDOWS.CALENDAR_DAYS);

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${lightOldest}&newest=${lightNewest}` +
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin,HRTLNDLT1`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${fullOldest}&newest=${fullNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/wellness?oldest=${wellOldest}&newest=${wellNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(`${INTERVALS_API_BASE}/athlete/0`, {
          headers: buildAuthHeaders()
        }).then((r) => r.text()),
      ]);
      // Calendar → Events (planned workouts)
      const calendar = await fetchFutureCalendar(DATA_WINDOWS.CALENDAR_DAYS);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "season",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        calendar,
        athlete
      };

      return await callRailway(payload, "SEASON", profTxt);
    }

    // ================================================================
    // WELLNESS
    // ================================================================
    if (pathname === "/run_wellness" && request.method === "GET") {
      console.log("[RUN_WELLNESS] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.WELLNESS_DAYS);
      const { start: calStart, end: calEnd } = getFutureDateRange(DATA_WINDOWS.CALENDAR_DAYS);

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${lightOldest}&newest=${lightNewest}` +
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin,HRTLNDLT1`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${fullOldest}&newest=${fullNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/wellness?oldest=${wellOldest}&newest=${wellNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(`${INTERVALS_API_BASE}/athlete/0`, {
          headers: buildAuthHeaders()
        }).then((r) => r.text()),
      ]);
      // Calendar → Events (planned workouts)
      const calendar = await fetchFutureCalendar(DATA_WINDOWS.CALENDAR_DAYS);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "wellness",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        calendar,
        athlete
      };

      return await callRailway(payload, "WELLNESS", profTxt);
    }

    // ================================================================
    // SUMMARY
    // ================================================================
    if (pathname === "/run_summary" && request.method === "GET") {
      console.log("[RUN_SUMMARY] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, DATA_WINDOWS.WELLNESS_DAYS);
      const { start: calStart, end: calEnd } = getFutureDateRange(DATA_WINDOWS.CALENDAR_DAYS);

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${lightOldest}&newest=${lightNewest}` +
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin,HRTLNDLT1`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/activities?oldest=${fullOldest}&newest=${fullNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(
          `${INTERVALS_API_BASE}/athlete/0/wellness?oldest=${wellOldest}&newest=${wellNewest}`,
          { headers: buildAuthHeaders() }
        ).then((r) => r.text()),

        fetch(`${INTERVALS_API_BASE}/athlete/0`, {
          headers: buildAuthHeaders()
        }).then((r) => r.text()),
      ]);
      // Calendar → Events (planned workouts)
      const calendar = await fetchFutureCalendar(
        parseInt(url.searchParams.get("daysAhead") || DATA_WINDOWS.CALENDAR_DAYS, 10)
      );
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "summary",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        calendar,
        athlete
      };

      return await callRailway(payload, "SUMMARY", profTxt);
    }

    // ================================================================
    // 📅 CALENDAR ENDPOINTS — using unified fetchFutureCalendar + flexible DATA_WINDOWS
    // ================================================================

    // === READ planned & future events ===
    if (pathname === "/calendar/read" && request.method === "GET") {
      let start = url.searchParams.get("start");
      let end = url.searchParams.get("end");

      // ✅ Determine lookahead window dynamically
      const daysAhead = parseInt(
        url.searchParams.get("daysAhead") || DATA_WINDOWS.CALENDAR_DAYS,
        10
      );

      // ✅ If user didn’t pass explicit start/end → compute from today
      if (!start || !end) {
        const { start: defStart, end: defEnd } = getFutureDateRange(daysAhead);
        start = start || defStart;
        end = end || defEnd;
      }

      console.log(`[CALENDAR READ] fetching events for ${start} → ${end} (daysAhead=${daysAhead})`);

      // Use unified helper that supports explicit range
      const calendar = await fetchFutureCalendarFromRange(start, end);

      return new Response(JSON.stringify(calendar), {
        status: 200,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }


    // === WRITE planned workouts / events ===
    if (pathname === "/calendar/write" && request.method === "POST") {
      const body = await request.json();

      // 🧩 Accept array, ChatGPT schema, or object
      let events = [];
      if (Array.isArray(body)) {
        events = body;
      } else if (Array.isArray(body.planned_workouts)) {
        events = body.planned_workouts;
      } else if (typeof body === "object" && Object.keys(body).length > 0) {
        events = [body];
      } else {
        return new Response(JSON.stringify({ error: "Missing event data" }), {
          status: 400,
          headers: { "content-type": "application/json" },
        });
      }

      // ================================================================
      // 📅 SMART CATEGORY + TYPE INFERENCE (schema-aligned)
      // ================================================================
      function inferCategoryAndType(name = "", description = "") {
        const n = `${name} ${description}`.toLowerCase();

        // 🎯 Race events
        if (n.match(/\b(a race|a-race|priority race|main event)\b/)) return { category: "RACE_A", type: "Ride" };
        if (n.match(/\b(b race|b-race)\b/)) return { category: "RACE_B", type: "Ride" };
        if (n.match(/\b(c race|c-race)\b/)) return { category: "RACE_C", type: "Ride" };
        if (n.match(/\b(race|competition|event|gran fondo|marathon|triathlon)\b/)) {
          if (n.includes("run")) return { category: "RACE_A", type: "Run" };
          if (n.includes("swim")) return { category: "RACE_A", type: "Swim" };
          return { category: "RACE_A", type: "Ride" };
        }

        // 🚴 Workouts
        if (n.match(/\b(ride|bike|zwift|trainer|tempo|interval|ftp|endurance|climb)\b/)) {
          if (n.includes("virtual")) return { category: "WORKOUT", type: "VirtualRide" };
          if (n.includes("mountain")) return { category: "WORKOUT", type: "MountainBikeRide" };
          if (n.includes("gravel")) return { category: "WORKOUT", type: "GravelRide" };
          return { category: "WORKOUT", type: "Ride" };
        }
        if (n.match(/\b(run|jog|trail|tempo run|track)\b/)) {
          if (n.includes("trail")) return { category: "WORKOUT", type: "TrailRun" };
          return { category: "WORKOUT", type: "Run" };
        }
        if (n.match(/\b(swim|laps|pool|open water)\b/)) {
          if (n.includes("open")) return { category: "WORKOUT", type: "OpenWaterSwim" };
          return { category: "WORKOUT", type: "Swim" };
        }

        // 🏋️ Strength & Cross-training
        if (n.match(/\b(weight|gym|strength|lifting|resistance|powerlifting|squat|deadlift|bench)\b/))
          return { category: "WORKOUT", type: "WeightTraining" };
        if (n.match(/\b(core|mobility|yoga|stretch|pilates|rehab|balance)\b/))
          return { category: "WORKOUT", type: "Yoga" };

        // 🥾 Outdoor activity
        if (n.match(/\b(hike|walk|trek)\b/)) return { category: "WORKOUT", type: "Hike" };

        // 💤 Recovery / Off days
        if (n.match(/\b(rest|recovery|off|easy|relax)\b/)) return { category: "NOTE", type: "Other" };

        // 🏖️ Holiday
        if (n.match(/\b(holiday|vacation|break|travel)\b/)) return { category: "HOLIDAY", type: "Other" };

        // ⚕️ Sick / Injured
        if (n.match(/\b(sick|ill|flu|cold)\b/)) return { category: "SICK", type: "Other" };
        if (n.match(/\b(injury|injured|rehab)\b/)) return { category: "INJURED", type: "Other" };

        // 🧪 FTP / fitness set
        if (n.match(/\b(ftp test|max hr|threshold|fitness test)\b/)) return { category: "SET_EFTP", type: "Ride" };

        // Default → note or plan
        if (n.match(/\b(plan|schedule|block)\b/)) return { category: "PLAN", type: "Other" };

        return { category: "NOTE", type: "Other" };
      }

      // 🧩 SMART DELETE: Delete matching events by date+name (inclusive date window)
      async function deleteMatchingEvents(events) {
        for (const e of events) {
          const date = e.date || e.start_date_local?.split("T")[0];
          const name = (e.title || e.name || "").trim().toLowerCase();
          if (!date || !name) continue;

          // 🔸 Widen date window to include events that cross midnight
          const oldest = `${date}T00:00:00`;
          const nextDay = new Date(date);
          nextDay.setDate(nextDay.getDate() + 1);
          const newest = `${nextDay.toISOString().split("T")[0]}T00:00:00`;

          const res = await fetch(
            `${INTERVALS_API_BASE}/athlete/0/events?oldest=${oldest}&newest=${newest}`,
            { headers: buildAuthHeaders() }
          );
          if (!res.ok) {
            console.warn(`[CALENDAR SMART DELETE] Failed to query for ${date} (${res.status})`);
            continue;
          }

          const existing = await res.json();

          // Normalize both names for comparison
          const matches = existing.filter(ev =>
            ev.name?.trim().toLowerCase() === name &&
            ev.start_date_local?.slice(0, 10) === date
          );

          if (matches.length === 0) {
            console.log(`[CALENDAR SMART DELETE] No matches for ${date} ${name}`);
            continue;
          }

          for (const m of matches) {
            await fetch(`${INTERVALS_API_BASE}/athlete/0/events/${m.id}`, {
              method: "DELETE",
              headers: buildAuthHeaders(),
            });
            console.log(`[CALENDAR SMART DELETE] Deleted id=${m.id} (${date} ${name})`);
          }
        }
      }

      const todayISO = new Date().toISOString().split("T")[0];

      const normalized = events.map((e) => {
        const start = e.start_date_local || (e.date ? `${e.date}T00:00:00` : `${todayISO}T00:00:00`);
        const name = e.name || e.title || "Untitled Session";
        const description = e.description || e.notes || e.note || "";
        const { category, type } = inferCategoryAndType(name, description);

        // detect if it's likely indoor
        const indoor = /\b(zwift|trainer|indoor)\b/i.test(name + description);

        return {
          start_date_local: start,
          end_date_local: e.end_date_local || start,
          category,
          type,
          name,
          description,
          moving_time: (e.duration_minutes ?? e.time_target ?? 0) * 60,  // ✅ convert to seconds
          icu_training_load: e.tss ?? e.load ?? null,  // ✅ Intervals accepts this
//          load_target: e.load_target ?? null,          // optional future support
//          time_target: e.time_target ?? e.duration_minutes ?? null,
          sub_type: e.sub_type || null,             // 🆕 subtype
          tags: e.tags || [],                       // 🆕 optional tags
          indoor,                                   // 🆕 auto flag
          color: e.color || null,                   // 🆕 user-set color
          show_on_fitness_line: e.show_on_fitness_line ?? false, // 🆕 optional
          visibility: "PUBLIC"
        };
      });


      const target = `${INTERVALS_API_BASE}/athlete/0/events/bulk?upsert=true`;
      console.log(`[CALENDAR WRITE → EVENTS] → ${target} (${normalized.length} events)`);

      const r = await fetch(target, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          Authorization: bearerToken,
        },
        body: JSON.stringify(normalized),
      });

      const txt = await r.text();
      console.log(`[CALENDAR WRITE RESPONSE] status=${r.status} bytes=${txt.length}`);
      if (r.status >= 400) console.error("[CALENDAR WRITE ERROR BODY]", txt);

      return new Response(txt, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }

    // === DELETE ITEMS (single ID, multiple IDs, or multiple dates) ===
    if (pathname === "/calendar/delete" && request.method === "POST") {
      const body = await request.json();
      const ids = Array.isArray(body.ids)
        ? body.ids
        : body.id
        ? [body.id]
        : [];
      const dates = Array.isArray(body.dates)
        ? body.dates
        : body.date
        ? [body.date]
        : [];

      // --- Helper: Delete by ID ---
      async function deleteEventById(id) {
        try {
          const r = await fetch(`${INTERVALS_API_BASE}/athlete/0/events/${id}`, {
            method: "DELETE",
            headers: buildAuthHeaders(),
          });
          if (!r.ok) {
            const errTxt = await r.text();
            console.warn(`[CALENDAR DELETE] Failed ID=${id}: ${r.status} ${errTxt.slice(0, 200)}`);
          }
          return r.ok;
        } catch (err) {
          console.error(`[CALENDAR DELETE] Exception for ID=${id}: ${err.message}`);
          return false;
        }
      }

      // --- Helper: Delete all events for a given date ---
      async function deleteEventsByDate(date) {
        try {
          const res = await fetch(
            `${INTERVALS_API_BASE}/athlete/0/events?oldest=${date}&newest=${date}`,
            { headers: buildAuthHeaders() }
          );

          if (!res.ok) {
            console.warn(`[CALENDAR DELETE] Could not fetch events for ${date} (HTTP ${res.status})`);
            return 0;
          }

          const events = await res.json();
          if (!Array.isArray(events) || !events.length) {
            console.log(`[CALENDAR DELETE] No events found on ${date}`);
            return 0;
          }

          const results = await Promise.allSettled(events.map(ev => deleteEventById(ev.id)));
          const deletedCount = results.filter(r => r.status === "fulfilled" && r.value).length;
          console.log(`[CALENDAR DELETE] ${date}: deleted ${deletedCount}/${events.length}`);
          return deletedCount;
        } catch (err) {
          console.error(`[CALENDAR DELETE] Exception while deleting date=${date}: ${err.message}`);
          return 0;
        }
      }

      // --- Case 1️⃣: Delete by explicit event IDs ---
      if (ids.length > 0) {
        console.log(`[CALENDAR DELETE] Bulk delete by IDs (${ids.length})`);
        const results = await Promise.allSettled(ids.map(deleteEventById));
        const deleted = results.filter(r => r.status === "fulfilled" && r.value).length;
        const failed = ids.length - deleted;

        const statusCode = failed > 0 ? 207 : 200; // 207 Multi-Status if partial failure
        return new Response(
          JSON.stringify({ mode: "ids", deleted, failed, total: ids.length }),
          {
            status: statusCode,
            headers: {
              "content-type": "application/json",
              "access-control-allow-origin": "*"
            }
          }
        );
      }

      // --- Case 2️⃣: Delete by one or more dates ---
      if (dates.length > 0) {
        console.log(`[CALENDAR DELETE] Deleting by dates: ${dates.join(", ")}`);
        let totalDeleted = 0;

        for (const date of dates) {
          const deletedForDate = await deleteEventsByDate(date);
          totalDeleted += deletedForDate;
        }

        return new Response(
          JSON.stringify({
            mode: "dates",
            deleted: totalDeleted,
            dates: dates.length
          }),
          {
            status: 200,
            headers: {
              "content-type": "application/json",
              "access-control-allow-origin": "*"
            }
          }
        );
      }

      // --- Case 3️⃣: Missing params ---
      return new Response(
        JSON.stringify({ error: "Missing id(s) or date(s) — must provide at least one." }),
        {
          status: 400,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        }
      );
    }


    // ================================================================
    // DEFAULT 404
    // ================================================================
    return new Response(
      JSON.stringify({ status: 404, error: `No matching route for ${pathname}` }),
      { status: 404, headers: { "content-type": "application/json", "access-control-allow-origin": "*" } }
    );
  }
};