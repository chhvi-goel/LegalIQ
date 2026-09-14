'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '@/components/shared/Header';
import { CitizenChat } from '@/components/citizen/CitizenChat';
import { LawyerWorkspace } from '@/components/lawyer/LawyerWorkspace';
import { MCPHubModal } from '@/components/shared/MCPHubModal';
import { AuthModal } from '@/components/shared/AuthModal';
import { fetchCurrentUserProfile, removeStoredToken } from '@/lib/api';

export default function Home() {
  const [roleMode, setRoleMode] = useState<'citizen' | 'lawyer'>('citizen');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isMCPModalOpen, setIsMCPModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [user, setUser] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const profile = await fetchCurrentUserProfile();
      if (profile) {
        setUser(profile);
        if (profile.role === 'lawyer') {
          setRoleMode('lawyer');
        }
      }
    } catch (e) {
      setUser(null);
    }
  };

  const handleLogout = () => {
    removeStoredToken();
    setUser(null);
    setSessionId(null);
  };

  const handleOpenAuth = (mode: 'login' | 'register' = 'login') => {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  };

  return (
    <main className="min-h-screen flex flex-col bg-slate-50 dark:bg-[#090d16] text-slate-900 dark:text-slate-100 transition-colors font-sans">
      <Header
        roleMode={roleMode}
        setRoleMode={setRoleMode}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        onOpenMCP={() => setIsMCPModalOpen(true)}
        user={user}
        onOpenAuth={handleOpenAuth}
        onLogout={handleLogout}
      />

      <div className="flex-1 overflow-hidden">
        {roleMode === 'citizen' ? (
          <CitizenChat sessionId={sessionId} setSessionId={setSessionId} />
        ) : (
          <LawyerWorkspace />
        )}
      </div>

      <MCPHubModal isOpen={isMCPModalOpen} onClose={() => setIsMCPModalOpen(false)} />
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={(uData) => {
          setUser(uData);
          if (uData.role === 'lawyer') setRoleMode('lawyer');
        }}
        initialMode={authMode}
      />
    </main>
  );
}
