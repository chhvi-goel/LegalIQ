import '@/styles/globals.css';
import React from 'react';

export const metadata = {
  title: 'LegalIQ — AI Legal Intelligence Platform',
  description: 'Production AI Legal Intelligence Platform with Dual UX (Citizen & Lawyer), Multi-Agent Architecture, MCP Integration & Real-time Streaming.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
        {children}
      </body>
    </html>
  );
}
