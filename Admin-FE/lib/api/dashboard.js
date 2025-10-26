import {apiFetch} from './client';

export async function fetchDashboardSummary({token, days = 90, tz = 'UTC', recentLimit = 10, signal}) {
  return apiFetch('/api/v1/dashboard/summary', {
    method: 'GET',
    token,
    signal,
    searchParams: {
      days,
      tz,
      recent_limit: recentLimit
    }
  });
}
