const DEFAULT_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(message, {status, body}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

function buildUrl(path, searchParams) {
  const url = path.startsWith('http') ? new URL(path) : new URL(path, DEFAULT_BASE_URL);
  if (searchParams) {
    Object.entries(searchParams)
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((v) => url.searchParams.append(key, String(v)));
        } else {
          url.searchParams.set(key, String(value));
        }
      });
  }
  return url;
}

export async function apiFetch(path, options = {}) {
  const {
    method = 'GET',
    headers = {},
    body,
    token,
    searchParams,
    signal,
    cache = 'no-store'
  } = options;

  const url = buildUrl(path, searchParams);
  const requestHeaders = new Headers({Accept: 'application/json', ...headers});

  if (token) {
    requestHeaders.set('Authorization', `Bearer ${token}`);
  }

  let requestBody = body;
  if (body && typeof body === 'object' && !(body instanceof FormData) && !(body instanceof URLSearchParams) && !headers['Content-Type']) {
    requestBody = JSON.stringify(body);
    requestHeaders.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: requestBody,
    signal,
    cache
  });

  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.clone().json();
    } catch (error) {
      errorBody = await response.text();
    }
    throw new ApiError('API 요청이 실패했습니다.', {
      status: response.status,
      body: errorBody
    });
  }

  if (response.status === 204) {
    return null;
  }

  const text = await response.text();
  return text ? JSON.parse(text) : null;
}
