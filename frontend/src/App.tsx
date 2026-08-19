import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  Search,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Bookmark,
  Building2,
  MapPin,
  Clock,
  ArrowUpRight,
  BellRing,
  LockKeyhole,
  BrainCircuit,
  Zap,
  LineChart,
  CheckCircle2,
  UserRound,
  Crown,
  ShieldCheck,
  FolderCheck,
  ExternalLink,
  Users,
  Filter,
  SlidersHorizontal,
  X,
  RotateCcw,
  DollarSign,
} from 'lucide-react';
import {
  Job,
  JobListResponse,
  JobStats,
  FilterOptions,
  User,
  UserProfileMatch,
} from './types/api';
import { jobsApi, authApi, savedJobsApi } from './services/api';

// Components
import { Header } from './components/Header';
import { JobCard } from './components/JobCard';
import { JobDetailModal } from './components/JobDetailModal';
import { FilterSidebar } from './components/FilterSidebar';
import { AuthModal } from './components/AuthModal';
import { MatchEngineView } from './components/MatchEngineView';
import { SavedJobsView } from './components/SavedJobsView';
import { JobAlertsView } from './components/JobAlertsView';
import { AdminDashboardView } from './components/AdminDashboardView';
import { ProfileView } from './components/ProfileView';
import { UpgradeModal } from './components/UpgradeModal';

export function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [activeTab, setActiveTab] = useState<
    'jobs' | 'match' | 'saved' | 'alerts' | 'admin' | 'profile'
  >('jobs');

  // Auth & Upgrade Modals
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [isUpgradeOpen, setIsUpgradeOpen] = useState(false);

  // Match profile passed from ProfileView
  const [matchProfile, setMatchProfile] = useState<UserProfileMatch | null>(null);

  // Explore Jobs state
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [useFTS, setUseFTS] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [selectedSeniority, setSelectedSeniority] = useState<string[]>([]);
  const [selectedEmpType, setSelectedEmpType] = useState<string[]>([]);
  const [minSalary, setMinSalary] = useState(0);

  // Selected Job for Modal & Saved IDs
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [savedJobIds, setSavedJobIds] = useState<number[]>([]);

  // Apply theme class to document body
  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark-theme' : 'light-theme';
  }, [theme]);

  // Check auth user on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authApi
        .getMe()
        .then((user) => {
          setCurrentUser(user);
          refreshSavedJobIds();
        })
        .catch(() => {
          localStorage.removeItem('access_token');
          setCurrentUser(null);
        });
    }

    jobsApi.getFilterOptions().then(setFilterOptions).catch(console.error);
    jobsApi.getJobStats().then(setStats).catch(console.error);
  }, []);

  const refreshSavedJobIds = async () => {
    try {
      const res = await savedJobsApi.getSavedJobs(100);
      setSavedJobIds(res.jobs.map((j) => j.job_id));
    } catch (err) {
      setSavedJobIds([]);
    }
  };

  const fetchStandardJobs = async (offsetVal: number) => {
    setLoading(true);
    try {
      let res: JobListResponse;
      if (useFTS && searchQuery.trim()) {
        res = await jobsApi.ftsSearchJobs(searchQuery.trim(), {
          limit,
          offset: offsetVal,
          category: selectedCategories.length ? selectedCategories : undefined,
          location: selectedLocations.length ? selectedLocations : undefined,
        });
      } else {
        res = await jobsApi.getJobs({
          limit,
          offset: offsetVal,
          search: searchQuery || undefined,
          category: selectedCategories.length ? selectedCategories : undefined,
          location: selectedLocations.length ? selectedLocations : undefined,
          seniority: selectedSeniority.length ? selectedSeniority : undefined,
          employment_type: selectedEmpType.length ? selectedEmpType : undefined,
          minimum_salary: minSalary || undefined,
        });
      }
      setJobs(res.jobs);
      setTotalJobs(res.total);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const offsetVal = (page - 1) * limit;
    fetchStandardJobs(offsetVal);
  }, [
    page,
    searchQuery,
    useFTS,
    selectedCategories,
    selectedLocations,
    selectedSeniority,
    selectedEmpType,
    minSalary,
  ]);

  const handleToggleSave = async (jobId: number) => {
    try {
      if (savedJobIds.includes(jobId)) {
        await savedJobsApi.unsaveJob(jobId);
        setSavedJobIds(savedJobIds.filter((id) => id !== jobId));
      } else {
        await savedJobsApi.saveJob(jobId);
        setSavedJobIds([...savedJobIds, jobId]);
      }
    } catch (err) {
      console.error('Save toggle error:', err);
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setUseFTS(false);
    setSelectedCategories([]);
    setSelectedLocations([]);
    setSelectedSeniority([]);
    setSelectedEmpType([]);
    setMinSalary(0);
    setPage(1);
  };

  const toggleEmpType = (type: string) => {
    if (selectedEmpType.includes(type)) {
      setSelectedEmpType(selectedEmpType.filter((t) => t !== type));
    } else {
      setSelectedEmpType([...selectedEmpType, type]);
    }
  };

  const toggleLocation = (loc: string) => {
    if (selectedLocations.includes(loc)) {
      setSelectedLocations(selectedLocations.filter((l) => l !== loc));
    } else {
      setSelectedLocations([...selectedLocations, loc]);
    }
  };

  const activeFilterCount =
    selectedEmpType.length +
    selectedLocations.length +
    selectedCategories.length +
    selectedSeniority.length +
    (minSalary > 0 ? 1 : 0) +
    (searchQuery ? 1 : 0);

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-300 ${isDark ? 'dark-theme' : 'light-theme'}`}>
      <div className="flex-1 md:ml-64 flex flex-col min-w-0">
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          currentUser={currentUser}
          onOpenAuth={() => setAuthModalOpen(true)}
          onLogout={() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setCurrentUser(null);
            setSavedJobIds([]);
            setActiveTab('jobs');
          }}
          onOpenUpgrade={() => setIsUpgradeOpen(true)}
          theme={theme}
          onToggleTheme={() => setTheme(isDark ? 'light' : 'dark')}
        />

        <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
          {/* TAB 1: EXPLORE JOBS */}
          {activeTab === 'jobs' && (
            <div className="space-y-6">
              {/* Top Grid: Hero Card + Right Column Cards */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Columns: Light Cream Hero Card */}
                <div className="lg:col-span-2 rounded-3xl border border-[#ebdcb4] bg-[#fbf8ee] p-6 md:p-8 text-[#0a2618] shadow-lg relative overflow-hidden flex flex-col justify-between">
                  <div>
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#f2e8c9] border border-[#ebd6a2] text-[#1b4d32] text-[11px] font-extrabold mb-4">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-700" /> AI POWERED
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                      <div>
                        <h2 className="text-3xl md:text-4xl font-extrabold text-[#0a2618] tracking-tight leading-tight mb-3">
                          Find Your Dream Career, <br />
                          <span className="text-[#2e7d52]">Smarter &amp; Faster</span>
                        </h2>
                        <p className="text-xs text-[#284937] leading-relaxed mb-6 font-medium">
                          Real-time job discovery powered by AI matching, precision filters, and intelligent recommendations.
                        </p>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left">
                          <div className="flex items-center gap-2">
                            <FolderCheck className="w-5 h-5 text-emerald-700 shrink-0" />
                            <div>
                              <span className="text-base font-extrabold text-[#0a2618] block leading-none">{stats?.total ?? 226}</span>
                              <span className="text-[10px] font-bold text-[#446654] uppercase tracking-wider">Total Jobs</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
                            <div>
                              <span className="text-base font-extrabold text-[#0a2618] block leading-none">{stats?.active ?? 225}</span>
                              <span className="text-[10px] font-bold text-[#446654] uppercase tracking-wider">Verified Jobs</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Zap className="w-5 h-5 text-emerald-700 shrink-0" />
                            <div>
                              <span className="text-base font-extrabold text-[#0a2618] block leading-none">100%</span>
                              <span className="text-[10px] font-bold text-[#446654] uppercase tracking-wider">Synced</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-emerald-700 shrink-0" />
                            <div>
                              <span className="text-base font-extrabold text-[#0a2618] block leading-none">Smart</span>
                              <span className="text-[10px] font-bold text-[#446654] uppercase tracking-wider">AI Engine</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Integrated Inset AI Match Card */}
                      <div className="rounded-2xl border border-[#e2dec9] bg-white p-5 text-[#0b2319] shadow-md space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-emerald-700" />
                            <h3 className="text-xs font-bold uppercase tracking-wider text-[#0a2618]">AI Match Score</h3>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          <div className="relative flex h-20 w-20 shrink-0 items-center justify-center rounded-full border-4 border-emerald-600 bg-emerald-50 text-center shadow-inner">
                            <div>
                              <span className="text-xl font-extrabold text-[#0a2618] block leading-none">85%</span>
                              <span className="text-[9px] font-bold text-emerald-800">Great Match</span>
                            </div>
                          </div>

                          <div className="flex-1 space-y-1.5 text-[11px]">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-600 font-semibold">Skills Match</span>
                              <span className="font-extrabold text-[#0a2618]">92%</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-slate-600 font-semibold">Title Overlap</span>
                              <span className="font-extrabold text-[#0a2618]">88%</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-slate-600 font-semibold">Location Match</span>
                              <span className="font-extrabold text-[#0a2618]">90%</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-slate-600 font-semibold">Salary Match</span>
                              <span className="font-extrabold text-[#0a2618]">70%</span>
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => setActiveTab('match')}
                          className="w-full btn-green-gradient py-2.5 text-xs flex items-center justify-center gap-1.5"
                        >
                          &rarr; Improve Your Match
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Column Cards */}
                <div className="space-y-6">
                  <div className="rounded-2xl border border-[#e4e8de] bg-white p-5 text-[#0b2319] shadow-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-extrabold text-[#0a2618]">Job Market Overview</h3>
                      <button className="text-[11px] font-bold text-slate-600 border border-slate-200 rounded-lg px-2.5 py-1 bg-slate-50">
                        This Month &or;
                      </button>
                    </div>

                    <div className="h-20 w-full rounded-xl bg-gradient-to-b from-emerald-50 to-white p-2 relative overflow-hidden flex items-end">
                      <svg className="w-full h-full text-emerald-500" viewBox="0 0 300 80" preserveAspectRatio="none">
                        <path
                          fill="rgba(46, 125, 82, 0.15)"
                          stroke="#2e7d52"
                          strokeWidth="3"
                          d="M0,60 Q50,20 100,45 T200,15 T300,30 L300,80 L0,80 Z"
                        />
                      </svg>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 text-center">
                      <div>
                        <span className="text-base font-extrabold text-[#0a2618] block leading-none">1,248</span>
                        <span className="text-[9px] font-bold text-slate-500 block mt-1 uppercase">Jobs Added</span>
                        <span className="text-[9px] font-extrabold text-emerald-600">&uarr; 18%</span>
                      </div>

                      <div>
                        <span className="text-base font-extrabold text-[#0a2618] block leading-none">8,456</span>
                        <span className="text-[9px] font-bold text-slate-500 block mt-1 uppercase">Applications</span>
                        <span className="text-[9px] font-extrabold text-emerald-600">&uarr; 24%</span>
                      </div>

                      <div>
                        <span className="text-base font-extrabold text-[#0a2618] block leading-none">320</span>
                        <span className="text-[9px] font-bold text-slate-500 block mt-1 uppercase">Companies</span>
                        <span className="text-[9px] font-extrabold text-emerald-600">&uarr; 12%</span>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-[#e4e8de] bg-white p-5 text-[#0b2319] shadow-sm space-y-3">
                    <h3 className="text-sm font-extrabold text-[#0a2618]">Quick Actions</h3>
                    <div className="space-y-2">
                      {([
                        { title: 'Create Job Alert', copy: 'Get notified about new matches', action: () => setActiveTab('alerts') },
                        { title: 'Update Profile', copy: 'Improve your match accuracy', action: () => setActiveTab('profile') },
                        { title: 'View Saved Jobs', copy: 'Access your bookmarked jobs', action: () => setActiveTab('saved') },
                        { title: 'Refer & Earn', copy: 'Invite friends & earn rewards', action: () => setIsUpgradeOpen(true) },
                      ]).map(({ title, copy, action }) => (
                        <button
                          key={title}
                          onClick={action}
                          className="w-full flex items-center justify-between p-2.5 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-emerald-50/50 hover:border-emerald-200 transition-all text-left group"
                        >
                          <div>
                            <p className="text-xs font-bold text-[#0a2618] group-hover:text-[#2e7d52]">{title}</p>
                            <p className="text-[10px] text-slate-500">{copy}</p>
                          </div>
                          <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-[#2e7d52]" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* INTERACTIVE PRECISION FILTER BAR (EMPLOYMENT TYPE, LOCATION, SALARY) */}
              <div className="rounded-2xl border border-[#e4e8de] bg-white p-5 shadow-sm space-y-4 text-[#0b2319]">
                <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <SlidersHorizontal className="w-4 h-4 text-[#2e7d52]" />
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#0a2618]">
                      Precision Job Filters
                    </h3>
                  </div>

                  <div className="flex items-center gap-3">
                    {activeFilterCount > 0 && (
                      <button
                        onClick={handleResetFilters}
                        className="text-xs font-bold text-slate-500 hover:text-red-600 flex items-center gap-1 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> Clear All ({activeFilterCount})
                      </button>
                    )}
                    <button
                      onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                      className={`text-xs font-bold px-3.5 py-1.5 rounded-xl border transition-all flex items-center gap-1.5 ${
                        showAdvancedFilters
                          ? 'bg-[#2e7d52] text-white border-[#2e7d52]'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      <Filter className="w-3.5 h-3.5" /> All Filters
                    </button>
                  </div>
                </div>

                {/* Filter Controls Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 text-xs">
                  {/* Filter 1: Employment Type */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                      <Briefcase className="w-3 h-3 text-[#2e7d52]" /> Job Type / Commitment
                    </label>
                    <div className="flex flex-wrap gap-1">
                      {['Full Time', 'Contractor', 'Internship', 'Part Time'].map((type) => {
                        const active = selectedEmpType.includes(type);
                        return (
                          <button
                            key={type}
                            onClick={() => toggleEmpType(type)}
                            className={`px-2.5 py-1 rounded-lg border font-bold transition-all text-[11px] ${
                              active
                                ? 'bg-[#e3edd9] border-[#c4dbb4] text-[#1e5a39]'
                                : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                            }`}
                          >
                            {type}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Filter 2: Location / Region */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-[#2e7d52]" /> Preferred Location
                    </label>
                    <div className="flex flex-wrap gap-1">
                      {['United States', 'Remote', 'Netherlands', 'United Kingdom'].map((loc) => {
                        const active = selectedLocations.includes(loc);
                        return (
                          <button
                            key={loc}
                            onClick={() => toggleLocation(loc)}
                            className={`px-2.5 py-1 rounded-lg border font-bold transition-all text-[11px] ${
                              active
                                ? 'bg-[#e3edd9] border-[#c4dbb4] text-[#1e5a39]'
                                : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                            }`}
                          >
                            {loc}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Filter 3: Minimum Salary Target */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-extrabold text-slate-500 uppercase">
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3 text-emerald-600" /> Min Salary
                      </span>
                      <span className="text-[#2e7d52] font-extrabold">
                        {minSalary > 0 ? `$${(minSalary / 1000).toFixed(0)}k/yr` : 'Any'}
                      </span>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={200000}
                      step={10000}
                      value={minSalary}
                      onChange={(e) => setMinSalary(Number(e.target.value))}
                      className="w-full accent-[#2e7d52] cursor-pointer"
                    />
                    <div className="flex justify-between text-[9px] text-slate-400 font-bold">
                      <span onClick={() => setMinSalary(0)} className="cursor-pointer hover:text-emerald-700">$0</span>
                      <span onClick={() => setMinSalary(50000)} className="cursor-pointer hover:text-emerald-700">$50k</span>
                      <span onClick={() => setMinSalary(100000)} className="cursor-pointer hover:text-emerald-700">$100k</span>
                      <span onClick={() => setMinSalary(150000)} className="cursor-pointer hover:text-emerald-700">$150k+</span>
                    </div>
                  </div>

                  {/* Filter 4: Keyword Search & FTS Engine */}
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                      <Search className="w-3 h-3 text-[#2e7d52]" /> Keyword Filter
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="e.g. Python, Marketing..."
                        className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-[#0a2618] placeholder-slate-400 focus:outline-none focus:border-[#2e7d52]"
                      />
                    </div>
                  </div>
                </div>

                {/* Advanced Filter Drawer */}
                {showAdvancedFilters && (
                  <div className="pt-4 border-t border-slate-100">
                    <FilterSidebar
                      searchQuery={searchQuery}
                      setSearchQuery={setSearchQuery}
                      useFTS={useFTS}
                      setUseFTS={setUseFTS}
                      selectedCategories={selectedCategories}
                      setSelectedCategories={setSelectedCategories}
                      selectedLocations={selectedLocations}
                      setSelectedLocations={setSelectedLocations}
                      selectedSeniority={selectedSeniority}
                      setSelectedSeniority={setSelectedSeniority}
                      selectedEmpType={selectedEmpType}
                      setSelectedEmpType={setSelectedEmpType}
                      minSalary={minSalary}
                      setMinSalary={setMinSalary}
                      filterOptions={filterOptions}
                      onReset={handleResetFilters}
                    />
                  </div>
                )}

                {/* Active Badges */}
                {activeFilterCount > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
                    <span className="text-[10px] font-extrabold text-slate-400 uppercase mr-1">Active:</span>
                    {selectedEmpType.map((t) => (
                      <span key={t} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#e3edd9] text-[#1e5a39] text-[10px] font-extrabold">
                        {t} <X className="w-3 h-3 cursor-pointer" onClick={() => toggleEmpType(t)} />
                      </span>
                    ))}
                    {selectedLocations.map((l) => (
                      <span key={l} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#e3edd9] text-[#1e5a39] text-[10px] font-extrabold">
                        {l} <X className="w-3 h-3 cursor-pointer" onClick={() => toggleLocation(l)} />
                      </span>
                    ))}
                    {minSalary > 0 && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#e3edd9] text-[#1e5a39] text-[10px] font-extrabold">
                        ${(minSalary / 1000).toFixed(0)}k+ <X className="w-3 h-3 cursor-pointer" onClick={() => setMinSalary(0)} />
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Middle Section: Latest Job Opportunities Grid */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-extrabold text-white dark:text-white light:text-slate-900 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-emerald-400" />
                    {activeFilterCount > 0 ? `Filtered Positions (${jobs.length})` : 'Latest Job Opportunities'}
                  </h3>
                  <button
                    onClick={handleResetFilters}
                    className={`btn-light-secondary text-xs px-4 py-2 flex items-center gap-1.5 ${
                      isDark ? 'btn-dark-secondary' : 'btn-light-secondary'
                    }`}
                  >
                    View All Jobs
                  </button>
                </div>

                {/* 2x2 White Job Cards Grid */}
                {loading ? (
                  <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500 font-semibold animate-pulse">
                    Loading jobs matching your filter criteria...
                  </div>
                ) : jobs.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {jobs.map((job, idx) => {
                      const avatarLetters = ['E', 'F', 'N', 'M'];
                      const avatarLetter = avatarLetters[idx % avatarLetters.length];
                      const isSaved = savedJobIds.includes(job.id);

                      return (
                        <div
                          key={job.id}
                          className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4 text-[#0b2319]"
                        >
                          <div>
                            <div className="flex items-start justify-between gap-4 mb-3">
                              <div className="flex items-center gap-3">
                                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#276e46] text-white font-extrabold text-base shadow">
                                  {avatarLetter}
                                </div>
                                <div>
                                  <h4
                                    onClick={() => setSelectedJob(job)}
                                    className="text-base font-extrabold text-[#0a2618] hover:text-[#2e7d52] cursor-pointer transition-colors line-clamp-1"
                                  >
                                    {job.title}
                                  </h4>
                                  <p className="text-xs font-semibold text-slate-500">{job.company}</p>
                                </div>
                              </div>

                              <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-slate-400">19/08/2026</span>
                                <button
                                  onClick={() => handleToggleSave(job.id)}
                                  className="text-slate-400 hover:text-emerald-600 transition-colors p-1"
                                >
                                  <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-emerald-600 text-emerald-600' : ''}`} />
                                </button>
                              </div>
                            </div>

                            <p className="text-xs text-slate-600 leading-relaxed line-clamp-2 mb-4">
                              {job.excerpt || job.description}
                            </p>

                            <div className="flex flex-wrap gap-2 mb-2">
                              {job.location_restrictions?.[0] && (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#e8f2ec] text-[#225738] text-[11px] font-bold">
                                  <MapPin className="w-3 h-3" /> {job.location_restrictions[0]}
                                </span>
                              )}
                              {job.employment_type && (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#f4f1e4] text-[#5e532b] text-[11px] font-bold">
                                  <Briefcase className="w-3 h-3" /> {job.employment_type}
                                </span>
                              )}
                              {job.minimum_salary && (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#eef7f0] text-[#1b5e39] text-[11px] font-extrabold">
                                  ${(job.minimum_salary / 1000).toFixed(0)}k/yr
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                            <button
                              onClick={() => setSelectedJob(job)}
                              className="text-xs font-extrabold text-[#2e7d52] hover:underline flex items-center gap-1"
                            >
                              &lowast; Similar Jobs
                            </button>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => setSelectedJob(job)}
                                className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors"
                              >
                                Details
                              </button>
                              <a
                                href={job.application_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-green-gradient px-4 py-2 text-xs flex items-center gap-1"
                              >
                                Apply Now &rarr;
                              </a>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500 space-y-3">
                    <Filter className="w-10 h-10 text-slate-300 mx-auto" />
                    <h4 className="text-base font-extrabold text-[#0a2618]">No Jobs Match These Filters</h4>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto font-medium">
                      Try clearing some filter options or selecting a broader location or salary threshold.
                    </p>
                    <button
                      onClick={handleResetFilters}
                      className="btn-green-gradient px-5 py-2.5 text-xs inline-flex items-center gap-1.5 mt-2"
                    >
                      <RotateCcw className="w-3.5 h-3.5" /> Reset Filters
                    </button>
                  </div>
                )}
              </div>

              {/* Bottom Feature Strip */}
              <div className="rounded-2xl border border-[#163826] bg-[#0d1e16] p-5 text-white grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <h5 className="text-xs font-extrabold text-white">Real-time Sync</h5>
                    <p className="text-[10px] text-slate-400">Live job updates from top portals</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Search className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <h5 className="text-xs font-extrabold text-white">FTS Search</h5>
                    <p className="text-[10px] text-slate-400">Lightning fast full-text search</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <BrainCircuit className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <h5 className="text-xs font-extrabold text-white">AI Matching</h5>
                    <p className="text-[10px] text-slate-400">Smart multi-factor recommendations</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <h5 className="text-xs font-extrabold text-white">Secure &amp; Private</h5>
                    <p className="text-[10px] text-slate-400">Your data is safe and encrypted</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: JOB MATCHER */}
          {activeTab === 'match' && (
            <MatchEngineView
              onSelectJob={(j) => setSelectedJob(j)}
              savedJobIds={savedJobIds}
              onToggleSave={handleToggleSave}
              initialProfile={matchProfile}
              onOpenUpgrade={() => setIsUpgradeOpen(true)}
            />
          )}

          {/* TAB 3: SAVED JOBS */}
          {activeTab === 'saved' && (
            <SavedJobsView
              onSelectJob={(j) => setSelectedJob(j)}
              onRefreshSavedIds={refreshSavedJobIds}
              onOpenUpgrade={() => setIsUpgradeOpen(true)}
            />
          )}

          {/* TAB 4: JOB ALERTS */}
          {activeTab === 'alerts' && (
            <JobAlertsView
              onSelectJob={(j) => setSelectedJob(j)}
              onOpenUpgrade={() => setIsUpgradeOpen(true)}
            />
          )}

          {/* TAB 5: PROFILE */}
          {activeTab === 'profile' && (
            <ProfileView
              currentUser={currentUser}
              onOpenUpgrade={() => setIsUpgradeOpen(true)}
              onNavigateToMatch={(prof) => {
                setMatchProfile(prof);
                setActiveTab('match');
              }}
            />
          )}

          {/* TAB 6: ADMIN DASHBOARD */}
          {activeTab === 'admin' && (
            <AdminDashboardView onSelectJob={(j) => setSelectedJob(j)} />
          )}
        </main>
      </div>

      {/* Global Modals */}
      <JobDetailModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        isSaved={selectedJob ? savedJobIds.includes(selectedJob.id) : false}
        onToggleSave={handleToggleSave}
        onSelectSimilarJob={(sim) => setSelectedJob(sim)}
        isAdmin={currentUser?.role === 'admin'}
        onDeleteJob={async (id) => {
          await jobsApi.softDeleteJob(id);
          setSelectedJob(null);
          fetchStandardJobs(0);
        }}
        onRestoreJob={async (id) => {
          await jobsApi.restoreJob(id);
          setSelectedJob(null);
          fetchStandardJobs(0);
        }}
      />

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={(u) => {
          setCurrentUser(u);
          refreshSavedJobIds();
        }}
      />

      <UpgradeModal
        isOpen={isUpgradeOpen}
        onClose={() => setIsUpgradeOpen(false)}
        onSuccess={(planId) => {
          console.log('Upgraded plan:', planId);
        }}
      />
    </div>
  );
}

export default App;
