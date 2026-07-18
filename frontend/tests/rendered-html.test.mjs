import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the campaign chronicle", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>The Salisbury Chronicle<\/title>/i);
  assert.match(html, /The Chronicle of the Year 485/);
  assert.match(html, /Of Sir Cadry/);
  assert.match(html, /Winter chronicle/);
});

test("wires annual chronicles from the player API into the responsive UI", async () => {
  const [page, css, route] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readFile(new URL("../app/api/campaign/route.ts", import.meta.url), "utf8"),
  ]);

  assert.match(page, /chronicles:\s*Array/);
  assert.match(page, /data\.chronicles/);
  assert.match(page, /annual-chronicle-sections/);
  assert.match(css, /\.annual-chronicle/);
  assert.match(route, /player-view/);
  assert.match(route, /cache:\s*"no-store"/);
});
