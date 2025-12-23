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

    // === LIGHT ACTIVITIES ===
    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, DATA_WINDOWS.LIGHT_DAYS);
      const fields =
        "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin";

      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${oldest}&newest=${newest}&fields=${encodeURIComponent(fields)}`;

      console.log(`[T0-LIGHT] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // === FULL ACTIVITIES ===
    if (
      pathname.startsWith(`/athlete/${athleteId}/activities`) &&
      !pathname.includes("t0light")
    ) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, DATA_WINDOWS.FULL_DAYS);
      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${oldest}&newest=${newest}`;
      console.log(`[FULL] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
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
      console.log(`[WELLNESS] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
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
      console.log(`[PROFILE] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
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
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin`,
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
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin`,
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
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin`,
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
            `&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin`,
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

      // 🧩 Accept top-level object, array, or ChatGPT JSON schema
      let events = [];
      if (Array.isArray(body)) {
        events = body;
      } else if (body.planned_workouts && Array.isArray(body.planned_workouts)) {
        events = body.planned_workouts;
      } else if (typeof body === "object" && Object.keys(body).length > 0) {
        events = [body];
      } else {
        return new Response(JSON.stringify({ error: "Missing event data" }), {
          status: 400,
          headers: { "content-type": "application/json" }
        });
      }

      // 🧠 Normalize category names
      const normalizeCategory = (cat = "NOTE") => {
        const c = cat.trim().toUpperCase();
        if (["NOTES", "MEMO"].includes(c)) return "NOTE";
        if (["HOLIDAY", "HOLIDAYS", "VACATION", "BREAK"].includes(c)) return "HOLIDAY";
        return c;
      };

      const todayISO = new Date().toISOString().split("T")[0];

      const normalized = events.map((e) => {
        const category = normalizeCategory(e.category || "NOTE");
        const start =
          e.start_date_local ||
          (e.date ? `${e.date}T00:00:00` : `${todayISO}T00:00:00`);
        const end =
          e.end_date_local ||
          e.end_date ||
          `${start.split("T")[0]}T00:00:00`; // ✅ required

        // 🧩 Map flexible fields → Intervals schema
        const name = e.name || e.title || "Note";
        const description = e.description || e.notes || e.note || e.text || "";

        // Minimal valid event
        const normalizedEvent = {
          start_date_local: start,
          end_date_local: end,
          category,
          name,
          description,
          duration_minutes: e.duration_minutes ?? 0,
          color: e.color || null
        };

        return normalizedEvent;
      });

      const target = `${INTERVALS_API_BASE}/athlete/0/events/bulk?upsert=true`;
      console.log(`[CALENDAR WRITE → EVENTS] → ${target} (${normalized.length} events)`);

      const r = await fetch(target, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          Authorization: bearerToken
        },
        body: JSON.stringify(normalized)
      });

      const txt = await r.text();
      console.log(`[CALENDAR WRITE RESPONSE] status=${r.status} bytes=${txt.length}`);

      return new Response(txt, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    if (pathname === "/calendar/delete" && request.method === "POST") {
      const body = await request.json();
      const id = body.id;
      const date = body.date;

      let target;
      if (id) {
        target = `${INTERVALS_API_BASE}/athlete/0/events/${id}`;
      } else if (date) {
        // fetch events on date, then delete all
        const res = await fetch(
          `${INTERVALS_API_BASE}/athlete/0/events?oldest=${date}&newest=${date}`,
          { headers: buildAuthHeaders() }
        );
        const events = res.ok ? await res.json() : [];
        for (const ev of events) {
          await fetch(`${INTERVALS_API_BASE}/athlete/0/events/${ev.id}`, {
            method: "DELETE",
            headers: buildAuthHeaders()
          });
        }
        return new Response(
          JSON.stringify({ deleted: events.length }),
          { status: 200, headers: { "content-type": "application/json", "access-control-allow-origin": "*" } }
        );
      }

      if (!target)
        return new Response(JSON.stringify({ error: "Missing id or date" }), {
          status: 400,
          headers: { "content-type": "application/json" }
        });

      const r = await fetch(target, {
        method: "DELETE",
        headers: buildAuthHeaders()
      });
      const txt = await r.text();

      return new Response(txt, {
        status: r.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
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