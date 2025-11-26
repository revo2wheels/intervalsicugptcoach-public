export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const authHeader = request.headers.get("Authorization");

    // --- OAuth authorize redirect ---
    if (pathname.startsWith("/oauth/authorize")) {
      const target = new URL(request.url.replace(
        /^https:\/\/intervalsicugptcoach\.clive-a5a\.workers\.dev/,
        "https://intervals.icu"
      ));

      // ✅ Redirect via Worker callback proxy
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
        },
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
      const target = "https://intervals.icu/api/oauth/token"; // ✅ CORRECT ENDPOINT
      console.log(`[OAUTH] Forwarding token exchange → ${target}`);

      const body = await request.text();
      const resp = await fetch(target, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
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
          "access-control-allow-methods": "GET, POST, OPTIONS",
        },
      });
    }

    // --- Fallback 401 if no Authorization ---
    if (!authHeader) {
      return new Response(
        JSON.stringify({
          status: 401,
          error: "Missing Authorization header. Ensure OAuth flow completed.",
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
      const iso = d.toISOString();
      return iso.split("T")[0];
    }

    // --- Extract athlete ID (default 0) ---
    const athleteMatch = pathname.match(/^\/athlete\/(\d+|0)\//);
    const athleteId = athleteMatch ? athleteMatch[1] : "0";

    // ====================================================================
    // ROUTE 0: Unified orchestrator (run_report) — Manifest Mode (Auto Fetch + Diagnostics)
    // ====================================================================
    if (pathname.startsWith("/run_report")) {
      const params = url.searchParams;
      const reportType = params.get("reportType") || "weekly";
      console.log(`[RUN_REPORT] Starting manifest-mode report: ${reportType}`);

      // --- Adjusted range configuration ---
      let range;
      if (reportType === "season") {
        range = { lightDays: 90, fullDays: 0, chunk: false }; // no chunking
      } else {
        range = { lightDays: 28, fullDays: 7, chunk: false }; // weekly or default
      }

      // --- Base for absolute URLs (important for ChatGPT) ---
      const baseWorker = "https://intervalsicugptcoach.clive-a5a.workers.dev";

      // ✅ Add lightweight field list HERE before datasets
      const lightFields =
        "id,name,type,start_date_local,distance,moving_time," +
        "icu_training_load,IF,average_heartrate,VO2MaxGarmin";

      // --- Dataset URLs (conditional per mode) ---
      const datasets = {
        profile: `${baseWorker}/athlete/${athleteId}/profile`,
        wellness: `${baseWorker}/athlete/${athleteId}/wellness?oldest=${getDate(reportType === "season" ? 42 : 28)}&newest=${getDate(0)}`,
        activities_light: `${baseWorker}/athlete/${athleteId}/activities_t0light?oldest=${getDate(range.lightDays)}&newest=${getDate(0)}&fields=${encodeURIComponent(lightFields)}`,
      };

      // Only include 7-day full for weekly reports
      if (reportType !== "season") {
        datasets.activities_full = `${baseWorker}/athlete/${athleteId}/activities?oldest=${getDate(range.fullDays)}&newest=${getDate(0)}`;
      }

      // --- Manifest for ChatGPT ---
      const manifest = {
        status: "ok",
        message: `[RUN_REPORT] Manifest ready for ${reportType} mode.`,
        reportType,
        athlete_id: athleteId,
        chunked: range.chunk,
        range,
        auto_fetch: true,
        require_user_confirmation: false,
        execution_mode: "auto",
        datasets,

        // ✅ Explicit action chain ChatGPT can follow
        actions: Object.entries(datasets).map(([key, url]) => ({
          type: "fetch",
          name:
            key === "profile"
              ? "getAthleteProfile"
              : key === "wellness"
              ? "listWellness"
              : key === "activities_light"
              ? "listActivitiesLight"
              : "listActivitiesFull",
          url,
          description: `Auto-fetch for ${key} dataset (${url})`,
        })),

        context: {
          render_hint: "manifest",
          auto_fetch: "immediate",
          auto_execute: true,
          interactive: false,
          fetch_order: Object.keys(datasets),
          required_datasets: Object.keys(datasets),
          retry_missing: true,
          priority: "sequential",
          mode: "prefetch",
          guidance: {
            instructions: [
              "Execute all actions in the 'actions' list immediately.",
              "Each 'fetch' returns JSON data to be merged client-side.",
              "Do not prompt user — auto-execute all requests in order.",
            ],
          },
          description: `Sequential auto-fetch of ${Object.keys(datasets).join(", ")} datasets for ${reportType} report.`,
        },

        diagnostics: {
          timestamp: new Date().toISOString(),
          reportType,
          urls_summary: Object.entries(datasets).map(([key, val]) => ({
            name: key,
            endpoint: val,
          })),
          expected_dataset_count: Object.keys(datasets).length,
          notes: [
            "All URLs are absolute and CORS-enabled.",
            "Payloads fetched individually to avoid ResponseTooLarge errors.",
            "ChatGPT must merge all fetched results for final analysis.",
          ],
        },
      };

      const payload = JSON.stringify(manifest, null, 2);
      console.log(`[RUN_REPORT] Returning manifest payload size = ${(payload.length / 1024).toFixed(2)} KB`);
      console.log(`[RUN_REPORT] Diagnostics:`);
      Object.entries(datasets).forEach(([name, url]) =>
        console.log(`  → ${name.padEnd(18)} ${url}`)
      );

      return new Response(payload, {
        status: 200,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*",
        },
      });
    }


    // ====================================================================
    // ROUTE 1: Tier-0 lightweight snapshot
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/activities_t0light`)) {
      const target = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities${url.search}`;
      console.log(`[T0-LIGHT] Proxying lightweight fetch → ${target}`);
      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /activities_t0light payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // ====================================================================
    // ROUTE 2: Full activity fetch
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/activities`)) {
      const target = `${INTERVALS_API_BASE}${pathname}${url.search}`;
      console.log(`[T1-FULL] Proxying full fetch → ${target}`);
      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /activities payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      });
    }

    // ====================================================================
    // ROUTE 3: Wellness
    // ====================================================================
    if (pathname.startsWith(`/athlete/${athleteId}/wellness`)) {
      const params = url.searchParams;
      const oldestRaw = params.get("oldest");
      const newestRaw = params.get("newest");

      const oldest = oldestRaw ? oldestRaw.substring(0, 10) : getDate(7);
      const newest = newestRaw ? newestRaw.substring(0, 10) : getDate(0);

      const target = `${INTERVALS_API_BASE}${pathname}?oldest=${encodeURIComponent(oldest)}&newest=${encodeURIComponent(newest)}`;
      console.log(`[WELLNESS] Normalized wellness fetch → ${target}`);

      const resp = await fetch(target, { headers: { Authorization: authHeader } });
      const text = await resp.text();
      console.log(`[SIZE] /wellness payload = ${(text.length / 1024).toFixed(2)} KB`);
      return new Response(text, {
        status: resp.status,
        headers: {
          "content-type": "application/json",
          "access-control-allow-origin": "*"
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
    // DEFAULT
    // ====================================================================
    return new Response(
      JSON.stringify({ status: 404, error: `No matching route for ${pathname}` }),
      { status: 404, headers: { "content-type": "application/json" } }
    );
  }
};
