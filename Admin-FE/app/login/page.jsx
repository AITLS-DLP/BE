'use client';

import {useState} from 'react';
import {useRouter} from 'next/navigation';
import PageHeader from '@/components/PageHeader';
import {useAuth} from '@/contexts/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const {login, isAuthenticated} = useAuth();
  const [form, setForm] = useState({username: '', password: ''});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(form);
      router.push('/dashboard');
    } catch (err) {
      const message = err?.body?.detail ?? err?.message ?? '로그인에 실패했습니다.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md space-y-6">
      <PageHeader title="로그인" description="관리자 계정으로 로그인하여 대시보드를 이용하세요." />
      {isAuthenticated ? (
        <div className="card space-y-2">
          <p className="text-sm">이미 로그인된 상태입니다.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="space-y-2">
            <label className="flex flex-col gap-1 text-sm">
              <span>이메일 또는 사용자명</span>
              <input
                type="text"
                required
                value={form.username}
                onChange={(event) => setForm((prev) => ({...prev, username: event.target.value}))}
                placeholder="admin@example.com"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span>비밀번호</span>
              <input
                type="password"
                required
                value={form.password}
                onChange={(event) => setForm((prev) => ({...prev, password: event.target.value}))}
                placeholder="••••••••"
              />
            </label>
          </div>
          {error ? <p className="text-sm text-rose-600">{error}</p> : null}
          <button
            type="submit"
            className="w-full rounded-md bg-slate-900 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>
      )}
    </div>
  );
}
