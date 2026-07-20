import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
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
  assert.match(page, /people:\s*Array/);
  assert.match(page, /data\.people/);
  assert.match(page, /setPeople\(livePeople\)/);
  assert.match(page, /annual-chronicle-sections/);
  assert.match(css, /\.annual-chronicle/);
  assert.match(route, /player-view/);
  assert.match(route, /cache:\s*"no-store"/);
});

test("serves responsive map variants without the runtime image optimizer", async () => {
  const response = await render();
  const html = await response.text();
  const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  const generatedMaps = [
    "logres-player-map-circa-510-640.avif",
    "logres-player-map-circa-510-1240.webp",
    "salisbury-county-circa-510-640.avif",
    "salisbury-county-circa-510-2400.webp",
  ];

  assert.doesNotMatch(html, /\/_vinext\/image/);
  assert.match(html, /<picture>/);
  assert.match(html, /logres-player-map-circa-510-640\.avif 640w/);
  assert.match(page, /salisbury-county-circa-510-2400\.webp 2400w/);

  for (const filename of generatedMaps) {
    const file = await stat(new URL(`../public/maps/${filename}`, import.meta.url));
    assert.ok(file.size > 0, `${filename} should be a non-empty generated map`);
  }
});
