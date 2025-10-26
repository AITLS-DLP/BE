import {apiFetch} from './client';

export async function login({username, password}) {
  const body = new URLSearchParams({
    username,
    password
  });

  return apiFetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body
  });
}

export async function fetchCurrentUser({token}) {
  return apiFetch('/api/v1/auth/me', {
    method: 'GET',
    token
  });
}
