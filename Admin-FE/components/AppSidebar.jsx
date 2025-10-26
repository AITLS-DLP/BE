'use client';

import Link from 'next/link';
import {useAuth} from '@/contexts/AuthContext';

const NAV_LINKS = [
  {href: '/dashboard', label: '대시보드'},
  {href: '/logs', label: '전체 로그'},
  {href: '/detection-settings', label: '탐지 설정'},
  {href: '/projects', label: '프로젝트 관리'},
  {href: '/system-settings', label: '시스템 설정'}
];

export default function AppSidebar() {
  const {isAuthenticated, user, logout} = useAuth();

  return (
    <nav className="flex min-w-56 flex-col gap-3 bg-slate-900 p-4 text-white">
      <div className="space-y-1">
        <span className="text-lg font-semibold">PII Admin</span>
        {isAuthenticated && user ? (
          <p className="text-xs text-slate-300">{user.email ?? user.username}</p>
        ) : null}
      </div>
      {NAV_LINKS.map(({href, label}) => (
        <Link key={href} href={href} className="rounded-md px-3 py-2 text-sm font-medium hover:bg-slate-700">
          {label}
        </Link>
      ))}
      <div className="mt-auto space-y-2">
        {isAuthenticated ? (
          <button
            className="w-full rounded-md bg-slate-700 px-3 py-2 text-left text-sm font-medium hover:bg-slate-600"
            onClick={logout}
          >
            로그아웃
          </button>
        ) : (
          <Link href="/login" className="block rounded-md bg-slate-700 px-3 py-2 text-sm font-medium hover:bg-slate-600">
            로그인
          </Link>
        )}
      </div>
    </nav>
  );
}
