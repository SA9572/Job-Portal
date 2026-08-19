import React, { useState } from 'react';
import {
  X,
  Lock,
  Mail,
  User as UserIcon,
  Sparkles,
  Rocket,
  Bell,
  Bookmark,
  BarChart3,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { authApi } from '../services/api';
import { User } from '../types/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: User) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (tab === 'register' && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);

    try {
      if (tab === 'login') {
        const res = await authApi.login({ email, password });
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('refresh_token', res.refresh_token);
        onSuccess(res.user);
        onClose();
      } else {
        const res = await authApi.register({
          email,
          password,
          full_name: fullName || undefined,
        });
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('refresh_token', res.refresh_token);
        onSuccess(res.user);
        onClose();
      }
    } catch (err: any) {
      const msg =
        err.response?.data?.error?.message ||
        err.response?.data?.detail ||
        'Authentication failed. Please check credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-[#07130e] text-white">
      <div className="min-h-screen grid lg:grid-cols-[minmax(380px,0.95fr)_minmax(520px,1.05fr)]">
        {/* LEFT SECTION: BRANDING & FEATURES (DARK FOREST GREEN) */}
        <section className="relative hidden lg:flex flex-col justify-between overflow-hidden border-r border-[#152e22] bg-[#091611] p-10 xl:p-14 text-white">
          <div className="pointer-events-none absolute left-1/2 top-[38%] h-96 w-96 -translate-x-1/2 rounded-full border-[24px] border-emerald-500/10 shadow-[0_0_120px_rgba(46,125,82,0.3)]" />

          {/* Brand Header */}
          <div className="relative flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#1b3d2b] border border-[#2e7d52] text-emerald-400 shadow-md">
              <Sparkles className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-extrabold tracking-tight text-white uppercase">INTELLIGENT</p>
              <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-400">Career Engine</p>
            </div>
          </div>

          {/* Hero Content */}
          <div className="relative max-w-lg space-y-4">
            <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-emerald-400">
              Your Next Chapter Starts Here
            </p>
            <h2 className="text-4xl xl:text-5xl font-extrabold leading-[1.1] tracking-tight text-white">
              Start Your Journey <br />
              to the <span className="text-emerald-400">Perfect Career</span>
            </h2>
            <p className="max-w-md text-xs leading-relaxed text-slate-300 font-medium">
              Create your account and unlock AI-powered job matching, smart alerts, and real-time career opportunities.
            </p>

            {/* Feature Bullet List */}
            <div className="pt-4 space-y-3.5">
              {[
                [Sparkles, 'AI-Powered Matching', 'Get personalized recommendations matching your exact skills.'],
                [Bell, 'Smart Job Alerts', 'Never miss the right opportunity with automated digest notifications.'],
                [Bookmark, 'Save & Track', 'Bookmark positions, track interview notes, and manage your applications.'],
                [BarChart3, 'Career Insights', 'Gain real-time insights into salary benchmarks and hiring trends.'],
              ].map(([Icon, title, copy]) => (
                <div key={title as string} className="flex items-center gap-3.5">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#1a402d] bg-[#0e241a] text-emerald-400 shadow-sm">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold text-white">{title as string}</p>
                    <p className="text-[10px] text-slate-400 font-medium">{copy as string}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Testimonial Quote */}
          <div className="relative max-w-sm rounded-2xl border border-[#1a402d] bg-[#0e241a] p-4 shadow-sm">
            <p className="text-xs leading-relaxed text-slate-300 italic font-medium">
              "Intelligent Career Engine helped me find my target Python Engineer role in just 2 weeks!"
            </p>
            <p className="mt-3 text-[11px] font-extrabold text-emerald-400">
              &starf;&starf;&starf;&starf;&starf; <span className="ml-2 text-slate-300 font-bold">Saurabh K., Software Engineer</span>
            </p>
          </div>
        </section>

        {/* RIGHT SECTION: SIGN IN / REGISTER FORM (CREAM & WHITE THEME) */}
        <section className="relative flex min-h-screen items-center justify-center p-6 sm:p-12 bg-[#fbf8ee] text-[#0b2319]">
          {/* Close Button */}
          <button
            onClick={onClose}
            aria-label="Close authentication"
            className="absolute right-6 top-6 rounded-full border border-slate-200 bg-white p-2 text-slate-500 hover:bg-slate-100 transition-colors shadow-sm"
          >
            <X className="h-5 w-5" />
          </button>

          <div className="w-full max-w-md py-6">
            {/* Header */}
            <div className="mb-6 text-center lg:text-left">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e3edd9] border border-[#d2e2c2] text-[#2e7d52] lg:mx-0 shadow-sm">
                <Rocket className="h-6 w-6 text-[#2e7d52]" />
              </div>
              <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-[#2e7d52]">
                Welcome to Intelligent Career Engine
              </p>
              <h2 className="mt-1.5 text-2xl md:text-3xl font-extrabold text-[#0a2618] tracking-tight">
                {tab === 'login' ? 'Sign In to Your Account' : 'Create Your Candidate Account'}
              </h2>
              <p className="mt-1 text-xs text-slate-600 font-medium">
                {tab === 'login'
                  ? 'Sign in to access your saved jobs and AI candidate matching.'
                  : 'Join thousands of software professionals accelerating their career.'}
              </p>
            </div>

            {/* Tab Toggle Switcher */}
            <div className="mb-6 flex rounded-xl border border-slate-200 bg-[#f0ece0] p-1 shadow-inner">
              <button
                onClick={() => {
                  setTab('login');
                  setError(null);
                }}
                className={`flex-1 py-2 text-xs font-extrabold rounded-lg transition-all ${
                  tab === 'login'
                    ? 'bg-[#2e7d52] text-white shadow-md'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => {
                  setTab('register');
                  setError(null);
                }}
                className={`flex-1 py-2 text-xs font-extrabold rounded-lg transition-all ${
                  tab === 'register'
                    ? 'bg-[#2e7d52] text-white shadow-md'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Register
              </button>
            </div>

            {/* Error Notice */}
            {error && (
              <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-3 text-center text-xs font-bold text-red-700">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4 text-xs font-semibold">
              {tab === 'register' && (
                <div>
                  <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Saurabh Kumar"
                      className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 py-2.5 text-xs text-[#0a2618] placeholder-slate-400 focus:border-[#2e7d52] focus:outline-none shadow-sm"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="developer@example.com"
                    className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 py-2.5 text-xs text-[#0a2618] placeholder-slate-400 focus:border-[#2e7d52] focus:outline-none shadow-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-11 py-2.5 text-xs text-[#0a2618] placeholder-slate-400 focus:border-[#2e7d52] focus:outline-none shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-2.5 text-slate-400 hover:text-slate-700"
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {tab === 'register' && (
                <div>
                  <label className="block text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-1">
                    Confirm Password *
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm password"
                      className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 py-2.5 text-xs text-[#0a2618] placeholder-slate-400 focus:border-[#2e7d52] focus:outline-none shadow-sm"
                    />
                  </div>
                </div>
              )}

              {tab === 'login' && (
                <div className="flex justify-end">
                  <button
                    type="button"
                    className="text-[11px] font-extrabold text-[#2e7d52] hover:underline"
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              {tab === 'register' && (
                <label className="flex items-center gap-2 text-xs text-slate-600 font-medium">
                  <input type="checkbox" required className="accent-[#2e7d52] rounded" />
                  I agree to the <span className="text-[#2e7d52] font-bold">Terms of Service</span> and <span className="text-[#2e7d52] font-bold">Privacy Policy</span>
                </label>
              )}

              <button
                type="submit"
                disabled={loading}
                className="btn-green-gradient w-full py-3 text-xs mt-2 flex items-center justify-center gap-2"
              >
                {loading ? 'Processing...' : tab === 'login' ? 'Sign In to Account' : 'Create Candidate Account'}{' '}
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            <p className="mt-6 text-center text-[10px] leading-relaxed text-slate-500 font-medium">
              By continuing, you agree to our <span className="text-[#2e7d52] font-bold">Terms of Service</span> and acknowledge our <span className="text-[#2e7d52] font-bold">Privacy Policy</span>.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};
