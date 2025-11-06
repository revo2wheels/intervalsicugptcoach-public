{
  "openapi": "3.1.0",
  "info": {
    "title": "Intervals.icu API (OAuth only, athlete_id=0) + Report Schemas",
    "description": "Merged schema including Intervals.icu API plus report validation for weekly and season summaries with mandatory enforcement rules.",
    "version": "3.7.0"
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
          { "name": "oldest", "in": "query", "schema": { "type": "string", "format": "date" } },
          { "name": "newest", "in": "query", "schema": { "type": "string", "format": "date" } },
          { "name": "page", "in": "query", "schema": { "type": "integer" } },
          { "name": "per_page", "in": "query", "schema": { "type": "integer" } },
          { "name": "chunk", "in": "query", "schema": { "type": "string" } },
          { "name": "auto", "in": "query", "schema": { "type": "boolean" } },
          { "name": "fields", "in": "query", "schema": { "type": "string" } }
        ],
        "responses": {
          "200": {
            "description": "List of activities",
            "content": {
              "application/json": {
                "schema": { "type": "array", "items": { "$ref": "#/components/schemas/Activity" } }
              }
            }
          }
        }
      }
    },
    "/athlete/0/activities.csv": {
      "get": {
        "summary": "Export activities as CSV (current athlete only)",
        "operationId": "listActivitiesCsv",
        "parameters": [
          { "name": "oldest", "in": "query", "schema": { "type": "string", "format": "date" }, "required": true },
          { "name": "newest", "in": "query", "schema": { "type": "string", "format": "date" }, "required": true },
          { "name": "cols", "in": "query", "schema": { "type": "string" } },
          { "name": "auto", "in": "query", "schema": { "type": "boolean" } }
        ],
        "responses": {
          "200": {
            "description": "CSV activities data",
            "content": { "text/csv": { "schema": { "type": "string" } } }
          }
        }
      }
    },
    "/athlete/0/wellness": {
      "get": {
        "summary": "List wellness data (current athlete only)",
        "operationId": "listWellness",
        "parameters": [
          { "name": "oldest", "in": "query", "schema": { "type": "string", "format": "date" } },
          { "name": "newest", "in": "query", "schema": { "type": "string", "format": "date" } },
          { "name": "page", "in": "query", "schema": { "type": "integer" } },
          { "name": "per_page", "in": "query", "schema": { "type": "integer" } },
          { "name": "chunk", "in": "query", "schema": { "type": "string" } },
          { "name": "auto", "in": "query", "schema": { "type": "boolean" } },
          { "name": "fields", "in": "query", "schema": { "type": "string" } }
        ],
        "responses": {
          "200": {
            "description": "List of wellness records",
            "content": {
              "application/json": {
                "schema": { "type": "array", "items": { "$ref": "#/components/schemas/Wellness" } }
              }
            }
          }
        }
      }
    },
    "/athlete/0/wellness.csv": {
      "get": {
        "summary": "Export wellness data as CSV (current athlete only)",
        "operationId": "listWellnessCsv",
        "parameters": [
          { "name": "oldest", "in": "query", "schema": { "type": "string", "format": "date" }, "required": true },
          { "name": "newest", "in": "query", "schema": { "type": "string", "format": "date" }, "required": true },
          { "name": "cols", "in": "query", "schema": { "type": "string" } },
          { "name": "auto", "in": "query", "schema": { "type": "boolean" } }
        ],
        "responses": {
          "200": {
            "description": "CSV wellness data",
            "content": { "text/csv": { "schema": { "type": "string" } } }
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
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "start_date_local": { "type": "string", "format": "date-time" },
          "distance": { "type": "number" },
          "moving_time": { "type": "number" },
          "elapsed_time": { "type": "number" },
          "average_heartrate": { "type": ["number", "null"] },
          "weighted_average_watts": { "type": ["number", "null"] },
          "icu_training_load": { "type": ["number", "null"] },
          "total_elevation_gain": { "type": ["number", "null"] },
          "rpe": { "type": ["number", "null"] },
          "feel": { "type": ["integer", "null"] },
          "pwhr_decoupling": { "type": ["number", "null"] },
          "pahr_decoupling": { "type": ["number", "null"] },
          "VO2MaxGarmin": { "type": ["number", "null"] },
          "PerformanceCondition": { "type": ["number", "null"] },
          "ftp": { "type": ["number", "null"] },
          "IF": { "type": ["number", "null"] },
          "zoneTimes": {
            "type": "object",
            "patternProperties": { "^Z[1-5]$": { "type": ["number", "null"] } },
            "additionalProperties": false
          },
          "zoneNames": { "type": "array", "items": { "type": "string" } },
          "zoneBoundaries": { "type": "array", "items": { "type": "number" } }
        }
      },
      "Wellness": {
        "type": "object",
        "properties": {
        "date": { "type": "string", "format": "date" },
      "ctl": { "type": "number" },
      "atl": { "type": "number" },
      "form": { "type": "number" },
      "rampRate": { "type": "number" },
      "ctlLoad": { "type": "number" },
      "atlLoad": { "type": "number" },

      "weight": { "type": "number" },
      "bodyFat": { "type": "number" },
      "abdomen": { "type": "number" },

      "sleepSecs": { "type": "number" },
      "sleepScore": { "type": "number" },
      "sleepQuality": { "type": "number" },
      "avgSleepingHr": { "type": "number" },

      "hrv": { "type": "number" },
      "hrvSDNN": { "type": "number" },
      "restingHr": { "type": "number" },

      "soreness": { "type": "number" },
      "fatigue": { "type": "number" },
      "stress": { "type": "number" },
      "mood": { "type": "number" },
      "motivation": { "type": "number" },

      "hydration": { "type": "number" },
      "hydrationVolume": { "type": "number" },
      "injury": { "type": "number" },
      "readiness": { "type": "number" },

      "spO2": { "type": "number" },
      "systolic": { "type": "number" },
      "diastolic": { "type": "number" },
      "bloodGlucose": { "type": "number" },
      "lactate": { "type": "number" },

      "menstrualPhase": { "type": "string" },
      "menstrualPhasePredicted": { "type": "string" },

      "vo2max": { "type": "number" },
      "Ride_eFTP": { "type": "number" },
      "Run_eFTP": { "type": "number" },

      "comments": { "type": ["string", "null"] }
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
              "ACTIVITY:READ": "Read activities",
              "WELLNESS:READ": "Read wellness data",
              "SETTINGS:READ": "Read athlete profile and configuration"
            }
          }
        }
      }
    }
  },
  "security": [
    {
      "OAuth2": [
        "ACTIVITY:READ",
        "WELLNESS:READ",
        "SETTINGS:READ"
      ]
    }
  ]
  },
}
