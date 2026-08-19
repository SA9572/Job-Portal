import React, { useEffect, useState } from 'react';
import {
  X,
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  Bookmark,
  Sparkles,
  Layers,
  Globe,
  Trash2,
  RotateCcw,
} from 'lucide-react';
import { Job } from '../types/api';
import { jobsApi } from '../services/api';

interface JobDetailModalProps {
  job: Job | null;
  onClose: () => void;
  isSaved?: boolean;
  onToggleSave?: (jobId: number) => void;
  onSelectSimilarJob?: (job: Job) => void;
  isAdmin?: boolean;
  onDeleteJob?: (jobId: number) => void;
  onRestoreJob?: (jobId: number) => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({
  job,
  onClose,
  isSaved = false,
  onToggleSave,
  onSelectSimilarJob,
  isAdmin = false,
  onDeleteJob,
  onRestoreJob,
}) => {
  const [similarJobs, setSimilarJobs] = useState<Job[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  useEffect(() => {
    if (!job) return;
    setLoadingSimilar(true);
    jobsApi
      .getSimilarJobs(job.id, 4)
      .then((res) => setSimilarJobs(res.jobs))
      .catch(() => setSimilarJobs([]))
      .finally(() => setLoadingSimilar(false));
  }, [job]);

  if (!job) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="glass-panel max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden relative my-8 border-indigo-500/30">
        {/* Header Bar */}
        <div className="p-6 border-b border-white/10 flex items-start justify-between gap-4 bg-slate-900/60">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-white/10 flex items-center justify-center overflow-hidden shrink-0">
              {job.company_logo ? (
                <img
                  src={job.company_logo}
                  alt={job.company}
                  className="w-full h-full object-cover"
                />
              ) : (
                <Building2 className="w-8 h-8 text-slate-400" />
              )}
            </div>
            <div>
              <h2 className="text-2xl font-extrabold text-white leading-tight">
                {job.title}
              </h2>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-slate-400">
                <span className="font-semibold text-cyan-400 flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {job.company}
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  {new Date(job.published_at).toLocaleDateString()}
                </span>
                {job.source && (
                  <span className="badge badge-purple text-xs">
                    Source: {job.source}
                  </span>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Key Badges Summary */}
          <div className="flex flex-wrap items-center gap-3 p-4 rounded-xl bg-slate-900/50 border border-white/5">
            {job.minimum_salary || job.maximum_salary ? (
              <span className="badge badge-emerald text-sm py-1.5 px-3">
                <DollarSign className="w-4 h-4" />
                {job.currency || '$'}
                {(job.minimum_salary || 0).toLocaleString()} -{' '}
                {(job.maximum_salary || 0).toLocaleString()} / {job.salary_period || 'year'}
              </span>
            ) : null}

            {job.location_restrictions.length > 0 ? (
              <span className="badge badge-cyan text-sm py-1.5 px-3">
                <MapPin className="w-4 h-4" />
                {job.location_restrictions.join(', ')}
              </span>
            ) : (
              <span className="badge badge-cyan text-sm py-1.5 px-3">
                <Globe className="w-4 h-4" /> Worldwide Remote
              </span>
            )}

            {job.employment_type && (
              <span className="badge badge-purple text-sm py-1.5 px-3">
                <Layers className="w-4 h-4" /> {job.employment_type}
              </span>
            )}

            {job.seniority.map((s, idx) => (
              <span key={idx} className="badge badge-amber text-sm py-1.5 px-3">
                {s}
              </span>
            ))}
          </div>

          {/* Categories / Tags */}
          {job.categories.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                Categories & Tags
              </h4>
              <div className="flex flex-wrap gap-2">
                {job.categories.map((cat, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs border border-white/5"
                  >
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Full Description */}
          <div>
            <h3 className="text-lg font-bold text-white mb-3">Job Description</h3>
            <div
              className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed space-y-4"
              dangerouslySetInnerHTML={{ __html: job.description }}
            />
          </div>

          {/* Similar Jobs Recommendation Panel */}
          <div className="pt-6 border-t border-white/10">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Recommended Similar Roles
            </h3>

            {loadingSimilar ? (
              <div className="text-slate-400 text-sm animate-pulse">
                Computing similarity scores...
              </div>
            ) : similarJobs.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {similarJobs.map((simJob) => (
                  <div
                    key={simJob.id}
                    onClick={() => onSelectSimilarJob && onSelectSimilarJob(simJob)}
                    className="p-4 rounded-xl bg-slate-900/60 border border-white/5 hover:border-indigo-500/40 cursor-pointer transition-all hover:bg-slate-800/80 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                        <span>{simJob.company}</span>
                        {simJob.similarity_score !== undefined && (
                          <span className="text-amber-400 font-bold">
                            {(simJob.similarity_score * 100).toFixed(0)}% Match
                          </span>
                        )}
                      </div>
                      <h4 className="text-sm font-bold text-white line-clamp-1">
                        {simJob.title}
                      </h4>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs">No similar roles found.</p>
            )}
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="p-6 border-t border-white/10 bg-slate-900/80 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {onToggleSave && (
              <button
                onClick={() => onToggleSave(job.id)}
                className={`btn-secondary flex items-center gap-2 text-sm ${
                  isSaved ? 'text-purple-400 border-purple-500/50' : ''
                }`}
              >
                <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-purple-400' : ''}`} />
                {isSaved ? 'Saved' : 'Save Job'}
              </button>
            )}

            {isAdmin && (
              <>
                {job.is_deleted ? (
                  <button
                    onClick={() => onRestoreJob && onRestoreJob(job.id)}
                    className="px-4 py-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-500/30 text-sm font-semibold flex items-center gap-1.5"
                  >
                    <RotateCcw className="w-4 h-4" /> Restore
                  </button>
                ) : (
                  <button
                    onClick={() => onDeleteJob && onDeleteJob(job.id)}
                    className="px-4 py-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/40 hover:bg-rose-500/30 text-sm font-semibold flex items-center gap-1.5"
                  >
                    <Trash2 className="w-4 h-4" /> Soft Delete
                  </button>
                )}
              </>
            )}
          </div>

          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="gradient-btn flex items-center gap-2 text-sm px-6 py-2.5"
          >
            Apply for this position <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
};
