'use client';

import useSWR from 'swr';
import {useMemo} from 'react';
import {fetchDashboardSummary} from '@/lib/api/dashboard';
import {useAuth} from '@/contexts/AuthContext';

export function useDashboardSummary({tz = 'UTC', days = 90, recentLimit = 10} = {}) {
  const {token} = useAuth();

  const key = useMemo(() => {
    if (!token) return null;
    return ['dashboard-summary', tz, days, recentLimit, token];
  }, [token, tz, days, recentLimit]);

  const {data, error, isLoading, mutate} = useSWR(key, ([, tzValue, daysValue, recentValue]) =>
    fetchDashboardSummary({token, tz: tzValue, days: daysValue, recentLimit: recentValue})
  );

  return {
    summary: data,
    isLoading,
    error,
    refresh: () => mutate()
  };
}
