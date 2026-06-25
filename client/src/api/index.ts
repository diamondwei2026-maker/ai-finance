/** fetch 请求封装层 — 超时、错误处理、响应类型。 */

import type { ApiResponse } from '@/types/api';
import { ErrorCode } from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════
// ApiError
// ═══════════════════════════════════════════════════════════════════════

/** API 错误异常类。 */
export class ApiError extends Error {
  /** 错误码（业务错误码或 HTTP 状态码）。 */
  code: number;

  constructor(code: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 配置
// ═══════════════════════════════════════════════════════════════════════

/** API 基础地址，默认本地开发环境。 */
export const BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/** 请求超时时间（毫秒）。 */
const REQUEST_TIMEOUT = 15000;

// ═══════════════════════════════════════════════════════════════════════
// baseFetch
// ═══════════════════════════════════════════════════════════════════════

/**
 * 基础 fetch 封装，带超时和统一错误处理。
 *
 * @param path 请求路径（以 / 开头，如 "/api/v1/funds/020741"）。
 * @param options 可选的 RequestInit 配置。
 * @returns 直接返回 ApiResponse 的 data 字段。
 * @throws {ApiError} 所有异常统一包装为 ApiError。
 */
export async function baseFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    // HTTP 状态码检查
    if (!res.ok) {
      throw new ApiError(res.status, `请求失败: ${res.statusText}`);
    }

    // 业务错误码检查
    const json: ApiResponse<T> = await res.json();

    if (json.code !== 0) {
      throw new ApiError(json.code, json.message);
    }

    return json.data as T;
  } catch (err: unknown) {
    // 已是 ApiError 实例，直接抛出
    if (err instanceof ApiError) {
      throw err;
    }

    // 超时（AbortController 触发）
    if (err instanceof Error && err.name === 'AbortError') {
      throw new ApiError(ErrorCode.TIMEOUT, '请求超时，请稍后重试');
    }

    // 其他网络异常
    throw new ApiError(ErrorCode.NETWORK_ERROR, '网络异常，请检查网络连接');
  } finally {
    clearTimeout(timeoutId);
  }
}
