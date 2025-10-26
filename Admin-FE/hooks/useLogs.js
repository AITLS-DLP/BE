'use client';

import {useMemo} from 'react';
import useSWR from 'swr';
import {fetchLogs, fetchLogStats, fetchRecentLogs} from '@/lib/api/logs';
import {useAuth} from '@/contexts/AuthContext';

export function useLogs(filters = {}) {
  const {token} = useAuth();
  const searchKey = useMemo(() => {
    if (!token) return null;
    const serialised = JSON.stringify(filters);
    return ['logs-search', serialised, token];
  }, [token, filters]);

  const statsKey = useMemo(() => {
    if (!token) return null;
    return ['logs-stats', filters?.statsDays ?? 7, token];
  }, [token, filters?.statsDays, filters]);

  const recentKey = useMemo(() => {
    if (!token) return null;
    return ['logs-recent', filters?.recentLimit ?? 10, token];
  }, [token, filters?.recentLimit, filters]);

  const {
    data: searchData,
    error: searchError,
    isLoading: searchLoading,
    mutate: refreshSearch
  } = useSWR(searchKey, ([, serialised]) => {
    const params = JSON.parse(serialised);
    const {statsDays: _statsDays, recentLimit: _recentLimit, ...searchParams} = params;
    return fetchLogs({token, params: searchParams});
  });

  const {
    data: statsData,
    error: statsError,
    isLoading: statsLoading,
    mutate: refreshStats
  } = useSWR(statsKey, ([, days]) => fetchLogStats({token, days}));

  const {
    data: recentData,
    error: recentError,
    isLoading: recentLoading,
    mutate: refreshRecent
  } = useSWR(recentKey, ([, limit]) => fetchRecentLogs({token, limit}));

  return {
    logs: searchData?.logs ?? [],
    total: searchData?.total ?? 0,
    page: searchData?.page ?? filters?.page ?? 1,
    size: searchData?.size ?? filters?.size ?? 20,
    stats: statsData,
    recent: recentData?.logs ?? [],
    isLoading: searchLoading || statsLoading || recentLoading,
    error: searchError || statsError || recentError,
    refresh: () => {
      refreshSearch();
      refreshStats();
      refreshRecent();
    }
  };
}
