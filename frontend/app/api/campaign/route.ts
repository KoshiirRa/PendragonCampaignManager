export async function GET(request: Request) {
  const apiUrl = process.env.PENDRAGON_API_URL;
  const apiKey = process.env.PENDRAGON_API_KEY;
  const campaignId = process.env.PENDRAGON_CAMPAIGN_ID;
  const campaignDomain = process.env.PENDRAGON_CAMPAIGN_DOMAIN;

  if (!apiUrl || !apiKey) {
    return Response.json({ detail: "Campaign data is not configured" }, { status: 503 });
  }

  const forwardedHost = request.headers.get("x-forwarded-host");
  const hostname = (forwardedHost || new URL(request.url).hostname).split(":")[0].toLowerCase();
  const suffix = campaignDomain ? `.${campaignDomain.toLowerCase()}` : null;
  const campaignSlug = suffix && hostname.endsWith(suffix)
    ? hostname.slice(0, -suffix.length)
    : null;
  const campaignPath = campaignSlug
    ? `by-slug/${encodeURIComponent(campaignSlug)}`
    : campaignId;

  if (!campaignPath || campaignSlug?.includes(".")) {
    return Response.json({ detail: "Campaign hostname is not recognized" }, { status: 404 });
  }

  const response = await fetch(
    `${apiUrl.replace(/\/$/, "")}/api/v1/campaigns/${campaignPath}/player-view`,
    { headers: { "X-API-Key": apiKey }, cache: "no-store" },
  );
  if (!response.ok) {
    return Response.json({ detail: "Campaign data is unavailable" }, { status: 502 });
  }
  return Response.json(await response.json(), {
    headers: { "Cache-Control": "private, no-store" },
  });
}
