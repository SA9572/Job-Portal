import React, { useEffect, useState } from 'react';
import {
  Bookmark,
  Edit3,
  Trash2,
  ExternalLink,
  FileText,
  Check,
  Search,
  Building2,
  Crown,
  Shield,
  Sparkles,
} from 'lucide-react';
import { SavedJob, Job } from '../types/api';
import { savedJobsApi } from '../services/api';

interface SavedJobsViewProps {
  onSelectJob: (job: Job) => void;
  onRefreshSavedIds: () => void;
  onOpenUpgrade?: () => void;
}

export const SavedJobsView: React.FC<SavedJobsViewProps> = ({
  onSelectJob,
  onRefreshSavedIds,
  onOpenUpgrade,
}) => {
  const [savedItems, setSavedItems] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [noteText, setNoteText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const res = await savedJobsApi.getSavedJobs(50);
      setSavedItems(res.jobs);
    } catch (err) {
      console.error('Failed to load saved jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (jobId: number) => {
    try {
      await savedJobsApi.unsaveJob(jobId);
      setSavedItems(savedItems.filter((item) => item.job_id !== jobId));
      onRefreshSavedIds();
    } catch (err) {
      console.error('Failed to unsave job:', err);
    }
  };

  const handleSaveNotes = async (jobId: number) => {
    try {
      await savedJobsApi.saveJob(jobId, noteText);
      setSavedItems(
        savedItems.map((item) =>
          item.job_id === jobId ? { ...item, notes: noteText } : item
        )
      );
      setEditingId(null);
    } catch (err) {
      console.error('Failed to save notes:', err);
    }
  };

  const filteredItems = savedItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.job.title.toLowerCase().includes(q) ||
      item.job.company.toLowerCase().includes(q) ||
      (item.notes && item.notes.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      {/* Top Banner (IMAGE 4 REPLICA) */}
      <div className="rounded-3xl border border-[#e4e8de] bg-[#f5f2e6] p-8 shadow-sm relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-[#e3edd9] border border-[#d2e2c2] text-[#2e7d52]">
            <Bookmark className="w-8 h-8 fill-[#2e7d52]" />
          </div>
          <div>
            <h2 className="text-3xl font-extrabold text-[#0a2618] tracking-tight">Your Saved Bookmarks</h2>
            <p className="text-xs text-slate-600 mt-1 font-medium">
              Track saved positions, interview notes, and application progress.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <button
            onClick={onOpenUpgrade}
            className="btn-light-secondary px-4 py-2.5 text-xs flex items-center gap-1.5 shrink-0"
          >
            <Crown className="w-4 h-4 text-emerald-700" /> Upgrade Plan
          </button>
          <span className="rounded-xl border border-[#d2e2c2] bg-[#e3edd9] px-4 py-2.5 text-xs font-extrabold text-[#225738] flex items-center gap-1">
            <Bookmark className="w-3.5 h-3.5 fill-[#225738]" /> {savedItems.length} Bookmarks
          </span>
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="relative">
        <Search className="absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search saved positions, companies or personal notes..."
          className="w-full rounded-2xl border border-[#e4e8de] bg-white pl-11 pr-4 py-3 text-xs text-[#0a2618] placeholder-slate-400 focus:border-[#2e7d52] focus:outline-none shadow-sm font-medium"
        />
      </div>

      {/* List Grid */}
      {loading ? (
        <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500 font-semibold animate-pulse">
          Loading saved jobs...
        </div>
      ) : filteredItems.length > 0 ? (
        <div className="space-y-4">
          {filteredItems.map((item) => {
            const isEditing = editingId === item.id;

            return (
              <div
                key={item.id}
                className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm hover:border-[#2e7d52] transition-all space-y-4 text-[#0b2319]"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4">
                    {/* Purple Shield Logo Icon */}
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-purple-100 border border-purple-200 text-purple-700">
                      <Shield className="w-6 h-6 fill-purple-600 text-purple-600" />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        <span className="text-xs font-bold text-[#2e7d52]">{item.job.company}</span>
                      </div>

                      <h3
                        onClick={() => onSelectJob(item.job)}
                        className="text-lg font-extrabold text-[#0a2618] hover:text-[#2e7d52] cursor-pointer transition-colors"
                      >
                        {item.job.title}
                      </h3>

                      {/* Personal Notes Box */}
                      <div className="mt-3 space-y-1">
                        <span className="inline-flex items-center gap-1 rounded-md bg-[#e3edd9] px-2 py-0.5 text-[10px] font-bold text-[#225738]">
                          <FileText className="w-3 h-3" /> Personal Notes
                        </span>
                        <p className="text-xs text-slate-600 leading-relaxed font-medium">
                          {item.notes ? `"${item.notes}"` : 'No notes added yet. Click edit to record thoughts.'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <button
                      onClick={() => {
                        setEditingId(item.id);
                        setNoteText(item.notes || '');
                      }}
                      className="text-xs font-bold text-[#2e7d52] hover:underline flex items-center gap-1"
                    >
                      <Edit3 className="w-3.5 h-3.5" /> Edit Note
                    </button>

                    <button
                      onClick={() => handleUnsave(item.job_id)}
                      className="text-slate-400 hover:text-red-600 transition-colors p-1"
                      title="Unsave"
                    >
                      <Bookmark className="w-5 h-5 fill-emerald-600 text-emerald-600" />
                    </button>
                  </div>
                </div>

                {/* Footer Bar */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-semibold">
                    Saved: {new Date(item.created_at).toLocaleDateString('en-GB')}
                  </span>

                  <a
                    href={item.job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-green-gradient px-4 py-2 text-xs flex items-center gap-1"
                  >
                    Apply Now &rarr;
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500 space-y-3">
          <Bookmark className="w-12 h-12 text-[#2e7d52]/40 mx-auto" />
          <h3 className="text-base font-extrabold text-[#0a2618]">No Saved Bookmarks</h3>
          <p className="text-xs max-w-sm mx-auto font-medium">
            {searchQuery
              ? 'No saved positions match your search query.'
              : 'Browse Explore Jobs or Job Matcher and click the bookmark icon on any job to save it here.'}
          </p>
        </div>
      )}
    </div>
  );
};
