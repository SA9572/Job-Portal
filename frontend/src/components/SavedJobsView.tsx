import React, { useEffect, useState } from 'react';
import { Bookmark, Edit3, Trash2, ExternalLink, FileText, Check } from 'lucide-react';
import { SavedJob, Job } from '../types/api';
import { savedJobsApi } from '../services/api';

interface SavedJobsViewProps {
  onSelectJob: (job: Job) => void;
  onRefreshSavedIds: () => void;
}

export const SavedJobsView: React.FC<SavedJobsViewProps> = ({
  onSelectJob,
  onRefreshSavedIds,
}) => {
  const [savedItems, setSavedItems] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [noteText, setNoteText] = useState('');

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Bookmark className="w-6 h-6 text-purple-400 fill-purple-400" />
            Your Saved Bookmarks
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Keep track of roles, interview notes, and application status
          </p>
        </div>
        <span className="badge badge-purple text-sm py-1.5 px-3">
          {savedItems.length} Bookmarks
        </span>
      </div>

      {/* List */}
      {loading ? (
        <div className="glass-panel p-12 text-center text-slate-400 animate-pulse">
          Loading saved jobs...
        </div>
      ) : savedItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {savedItems.map((item) => {
            const isEditing = editingId === item.id;

            return (
              <div
                key={item.id}
                className="glass-panel glass-card-hover p-6 flex flex-col justify-between space-y-4 border-purple-500/20"
              >
                <div>
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div>
                      <span className="text-xs text-slate-400 font-medium">
                        {item.job.company}
                      </span>
                      <h3
                        onClick={() => onSelectJob(item.job)}
                        className="text-lg font-bold text-white hover:text-cyan-400 cursor-pointer transition-colors line-clamp-1"
                      >
                        {item.job.title}
                      </h3>
                    </div>

                    <button
                      onClick={() => handleUnsave(item.job_id)}
                      className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors"
                      title="Unsave Job"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Personal Notes Box */}
                  <div className="mt-4 p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-2">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span className="font-semibold flex items-center gap-1">
                        <FileText className="w-3.5 h-3.5 text-purple-400" /> Personal Notes
                      </span>
                      {!isEditing && (
                        <button
                          onClick={() => {
                            setEditingId(item.id);
                            setNoteText(item.notes || '');
                          }}
                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                        >
                          <Edit3 className="w-3 h-3" /> Edit
                        </button>
                      )}
                    </div>

                    {isEditing ? (
                      <div className="space-y-2">
                        <textarea
                          value={noteText}
                          onChange={(e) => setNoteText(e.target.value)}
                          placeholder="Add notes about application status, recruiter contact, etc..."
                          className="w-full bg-slate-950 border border-cyan-500/50 rounded-lg p-2 text-xs text-white focus:outline-none h-20 resize-none"
                        />
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setEditingId(null)}
                            className="btn-secondary text-[11px] py-1 px-2.5"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleSaveNotes(item.job_id)}
                            className="gradient-btn text-[11px] py-1 px-3 flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" /> Save Note
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-300 italic">
                        {item.notes ? `"${item.notes}"` : 'No notes added yet.'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Footer Action */}
                <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    Saved on {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  <a
                    href={item.job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="gradient-btn text-xs py-1.5 px-3 flex items-center gap-1"
                  >
                    Apply Now <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-2">
          <Bookmark className="w-12 h-12 text-purple-400/40 mx-auto" />
          <h3 className="text-base font-bold text-white">No Saved Jobs Yet</h3>
          <p className="text-xs max-w-sm mx-auto">
            Browse the Explore Jobs page and click the bookmark icon on any position to save it here.
          </p>
        </div>
      )}
    </div>
  );
};
