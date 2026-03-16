import { NextRequest, NextResponse } from "next/server";

import { getServerApiBaseUrl } from "@/lib/api";

const ALLOWED_METHODS = new Set(["GET", "POST", "PUT", "DELETE", "PATCH"]);

async function proxyRequest(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  const targetBaseUrl = getServerApiBaseUrl();

  if (!targetBaseUrl) {
    return NextResponse.json(
      {
        error:
          "API_BASE_URL is not configured on the Vercel project. Set it to your Railway backend URL.",
      },
      { status: 500 },
    );
  }

  if (!ALLOWED_METHODS.has(request.method)) {
    return NextResponse.json(
      { error: `method ${request.method} is not supported by the proxy` },
      { status: 405 },
    );
  }

  const search = request.nextUrl.search || "";
  const targetUrl = `${targetBaseUrl}/${path.join("/")}${search}`;
  const requestHeaders = new Headers(request.headers);
  requestHeaders.delete("host");
  requestHeaders.delete("connection");
  requestHeaders.delete("content-length");

  const init: RequestInit = {
    method: request.method,
    headers: requestHeaders,
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(request.method)) {
    init.body = await request.text();
  }

  try {
    const upstreamResponse = await fetch(targetUrl, init);
    const responseHeaders = new Headers(upstreamResponse.headers);
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("content-length");
    responseHeaders.set("x-proxied-by", "vercel-app-api");

    return new NextResponse(upstreamResponse.body, {
      status: upstreamResponse.status,
      headers: responseHeaders,
    });
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "unknown proxy request error",
        targetUrl,
      },
      { status: 502 },
    );
  }
}

export { proxyRequest as GET, proxyRequest as POST, proxyRequest as PUT };
