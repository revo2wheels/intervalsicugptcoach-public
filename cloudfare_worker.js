export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const RAILWAY_BASE = "https://intervalsicugptcoach-public-production.up.railway.app";
    const authHeader = request.headers.get("Authorization");

    // ================================================================
    // 🧠 UNIFIED AUTH HANDLING
    // ================================================================
    let bearerToken = null;

    if (authHeader && authHeader.startsWith("Bearer ")) {
      bearerToken = authHeader.trim();
    } else if (env.ICU_OAUTH) {
      bearerToken = `Bearer ${env.ICU_OAUTH}`;
      console.log("[AUTH] Using fallback ICU_OAUTH");
    }

    if (!bearerToken) {
      return new Response(
        JSON.stringify({ status: 401, error: "Missing Authorization token." }),
        { status: 401, headers: { "content-type": "application/json", "access-control-allow-origin": "*" } }
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

    const safeParse = (txt) => {
      try {
        return JSON.parse(txt);
      } catch {
        return Array.isArray(txt) ? [] : {};
      }
    };

    const logPayload = (tag, payload) => {
      const light = Array.isArray(payload.activities_light) ? payload.activities_light.length : 0;
      const full = Array.isArray(payload.activities_full) ? payload.activities_full.length : 0;
      const well = Array.isArray(payload.wellness) ? payload.wellness.length : 0;

      console.log(
        `[${tag}] range=${payload.range} | light=${light} | full=${full} | wellness=${well}`
      );
    };

    const callRailway = async (payload, tag) => {
      logPayload(tag, payload);

      const resp = await fetch(`${RAILWAY_BASE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const text = await resp.text();
      console.log(`[${tag}] Railway returned ${resp.status} (${text.length} bytes)`);

      return new Response(text, {
        status: resp.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    };

    // ================================================================
    // OAuth redirect handlers
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

    // Token exchange
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

    // CORS
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
    // INTERNAL DATA ROUTES (NOT IN SCHEMA)
    // ================================================================
    const athleteIdMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteIdMatch ? athleteIdMatch[1] : "0";

    // 90-day light
    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 90);
      const fields = "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin";

      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities?oldest=${oldest}&newest=${newest}&fields=${encodeURIComponent(fields)}`;
      console.log(`[T0-LIGHT] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    // 7-day full (must request ALL fields)
    if (pathname.startsWith(`/athlete/${athleteId}/activities`) &&
        !pathname.includes("t0light")) {

      const { oldest, newest } = normaliseDateParams(url.searchParams, 7);

      // request all activity fields
      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities` +
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

    // 42-day wellness
    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 42);
      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness?oldest=${oldest}&newest=${newest}`;
      console.log(`[WELLNESS] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    // Profile
    if (pathname.startsWith(`/athlete/${athleteId}/profile`)) {
      const target = `${INTERVALS_API_BASE}${pathname}`;
      console.log(`[PROFILE] → ${target}`);

      const r = await fetch(target, { headers: buildAuthHeaders() });
      return new Response(await r.text(), {
        status: r.status,
        headers: { "content-type": "application/json", "access-control-allow-origin": "*" }
      });
    }

    // ================================================================
    // REPORT ROUTES (GET — matches schema)
    // ================================================================

    // WEEKLY REPORT
    if (pathname === "/run_weekly" && request.method === "GET") {
      console.log("[RUN_WEEKLY] Fetching datasets…");

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        fetch(`${url.origin}/athlete/0/activities_t0light`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/activities`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/wellness`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/profile`, { headers: buildAuthHeaders() }).then(r => r.text())
      ]);

      const payload = {
        range: "weekly",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt),
        activities_full: safeParse(fullTxt),
        wellness: safeParse(wellTxt),
        athlete: safeParse(profTxt)
      };

      return await callRailway(payload, "WEEKLY");
    }

    // SEASON REPORT (90d light only)
    if (pathname === "/run_season" && request.method === "GET") {
      console.log("[RUN_SEASON] Fetching datasets…");

      const [lightTxt, wellTxt, profTxt] = await Promise.all([
        fetch(`${url.origin}/athlete/0/activities_t0light`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/wellness`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/profile`, { headers: buildAuthHeaders() }).then(r => r.text())
      ]);

      const payload = {
        range: "season",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt),
        activities_full: [],
        wellness: safeParse(wellTxt),
        athlete: safeParse(profTxt)
      };

      return await callRailway(payload, "SEASON");
    }

    // WELLNESS REPORT (42d only)
    if (pathname === "/run_wellness" && request.method === "GET") {
      console.log("[RUN_WELLNESS] Fetching datasets…");

      const wellTxt = await fetch(`${url.origin}/athlete/0/wellness`, {
        headers: buildAuthHeaders()
      }).then((r) => r.text());

      const payload = {
        range: "wellness",
        format: url.searchParams.get("format") || "semantic",
        activities_light: [],
        activities_full: [],
        wellness: safeParse(wellTxt),
        athlete: {}
      };

      return await callRailway(payload, "WELLNESS");
    }

    // SUMMARY REPORT
    if (pathname === "/run_summary" && request.method === "GET") {
      console.log("[RUN_SUMMARY] Fetching datasets…");

      const [lightTxt, fullTxt, wellTxt, profTxt] = await Promise.all([
        fetch(`${url.origin}/athlete/0/activities_t0light`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/activities`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/wellness`, { headers: buildAuthHeaders() }).then(r => r.text()),
        fetch(`${url.origin}/athlete/0/profile`, { headers: buildAuthHeaders() }).then(r => r.text())
      ]);

      const payload = {
        range: "summary",
        format: url.searchParams.get("format") || "semantic",
        activities_light: safeParse(lightTxt),
        activities_full: safeParse(fullTxt),
        wellness: safeParse(wellTxt),
        athlete: safeParse(profTxt)
      };

      return await callRailway(payload, "SUMMARY");
    }

    // ================================================================
    // DEFAULT
    // ================================================================
    return new Response(
      JSON.stringify({ status: 404, error: `No matching route for ${pathname}` }),
      { status: 404, headers: { "content-type": "application/json", "access-control-allow-origin": "*" } }
    );
  }
};
