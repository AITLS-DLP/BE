'use client';

import useSWR from 'swr';
import {useMemo, useCallback} from 'react';
import {listProjects, createProject, updateProject, deleteProject} from '@/lib/api/projects';
import {useAuth} from '@/contexts/AuthContext';

export function useProjects() {
  const {token} = useAuth();
  const key = useMemo(() => (token ? ['projects', token] : null), [token]);

  const {
    data,
    error,
    isLoading,
    mutate
  } = useSWR(key, () => listProjects({token}));

  const handleCreate = useCallback(
    async (payload) => {
      await createProject({token, payload});
      await mutate();
    },
    [token, mutate]
  );

  const handleUpdate = useCallback(
    async (projectId, payload) => {
      await updateProject({token, projectId, payload});
      await mutate();
    },
    [token, mutate]
  );

  const handleDelete = useCallback(
    async (projectId) => {
      await deleteProject({token, projectId});
      await mutate();
    },
    [token, mutate]
  );

  return {
    projects: data ?? [],
    isLoading,
    error,
    createProject: handleCreate,
    updateProject: handleUpdate,
    deleteProject: handleDelete,
    refresh: () => mutate()
  };
}
