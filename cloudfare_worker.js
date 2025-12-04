export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const authHeader = request.headers.get("Authorization");

    // ================================================================
    // 🧠 UNIFIED AUTH HANDLING
    // ================================================================
    let bearerToken = null;

    // 1️⃣ Prefer Authorization header from ChatGPT or local curl
    if (authHeader && authHeader.startsWith("Bearer ")) {
      bearerToken = authHeader.trim();
    }
    // 2️⃣ Fallback to Worker environment variable (for Railway/local dev)
    else if (env.ICU_OAUTH) {
      bearerToken = `Bearer ${env.ICU_OAUTH}`;
      console.log("[AUTH] Using fallback ICU_OAUTH from environment.");
    }
    // 3️⃣ Reject if missing
    if (!bearerToken) {
      return new Response(
        JSON.stringify({
          status: 401,
          error: "Missing or invalid Authorization token. OAuth flow required.",
        }),
        {
          status: 401,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
          },
        }
      );
    }

    // ================================================================
    // 🧩 Helpers
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
      const validDate = (d) => /^\d{4}-\d{2}-\d{2}$/.test(d);

      const norm = {
        oldest: validDate(oldest) ? oldest : getDate(defaultDays),
        newest: validDate(newest) ? newest : getDate(0),
      };

      if (!validDate(oldest) || !validDate(newest)) {
        console.log(
          `[NORMALISE] Using default window ${defaultDays}d (${norm.oldest} → ${norm.newest})`
        );
      }
      return norm;
    };

    const athleteMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteMatch ? athleteMatch[1] : "0";

    // ================================================================
    // 🔐 OAuth authorize redirect
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
          "access-control-allow-origin": "*",
        },
      });
    }

    // ================================================================
    // OAuth callback proxy
    // ================================================================
    if (pathname.startsWith("/oauth/callback")) {
      const redirectTarget = `https://chat.openai.com/aip/g-3b0244cf708774fb9151458671c462eb5460f41e/oauth/callback${url.search}`;
      console.log(`[OAUTH] Proxying callback → ${redirectTarget}`);
      return Response.redirect(redirectTarget, 302);
    }

    // ================================================================
    // Token exchange passthrough
    // ================================================================
    if (pathname.startsWith("/api/oauth/token")) {
      const target = "https://intervals.icu/api/oauth/token";
      console.log(`[OAUTH] Forwarding token exchange → ${target}`);

      const body = await request.text();
      const resp = await fetch(target, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      const text = await resp.text();

      const headers = new Headers(resp.headers);
      headers.set("access-control-allow-origin", "*");
      headers.set("access-control-allow-headers", "Authorization, Content-Type");
      headers.set("access-control-allow-methods", "GET, POST, OPTIONS");
      return new Response(text, { status: resp.status, headers });
    }

    // ================================================================
    // CORS Preflight
    // ================================================================
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, POST, OPTIONS",
        },
      });
    }

    // ================================================================
    // ROUTE 1: Tier-0 Lightweight snapshot
    // ================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 90);
      const fields =
        url.searchParams.get("fields") ||
        "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin";
      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities?oldest=${oldest}&newest=${newest}&fields=${encodeURIComponent(fields)}`;
      console.log(`[T0-LIGHT] Fetch → ${target}`);

      const resp = await fetch(target, { headers: buildAuthHeaders() });
      const text = await resp.text();
      console.log(`[SIZE] /activities_t0light = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }

    // ================================================================
    // ROUTE 2: Full activities (7d)
    // ================================================================
    if (
      pathname.startsWith(`/athlete/${athleteId}/activities`) &&
      !pathname.includes("t0light")
    ) {
      let oldest = url.searchParams.get("oldest");
      let newest = url.searchParams.get("newest");
      const clean = (d) => (d?.match(/^(\d{4}-\d{2}-\d{2})/) || [])[1] || null;

      oldest = clean(oldest);
      newest = clean(newest);
      if (!oldest || !newest) {
        const norm = normaliseDateParams(url.searchParams, 7);
        oldest = norm.oldest;
        newest = norm.newest;
      }

      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities?oldest=${oldest}&newest=${newest}`;
      console.log(`[T1-FULL] Fetch → ${target}`);

      const resp = await fetch(target, { headers: buildAuthHeaders() });
      const text = await resp.text();
      console.log(`[SIZE] /activities = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }

    // ================================================================
    // ROUTE 3: Wellness (42d)
    // ================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      const { oldest, newest } = normaliseDateParams(url.searchParams, 42);
      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness?oldest=${oldest}&newest=${newest}`;
      console.log(`[WELLNESS] Fetch → ${target}`);

      const resp = await fetch(target, { headers: buildAuthHeaders() });
      const text = await resp.text();
      console.log(`[SIZE] /wellness = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }

    // ================================================================
    // ROUTE 4: Athlete profile
    // ================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/profile`)) {
      const target = `${INTERVALS_API_BASE}${pathname}${url.search}`;
      console.log(`[PROFILE] Fetch → ${target}`);

      const resp = await fetch(target, { headers: buildAuthHeaders() });
      const text = await resp.text();
      console.log(`[SIZE] /profile = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }

    // ================================================================
    // ROUTE 5: Weekly report handoff → Railway backend
    // ================================================================
    if (pathname === "/run_weekly") {
      console.log("[WORKER] Running full weekly fetch + Railway handoff");
      try {
        const [actsLight, actsFull, wellness, profile] = await Promise.all([
          fetch(`${url.origin}/athlete/0/activities_t0light`, {
            headers: buildAuthHeaders(),
          }).then((r) => r.text()),
          fetch(`${url.origin}/athlete/0/activities`, {
            headers: buildAuthHeaders(),
          }).then((r) => r.text()),
          fetch(`${url.origin}/athlete/0/wellness`, {
            headers: buildAuthHeaders(),
          }).then((r) => r.text()),
          fetch(`${url.origin}/athlete/0/profile`, {
            headers: buildAuthHeaders(),
          }).then((r) => r.text()),
        ]);

        console.log(
          `[DEBUG] Raw payload sizes → light=${actsLight.length} full=${actsFull.length} wellness=${wellness.length} profile=${profile.length}`
        );

        const safeParse = (t) => {
          try {
            return JSON.parse(t);
          } catch {
            return [];
          }
        };

        const payload = {
          range: "weekly",
          activities_light: safeParse(actsLight),
          activities_full: safeParse(actsFull),
          wellness: safeParse(wellness),
          athlete: safeParse(profile),
        };

        const railwayUrl = "https://intervalsicugptcoach-public-production.up.railway.app/run";
        const response = await fetch(railwayUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const text = await response.text();
        console.log(`[WORKER] Railway response ${response.status} (${text.length} bytes)`);

        return new Response(text, {
          status: response.status,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
          },
        });
      } catch (err) {
        console.error(`[WORKER] run_weekly failed → ${err.stack || err}`);
        return new Response(JSON.stringify({ status: "error", message: err.message }), {
          status: 500,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
          },
        });
      }
    }

    // ================================================================
    // DEBUG: Which token is active
    // ================================================================
    if (pathname === "/debug_token") {
      const masked = bearerToken ? bearerToken.slice(0, 15) + "…" : "none";
      return new Response(
        JSON.stringify({ bearer_in_use: masked }),
        {
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
          },
        }
      );
    }

    // ================================================================
    // DEFAULT
    // ================================================================
    return new Response(
      JSON.stringify({ status: 404, error: `No matching route for ${pathname}` }),
      { status: 404, headers: { "content-type": "application/json" } }
    );
  },
};
