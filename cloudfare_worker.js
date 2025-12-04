export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const authHeader = request.headers.get("Authorization");

    // --- OAuth authorize redirect ---
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

      console.log(`[OAUTH] Redirecting viewer to → ${target}`);

      const html = `
        <!DOCTYPE html><html><head><meta charset="utf-8" />
        <title>Redirecting…</title></head>
        <body>
          <p>Opening Intervals.icu authorization page…</p>
          <script>window.location.replace("${target.toString()}");</script>
        </body></html>`;
      return new Response(html, {
        status: 200,
        headers: {
          "content-type": "text/html",
          "access-control-allow-origin": "*"
        }
      });
    }

    // --- OAuth callback proxy (NEW) ---
    if (pathname.startsWith("/oauth/callback")) {
      const redirectTarget = `https://chat.openai.com/aip/g-3b0244cf708774fb9151458671c462eb5460f41e/oauth/callback${url.search}`;
      console.log(`[OAUTH] Proxying callback → ${redirectTarget}`);
      return Response.redirect(redirectTarget, 302);
    }

    // --- OAuth token passthrough ---
    if (pathname.startsWith("/api/oauth/token")) {
      const target = "https://intervals.icu/api/oauth/token";
      console.log(`[OAUTH] Forwarding token exchange → ${target}`);

      const body = await request.text();
      const resp = await fetch(target, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body
      });

      console.log(`[OAUTH] Token response → ${resp.status}`);

      const text = await resp.text();
      const headers = new Headers(resp.headers);
      headers.set("access-control-allow-origin", "*");
      headers.set("access-control-allow-headers", "Authorization, Content-Type");
      headers.set("access-control-allow-methods", "GET, POST, OPTIONS");

      return new Response(text, { status: resp.status, headers });
    }

    // --- CORS preflight ---
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, POST, OPTIONS"
        }
      });
    }

    // --- Fallback 401 if no Authorization ---
    if (!authHeader) {
      return new Response(
        JSON.stringify({
          status: 401,
          error: "Missing Authorization header. Ensure OAuth flow completed."
        }),
        {
          status: 401,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        }
      );
    }

    // --- Utility: date offset ---
    function getDate(daysAgo) {
      const d = new Date();
      d.setUTCDate(d.getUTCDate() - daysAgo);
      return d.toISOString().split("T")[0];
    }

    // --- 🔧 Date normalization helper ---
    function normaliseDateParams(params, defaultDays) {
      const oldest = params.get("oldest");
      const newest = params.get("newest");
      const validDate = d => /^\d{4}-\d{2}-\d{2}$/.test(d);

      const norm = {
        oldest: validDate(oldest) ? oldest : getDate(defaultDays),
        newest: validDate(newest) ? newest : getDate(0)
      };

      if (!validDate(oldest) || !validDate(newest)) {
        console.log(
          `[NORMALISE] Missing or invalid date params → default window ${defaultDays}d (${norm.oldest} → ${norm.newest})`
        );
      }

      return norm;
    }

    // --- Extract athlete ID (default 0) ---
    const athleteMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteMatch ? athleteMatch[1] : "0";

    // ====================================================================
    // ROUTE 0: Backwards compatibility stub
    // ====================================================================
    if (pathname.startsWith("/run_report")) {
      console.log("[RUN_REPORT] Stub invoked – sequential endpoints required.");
      return new Response(
        JSON.stringify({
          status: "stub",
          message:
            "Use sequential endpoint calls: profile → 90d light → 42d wellness → 7d full."
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

    // ====================================================================
    // ROUTE 1: Tier-0 lightweight snapshot (default 90 days)
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 90);

      // Preserve or inject lightweight field set
      const fields =
        url.searchParams.get("fields") ||
        "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin";

      // Build target URL with all required query params
      const target =
        `${INTERVALS_API_BASE}/athlete/${athleteId}/activities?` +
        `oldest=${oldest}&newest=${newest}&fields=${encodeURIComponent(fields)}`;

      console.log(`[T0-LIGHT] Normalized fetch → ${target}`);

      try {
        const resp = await fetch(target, { headers: { Authorization: authHeader } });
        const text = await resp.text();
        console.log(`[SIZE] /activities_t0light payload = ${(text.length / 1024).toFixed(2)} KB`);
        return new Response(text, {
          status: resp.status,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
            "x-proxy-endpoint": "activities_t0light"
          }
        });
      } catch (err) {
        console.error(`[T0-LIGHT] Upstream fetch error → ${err.message}`);
        return new Response(
          JSON.stringify({ error: "Upstream fetch failed", details: err.message }),
          { status: 500, headers: { "content-type": "application/json" } }
        );
      }
    }


    // ====================================================================
    // ROUTE 2: Full activity fetch (default 7 days, supports chunked calls)
    // ====================================================================
    if (
      pathname.startsWith(`/athlete/${athleteId}/activities`) &&
      !pathname.includes("t0light")
    ) {
      // Read incoming params
      let oldest = url.searchParams.get("oldest");
      let newest = url.searchParams.get("newest");

      // Allow timestamped inputs from Python like "2025-11-20 08:25:48.123456"
      function cleanDate(d) {
        if (!d) return null;
        const m = d.match(/^(\d{4}-\d{2}-\d{2})/);
        return m ? m[1] : null;
      }

      oldest = cleanDate(oldest);
      newest = cleanDate(newest);

      // Fallback only if both missing or invalid
      if (!oldest || !newest) {
        const norm = normaliseDateParams(url.searchParams, 7);
        oldest = norm.oldest;
        newest = norm.newest;
      }

      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities?oldest=${oldest}&newest=${newest}`;
      console.log(`[T1-FULL] Normalized fetch → ${target}`);

      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /activities payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
          "x-proxy-endpoint": "activities_full"
        }
      });
    }


    // ====================================================================
    // ROUTE 3: Wellness (default 42 days, supports chunked calls)
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      // Read incoming params as-is
      let oldest = url.searchParams.get("oldest");
      let newest = url.searchParams.get("newest");

      // Try to normalize timestamped params like "2025-10-10 08:53:48.795267"
      function cleanDate(d) {
        if (!d) return null;
        const m = d.match(/^(\d{4}-\d{2}-\d{2})/);
        return m ? m[1] : null;
      }

      oldest = cleanDate(oldest);
      newest = cleanDate(newest);

      // Fallback only if both missing or invalid
      if (!oldest || !newest) {
        const norm = normaliseDateParams(url.searchParams, 42);
        oldest = norm.oldest;
        newest = norm.newest;
      }

      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness?oldest=${oldest}&newest=${newest}`;
      console.log(`[WELLNESS] Normalized fetch → ${target}`);

      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /wellness payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
          "x-proxy-endpoint": "wellness"
        }
      });
    }


    // ====================================================================
    // ROUTE 4: Athlete profile
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/profile`)) {
      const target = `${INTERVALS_API_BASE}${pathname}${url.search}`;
      console.log(`[PROFILE] Proxying profile fetch → ${target}`);

      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /profile payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }
    
    // ====================================================================
    // ROUTE 5: Weekly report handoff → Railway backend
    //====================================================================
    if (pathname === "/run_weekly") {
      console.log("[WORKER] Running full weekly fetch + Railway handoff");

      const headers = { Authorization: authHeader };

      // Fetch from Intervals.icu via this same Worker
      const [actsLight, actsFull, wellness, profile] = await Promise.all([
        fetch(`${url.origin}/athlete/0/activities_t0light`, { headers }).then(r => r.json()),
        fetch(`${url.origin}/athlete/0/activities`, { headers }).then(r => r.json()),
        fetch(`${url.origin}/athlete/0/wellness`, { headers }).then(r => r.json()),
        fetch(`${url.origin}/athlete/0/profile`, { headers }).then(r => r.json()),
      ]);

      const payload = {
        range: "weekly",
        activities_light: actsLight,
        activities_full: actsFull,
        wellness,
        athlete: profile,
      };

      const railwayUrl = "https://intervalsicugptcoach-public-production.up.railway.app/run";
      const response = await fetch(railwayUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: authHeader || "",
        },
        body: JSON.stringify(payload),
      });

      const text = await response.text();
      console.log(`[WORKER] Railway response ${response.status}: ${text.slice(0, 300)}...`);

      return new Response(text, {
        status: response.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, POST, OPTIONS",
        },
      });
    }


    // ====================================================================
    // DEFAULT
    // ====================================================================
    return new Response(
      JSON.stringify({ status: 404, error: `No matching route for ${pathname}` }),
      { status: 404, headers: { "content-type": "application/json" } }
    );
  }
};
