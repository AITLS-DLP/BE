'use client';

import useSWR from 'swr';
import {useMemo, useCallback} from 'react';
import {fetchSystemSettings, updateSystemSettings} from '@/lib/api/systemSettings';
import {useAuth} from '@/contexts/AuthContext';

export function useSystemSettings() {
  const {token} = useAuth();
  const key = useMemo(() => (token ? ['system-settings', token] : null), [token]);

  const {
    data,
    error,
    isLoading,
    mutate
  } = useSWR(key, () => fetchSystemSettings({token}));

  const save = useCallback(
    async (payload) => {
      const updated = await updateSystemSettings({token, payload});
      await mutate(updated, {revalidate: false});
      return updated;
    },
    [token, mutate]
  );

  return {
    settings: data ?? null,
    isLoading,
    error,
    save,
    refresh: () => mutate()
  };
}
