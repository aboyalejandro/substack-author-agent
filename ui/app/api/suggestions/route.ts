// Proxies follow-up suggestion requests to the Python backend's /suggestions
// endpoint (server-side, so no CORS). The backend runs a forced-tool Claude
// call — see agui_server.py.
const AGUI_URL = process.env.AGNO_AGUI_URL ?? "http://localhost:8000/agui";
const SUGGESTIONS_URL = AGUI_URL.replace(/\/agui\/?$/, "") + "/suggestions";

export async function POST(req: Request) {
  try {
    const body = await req.text();
    const res = await fetch(SUGGESTIONS_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    return new Response(await res.text(), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json({ suggestions: [] });
  }
}
