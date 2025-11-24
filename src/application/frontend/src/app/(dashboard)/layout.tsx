import { AuthRequired } from '@/components/features/auth/auth-required';
import { DashboardHeader } from '@/components/layout/dashboard-header';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <AuthRequired>
      <section className="flex flex-col min-h-screen">
        <DashboardHeader />
        {children}
      </section>
    </AuthRequired>
  );
}
