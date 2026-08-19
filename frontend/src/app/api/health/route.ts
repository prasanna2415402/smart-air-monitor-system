export const dynamic = "force-dynamic";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export async function GET() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/docs/swagger.json`, {
      cache: "no-store",
    });
    return Response.json({ ok: res.ok, backend: API_BASE_URL });
  } catch {
    return Response.json({ ok: false, backend: API_BASE_URL }, { status: 500 });
  }
}
