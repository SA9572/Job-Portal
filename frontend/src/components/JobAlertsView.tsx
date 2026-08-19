import React, { useEffect, useState } from 'react';
import { Bell, Plus, Sparkles, Trash2, CheckCircle2, Clock } from 'lucide-react';
import { JobAlert, Job } from '../types/api';
import { alertsApi } from '../services/api';

interface JobAlertsViewProps {
  onSelectJob: (job: Job) => void;
  onOpenUpgrade?: () => void;
}

export const JobAlertsView: React.FC<JobAlertsViewProps> = ({
  onSelectJob,
  onOpenUpgrade,
}) => {
  const [alerts, setAlerts] = useState<JobAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');
  const [minSalary, setMinSalary] = useState<number | ''>('');
  const [frequency, setFrequency] = useState('daily');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await alertsApi.getAlerts();
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

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await alertsApi.createAlert({
        name,
        keywords: keywords || undefined,
        location: location || undefined,
        min_salary: minSalary ? Number(minSalary) : undefined,
        frequency,
      });

      setName('');
      setKeywords('');
      setLocation('');
      setMinSalary('');
      setShowModal(false);
      fetchAlerts();
    } catch (err) {
      console.error('Failed to create alert:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await alertsApi.deleteAlert(id);
      setAlerts(alerts.filter((a) => a.id !== id));
    } catch (err) {
      console.error('Failed to delete alert:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner (IMAGE 3 REPLICA) */}
      <div className="rounded-3xl border border-[#e4e8de] bg-[#f5f2e6] p-8 shadow-sm relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-[#e3edd9] border border-[#d2e2c2] text-[#2e7d52]">
            <Bell className="w-8 h-8 text-[#2e7d52]" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#e3edd9] border border-[#d2e2c2] text-[#225738] text-[10px] font-extrabold mb-2">
              <Bell className="w-3 h-3 text-[#2e7d52]" /> AUTOMATED ALERTS
            </div>
            <h2 className="text-3xl font-extrabold text-[#0a2618] tracking-tight">Subscription Alerts</h2>
            <p className="text-xs text-slate-600 mt-1 font-medium">
              Automated notifications matching your specific job criteria.
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="btn-green-gradient px-5 py-3 text-xs flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" /> Create Alert
        </button>
      </div>

      {/* Secondary Notice Banner */}
      <div className="rounded-2xl border border-[#dce8d2] bg-[#f2f7ec] p-4 text-xs font-bold text-[#1e5a39] flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-[#2e7d52]" /> Click "Create Alert" above to configure automated job digest alerts.
      </div>

      {/* Main Empty State (IMAGE 3 REPLICA) */}
      {loading ? (
        <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500 font-semibold animate-pulse">
          Loading alerts...
        </div>
      ) : alerts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm flex flex-col justify-between space-y-4 text-[#0b2319]"
            >
              <div>
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h3 className="text-base font-extrabold text-[#0a2618]">{alert.name}</h3>
                  <button
                    onClick={() => handleDelete(alert.id)}
                    className="text-slate-400 hover:text-red-600 transition-colors p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-1 text-xs text-slate-600 font-medium">
                  {alert.keywords && <p>Keywords: <span className="font-bold text-[#0a2618]">{alert.keywords}</span></p>}
                  {alert.location && <p>Location: <span className="font-bold text-[#0a2618]">{alert.location}</span></p>}
                  {alert.min_salary && <p>Min Salary: <span className="font-bold text-[#2e7d52]">${alert.min_salary.toLocaleString()}/yr</span></p>}
                  <p>Frequency: <span className="font-bold text-[#0a2618] capitalize">{alert.frequency}</span></p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-semibold">
                <span>Created: {new Date(alert.created_at).toLocaleDateString()}</span>
                <span className="text-emerald-700 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Active
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-[#e4e8de] bg-white p-16 text-center text-slate-600 space-y-4 shadow-sm flex flex-col items-center justify-center min-h-[320px]">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#f2f7ec] border border-[#dce8d2] text-[#2e7d52]">
            <Bell className="w-8 h-8 text-[#2e7d52]" />
          </div>

          <h3 className="text-xl font-extrabold text-[#0a2618]">No Subscription Alerts</h3>
          <p className="text-xs text-slate-500 max-w-md font-medium leading-relaxed">
            You haven't created any subscription alerts yet. Create an alert to get notified about new jobs that match your preferences.
          </p>
        </div>
      )}

      {/* Create Alert Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl border border-[#e4e8de] bg-white p-6 shadow-2xl text-[#0b2319]">
            <h3 className="text-lg font-extrabold text-[#0a2618] mb-4">Create Subscription Alert</h3>
            <form onSubmit={handleCreateAlert} className="space-y-4 text-xs font-semibold">
              <div>
                <label className="block text-slate-600 mb-1">Alert Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Remote Python Engineer"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-slate-900 focus:outline-none focus:border-[#2e7d52]"
                />
              </div>

              <div>
                <label className="block text-slate-600 mb-1">Keywords</label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g. Python, FastAPI"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-slate-900 focus:outline-none focus:border-[#2e7d52]"
                />
              </div>

              <div>
                <label className="block text-slate-600 mb-1">Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Remote, US"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-slate-900 focus:outline-none focus:border-[#2e7d52]"
                />
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 bg-slate-100 text-slate-700"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-green-gradient px-5 py-2">
                  Create Alert
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
