{
  "openapi": "3.1.0",
  "info": {
    "title": "Intervals.icu API (OAuth only, athlete_id=0)",
    "description": "All endpoints use athlete_id=0 (current athlete). Authentication is via OAuth2 only.",
    "version": "2.7.3"
  },
  "servers": [
    { "url": "https://intervals.icu/api/v1" }
  ],
  "paths": {
    "/athlete/0/activities": {
      "get": {
        "summary": "List activities (current athlete only, JSON, auto-pagination, summary/metrics filters available)",
        "operationId": "listActivities",
        "parameters": [
          { "name": "oldest", "in": "query", "description": "Start date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "newest", "in": "query", "description": "End date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "page", "in": "query", "description": "Page number for pagination.", "schema": { "type": "integer", "minimum": 1, "default": 1 } },
          { "name": "per_page", "in": "query", "description": "Number of activities per page. Max 50.", "schema": { "type": "integer", "minimum": 1, "maximum": 50, "default": 20 } },
          { "name": "chunk", "in": "query", "description": "Split long ranges into weekly chunks.", "schema": { "type": "string", "enum": ["week"] } },
          { "name": "auto", "in": "query", "description": "If true, automatically paginate/chunk.", "schema": { "type": "boolean", "default": false } },
          { "name": "summary", "in": "query", "description": "If true, return only summary-level metrics.", "schema": { "type": "boolean", "default": false } },
          { "name": "summaryOnly", "in": "query", "description": "If true, return only load/summary data.", "schema": { "type": "boolean", "default": false } },
          { "name": "metrics", "in": "query", "description": "Optional list of metrics (comma-separated).", "schema": { "type": "string" } },
          { "name": "fields", "in": "query", "description": "Comma-separated list of fields to include.", "schema": { "type": "string" } }
        ],
        "responses": {
          "200": {
            "description": "List of activities (only requested fields if using `fields`, summary if `summaryOnly` true).",
            "content": {
              "application/json": {
                "schema": { "type": "array", "items": { "$ref": "#/components/schemas/Activity" } }
              }
            }
          }
        },
        "examples": {
          "basic": {
            "summary": "Last 7 days of activities",
            "value": "/athlete/0/activities?oldest=2025-09-17&newest=2025-09-24"
          },
          "withFields": {
            "summary": "Trimmed response with selected fields",
            "value": "/athlete/0/activities?oldest=2025-01-01&newest=2025-01-31&fields=id,name,type,distance,icu_training_load,pwhr_decoupling"
          },
          "summaryOnly": {
            "summary": "Load summary only",
            "value": "/athlete/0/activities?oldest=2025-01-01&newest=2025-01-31&summaryOnly=true"
          },
          "pagination": {
            "summary": "Page 2 with 20 results",
            "value": "/athlete/0/activities?page=2&per_page=20"
          }
        }
      }
    },
    "/athlete/0/wellness": {
      "get": {
        "summary": "List wellness data (current athlete only, JSON, summary/metrics filters available)",
        "operationId": "listWellness",
        "parameters": [
          { "name": "oldest", "in": "query", "description": "Start date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "newest", "in": "query", "description": "End date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "page", "in": "query", "description": "Page number for pagination.", "schema": { "type": "integer", "minimum": 1, "default": 1 } },
          { "name": "per_page", "in": "query", "description": "Number of wellness records per page. Max 200.", "schema": { "type": "integer", "minimum": 1, "maximum": 200, "default": 200 } },
          { "name": "chunk", "in": "query", "description": "Split long ranges into weekly chunks.", "schema": { "type": "string", "enum": ["week"] } },
          { "name": "auto", "in": "query", "description": "If true, automatically paginate/chunk.", "schema": { "type": "boolean", "default": false } },
          { "name": "summary", "in": "query", "description": "If true, return only summary-level metrics.", "schema": { "type": "boolean", "default": false } },
          { "name": "summaryOnly", "in": "query", "description": "If true, return only load/summary data (CTL, ATL, Form).", "schema": { "type": "boolean", "default": false } },
          { "name": "metrics", "in": "query", "description": "Optional list of metrics (comma-separated).", "schema": { "type": "string" } },
          { "name": "fields", "in": "query", "description": "Comma-separated list of fields to include.", "schema": { "type": "string" } }
        ],
        "responses": {
          "200": {
            "description": "List of wellness records (only requested fields if using `fields`, summary if `summaryOnly` true).",
            "content": {
              "application/json": {
                "schema": { "type": "array", "items": { "$ref": "#/components/schemas/Wellness" } }
              }
            }
          }
        },
        "examples": {
          "basic": {
            "summary": "Last 7 days of wellness",
            "value": "/athlete/0/wellness?oldest=2025-09-17&newest=2025-09-24"
          },
          "withFields": {
            "summary": "Trimmed wellness response",
            "value": "/athlete/0/wellness?oldest=2025-01-01&newest=2025-01-31&fields=date,ctl,atl,form,hrv,restingHr"
          },
          "summaryOnly": {
            "summary": "Load summary only",
            "value": "/athlete/0/wellness?oldest=2025-01-01&newest=2025-01-31&summaryOnly=true"
          },
          "pagination": {
            "summary": "Page 2 with 100 results",
            "value": "/athlete/0/wellness?page=2&per_page=100"
          }
        }
      }
    },
    "/athlete/0/wellness.csv": {
      "get": {
        "summary": "Export wellness data as CSV (current athlete only)",
        "operationId": "listWellnessCsv",
        "parameters": [
          { "name": "oldest", "in": "query", "required": true, "description": "Start date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "newest", "in": "query", "required": true, "description": "End date (YYYY-MM-DD).", "schema": { "type": "string", "format": "date" } },
          { "name": "cols", "in": "query", "description": "Optional comma-separated list of columns to include.", "schema": { "type": "string" } },
          { "name": "auto", "in": "query", "description": "If true, automatically paginate/chunk.", "schema": { "type": "boolean", "default": false } }
        ],
        "responses": {
          "200": {
            "description": "CSV wellness data",
            "content": {
              "text/csv": { "schema": { "type": "string" } }
            }
          }
        },
        "examples": {
          "basic": {
            "summary": "CSV export of January 2025",
            "value": "/athlete/0/wellness.csv?oldest=2025-01-01&newest=2025-01-31"
          },
          "withCols": {
            "summary": "CSV with selected columns",
            "value": "/athlete/0/wellness.csv?oldest=2025-01-01&newest=2025-01-31&cols=date,ctl,atl,form,hrv"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Activity": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "description": "Unique activity ID" },
          "name": { "type": "string", "description": "Activity title" },
          "type": { "type": "string", "description": "Activity type (Ride, Run, Swim, etc.)" },
          "start_date_local": { "type": "string", "format": "date-time", "description": "Local start date/time" },
          "distance": { "type": "number", "description": "Total distance (meters)" },
          "moving_time": { "type": "number", "description": "Moving time (seconds)" },
          "elapsed_time": { "type": "number", "description": "Elapsed time (seconds)" },
          "average_heartrate": { "type": ["number","null"], "description": "Average HR (bpm)" },
          "weighted_average_watts": { "type": ["number","null"], "description": "Weighted avg. power (W)" },
          "icu_training_load": { "type": ["number","null"], "description": "Training load score (similar to TSS)" },
          "total_elevation_gain": { "type": ["number","null"], "description": "Elevation gain (meters)" },
          "rpe": { "type": ["number","null"], "description": "Rate of perceived exertion (1–10)" },
          "feel": { "type": ["integer","null"], "description": "Subjective feel rating (easy=1 → very hard=5)" },
          "pwhr_decoupling": { "type": ["number","null"], "description": "Cycling HR drift (power vs HR decoupling, %)" },
          "pahr_decoupling": { "type": ["number","null"], "description": "Running HR drift (pace vs HR decoupling, %)" }
        }
      },
      "Wellness": {
        "type": "object",
        "properties": {
          "date": { "type": "string", "format": "date", "description": "Date of record" },
          "ctl": { "type": ["number","null"], "description": "Chronic Training Load (42-day rolling avg)" },
          "atl": { "type": ["number","null"], "description": "Acute Training Load (7-day rolling avg)" },
          "form": { "type": ["number","null"], "description": "Form = CTL - ATL (positive=fresh, negative=fatigued)" },
          "rampRate": { "type": ["number","null"], "description": "Weekly change in CTL" },
          "ctlLoad": { "type": ["number","null"], "description": "Daily CTL contribution" },
          "atlLoad": { "type": ["number","null"], "description": "Daily ATL contribution" },
          "weight": { "type": ["number","null"], "description": "Weight (kg)" },
          "sleepSecs": { "type": ["number","null"], "description": "Sleep duration (seconds)" },
          "hrv": { "type": ["number","null"], "description": "HRV (ms, RMSSD or similar)" },
          "restingHr": { "type": ["number","null"], "description": "Resting HR (bpm)" },
          "comments": { "type": ["string","null"], "description": "Subjective notes (mood, stress, soreness)" }
        }
      }
    },
    "securitySchemes": {
      "OAuth2": {
        "type": "oauth2",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://intervals.icu/oauth/authorize",
            "tokenUrl": "https://intervals.icu/api/oauth/token",
            "scopes": {
              "read": "Read activities and wellness data"
            }
          }
        }
      }
    }
  },
  "security": [
    { "OAuth2": ["read"] }
  ]
}
* * *