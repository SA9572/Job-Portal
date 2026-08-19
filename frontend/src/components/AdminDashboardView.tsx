import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Play,
  RotateCcw,
  Trash2,
  Activity,
  Layers,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
} from 'lucide-react';
import { Job, JobStats, IngestionRunResponse } from '../types/api';
import { adminApi, jobsApi } from '../services/api';
import { JobCard } from './JobCard';

interface AdminDashboardViewProps {
  onSelectJob: (job: Job) => void;
}

export const AdminDashboardView: React.FC<AdminDashboardViewProps> = ({
  onSelectJob,
}) => {
  const [stats, setStats] = useState<JobStats | null>(null);
  const [maxPages, setMaxPages] = useState<number>(5);
  const [pageSize, setPageSize] = useState<number>(20);
  const [running, setRunning] = useState(false);
  const [lastRun, setLastRun] = useState<IngestionRunResponse | null>(null);

  // Soft deleted jobs list
  const [deletedJobs, setDeletedJobs] = useState<Job[]>([]);
  const [loadingDeleted, setLoadingDeleted] = useState(false);
  const [activeTab, setActiveTab] = useState<'control' | 'trash'>('control');

  const fetchStats = async () => {
    try {
      const data = await jobsApi.getJobStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchDeleted = async () => {
    setLoadingDeleted(true);
    try {
      const res = await jobsApi.getJobs({ include_deleted: true, limit: 50 });
      setDeletedJobs(res.jobs.filter((j) => j.is_deleted));
    } catch (err) {
      console.error('Failed to fetch deleted jobs:', err);
    } finally {
      setLoadingDeleted(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchDeleted();
  }, []);

  const handleRunIngestion = async () => {
    setRunning(true);
    setLastRun(null);
    try {
      const res = await adminApi.runIngestion(maxPages, pageSize);
      setLastRun(res);
      fetchStats();
    } catch (err: any) {
      console.error('Ingestion failed:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleRestore = async (jobId: number) => {
    try {
      await jobsApi.restoreJob(jobId);
      setDeletedJobs(deletedJobs.filter((j) => j.id !== jobId));
      fetchStats();
    } catch (err) {
      console.error('Failed to restore job:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 border-rose-500/30 bg-gradient-to-r from-rose-950/40 via-slate-900/80 to-amber-950/40 flex items-center justify-between">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold mb-2">
            <ShieldCheck className="w-3.5 h-3.5" /> Admin Control Portal
          </div>
          <h2 className="text-2xl font-extrabold text-white">
            Ingestion Pipeline & Content Health
          </h2>
        </div>
      </div>

      {/* Telemetry Stats Banner */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-5 border-indigo-500/20">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Total Managed Jobs
            </span>
            <span className="text-2xl font-extrabold text-white">{stats.total}</span>
          </div>

          <div className="glass-panel p-5 border-emerald-500/20">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Active Public Jobs
            </span>
            <span className="text-2xl font-extrabold text-emerald-400">{stats.active}</span>
          </div>

          <div className="glass-panel p-5 border-amber-500/20">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Expired Jobs
            </span>
            <span className="text-2xl font-extrabold text-amber-400">{stats.expired}</span>
          </div>

          <div className="glass-panel p-5 border-rose-500/20">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Soft-Deleted Jobs
            </span>
            <span className="text-2xl font-extrabold text-rose-400">{stats.deleted}</span>
          </div>
        </div>
      )}

      {/* Mode Sub-Tabs */}
      <div className="flex border-b border-white/10 gap-4">
        <button
          onClick={() => setActiveTab('control')}
          className={`pb-3 text-sm font-bold border-b-2 transition-colors ${
            activeTab === 'control'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Ingestion Controller
        </button>

        <button
          onClick={() => {
            setActiveTab('trash');
            fetchDeleted();
          }}
          className={`pb-3 text-sm font-bold border-b-2 transition-colors ${
            activeTab === 'trash'
              ? 'border-rose-500 text-rose-400'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Trash & Soft-Deleted ({deletedJobs.length})
        </button>
      </div>

      {/* Tab 1: Ingestion Controller */}
      {activeTab === 'control' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-panel p-6 space-y-6 border-cyan-500/20">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              Trigger Live Himalayas Scraper
            </h3>

            {/* Max Pages Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <label className="font-bold text-slate-300 uppercase tracking-wider">
                  Max Scraper Pages
                </label>
                <span className="text-cyan-400 font-bold">{maxPages} pages</span>
              </div>
              <input
                type="range"
                min={1}
                max={20}
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            {/* Page Size Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <label className="font-bold text-slate-300 uppercase tracking-wider">
                  Page Size Limit
                </label>
                <span className="text-cyan-400 font-bold">{pageSize} jobs/page</span>
              </div>
              <input
                type="range"
                min={5}
                max={100}
                step={5}
                value={pageSize}
                onChange={(e) => setPageSize(Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <button
              onClick={handleRunIngestion}
              disabled={running}
              className="gradient-btn w-full py-3.5 text-sm flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4 fill-white" />
              {running ? 'Running Scraper Run...' : 'Execute Ingestion Job'}
            </button>
          </div>

          {/* Execution Log */}
          <div className="glass-panel p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-emerald-400" />
              Latest Run Execution Report
            </h3>

            {lastRun ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold">
                  {lastRun.message}
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-slate-500 block">Pages Attempted</span>
                    <span className="text-base font-bold text-white">
                      {lastRun.pages_attempted}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-slate-500 block">Jobs Fetched</span>
                    <span className="text-base font-bold text-white">
                      {lastRun.jobs_fetched}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-slate-500 block">New Jobs Added</span>
                    <span className="text-base font-bold text-emerald-400">
                      +{lastRun.jobs_new}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-slate-500 block">Duplicates Filtered</span>
                    <span className="text-base font-bold text-amber-400">
                      {lastRun.jobs_duplicate}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-slate-500 text-xs py-8 text-center">
                No ingestion runs performed in current session. Configure bounds on left and execute.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Soft Deleted Trash */}
      {activeTab === 'trash' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
            Soft-Deleted Records (Recoverable)
          </h3>

          {loadingDeleted ? (
            <div className="glass-panel p-12 text-center text-slate-400 animate-pulse">
              Loading soft-deleted jobs...
            </div>
          ) : deletedJobs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {deletedJobs.map((job) => (
                <div
                  key={job.id}
                  className="glass-panel p-5 space-y-3 border-rose-500/30 bg-rose-950/10"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-xs text-rose-400 font-semibold">
                        DELETED RECORD
                      </span>
                      <h4 className="text-base font-bold text-white">{job.title}</h4>
                      <p className="text-xs text-slate-400">{job.company}</p>
                    </div>

                    <button
                      onClick={() => handleRestore(job.id)}
                      className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10"
                    >
                      <RotateCcw className="w-3.5 h-3.5" /> Restore
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-slate-400">
              Trash is empty. No soft-deleted jobs found.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
