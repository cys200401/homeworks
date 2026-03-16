const SERVER_API_BASE_URL =
  process.env.API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL ??
  "";

export function getApiBaseUrl() {
  return "";
}

export function getServerApiBaseUrl() {
  return SERVER_API_BASE_URL.replace(/\/+$/, "");
}

export function toApiPath(path: string) {
  if (!path.startsWith("/")) {
    return `/api/${path}`;
  }
  if (path.startsWith("/api/")) {
    return path;
  }
  return `/api${path}`;
}
