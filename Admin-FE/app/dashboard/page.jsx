'use client';

import {useMemo, useState} from 'react';
import PageHeader from '@/components/PageHeader';
import Section from '@/components/Section';
import DataCard from '@/components/DataCard';
import SimpleTable from '@/components/SimpleTable';
import RequireAuth from '@/components/RequireAuth';
import {useDashboardSummary} from '@/hooks/useDashboardSummary';

function Overview({summary}) {
  const overview = summary?.overview;
  if (!overview) return null;
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <DataCard title="전체 로그" value={overview.total_logs.toLocaleString()} description="선택한 기간 동안 수집된 로그" tone="info" />
      <DataCard
        title="PII 탐지 건수"
        value={overview.pii_detected_count.toLocaleString()}
        description="탐지된 개인정보 이벤트"
        tone="success"
      />
      <DataCard
        title="PII 탐지율"
        value={`${overview.pii_detection_rate.toFixed(1)}%`}
        description="탐지/전체 비율"
        tone="default"
      />
    </div>
  );
}

function RealTimeStats({summary}) {
  const stats = summary?.real_time;
  if (!stats) return null;
  const rows = Object.entries(stats.hourly_counts ?? {}).map(([hour, count]) => ({hour, count}));
  return (
    <Section
      title="실시간 탐지 현황"
      description={`최근 24시간 탐지 추이 (${stats.timezone} 기준)`}
    >
      <div className="flex flex-wrap gap-4">
        <span className="badge">최근 1시간 {stats.total_last_hour}건</span>
        <span className="text-xs text-slate-500">마지막 갱신: {new Date(stats.last_updated).toLocaleString()}</span>
      </div>
      <SimpleTable
        columns={[
          {key: 'hour', header: '시간'},
          {key: 'count', header: '탐지 건수'}
        ]}
        data={rows}
        emptyMessage="탐지 데이터가 없습니다."
      />
    </Section>
  );
}

function TopIps({summary}) {
  const columns = useMemo(
    () => [
      {key: 'ip', header: 'IP'},
      {key: 'count', header: '탐지 건수'}
    ],
    []
  );
  return (
    <Section title="IP별 통계" description="탐지 및 차단 상위 IP">
      <SimpleTable columns={columns} data={summary?.top_ips ?? []} emptyMessage="집계된 IP 데이터가 없습니다." />
    </Section>
  );
}

function LabelBreakdown({summary}) {
  const labelStats = Object.entries(summary?.label_stats ?? {}).map(([label, count]) => ({label, count}));
  const actionStats = Object.entries(summary?.label_action_breakdown ?? {}).map(([label, actions]) => ({label, actions}));
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Section title="라벨 통계" description="탐지된 라벨별 건수">
        <SimpleTable
          columns={[
            {key: 'label', header: '라벨'},
            {key: 'count', header: '건수'}
          ]}
          data={labelStats}
          emptyMessage="라벨 데이터가 없습니다."
        />
      </Section>
      <Section title="라벨별 차단 여부" description="ALLOW/BLOCK 분포">
        <SimpleTable
          columns={[
            {key: 'label', header: '라벨'},
            {
              key: 'actions',
              header: '결과',
              render: (row) => (
                <div className="flex gap-2 text-sm">
                  {Object.entries(row.actions).map(([action, value]) => (
                    <span key={action} className="badge">
                      {action}: {value}
                    </span>
                  ))}
                </div>
              )
            }
          ]}
          data={actionStats}
          emptyMessage="차단 통계가 없습니다."
        />
      </Section>
    </div>
  );
}

function ProjectAndServiceStats({summary}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Section title="프로젝트 통계" description="프로젝트별 탐지 건수">
        <SimpleTable
          columns={[
            {key: 'project', header: '프로젝트'},
            {key: 'count', header: '탐지 건수'}
          ]}
          data={summary?.project_stats ?? []}
          emptyMessage="프로젝트 집계가 없습니다."
        />
      </Section>
      <Section title="AI 서비스별 탐지 현황" description="서비스 태그별 탐지 건수">
        <SimpleTable
          columns={[
            {key: 'service', header: '서비스'},
            {key: 'count', header: '탐지 건수'}
          ]}
          data={Object.entries(summary?.ai_service_stats ?? {}).map(([service, count]) => ({service, count}))}
          emptyMessage="AI 서비스 통계가 없습니다."
        />
      </Section>
    </div>
  );
}

function RecentDetections({summary}) {
  const detections = summary?.detections ?? [];
  return (
    <Section title="탐지된 내역" description="최근 탐지 이벤트">
      <SimpleTable
        columns={[
          {key: 'id', header: 'ID'},
          {key: 'timestamp', header: '발생 시간', render: (row) => new Date(row.timestamp).toLocaleString()},
          {key: 'client_ip', header: 'IP'},
          {
            key: 'detected_entities',
            header: '라벨',
            render: (row) => row.detected_entities?.map((entity) => entity.entity_type).join(', ') ?? '-'
          },
          {
            key: 'metadata',
            header: '프로젝트',
            render: (row) => row.metadata?.project ?? '-'
          }
        ]}
        data={detections}
        emptyMessage="최근 탐지된 내역이 없습니다."
      />
    </Section>
  );
}

export default function DashboardPage() {
  const [timezone, setTimezone] = useState('UTC');
  const {summary, isLoading, error, refresh} = useDashboardSummary({tz: timezone});

  return (
    <RequireAuth>
      <div className="space-y-6">
        <PageHeader
          title="개인정보 탐지 현황"
          description="대시보드 위젯이 백엔드 요약 API와 연결되어 실시간 데이터를 표시합니다."
          actions={
            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-600">
                타임존
                <select
                  value={timezone}
                  onChange={(event) => setTimezone(event.target.value)}
                  className="ml-2 border border-slate-300 rounded-md px-2 py-1"
                >
                  <option value="UTC">UTC</option>
                  <option value="Asia/Seoul">Asia/Seoul</option>
                  <option value="America/Los_Angeles">America/Los_Angeles</option>
                </select>
              </label>
              <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={refresh}>
                새로고침
              </button>
            </div>
          }
        />

        {error ? <div className="card text-sm text-rose-600">대시보드를 불러오지 못했습니다.</div> : null}
        {isLoading ? <div className="card">대시보드 데이터를 불러오는 중입니다...</div> : null}
        {summary ? (
          <div className="space-y-6">
            <Overview summary={summary} />
            <RealTimeStats summary={summary} />
            <Section
              title="분기별 탐지 통계"
              description={`${summary.range_days}일 범위 내 분기별 통계입니다.`}
            >
              <SimpleTable
                columns={[
                  {key: 'label', header: '분기'},
                  {key: 'total_count', header: '전체'},
                  {key: 'pii_detected_count', header: 'PII 탐지'}
                ]}
                data={summary.quarterly_stats}
                emptyMessage="분기별 통계가 없습니다."
              />
            </Section>
            <TopIps summary={summary} />
            <LabelBreakdown summary={summary} />
            <Section title="로그 여부" description="로그 상태별 통계">
              <SimpleTable
                columns={[
                  {key: 'status', header: '상태'},
                  {key: 'count', header: '건수'}
                ]}
                data={Object.entries(summary.log_status_stats ?? {}).map(([status, count]) => ({status, count}))}
                emptyMessage="로그 상태 통계가 없습니다."
              />
            </Section>
            <ProjectAndServiceStats summary={summary} />
            <RecentDetections summary={summary} />
          </div>
        ) : null}
      </div>
    </RequireAuth>
  );
}
