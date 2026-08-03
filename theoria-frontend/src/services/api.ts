import { API_BASE_URL } from "@/utils/constants";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/utils/storage";

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function apiFetch<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requiresAuth = true, headers = {}, ...rest } = options;

  const requestHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  if (requiresAuth) {
    const token = getAccessToken();
    if (token) {
      requestHeaders["Authorization"] = `Bearer ${token}`;
    }
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  let response = await fetch(url, {
    headers: requestHeaders,
    ...rest,
  });

  // If 401 Unauthorized, attempt token refresh once
  if (response.status === 401 && requiresAuth) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        const refreshResp = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResp.ok) {
          const data = await refreshResp.json();
          setTokens(data.access_token, data.refresh_token);
          requestHeaders["Authorization"] = `Bearer ${data.access_token}`;

          // Retry original request
          response = await fetch(url, {
            headers: requestHeaders,
            ...rest,
          });
        } else {
          clearTokens();
        }
      } catch (err) {
        clearTokens();
      }
    }
  }

  if (!response.ok) {
    let errorMessage = `Request failed (${response.status})`
    try {
      const errorData = await response.json()
      const detail = errorData.detail ?? errorData.message

      if (typeof detail === "string") {
        // Simple string error e.g. "Email already registered"
        errorMessage = detail
      } else if (Array.isArray(detail)) {
        // FastAPI validation errors: [{loc, msg, type}, ...]
        errorMessage = detail
          .map((e: { msg?: string; loc?: string[] }) =>
            [e.loc?.slice(1).join(" → "), e.msg].filter(Boolean).join(": ")
          )
          .join("; ")
      } else if (detail) {
        errorMessage = String(detail)
      }
    } catch {
      errorMessage = response.statusText || errorMessage
    }
    throw new Error(errorMessage)
  }

  return response.json();
}
