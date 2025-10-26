'use client';

import {useEffect, useState} from 'react';
import PageHeader from '@/components/PageHeader';
import Section from '@/components/Section';
import SimpleTable from '@/components/SimpleTable';
import ToggleField from '@/components/ToggleField';
import RequireAuth from '@/components/RequireAuth';
import {useDetectionSettings} from '@/hooks/useDetectionSettings';

function LabelPolicyTable({labels, onToggle}) {
  return (
    <Section title="라벨별 차단 정책" description="탐지된 라벨에 대한 차단 여부를 백엔드 정책과 동기화합니다.">
      <SimpleTable
        columns={[
          {key: 'label', header: '라벨'},
          {
            key: 'block',
            header: '차단 여부',
            render: (row) => (
              <input
                type="checkbox"
                checked={row.block}
                onChange={(event) => onToggle(row.label, event.target.checked)}
              />
            )
          },
          {
            key: 'updated_at',
            header: '업데이트 시각',
            render: (row) => new Date(row.updated_at).toLocaleString()
          },
          {key: 'updated_by', header: '최종 수정자'}
        ]}
        data={labels}
        emptyMessage="아직 등록된 라벨 정책이 없습니다."
      />
    </Section>
  );
}

function DetectionToggleSection({toggles, onUpdate}) {
  const [pending, setPending] = useState(false);
  const [state, setState] = useState(toggles ?? {logging_enabled: false, pseudonymize_enabled: false});

  useEffect(() => {
    setState(toggles ?? {logging_enabled: false, pseudonymize_enabled: false});
  }, [toggles]);

  async function handleSave() {
    setPending(true);
    try {
      await onUpdate(state);
    } finally {
      setPending(false);
    }
  }

  return (
    <Section
      title="탐지 기능 토글"
      description="로그 저장 및 가명화 설정이 시스템 설정과 연동됩니다."
      actions={
        <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={handleSave} disabled={pending}>
          {pending ? '저장 중...' : '변경 사항 저장'}
        </button>
      }
    >
      <div className="space-y-3">
        <ToggleField
          label="로그 저장"
          description="탐지 이벤트를 영구 로그에 기록합니다."
          checked={state.logging_enabled}
          onChange={(value) => setState((prev) => ({...prev, logging_enabled: value}))}
        />
        <ToggleField
          label="가명화 활성화"
          description="민감 정보 저장 시 마스킹을 적용합니다."
          checked={state.pseudonymize_enabled}
          onChange={(value) => setState((prev) => ({...prev, pseudonymize_enabled: value}))}
        />
      </div>
    </Section>
  );
}

export default function DetectionSettingsPage() {
  const {labels, toggles, isLoading, error, saveLabelPolicy, saveToggles, refresh} = useDetectionSettings();

  async function handleLabelToggle(label, block) {
    await saveLabelPolicy(label, {block});
  }

  return (
    <RequireAuth>
      <div className="space-y-6">
        <PageHeader
          title="탐지 기능 설정"
          description="라벨별 차단 정책과 가명화, 로그 저장 옵션이 백엔드 설정 API와 연동되었습니다."
          actions={
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={refresh}>
              새로고침
            </button>
          }
        />
        {error ? <div className="card text-sm text-rose-600">설정 정보를 불러오지 못했습니다.</div> : null}
        {isLoading ? <div className="card">설정 정보를 불러오는 중입니다...</div> : null}
        <DetectionToggleSection toggles={toggles ?? {logging_enabled: false, pseudonymize_enabled: false}} onUpdate={saveToggles} />
        <LabelPolicyTable labels={labels} onToggle={handleLabelToggle} />
      </div>
    </RequireAuth>
  );
}
