const API_BASE = ''

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiCall<T = unknown>(url: string, options: RequestInit = {}, timeoutMs = 30000): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const res = await fetch(API_BASE + url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      const detail = errData.detail || errData.message || `Request failed (${res.status})`
      throw new ApiError(detail, res.status)
    }

    return (await res.json()) as T
  } catch (err) {
    if (err instanceof ApiError) throw err
    if ((err as Error).name === 'AbortError') {
      throw new ApiError('请求超时，请检查服务是否启动', 408)
    }
    throw new ApiError((err as Error).message || '网络错误', 0)
  } finally {
    clearTimeout(timeout)
  }
}

export function get<T = unknown>(url: string, timeoutMs?: number): Promise<T> {
  return apiCall<T>(url, { method: 'GET' }, timeoutMs)
}

export function post<T = unknown>(url: string, body: unknown, timeoutMs?: number): Promise<T> {
  return apiCall<T>(url, { method: 'POST', body: JSON.stringify(body) }, timeoutMs)
}

export function del<T = unknown>(url: string, timeoutMs?: number): Promise<T> {
  return apiCall<T>(url, { method: 'DELETE' }, timeoutMs)
}
