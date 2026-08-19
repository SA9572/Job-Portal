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
} from 'lucide-react';
import {
  Job,
  JobListResponse,
  JobStats,
  FilterOptions,
  User,
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

export function App() {
  const [activeTab, setActiveTab] = useState<
    'jobs' | 'match' | 'saved' | 'alerts' | 'admin'
  >('jobs');

  // Auth state
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  // Explore Jobs state
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [useFTS, setUseFTS] = useState(true);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [selectedSeniority, setSelectedSeniority] = useState<string[]>([]);
  const [selectedEmpType, setSelectedEmpType] = useState<string[]>([]);
  const [minSalary, setMinSalary] = useState(0);

  // Selected Job for Modal & Saved IDs
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [savedJobIds, setSavedJobIds] = useState<number[]>([]);

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

    // Load filter options & stats
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

  // Fetch Jobs Effect
  useEffect(() => {
    if (activeTab !== 'jobs') return;

    setLoading(true);
    const offset = (page - 1) * limit;

    if (useFTS && searchQuery.trim().length > 0) {
      jobsApi
        .ftsSearchJobs(searchQuery, {
          limit,
          offset,
          category: selectedCategories.length ? selectedCategories : undefined,
          location: selectedLocations.length ? selectedLocations : undefined,
        })
        .then((res) => {
          setJobs(res.jobs);
          setTotalJobs(res.total);
        })
        .catch(() => fetchStandardJobs(offset))
        .finally(() => setLoading(false));
    } else {
      fetchStandardJobs(offset);
    }
  }, [
    activeTab,
    page,
    searchQuery,
    useFTS,
    selectedCategories,
    selectedLocations,
    selectedSeniority,
    selectedEmpType,
    minSalary,
  ]);

  const fetchStandardJobs = (offset: number) => {
    jobsApi
      .getJobs({
        limit,
        offset,
        search: searchQuery || undefined,
        category: selectedCategories.length ? selectedCategories : undefined,
        location: selectedLocations.length ? selectedLocations : undefined,
        seniority: selectedSeniority.length ? selectedSeniority : undefined,
        employment_type: selectedEmpType.length ? selectedEmpType : undefined,
        minimum_salary: minSalary > 0 ? minSalary : undefined,
      })
      .then((res) => {
        setJobs(res.jobs);
        setTotalJobs(res.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleToggleSave = async (jobId: number) => {
    if (!currentUser) {
      setAuthModalOpen(true);
      return;
    }

    try {
      if (savedJobIds.includes(jobId)) {
        await savedJobsApi.unsaveJob(jobId);
        setSavedJobIds(savedJobIds.filter((id) => id !== jobId));
      } else {
        await savedJobsApi.saveJob(jobId);
        setSavedJobIds([...savedJobIds, jobId]);
      }
    } catch (err) {
      console.error('Failed to toggle save:', err);
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategories([]);
    setSelectedLocations([]);
    setSelectedSeniority([]);
    setSelectedEmpType([]);
    setMinSalary(0);
    setPage(1);
  };

  const totalPages = Math.ceil(totalJobs / limit) || 1;

  return (
    <div className="min-h-screen flex flex-col">
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
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* TAB 1: EXPLORE JOBS */}
        {activeTab === 'jobs' && (
          <div className="space-y-8">
            {/* Hero Stats & Feature Banner */}
            <div className="glass-panel p-8 relative overflow-hidden bg-gradient-to-r from-cyan-950/40 via-slate-900/80 to-indigo-950/40">
              <div className="max-w-3xl space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold">
                  <Sparkles className="w-3.5 h-3.5" /> High-Precision Career Discovery
                </div>
                <h2 className="text-3xl font-extrabold text-white">
                  Discover Top Software & Engineering Opportunities
                </h2>
                <p className="text-sm text-slate-300">
                  Real-time Himalayas scraper integration with SQLite FTS5 BM25 search engine,
                  soft-delete tracking, and multi-factor recommendation algorithm.
                </p>
              </div>

              {/* Stats Bar */}
              {stats && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10 text-xs">
                  <div>
                    <span className="text-slate-400 block">Total Database Records</span>
                    <span className="text-lg font-bold text-white">{stats.total}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Active Verified Jobs</span>
                    <span className="text-lg font-bold text-emerald-400">{stats.active}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">FTS5 Indexed Terms</span>
                    <span className="text-lg font-bold text-cyan-400">100% Synced</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Recommendation Engine</span>
                    <span className="text-lg font-bold text-amber-400">Weighted Multi-Factor</span>
                  </div>
                </div>
              )}
            </div>

            {/* Layout: Sidebar & Job Cards Grid */}
            <div className="flex flex-col lg:flex-row gap-8">
              <FilterSidebar
                searchQuery={searchQuery}
                setSearchQuery={(q) => {
                  setSearchQuery(q);
                  setPage(1);
                }}
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

              <div className="flex-1 space-y-6">
                {/* Results Header */}
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                    {totalJobs} Jobs Found
                  </h3>
                  {useFTS && searchQuery && (
                    <span className="text-xs text-amber-400 font-semibold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" /> FTS5 Relevance Ranked
                    </span>
                  )}
                </div>

                {/* Job Cards Grid */}
                {loading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[1, 2, 3, 4].map((n) => (
                      <div
                        key={n}
                        className="glass-panel h-64 animate-pulse p-6 space-y-4"
                      />
                    ))}
                  </div>
                ) : jobs.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {jobs.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        isSaved={savedJobIds.includes(job.id)}
                        onToggleSave={handleToggleSave}
                        onSelectJob={(j) => setSelectedJob(j)}
                        onViewSimilar={(j) => setSelectedJob(j)}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="glass-panel p-16 text-center text-slate-400 space-y-3">
                    <Search className="w-12 h-12 text-slate-600 mx-auto" />
                    <h3 className="text-lg font-bold text-white">No Jobs Found</h3>
                    <p className="text-xs max-w-sm mx-auto">
                      Try clearing filters or disabling SQLite FTS search.
                    </p>
                    <button
                      onClick={handleResetFilters}
                      className="gradient-btn text-xs mt-2"
                    >
                      Reset All Filters
                    </button>
                  </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-4 pt-6">
                    <button
                      disabled={page === 1}
                      onClick={() => setPage(page - 1)}
                      className="btn-secondary px-3 py-2 text-xs flex items-center gap-1 disabled:opacity-40"
                    >
                      <ChevronLeft className="w-4 h-4" /> Previous
                    </button>
                    <span className="text-xs font-semibold text-slate-400">
                      Page <strong className="text-white">{page}</strong> of{' '}
                      <strong className="text-white">{totalPages}</strong>
                    </span>
                    <button
                      disabled={page === totalPages}
                      onClick={() => setPage(page + 1)}
                      className="btn-secondary px-3 py-2 text-xs flex items-center gap-1 disabled:opacity-40"
                    >
                      Next <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
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
          />
        )}

        {/* TAB 3: SAVED JOBS */}
        {activeTab === 'saved' && (
          <SavedJobsView
            onSelectJob={(j) => setSelectedJob(j)}
            onRefreshSavedIds={refreshSavedJobIds}
          />
        )}

        {/* TAB 4: JOB ALERTS */}
        {activeTab === 'alerts' && (
          <JobAlertsView onSelectJob={(j) => setSelectedJob(j)} />
        )}

        {/* TAB 5: ADMIN DASHBOARD */}
        {activeTab === 'admin' && (
          <AdminDashboardView onSelectJob={(j) => setSelectedJob(j)} />
        )}
      </main>

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
    </div>
  );
}

export default App;
