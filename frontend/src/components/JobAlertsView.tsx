import React, { useEffect, useState } from 'react';
import { Bell, Plus, Trash2, Play, Sparkles, Check, ToggleLeft, ToggleRight } from 'lucide-react';
import { JobAlert, Job } from '../types/api';
import { alertsApi } from '../services/api';
import { JobCard } from './JobCard';

interface JobAlertsViewProps {
  onSelectJob: (job: Job) => void;
}

export const JobAlertsView: React.FC<JobAlertsViewProps> = ({ onSelectJob }) => {
  const [alerts, setAlerts] = useState<JobAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');
  const [category, setCategory] = useState('');
  const [minSalary, setMinSalary] = useState('');
  const [frequency, setFrequency] = useState('daily');

  // Test Match State
  const [testResults, setTestResults] = useState<{ alertId: number; name: string; jobs: Job[] } | null>(null);
  const [testingId, setTestingId] = useState<number | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await alertsApi.getAlerts(50);
      setAlerts(res.alerts);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      const newAlert = await alertsApi.createAlert({
        name,
        keywords: keywords || undefined,
        location: location || undefined,
        category: category || undefined,
        min_salary: minSalary ? Number(minSalary) : undefined,
        frequency,
        is_active: true,
      });
      setAlerts([newAlert, ...alerts]);
      setShowCreate(false);
      setName('');
      setKeywords('');
      setLocation('');
      setCategory('');
      setMinSalary('');
    } catch (err) {
      console.error('Failed to create alert:', err);
    }
  };

  const handleToggleActive = async (alert: JobAlert) => {
    try {
      const updated = await alertsApi.updateAlert(alert.id, {
        is_active: !alert.is_active,
      });
      setAlerts(alerts.map((a) => (a.id === alert.id ? updated : a)));
    } catch (err) {
      console.error('Failed to toggle alert:', err);
    }
  };

  const handleDelete = async (alertId: number) => {
    try {
      await alertsApi.deleteAlert(alertId);
      setAlerts(alerts.filter((a) => a.id !== alertId));
      if (testResults?.alertId === alertId) setTestResults(null);
    } catch (err) {
      console.error('Failed to delete alert:', err);
    }
  };

  const handleTestMatch = async (alertId: number, alertName: string) => {
    setTestingId(alertId);
    try {
      const res = await alertsApi.testMatch(alertId);
      setTestResults({
        alertId,
        name: alertName,
        jobs: res.jobs,
      });
    } catch (err) {
      console.error('Failed to test match:', err);
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Bell className="w-6 h-6 text-emerald-400" />
            Job Subscription Alerts
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated notifications matching your specific job criteria
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="gradient-btn text-xs py-2 px-4 flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" /> Create Alert
        </button>
      </div>

      {/* Create Alert Form Drawer */}
      {showCreate && (
        <form
          onSubmit={handleCreate}
          className="glass-panel p-6 space-y-4 border-emerald-500/30 bg-slate-900/90"
        >
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
            New Job Subscription Alert
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Alert Name *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Remote Senior Python"
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Keywords
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g. python, fastapi"
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Location
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Remote, US"
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Category
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Software Engineering"
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Min Salary ($)
              </label>
              <input
                type="number"
                value={minSalary}
                onChange={(e) => setMinSalary(e.target.value)}
                placeholder="e.g. 90000"
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Frequency
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="daily">Daily Digest</option>
                <option value="weekly">Weekly Summary</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="btn-secondary text-xs"
            >
              Cancel
            </button>
            <button type="submit" className="gradient-btn text-xs py-2 px-5">
              Save Alert Subscription
            </button>
          </div>
        </form>
      )}

      {/* Alert List */}
      {loading ? (
        <div className="glass-panel p-12 text-center text-slate-400 animate-pulse">
          Loading subscription alerts...
        </div>
      ) : alerts.length > 0 ? (
        <div className="space-y-4">
          {alerts.map((a) => (
            <div
              key={a.id}
              className="glass-panel p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-emerald-500/20"
            >
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white">{a.name}</h3>
                  <span
                    className={`badge text-[10px] ${
                      a.is_active ? 'badge-emerald' : 'badge-amber'
                    }`}
                  >
                    {a.is_active ? 'Active' : 'Paused'}
                  </span>
                  <span className="badge badge-purple text-[10px]">
                    {a.frequency}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mt-2">
                  {a.keywords && <span>Keywords: <strong>{a.keywords}</strong></span>}
                  {a.location && <span>Location: <strong>{a.location}</strong></span>}
                  {a.category && <span>Category: <strong>{a.category}</strong></span>}
                  {a.min_salary && <span>Min Salary: <strong>${a.min_salary.toLocaleString()}</strong></span>}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleTestMatch(a.id, a.name)}
                  disabled={testingId === a.id}
                  className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1 text-cyan-400 hover:text-cyan-300"
                >
                  <Play className="w-3.5 h-3.5" />
                  {testingId === a.id ? 'Testing...' : 'Test Match'}
                </button>

                <button
                  onClick={() => handleToggleActive(a)}
                  className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-white/5"
                  title="Toggle Active"
                >
                  {a.is_active ? (
                    <ToggleRight className="w-6 h-6 text-emerald-400" />
                  ) : (
                    <ToggleLeft className="w-6 h-6 text-slate-500" />
                  )}
                </button>

                <button
                  onClick={() => handleDelete(a.id)}
                  className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-500/10"
                  title="Delete Alert"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-2">
          <Bell className="w-12 h-12 text-emerald-400/40 mx-auto" />
          <h3 className="text-base font-bold text-white">No Subscription Alerts</h3>
          <p className="text-xs max-w-sm mx-auto">
            Click "Create Alert" above to configure automated job digest alerts.
          </p>
        </div>
      )}

      {/* Dry Run Test Match Results Drawer */}
      {testResults && (
        <div className="glass-panel p-6 space-y-4 border-cyan-500/40 bg-slate-900/90">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <h3 className="font-bold text-white flex items-center gap-2 text-sm">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Live Test Matches for "{testResults.name}" ({testResults.jobs.length} roles found)
            </h3>
            <button
              onClick={() => setTestResults(null)}
              className="text-xs text-slate-400 hover:text-white"
            >
              Close Results
            </button>
          </div>

          {testResults.jobs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {testResults.jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onSelectJob={onSelectJob}
                />
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-4 text-center">
              No active jobs currently match these alert parameters.
            </p>
          )}
        </div>
      )}
    </div>
  );
};
