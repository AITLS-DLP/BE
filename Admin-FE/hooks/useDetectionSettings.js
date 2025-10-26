'use client';

import useSWR from 'swr';
import {useMemo, useCallback} from 'react';
import {
  listLabelPolicies,
  upsertLabelPolicy,
  fetchDetectionToggles,
  updateDetectionToggles
} from '@/lib/api/detectionSettings';
import {useAuth} from '@/contexts/AuthContext';

export function useDetectionSettings() {
  const {token} = useAuth();

  const labelsKey = useMemo(() => (token ? ['label-policies', token] : null), [token]);
  const togglesKey = useMemo(() => (token ? ['detection-toggles', token] : null), [token]);

  const {
    data: labels,
    error: labelsError,
    isLoading: labelsLoading,
    mutate: refreshLabels
  } = useSWR(labelsKey, () => listLabelPolicies({token}));

  const {
    data: toggles,
    error: togglesError,
    isLoading: togglesLoading,
    mutate: refreshToggles
  } = useSWR(togglesKey, () => fetchDetectionToggles({token}));

  const saveLabelPolicy = useCallback(
    async (label, payload) => {
      await upsertLabelPolicy({token, label, payload});
      await refreshLabels();
    },
    [token, refreshLabels]
  );

  const saveToggles = useCallback(
    async (payload) => {
      const updated = await updateDetectionToggles({token, payload});
      await refreshToggles();
      return updated;
    },
    [token, refreshToggles]
  );

  return {
    labels: labels ?? [],
    toggles: toggles ?? null,
    isLoading: labelsLoading || togglesLoading,
    error: labelsError || togglesError,
    saveLabelPolicy,
    saveToggles,
    refresh: () => {
      refreshLabels();
      refreshToggles();
    }
  };
}
