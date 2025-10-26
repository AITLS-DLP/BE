'use client';

import {useState} from 'react';
import PageHeader from '@/components/PageHeader';
import Section from '@/components/Section';
import SimpleTable from '@/components/SimpleTable';
import RequireAuth from '@/components/RequireAuth';
import {useProjects} from '@/hooks/useProjects';

function CreateProjectForm({onCreate}) {
  const [form, setForm] = useState({name: '', description: '', owner: '', status: 'ACTIVE'});
  const [pending, setPending] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setPending(true);
    try {
      await onCreate(form);
      setForm({name: '', description: '', owner: '', status: 'ACTIVE'});
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="card grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
      <label className="flex flex-col gap-1 text-sm">
        <span>프로젝트 이름</span>
        <input value={form.name} onChange={(event) => setForm((prev) => ({...prev, name: event.target.value}))} required />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>담당자</span>
        <input value={form.owner} onChange={(event) => setForm((prev) => ({...prev, owner: event.target.value}))} />
      </label>
      <label className="flex flex-col gap-1 text-sm md:col-span-2">
        <span>설명</span>
        <textarea
          rows={3}
          value={form.description}
          onChange={(event) => setForm((prev) => ({...prev, description: event.target.value}))}
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span>상태</span>
        <select value={form.status} onChange={(event) => setForm((prev) => ({...prev, status: event.target.value}))}>
          <option value="ACTIVE">활성</option>
          <option value="INACTIVE">비활성</option>
          <option value="ARCHIVED">보관</option>
        </select>
      </label>
      <div className="md:col-span-2 flex justify-end">
        <button type="submit" className="rounded-md bg-slate-900 px-4 py-2 text-white" disabled={pending}>
          {pending ? '생성 중...' : '프로젝트 생성'}
        </button>
      </div>
    </form>
  );
}

function ProjectsTable({projects, onUpdate, onDelete}) {
  return (
    <Section title="프로젝트 목록" description="프로젝트 관리 API에서 불러온 실시간 데이터">
      <SimpleTable
        columns={[
          {key: 'id', header: 'ID'},
          {key: 'name', header: '이름'},
          {key: 'owner', header: '담당자'},
          {key: 'status', header: '상태'},
          {key: 'total_detections', header: '탐지 건수'},
          {key: 'blocked_count', header: '차단 건수'},
          {
            key: 'actions',
            header: '관리',
            render: (row) => (
              <div className="flex gap-2">
                <button
                  className="badge"
                  onClick={() =>
                    onUpdate(row.id, {
                      status: row.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
                    })
                  }
                >
                  상태 전환
                </button>
                <button className="badge" onClick={() => onDelete(row.id)}>
                  삭제
                </button>
              </div>
            )
          }
        ]}
        data={projects}
        emptyMessage="등록된 프로젝트가 없습니다."
      />
    </Section>
  );
}

export default function ProjectsPage() {
  const {projects, isLoading, error, createProject, updateProject, deleteProject, refresh} = useProjects();

  return (
    <RequireAuth>
      <div className="space-y-6">
        <PageHeader
          title="프로젝트 관리"
          description="프로젝트 CRUD가 백엔드 프로젝트 API와 연결되었습니다."
          actions={
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white" onClick={refresh}>
              새로고침
            </button>
          }
        />
        <CreateProjectForm onCreate={createProject} />
        {error ? <div className="card text-sm text-rose-600">프로젝트 정보를 불러오지 못했습니다.</div> : null}
        {isLoading ? <div className="card">프로젝트를 불러오는 중입니다...</div> : null}
        <ProjectsTable projects={projects} onUpdate={updateProject} onDelete={deleteProject} />
      </div>
    </RequireAuth>
  );
}
