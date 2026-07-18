import assert from "node:assert/strict";
import test from "node:test";

import worker from "../worker/index.js";

const env = { PENDRAGON_API_URL: "https://backend.example" };

test("play host serves its schema with the gateway server URL", async (context) => {
  context.mock.method(globalThis, "fetch", async (request) => {
    assert.equal(request.toString(), "https://backend.example/openapi-gpt-play.json");
    return Response.json({ info: { title: "Play" }, servers: [], paths: {} });
  });
  const response = await worker.fetch(
    new Request("https://play-api.pendragon-chronicle.dwarvenbard.com/openapi.json"),
    env,
  );
  const schema = await response.json();
  assert.equal(response.status, 200);
  assert.equal(schema.servers[0].url, "https://play-api.pendragon-chronicle.dwarvenbard.com");
});

test("dynasty host selects the dynasty schema", async (context) => {
  context.mock.method(globalThis, "fetch", async (request) => {
    assert.equal(request.toString(), "https://backend.example/openapi-gpt-dynasty.json");
    return Response.json({ info: { title: "Dynasty" }, paths: {} });
  });
  const response = await worker.fetch(
    new Request("https://dynasty-api.pendragon-chronicle.dwarvenbard.com/openapi.json"),
    env,
  );
  assert.equal(response.status, 200);
});

test("winter host selects the Winter Phase schema", async (context) => {
  context.mock.method(globalThis, "fetch", async (request) => {
    assert.equal(request.toString(), "https://backend.example/openapi-gpt-winter.json");
    return Response.json({ info: { title: "Winter" }, paths: {} });
  });
  const response = await worker.fetch(
    new Request("https://winter-api.pendragon-chronicle.dwarvenbard.com/openapi.json"),
    env,
  );
  assert.equal(response.status, 200);
});

test("API requests preserve authentication and proxy to the backend", async (context) => {
  context.mock.method(globalThis, "fetch", async (request) => {
    assert.equal(request.url, "https://backend.example/api/v1/campaigns?limit=10");
    assert.equal(request.headers.get("x-api-key"), "secret-value");
    assert.equal(
      request.headers.get("x-forwarded-host"),
      "play-api.pendragon-chronicle.dwarvenbard.com",
    );
    return Response.json([]);
  });
  const response = await worker.fetch(
    new Request(
      "https://play-api.pendragon-chronicle.dwarvenbard.com/api/v1/campaigns?limit=10",
      { headers: { "x-api-key": "secret-value" } },
    ),
    env,
  );
  assert.equal(response.status, 200);
});

test("unknown hosts are rejected", async () => {
  const response = await worker.fetch(new Request("https://unknown.example/openapi.json"), env);
  assert.equal(response.status, 404);
});
