import {apiFetch} from './client';

export async function fetchLogs({token, params = {}, signal}) {
  return apiFetch('/api/v1/logs/search', {
    method: 'GET',
    token,
    searchParams: params,
    signal
  });
}

export async function fetchLogById({token, logId, signal}) {
  return apiFetch(`/api/v1/logs/${logId}`, {
    method: 'GET',
    token,
    signal
  });
}

export async function fetchLogStats({token, days = 7, signal}) {
  return apiFetch('/api/v1/logs/stats', {
    method: 'GET',
    token,
    searchParams: {days},
    signal
  });
}

export async function fetchRecentLogs({token, limit = 20, signal}) {
  return apiFetch('/api/v1/logs/recent', {
    method: 'GET',
    token,
    searchParams: {limit},
    signal
  });
}
