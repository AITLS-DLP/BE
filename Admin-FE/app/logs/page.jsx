'use client';

import {useEffect, useMemo, useState} from 'react';
import PageHeader from '@/components/PageHeader';
import Section from '@/components/Section';
import SimpleTable from '@/components/SimpleTable';
import RequireAuth from '@/components/RequireAuth';
import {useLogs} from '@/hooks/useLogs';

const DEFAULT_FILTERS = {
  page: 1,
  size: 20,
  sort_by: 'timestamp',
  sort_order: 'desc',
  statsDays: 7,
  recentLimit: 10,
  entity_types: []
};

function FilterForm({onSubmit, filters}) {
  const [form, setForm] = useState({...filters, entity_types_text: filters.entity_types?.join(', ') ?? ''});

  useEffect(() => {
    setForm({...filters, entity_types_text: filters.entity_types?.join(', ') ?? ''});
  }, [filters]);

  function handleChange(name, value) {
    setForm((prev) => ({...prev, [name]: value}));
  }

  return (
    <form
      className="card grid gap-4 md:grid-cols-4"
      onSubmit={(event) => {
        event.preventDefault();
        const entityTypes = form.entity_types_text
          ? form.entity_types_text.split(',').map((value) => value.trim()).filter(Boolean)
          : undefined;
        const nextFilters = {...form, entity_types: entityTypes};
        delete nextFilters.entity_types_text;
        onSubmit(nextFilters);
      }}
    >
      <label className="flex flex-col gap-1 text-sm">
        <span>시작 시간</span>
        <input
          type="datetime-local"
          value={form.start_time ?? ''}
          onChange={(event) => handleChange('start_time', event.target.value)}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>종료 시간</span>
        <input
          type="datetime-local"
          value={form.end_time ?? ''}
          onChange={(event) => handleChange('end_time', event.target.value)}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>클라이언트 IP</span>
        <input type="text" value={form.client_ip ?? ''} onChange={(event) => handleChange('client_ip', event.target.value)} />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>라벨(쉼표로 구분)</span>
        <input
          type="text"
          value={form.entity_types_text ?? ''}
          onChange={(event) => handleChange('entity_types_text', event.target.value)}
          placeholder="PERSON,PHONE"
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>PII 탐지 여부</span>
        <select
          value={form.has_pii ?? ''}
          onChange={(event) => {
            const {value} = event.target;
            handleChange('has_pii', value === '' ? undefined : value === 'true');
          }}
        >
          <option value="">전체</option>
          <option value="true">탐지됨</option>
          <option value="false">탐지 안 됨</option>
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>페이지 크기</span>
        <input
          type="number"
          min={5}
          max={100}
          value={form.size ?? 20}
          onChange={(event) => handleChange('size', Number(event.target.value))}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>정렬</span>
        <select value={form.sort_order} onChange={(event) => handleChange('sort_order', event.target.value)}>
          <option value="desc">최신순</option>
          <option value="asc">오래된순</option>
        </select>
      </label>
      <div className="flex items-end">
        <button type="submit" className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm text-white">
          검색
        </button>
      </div>
    </form>
  );
}

function LogTables({logs, stats, recent}) {
  const columns = useMemo(
    () => [
      {key: 'timestamp', header: '시간', render: (row) => new Date(row.timestamp).toLocaleString()},
      {key: 'client_ip', header: 'IP'},
      {
        key: 'detected_entities',
        header: '탐지 라벨',
        render: (row) => row.detected_entities?.map((entity) => entity.entity_type).join(', ') ?? '-'
      },
      {
        key: 'metadata',
        header: '차단 여부',
        render: (row) => row.metadata?.action ?? '-'
      },
      {key: 'level', header: '레벨'}
    ],
    []
  );
  return (
    <div className="space-y-6">
      <Section title="탐지 로그" description="필터에 맞는 탐지 이벤트">
        <SimpleTable columns={columns} data={logs} emptyMessage="해당 조건의 탐지 로그가 없습니다." />
      </Section>
      <Section title="최근 탐지" description="최근 24시간 내 탐지된 이벤트">
        <SimpleTable columns={columns} data={recent} emptyMessage="최근 탐지 데이터가 없습니다." />
      </Section>
      {stats ? (
        <Section title="요약 통계" description="검색 조건 기반 통계">
          <SimpleTable
            columns={[
              {key: 'metric', header: '항목'},
              {key: 'value', header: '값'}
            ]}
            data={[
              {metric: '총 로그', value: stats.total_logs},
              {metric: 'PII 탐지 건수', value: stats.pii_detected_count},
              {metric: 'PII 탐지율', value: `${stats.pii_detection_rate.toFixed(1)}%`},
              {metric: '평균 처리 시간 (ms)', value: stats.avg_processing_time}
            ]}
          />
        </Section>
      ) : null}
    </div>
  );
}

export default function LogsPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const {logs, stats, recent, isLoading, error, refresh} = useLogs(filters);

  return (
    <RequireAuth>
      <div className="space-y-6">
        <PageHeader
          title="전체 로그"
          description="필터와 정렬 기준이 백엔드 검색 API와 연동되어 실데이터를 보여줍니다."
          actions={
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={refresh}>
              새로고침
            </button>
          }
        />
        <FilterForm onSubmit={setFilters} filters={filters} />
        {error ? <div className="card text-sm text-rose-600">로그 데이터를 불러오지 못했습니다.</div> : null}
        {isLoading ? <div className="card">로그를 불러오는 중입니다...</div> : null}
        <LogTables logs={logs} stats={stats} recent={recent} />
      </div>
    </RequireAuth>
  );
}
