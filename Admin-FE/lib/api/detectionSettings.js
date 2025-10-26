import {apiFetch} from './client';

export async function listLabelPolicies({token, signal}) {
  return apiFetch('/api/v1/detection-settings/labels', {
    method: 'GET',
    token,
    signal
  });
}

export async function upsertLabelPolicy({token, label, payload}) {
  return apiFetch(`/api/v1/detection-settings/labels/${encodeURIComponent(label)}`, {
    method: 'PUT',
    token,
    body: payload
  });
}

export async function fetchDetectionToggles({token, signal}) {
  return apiFetch('/api/v1/detection-settings/toggles', {
    method: 'GET',
    token,
    signal
  });
}

export async function updateDetectionToggles({token, payload}) {
  return apiFetch('/api/v1/detection-settings/toggles', {
    method: 'PATCH',
    token,
    body: payload
  });
}
