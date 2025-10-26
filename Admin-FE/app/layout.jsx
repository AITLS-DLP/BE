import './globals.css';
import {AuthProvider} from '@/contexts/AuthContext';
import AppSidebar from '@/components/AppSidebar';

export const metadata = {
  title: 'PII Admin Console',
  description: 'PII 탐지 관리자 대시보드'
};

export default function RootLayout({children}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-slate-100 text-slate-900">
        <AuthProvider>
          <div className="flex min-h-screen">
            <AppSidebar />
            <main className="flex-1 p-6 space-y-6">{children}</main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
