import React from 'react';
import { UserCheck, ShieldCheck, Scale, Cpu, Sun, Moon, Sparkles, BookOpen, LogIn, LogOut, User } from 'lucide-react';

interface HeaderProps {
  roleMode: 'citizen' | 'lawyer';
  setRoleMode: (mode: 'citizen' | 'lawyer') => void;
  isDarkMode: boolean;
  setIsDarkMode: (val: boolean) => void;
  onOpenMCP: () => void;
  user: any;
  onOpenAuth: (mode?: 'login' | 'register') => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  roleMode,
  setRoleMode,
  isDarkMode,
  setIsDarkMode,
  onOpenMCP,
  user,
  onOpenAuth,
  onLogout,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b px-4 lg:px-8 py-3 flex items-center justify-between transition-colors">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-sky-500 via-indigo-600 to-blue-700 flex items-center justify-center shadow-lg shadow-sky-500/20 text-white font-bold">
          <Scale className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-sky-600 via-indigo-600 to-purple-600 dark:from-sky-400 dark:via-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              LegalIQ
            </span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
              v1.0 Multi-Agent RAG
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
            AI-Powered Production Legal Intelligence Platform
          </p>
        </div>
      </div>

      {/* Role Mode Switcher (Citizen vs Lawyer) */}
      <div className="flex items-center bg-slate-200/70 dark:bg-slate-800/70 p-1 rounded-xl border border-slate-300/50 dark:border-slate-700/50">
        <button
          onClick={() => setRoleMode('citizen')}
          className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            roleMode === 'citizen'
              ? 'bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-md'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>Citizen Mode</span>
        </button>
        <button
          onClick={() => setRoleMode('lawyer')}
          className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            roleMode === 'lawyer'
              ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-md'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          <BookOpen className="h-3.5 w-3.5" />
          <span>Lawyer Workspace</span>
        </button>
      </div>

      {/* Actions: User Auth, Theme Toggle & MCP Status */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenMCP}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-medium hover:bg-emerald-500/20 transition-all"
          title="Open Model Context Protocol (MCP) Server Hub"
        >
          <Cpu className="h-3.5 w-3.5" />
          <span className="hidden md:inline">MCP Layer</span>
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
        </button>

        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          aria-label="Toggle Dark Mode"
        >
          {isDarkMode ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-slate-600" />}
        </button>

        {/* User Auth Controls */}
        {user ? (
          <div className="flex items-center space-x-2 bg-slate-100 dark:bg-slate-800/80 p-1 pl-2.5 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="flex items-center space-x-1.5 text-xs">
              <div className="h-6 w-6 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px]">
                {user.full_name?.charAt(0) || 'U'}
              </div>
              <span className="font-bold text-slate-800 dark:text-slate-200 max-w-[100px] truncate hidden sm:inline">
                {user.full_name || user.email}
              </span>
            </div>

            <button
              onClick={onLogout}
              className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 transition-colors text-xs font-bold flex items-center space-x-1"
              title="Log Out"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden md:inline">Log Out</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => onOpenAuth('login')}
              className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-all flex items-center space-x-1"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span>Log In</span>
            </button>
            <button
              onClick={() => onOpenAuth('register')}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-extrabold shadow-md shadow-indigo-600/30 transition-all"
            >
              Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
