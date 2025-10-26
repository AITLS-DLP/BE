'use client';

import Link from 'next/link';
import {useAuth} from '@/contexts/AuthContext';

export default function RequireAuth({children}) {
  const {isAuthenticated, loading} = useAuth();

  if (loading) {
    return <div className="card">인증 정보를 확인하는 중입니다...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="card space-y-3">
        <h2 className="text-xl font-semibold">로그인이 필요합니다</h2>
        <p className="text-sm text-slate-600">해당 페이지를 사용하려면 관리자 계정으로 로그인하세요.</p>
        <Link href="/login" className="badge">로그인 페이지로 이동</Link>
      </div>
    );
  }

  return children;
}
