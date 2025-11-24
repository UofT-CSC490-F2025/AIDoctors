import './globals.css';
import { UserProvider } from '@/components/auth/user-context';
import type { Metadata, Viewport } from 'next';
import { Manrope } from 'next/font/google';

export const metadata: Metadata = {
  title: 'AI Doctors',
  description:
    'Surface medication interaction risks with ML-powered, patient-specific alerts.',
};

export const viewport: Viewport = {
  maximumScale: 1,
};

const manrope = Manrope({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`bg-white dark:bg-gray-950 text-black dark:text-white ${manrope.className}`}
    >
      <body className="min-h-[100dvh] bg-gray-50">
        {<UserProvider>{children}</UserProvider>}
      </body>
    </html>
  );
}
