import {apiFetch} from './client';

export async function fetchSystemSettings({token, signal}) {
  return apiFetch('/api/v1/system-settings/', {
    method: 'GET',
    token,
    signal
  });
}

export async function updateSystemSettings({token, payload}) {
  return apiFetch('/api/v1/system-settings/', {
    method: 'PATCH',
    token,
    body: payload
  });
}
