import React from 'react';
import {
  Briefcase,
  Sparkles,
  Bookmark,
  Bell,
  UserRound,
  ShieldCheck,
  Search,
  Sun,
  Moon,
  Crown,
  Lightbulb,
  ArrowRight,
  Menu,
  X,
} from 'lucide-react';
import { User } from '../types/api';

interface HeaderProps {
  activeTab: 'jobs' | 'match' | 'saved' | 'alerts' | 'admin' | 'profile';
  setActiveTab: (tab: 'jobs' | 'match' | 'saved' | 'alerts' | 'admin' | 'profile') => void;
  currentUser: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
  onOpenUpgrade?: () => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onOpenAuth,
  onLogout,
  onOpenUpgrade,
  theme,
  onToggleTheme,
}) => {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const navigate = (tab: HeaderProps['activeTab']) => {
    setActiveTab(tab);
    setMobileOpen(false);
  };

  const isDark = theme === 'dark';

  return (
    <>
      {/* LEFT FIXED SIDEBAR */}
      <aside
        className={`sidebar-container hidden md:flex fixed left-0 top-0 bottom-0 z-50 w-64 flex-col border-r px-4 py-5 overflow-y-auto ${
          isDark ? 'bg-[#091611] border-[#152e22] text-slate-100' : 'bg-[#f8f6ed] border-[#e6e2d3] text-slate-800'
        }`}
      >
        {/* Brand Logo */}
        <div
          onClick={() => navigate('jobs')}
          className="flex items-center gap-3 px-2 cursor-pointer mb-6"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600/20 text-emerald-400 border border-emerald-500/30">
            <Sparkles className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="font-extrabold text-xs tracking-tight uppercase leading-tight text-white dark:text-white light:text-slate-900">
              INTELLIGENT
            </h1>
            <p className="text-[10px] font-bold text-emerald-400 tracking-wider uppercase">
              CAREER ENGINE
            </p>
          </div>
        </div>

        {/* Section 1: DISCOVER */}
        <div className="mb-5">
          <p className="px-3 mb-2 text-[9px] font-extrabold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-400">
            DISCOVER
          </p>
          <div className="space-y-1">
            {([
              { tab: 'jobs', label: 'Explore Jobs', Icon: Briefcase },
              { tab: 'match', label: 'Job Matcher', Icon: Sparkles },
              { tab: 'saved', label: 'Saved Jobs', Icon: Bookmark },
              { tab: 'alerts', label: 'Job Alerts', Icon: Bell },
            ] as const).map(({ tab, label, Icon }) => {
              const active = activeTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => navigate(tab)}
                  className={`w-full flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-bold transition-all ${
                    active
                      ? isDark
                        ? 'bg-[#1b3d2b] text-emerald-300 border-l-4 border-emerald-400 shadow-sm'
                        : 'bg-[#e3edd9] text-[#225738] border-l-4 border-[#2e7d52] shadow-sm'
                      : isDark
                      ? 'text-slate-400 hover:bg-white/5 hover:text-white'
                      : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? (isDark ? 'text-emerald-300' : 'text-[#225738]') : ''}`} />
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Section 2: MY DASHBOARD */}
        <div className="mb-5">
          <p className="px-3 mb-2 text-[9px] font-extrabold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-400">
            MY DASHBOARD
          </p>
          <div className="space-y-1">
            <button
              onClick={() => navigate('profile')}
              className={`w-full flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-bold transition-all ${
                activeTab === 'profile'
                  ? isDark
                    ? 'bg-[#1b3d2b] text-emerald-300 border-l-4 border-emerald-400'
                    : 'bg-[#e3edd9] text-[#225738] border-l-4 border-[#2e7d52]'
                  : isDark
                  ? 'text-slate-400 hover:bg-white/5 hover:text-white'
                  : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
              }`}
            >
              <UserRound className="w-4 h-4" /> Profile
            </button>

            <button
              onClick={() => navigate('saved')}
              className={`w-full flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-bold transition-all ${
                activeTab === 'saved'
                  ? isDark
                    ? 'bg-[#1b3d2b] text-emerald-300 border-l-4 border-emerald-400'
                    : 'bg-[#e3edd9] text-[#225738] border-l-4 border-[#2e7d52]'
                  : isDark
                  ? 'text-slate-400 hover:bg-white/5 hover:text-white'
                  : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
              }`}
            >
              <Bookmark className="w-4 h-4" /> Applied Jobs
            </button>

            <button
              onClick={() => navigate('alerts')}
              className={`w-full flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-bold transition-all ${
                activeTab === 'alerts'
                  ? isDark
                    ? 'bg-[#1b3d2b] text-emerald-300 border-l-4 border-emerald-400'
                    : 'bg-[#e3edd9] text-[#225738] border-l-4 border-[#2e7d52]'
                  : isDark
                  ? 'text-slate-400 hover:bg-white/5 hover:text-white'
                  : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
              }`}
            >
              <Bell className="w-4 h-4" /> Subscription Alerts
            </button>

            {currentUser?.role === 'admin' && (
              <button
                onClick={() => navigate('admin')}
                className={`w-full flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-bold transition-all ${
                  activeTab === 'admin'
                    ? isDark
                      ? 'bg-[#1b3d2b] text-emerald-300 border-l-4 border-emerald-400'
                      : 'bg-[#e3edd9] text-[#225738] border-l-4 border-[#2e7d52]'
                    : isDark
                    ? 'text-slate-400 hover:bg-white/5 hover:text-white'
                    : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
                }`}
              >
                <ShieldCheck className="w-4 h-4" /> Admin Portal
              </button>
            )}
          </div>
        </div>

        {/* PROMO CARD 1: Upgrade Your Career */}
        <div className={`mt-auto mb-4 rounded-2xl border p-4 shadow-md ${
          isDark ? 'bg-[#0b2417] border-[#18452e]' : 'bg-[#eef5e7] border-[#cce0be]'
        }`}>
          <div className="flex items-center gap-2 mb-1.5">
            <Crown className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-extrabold text-white dark:text-white light:text-slate-900">
              Upgrade Your Career
            </h4>
          </div>
          <p className="text-[10px] leading-relaxed text-slate-300 dark:text-slate-300 light:text-slate-600 mb-3">
            Get AI-powered recommendations &amp; unlimited alerts.
          </p>
          <button
            onClick={onOpenUpgrade || onOpenAuth}
            className="w-full btn-green-gradient py-2 text-[11px] flex items-center justify-center gap-1.5 shadow"
          >
            Upgrade Now <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* PROMO CARD 2: Career Tip of the Day */}
        <div className={`rounded-2xl border p-4 ${
          isDark ? 'bg-[#091b12] border-[#133824]' : 'bg-[#f4f1e4] border-[#e2dcc8]'
        }`}>
          <div className="flex items-center gap-2 mb-1.5">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-bold text-white dark:text-white light:text-slate-900">
              Career Tip of the Day
            </h4>
          </div>
          <p className="text-[10px] leading-relaxed text-slate-300 dark:text-slate-300 light:text-slate-600 mb-3">
            Tailor your resume to match the job description. You're 2x more likely to get noticed!
          </p>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400">2/5</span>
            <button className="text-[10px] font-extrabold text-emerald-400 hover:underline">
              View All Tips
            </button>
          </div>
        </div>
      </aside>

      {/* TOP HEADER BAR */}
      <header className={`sticky top-0 z-40 w-full border-b h-16 px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4 transition-colors duration-300 ${
        isDark ? 'bg-[#091611] border-[#152e22]' : 'bg-[#f8f6ed] border-[#e6e2d3]'
      }`}>
        {/* Mobile menu trigger */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 rounded-xl border text-slate-400 hover:text-white"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        {/* Search input bar */}
        <div className="flex-1 max-w-md relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search jobs, roles or companies..."
            className={`w-full rounded-xl pl-10 pr-16 py-2 text-xs transition-colors focus:outline-none ${
              isDark
                ? 'bg-[#0e241a] border border-[#1a402d] text-white placeholder-slate-400 focus:border-emerald-400'
                : 'bg-[#ffffff] border border-[#e4e8de] text-slate-900 placeholder-slate-400 focus:border-[#2e7d52]'
            }`}
          />
          <span className={`absolute right-3 px-2 py-0.5 rounded text-[10px] font-extrabold uppercase border ${
            isDark ? 'bg-[#123023] border-[#1c4733] text-slate-300' : 'bg-[#f0ece0] border-[#d8d2bf] text-slate-600'
          }`}>
            Ctrl + K
          </span>
        </div>

        {/* Right Tools: Theme Switcher, Notifications, User Chip */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle Button */}
          <button
            onClick={onToggleTheme}
            className={`p-2 rounded-xl border transition-all ${
              isDark
                ? 'bg-[#0e241a] border-[#1a402d] text-amber-300 hover:bg-[#153626]'
                : 'bg-white border-[#e4e8de] text-slate-700 hover:bg-[#f5f2e6]'
            }`}
            title="Toggle Light / Dark Mode"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* Bell Notification */}
          <div className="relative">
            <button className={`p-2 rounded-xl border transition-all ${
              isDark ? 'bg-[#0e241a] border-[#1a402d] text-slate-300' : 'bg-white border-[#e4e8de] text-slate-700'
            }`}>
              <Bell className="w-4 h-4" />
            </button>
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-400 text-[10px] font-extrabold text-slate-950 shadow">
              4
            </span>
          </div>

          {/* User Profile / Auth Action Chip */}
          {currentUser ? (
            <div
              onClick={onLogout}
              className={`flex items-center gap-2.5 rounded-xl border p-1.5 pr-3 cursor-pointer transition-all ${
                isDark ? 'bg-[#0e241a] border-[#1a402d] hover:bg-[#153626]' : 'bg-white border-[#e4e8de] hover:bg-[#f5f2e6]'
              }`}
              title="Click to Sign Out"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#2e7d52] text-xs font-extrabold text-white shadow">
                {currentUser.full_name ? currentUser.full_name.substring(0, 2).toUpperCase() : 'SK'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-extrabold leading-tight text-white dark:text-white light:text-slate-900">
                  {currentUser.full_name}
                </p>
                <p className="text-[9px] font-bold text-emerald-400 leading-tight">
                  Sign Out
                </p>
              </div>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn-green-gradient px-4 py-2 text-xs flex items-center gap-1.5 shadow"
            >
              <UserRound className="w-3.5 h-3.5" /> Sign In
            </button>
          )}
        </div>
      </header>

      {/* MOBILE DRAWER */}
      {mobileOpen && (
        <nav className={`md:hidden border-t px-4 py-3 space-y-1 ${
          isDark ? 'bg-[#091611] border-[#152e22]' : 'bg-[#f8f6ed] border-[#e6e2d3]'
        }`}>
          {([
            { tab: 'jobs', label: 'Explore Jobs', Icon: Briefcase },
            { tab: 'match', label: 'Job Matcher', Icon: Sparkles },
            { tab: 'saved', label: 'Saved Jobs', Icon: Bookmark },
            { tab: 'alerts', label: 'Job Alerts', Icon: Bell },
            { tab: 'profile', label: 'My Profile', Icon: UserRound },
          ] as const).map(({ tab, label, Icon }) => (
            <button
              key={tab}
              onClick={() => navigate(tab)}
              className={`w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold ${
                activeTab === tab ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </nav>
      )}
    </>
  );
};
