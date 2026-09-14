import React, { useState } from 'react';
import { X, Lock, Mail, User, ShieldCheck, Scale, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { loginUser, registerUser } from '@/lib/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (userData: any) => void;
  initialMode?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialMode = 'login',
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'citizen' | 'lawyer'>('lawyer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'login') {
        const res = await loginUser(email, password);
        onSuccess(res.user);
        onClose();
      } else {
        const res = await registerUser(email, password, fullName, role);
        onSuccess(res.user);
        onClose();
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await loginUser('demo@legaliq.ai', 'demo1234');
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      setError('Demo login failed. Make sure backend is active.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl overflow-hidden">
        {/* Top Decorative Flare */}
        <div className="absolute -top-24 -right-24 h-48 w-48 bg-gradient-to-br from-indigo-500/20 to-sky-500/20 rounded-full blur-2xl pointer-events-none" />

        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-5">
          <div className="flex items-center space-x-2.5">
            <div className="h-9 w-9 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-100">
                {mode === 'login' ? 'Sign In to LegalIQ' : 'Create LegalIQ Account'}
              </h3>
              <p className="text-[11px] text-slate-400">Access AI legal assistant & research workspace</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {error && (
          <div className="flex items-center space-x-2 p-3 mb-4 bg-rose-950/60 border border-rose-800/80 rounded-xl text-rose-300 text-xs">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {mode === 'register' && (
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Full Name:</label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Adv. Rajesh Sharma"
                  className="w-full pl-9 pr-3 py-2 text-xs bg-slate-800/80 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <User className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
              </div>
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address:</label>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="advocate@firm.com"
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-800/80 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <Mail className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Password:</label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-800/80 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <Lock className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
            </div>
          </div>

          {mode === 'register' && (
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Primary Role:</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole('citizen')}
                  className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all ${
                    role === 'citizen'
                      ? 'bg-sky-600 border-sky-500 text-white shadow-md'
                      : 'bg-slate-800 border-slate-700 text-slate-400'
                  }`}
                >
                  Citizen User
                </button>
                <button
                  type="button"
                  onClick={() => setRole('lawyer')}
                  className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all ${
                    role === 'lawyer'
                      ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-800 border-slate-700 text-slate-400'
                  }`}
                >
                  Legal Practitioner
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-indigo-600 via-indigo-500 to-sky-600 hover:from-indigo-700 text-white font-extrabold rounded-xl text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-1.5 disabled:opacity-50 mt-2"
          >
            <span>{loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </form>

        <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
          <button
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="text-indigo-400 hover:text-indigo-300 font-semibold"
          >
            {mode === 'login' ? "Don't have an account? Sign Up" : "Already registered? Sign In"}
          </button>

          <button
            onClick={handleDemoLogin}
            className="text-slate-400 hover:text-slate-200 font-mono text-[11px] underline"
          >
            Instant Demo Login
          </button>
        </div>
      </div>
    </div>
  );
};
