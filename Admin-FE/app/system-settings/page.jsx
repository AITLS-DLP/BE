'use client';

import {useEffect, useState} from 'react';
import PageHeader from '@/components/PageHeader';
import Section from '@/components/Section';
import RequireAuth from '@/components/RequireAuth';
import {useSystemSettings} from '@/hooks/useSystemSettings';

function SystemSettingsForm({settings, onSave}) {
  const [form, setForm] = useState(settings ?? {
    default_timezone: 'UTC',
    data_retention_days: 30,
    maintenance_mode: false,
    alert_email: ''
  });
  const [pending, setPending] = useState(false);

  useEffect(() => {
    setForm(settings ?? {
      default_timezone: 'UTC',
      data_retention_days: 30,
      maintenance_mode: false,
      alert_email: ''
    });
  }, [settings]);

  async function handleSubmit(event) {
    event.preventDefault();
    setPending(true);
    try {
      await onSave(form);
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <label className="flex flex-col gap-1 text-sm">
        <span>기본 시간대</span>
        <select
          value={form.default_timezone}
          onChange={(event) => setForm((prev) => ({...prev, default_timezone: event.target.value}))}
        >
          <option value="UTC">UTC</option>
          <option value="Asia/Seoul">Asia/Seoul</option>
          <option value="America/New_York">America/New_York</option>
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>로그 보관 일수</span>
        <input
          type="number"
          min={1}
          value={form.data_retention_days}
          onChange={(event) => setForm((prev) => ({...prev, data_retention_days: Number(event.target.value)}))}
        />
      </label>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={form.maintenance_mode}
          onChange={(event) => setForm((prev) => ({...prev, maintenance_mode: event.target.checked}))}
        />
        <span>시스템 점검 모드 활성화</span>
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>알림 이메일</span>
        <input
          type="email"
          value={form.alert_email ?? ''}
          onChange={(event) => setForm((prev) => ({...prev, alert_email: event.target.value}))}
          placeholder="security@example.com"
        />
      </label>
      <div className="flex justify-end">
        <button type="submit" className="rounded-md bg-slate-900 px-4 py-2 text-white" disabled={pending}>
          {pending ? '저장 중...' : '변경 사항 저장'}
        </button>
      </div>
    </form>
  );
}

export default function SystemSettingsPage() {
  const {settings, isLoading, error, save, refresh} = useSystemSettings();

  return (
    <RequireAuth>
      <div className="space-y-6">
        <PageHeader
          title="시스템 설정"
          description="글로벌 설정이 백엔드 시스템 설정 API와 연동되었습니다."
          actions={
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={refresh}>
              새로고침
            </button>
          }
        />
        {error ? <div className="card text-sm text-rose-600">시스템 설정을 불러오지 못했습니다.</div> : null}
        {isLoading ? <div className="card">시스템 설정을 불러오는 중입니다...</div> : null}
        {settings ? (
          <Section title="환경 설정" description="변경 사항은 저장 후 바로 반영됩니다.">
            <SystemSettingsForm settings={settings} onSave={save} />
          </Section>
        ) : null}
      </div>
    </RequireAuth>
  );
}
