import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ClientProviders } from '@/components/ClientProviders';

const inter = Inter({ subsets: ['latin'], display: 'swap' });

export const metadata: Metadata = {
  title: 'AgriSmart AI — Smart Kisan Intelligence & Precision Farming',
  description:
    'AI-powered agricultural portal for Indian farmers: voice assistant in Gujarati/Hindi/English, crop disease detection with live camera, smart irrigation advisory, and weather risk forecast.',
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="gu" suppressHydrationWarning className="dark">
      <body
        className={`${inter.className} min-h-screen bg-slate-950 text-slate-100 antialiased`}
        suppressHydrationWarning
      >
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}
