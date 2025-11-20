export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const INTERVALS_API_BASE = "https://intervals.icu/api/v1";
    const authHeader = request.headers.get("Authorization");

    // --- CORS preflight ---
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-headers": "Authorization, Content-Type",
          "access-control-allow-methods": "GET, OPTIONS"
        }
      });
    }

    // --- 401 if no auth ---
    if (!authHeader) {
      return new Response(
        JSON.stringify({
          status: 401,
          error: "Missing Authorization header. Ensure OAuth flow completed."
        }),
        { status: 401, headers: { "content-type": "application/json" } }
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
    // ROUTE 0: Unified orchestrator (run_report)
    // ====================================================================
    if (pathname.startsWith("/run_report")) {
      const params = url.searchParams;
      const reportType = params.get("reportType") || "weekly";

      console.log(`[RUN_REPORT] Starting unified report: ${reportType}`);

      const range =
        reportType === "season"
          ? { lightDays: 90, fullDays: 42, chunk: true }
          : { lightDays: 90, fullDays: 7, chunk: false };

      const baseActUrl = `${INTERVALS_API_BASE}/athlete/${athleteId}/activities`;
      const baseWellUrl = `${INTERVALS_API_BASE}/athlete/${athleteId}/wellness`;
      const profileUrl = `${INTERVALS_API_BASE}/athlete/${athleteId}/profile`;

      // --- Chunked fetch helper ---
      async function fetchChunked(baseUrl, totalDays, chunkSize, extraParams = "") {
        const results = [];
        const totalBlocks = Math.ceil(totalDays / chunkSize);
        console.log(`[CHUNK] Splitting ${totalDays} days into ${totalBlocks} blocks...`);

        for (let i = totalBlocks - 1; i >= 0; i--) {
          const startOffset = i * chunkSize;
          const endOffset = Math.min(startOffset + chunkSize, totalDays);
          const oldest = getDate(endOffset);
          const newest = getDate(startOffset);
          const chunkUrl = `${baseUrl}?oldest=${oldest}&newest=${newest}${extraParams}`;
          console.log(`[CHUNK ${totalBlocks - i}/${totalBlocks}] ${chunkUrl}`);

          const resp = await fetch(chunkUrl, { headers: { Authorization: authHeader } });
          if (!resp.ok) {
            console.error(`[CHUNK ${totalBlocks - i}] failed: ${resp.status}`);
            continue;
          }

          const json = await resp.json();
          if (Array.isArray(json) && json.length > 0) {
            console.log(`[CHUNK ${totalBlocks - i}] received ${json.length} records`);
            results.push(...json);
          } else {
            console.warn(`[CHUNK ${totalBlocks - i}] empty or invalid response`);
          }
        }

        console.log(`[CHUNK] Combined ${results.length} records total`);
        return results;
      }

      try {
        let light = [], full = [], wellness = [], profile = {};

        if (reportType === "season") {
          console.log("[RUN_REPORT] Season mode → single-call lightweight fetch (no chunking for 90 days).");

          const oldest = getDate(range.lightDays);
          const newest = getDate(0);

          // --- Single-call lightweight fetches (no chunking) --------------------------

          // --- Activities (single 90-day call) ---------------------------------------
          const actOldest = getDate(range.lightDays);
          const actNewest = getDate(0);
          const actUrl =
            `${baseActUrl}?oldest=${actOldest}&newest=${actNewest}` +
            "&fields=id,name,type,start_date_local,distance,moving_time," +
            "icu_training_load,IF,average_heartrate,VO2MaxGarmin";

          console.log(`[RUN_REPORT] Fetching lightweight 90-day dataset → ${actUrl}`);

          const actResp = await fetch(actUrl, { headers: { Authorization: authHeader } });
          if (!actResp.ok)
            throw new Error(`Season lightweight fetch failed: ${actResp.status}`);
          const light = await actResp.json();

          console.log(`[RUN_REPORT] Retrieved ${light.length} activities (un-chunked)`);

          // --- Wellness (single 42-day call, not chunked) -----------------------------
          const wellOldest = getDate(range.fullDays);
          const wellNewest = getDate(0);
          const wellnessUrl = `${baseWellUrl}?oldest=${wellOldest}&newest=${wellNewest}`;
          console.log(`[RUN_REPORT] Fetching wellness (single call, 42 days) → ${wellnessUrl}`);

          const wellnessResp = await fetch(wellnessUrl, { headers: { Authorization: authHeader } });
          if (!wellnessResp.ok)
            throw new Error(`Wellness fetch failed: ${wellnessResp.status}`);
          const wellness = await wellnessResp.json();

          console.log(`[RUN_REPORT] Retrieved ${wellness.length} wellness records`);


          // --- Profile fetch (unchanged) -------------------------------------------
          const profile = await fetch(profileUrl, { headers: { Authorization: authHeader } }).then(r => r.json());

          // --- Build unified payload summary ---------------------------------------
          const summary = {
            status: "ok",
            message: `[RUN_REPORT] Completed single-call lightweight season fetch (${light.length} activities, ${wellness.length} wellness records)`,
            reportType,
            athlete_id: athleteId,
            chunked: false,
            range,
            summary: {
              light_count: light.length,
              wellness_count: wellness.length,
              start_date: oldest,
              end_date: newest,
            },
            athlete_profile: profile?.athlete || {},
          };

          const payload = JSON.stringify(summary);
          console.log(`[SIZE] /run_report (season) payload = ${(payload.length / 1024).toFixed(2)} KB`);

          return new Response(payload, {
            status: 200,
            headers: {
              "content-type": "application/json",
              "access-control-allow-origin": "*"
            }
          });
        }

      // --- Normal full-detail mode (weekly/block) ---
      console.log("[RUN_REPORT] Weekly/Block mode → fetching full dataset.");

      [light, full, wellness, profile] = await Promise.all([
        range.chunk
          ? fetchChunked(
              baseActUrl,
              range.lightDays,
              14,
              "&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin"
            )
          : fetch(
              `${baseActUrl}?oldest=${getDate(range.lightDays)}&newest=${getDate(0)}&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin`,
              { headers: { Authorization: authHeader } }
            ).then(r => r.json()),

        range.chunk
          ? fetchChunked(baseActUrl, range.fullDays, 7)
          : fetch(`${baseActUrl}?oldest=${getDate(range.fullDays)}&newest=${getDate(0)}`, {
              headers: { Authorization: authHeader }
            }).then(r => r.json()),

        // --- Wellness: always 42-day single call (no chunking) ---
        fetch(`${baseWellUrl}?oldest=${getDate(42)}&newest=${getDate(0)}`, {
          headers: { Authorization: authHeader }
        }).then(r => r.json()),

        fetch(profileUrl, { headers: { Authorization: authHeader } }).then(r => r.json())
      ]);

      console.log(
        `[RUN_REPORT] Completed unified fetch (light=${light?.length || 0}, full=${full?.length || 0}, wellness=${wellness?.length || 0})`
      );


        const payload = JSON.stringify({
          status: "ok",
          message: `Unified report (${reportType}) data fetched successfully.`,
          reportType,
          athlete_id: athleteId,
          chunked: range.chunk,
          render_hint: "data",
          athlete_profile: profile?.athlete || {},
          activities_light: light,
          activities_full: full,
          wellness
        });

        console.log(`[SIZE] /run_report (weekly) payload = ${(payload.length / 1024).toFixed(2)} KB`);

        return new Response(payload, {
          status: 200,
          headers: {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        });
      } catch (e) {
        console.error(`[RUN_REPORT] ERROR: ${e.message}`);
        return new Response(
          JSON.stringify({
            status: 500,
            error: `Report orchestration failed: ${e.message}`
          }),
          { status: 500, headers: { "content-type": "application/json" } }
        );
      }
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
