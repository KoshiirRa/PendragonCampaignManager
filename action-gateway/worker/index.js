const ACTION_SCHEMAS = Object.freeze({
  "play-api.pendragon-chronicle.dwarvenbard.com": "/openapi-gpt-play.json",
  "dynasty-api.pendragon-chronicle.dwarvenbard.com": "/openapi-gpt-dynasty.json",
  "winter-api.pendragon-chronicle.dwarvenbard.com": "/openapi-gpt-winter.json",
});

function jsonResponse(value, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

async function serveSchema(requestUrl, schemaPath, upstreamOrigin) {
  const upstreamUrl = new URL(schemaPath, upstreamOrigin);
  const response = await fetch(upstreamUrl, { headers: { accept: "application/json" } });
  if (!response.ok) {
    return jsonResponse({ detail: "Action schema is temporarily unavailable" }, 502);
  }
  const schema = await response.json();
  schema.servers = [
    {
      url: requestUrl.origin,
      description: `${schema.info?.title ?? "Pendragon Action"} gateway`,
    },
  ];
  return jsonResponse(schema);
}

async function proxyRequest(request, requestUrl, upstreamOrigin) {
  const upstreamUrl = new URL(`${requestUrl.pathname}${requestUrl.search}`, upstreamOrigin);
  const headers = new Headers(request.headers);
  headers.set("x-forwarded-host", requestUrl.host);
  return fetch(new Request(upstreamUrl, { method: request.method, headers, body: request.body }));
}

export default {
  async fetch(request, env) {
    const requestUrl = new URL(request.url);
    const schemaPath = ACTION_SCHEMAS[requestUrl.hostname];
    if (!schemaPath) {
      return jsonResponse({ detail: "Unknown Pendragon Action host" }, 404);
    }
    if (requestUrl.pathname === "/") {
      return Response.redirect(`${requestUrl.origin}/openapi.json`, 302);
    }
    if (requestUrl.pathname === "/openapi.json") {
      return serveSchema(requestUrl, schemaPath, env.PENDRAGON_API_URL);
    }
    return proxyRequest(request, requestUrl, env.PENDRAGON_API_URL);
  },
};
