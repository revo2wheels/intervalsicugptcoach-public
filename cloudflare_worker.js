// ================================================================
// CLOUDFLARE WORKER V17 INTERVALS ICU RAILWAY
// ================================================================
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const RAILWAY_BASE = "https://intervalsicugptcoach-public-production.up.railway.app";
    const authHeader = request.headers.get("Authorization");

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
    // 🔥 Unified payload logger including athlete debug
    // ================================================================
    const logPayload = (tag, payload, athleteRawText = "") => {
      const light = Array.isArray(payload.activities_light)
        ? payload.activities_light.length
        : 0;
      const full = Array.isArray(payload.activities_full)
        ? payload.activities_full.length
        : 0;
      const well = Array.isArray(payload.wellness)
        ? payload.wellness.length
        : 0;

      const athleteObj = payload.athlete || {};
      const athleteId = athleteObj.id ? athleteObj.id : "<missing>";

      console.log(
        JSON.stringify({
          message: `[${tag}] range=${payload.range} | light=${light} | full=${full} | wellness=${well}`,
          athlete: {
            id: athleteId,
            raw: athleteRawText ? athleteRawText.slice(0, 200) : "<no raw profile>",
            parsed: athleteObj
          }
        })
      );
    };

    // ================================================================
    // 🔥 Correct callRailway (with athleteRawText support)
    // ================================================================
    const callRailway = async (payload, tag, athleteRawText = "") => {
      logPayload(tag, payload, athleteRawText);

      const resp = await fetch(`${RAILWAY_BASE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const text = await resp.text();
      console.log(`[${tag}] Railway returned ${resp.status} (${text.length} bytes)`);

      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    };

    // ================================================================
    // OAuth proxy routes
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
      console.log(`[OAUTH] Redirecting to ${target}`);
      return Response.redirect(target.toString(), 302);
    }

    if (pathname.startsWith("/oauth/callback")) {
      const redirectTarget =
        "https://chat.openai.com/aip/g-3b0244cf708774fb9151458671c462eb5460f41e/oauth/callback" +
        url.search;
      console.log(`[OAUTH] Proxying callback → ${redirectTarget}`);
      return Response.redirect(redirectTarget, 302);
    }

    if (pathname.startsWith("/api/oauth/token")) {
      const resp = await fetch("https://intervals.icu/api/oauth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: await request.text()
      });
      return new Response(await resp.text(), {
        status: resp.status,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type"
        }
      });
    }

    // CORS support
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, OPTIONS"
        }
      });
    }

    // ================================================================
    // INTERNAL DATA ROUTES
    // ================================================================
    const athleteIdMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteIdMatch ? athleteIdMatch[1] : "0";

    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 90);
      const fields =
        "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin";

      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${oldest}&newest=${newest}&fields=${encodeURIComponent(fields)}`;

      console.log(`[T0-LIGHT] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    if (
      pathname.startsWith(`/athlete/${athleteId}/activities`) &&
      !pathname.includes("t0light")
    ) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 7);

      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
        `?oldest=${oldest}&newest=${newest}`;

      console.log(`[FULL] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 42);

      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness` +
        `?oldest=${oldest}&newest=${newest}`;

      console.log(`[WELLNESS] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    if (pathname.startsWith(`/athlete/${athleteId}`)) {
      const target = `${INTERVALS_API_BASE}${pathname}`;
      console.log(`[PROFILE] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    // ================================================================
    // REPORT ROUTES
    // ================================================================
    const runWeekly = async () => {
      console.log("[RUN_WEEKLY] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, 90);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, 7);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, 42);

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

        // profile
        fetch(`${INTERVALS_API_BASE}/athlete/0`, {
          headers: buildAuthHeaders()
        }).then((r) => r.text())
      ]);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "weekly",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        athlete
      };

      return await callRailway(payload, "WEEKLY", profTxt);
    };

    if (pathname === "/run_weekly" && request.method === "GET") {
      return runWeekly();
    }

    // SEASON
    if (pathname === "/run_season" && request.method === "GET") {
      console.log("[RUN_SEASON] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, 90);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, 7);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, 42);

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
        }).then((r) => r.text())
      ]);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "season",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        athlete
      };

      return await callRailway(payload, "SEASON", profTxt);
    }

    // WELLNESS
    if (pathname === "/run_wellness" && request.method === "GET") {
      console.log("[RUN_WELLNESS] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, 90);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, 7);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, 42);

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
        }).then((r) => r.text())
      ]);
      const athlete = extractAthlete(profTxt);
      const payload = {
        range: "wellness",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        athlete
      };

      return await callRailway(payload, "WELLNESS", profTxt);
    }

    // SUMMARY
    if (pathname === "/run_summary" && request.method === "GET") {
      console.log("[RUN_SUMMARY] Fetching datasets…");

      const { oldest: lightOldest, newest: lightNewest } =
        normaliseDateParams(url.searchParams, 90);
      const { oldest: fullOldest, newest: fullNewest } =
        normaliseDateParams(url.searchParams, 7);
      const { oldest: wellOldest, newest: wellNewest } =
        normaliseDateParams(url.searchParams, 42);

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
        }).then((r) => r.text())
      ]);

      const athlete = extractAthlete(profTxt);

      const payload = {
        range: "summary",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt, "array"),
        activities_full: safeParse(fullTxt, "array"),
        wellness: safeParse(wellTxt, "array"),
        athlete
      };

      return await callRailway(payload, "SUMMARY", profTxt);
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
