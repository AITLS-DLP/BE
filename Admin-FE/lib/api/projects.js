import {apiFetch} from './client';

export async function listProjects({token, signal}) {
  return apiFetch('/api/v1/projects/', {
    method: 'GET',
    token,
    signal
  });
}

export async function createProject({token, payload}) {
  return apiFetch('/api/v1/projects/', {
    method: 'POST',
    token,
    body: payload
  });
}

export async function updateProject({token, projectId, payload}) {
  return apiFetch(`/api/v1/projects/${projectId}`, {
    method: 'PATCH',
    token,
    body: payload
  });
}

export async function deleteProject({token, projectId}) {
  return apiFetch(`/api/v1/projects/${projectId}`, {
    method: 'DELETE',
    token
  });
}
