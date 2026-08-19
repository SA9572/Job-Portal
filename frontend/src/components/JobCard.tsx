import React from 'react';
import {
  Building2,
  MapPin,
  DollarSign,
  Bookmark,
  ExternalLink,
  Sparkles,
  Layers,
  Clock,
} from 'lucide-react';
import { Job } from '../types/api';

interface JobCardProps {
  job: Job;
  isSaved?: boolean;
  onToggleSave?: (jobId: number) => void;
  onSelectJob: (job: Job) => void;
  onViewSimilar?: (job: Job) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  isSaved = false,
  onToggleSave,
  onSelectJob,
  onViewSimilar,
}) => {
  const formatSalary = () => {
    if (!job.minimum_salary && !job.maximum_salary) return null;
    const curr = job.currency || '$';
    if (job.minimum_salary && job.maximum_salary) {
      return `${curr}${(job.minimum_salary / 1000).toFixed(0)}k - ${curr}${(job.maximum_salary / 1000).toFixed(0)}k`;
    }
    const val = job.minimum_salary || job.maximum_salary || 0;
    return `${curr}${(val / 1000).toFixed(0)}k+`;
  };

  const salaryText = formatSalary();

  return (
    <div className="glass-panel glass-card-hover p-6 flex flex-col justify-between relative group">
      {/* Top Bar: Company Logo & Bookmark Action */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-white/10 flex items-center justify-center overflow-hidden shrink-0">
            {job.company_logo ? (
              <img
                src={job.company_logo}
                alt={job.company}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />
            ) : (
              <Building2 className="w-6 h-6 text-slate-400" />
            )}
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-1.5">
              {job.company}
            </h4>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(job.published_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        {/* Save Bookmark Action */}
        {onToggleSave && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleSave(job.id);
            }}
            className={`p-2.5 rounded-xl border transition-all ${
              isSaved
                ? 'bg-purple-500/20 border-purple-500/50 text-purple-400 shadow-lg shadow-purple-500/20'
                : 'bg-slate-800/50 border-white/5 text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
            title={isSaved ? 'Remove from Saved' : 'Save Job'}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-purple-400' : ''}`} />
          </button>
        )}
      </div>

      {/* Title & Clickable Detail Trigger */}
      <div className="mb-4 cursor-pointer" onClick={() => onSelectJob(job)}>
        <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors line-clamp-2">
          {job.title}
        </h3>

        {/* FTS Snippet or Excerpt */}
        {job.fts_snippet ? (
          <p
            className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: job.fts_snippet }}
          />
        ) : job.excerpt ? (
          <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
            {job.excerpt}
          </p>
        ) : null}
      </div>

      {/* Badges: Salary, Location, Seniority */}
      <div className="flex flex-wrap items-center gap-2 mb-5">
        {salaryText && (
          <span className="badge badge-emerald">
            <DollarSign className="w-3 h-3" />
            {salaryText}
          </span>
        )}

        {job.location_restrictions.length > 0 ? (
          <span className="badge badge-cyan">
            <MapPin className="w-3 h-3" />
            {job.location_restrictions.slice(0, 2).join(', ')}
          </span>
        ) : (
          <span className="badge badge-cyan">
            <MapPin className="w-3 h-3" />
            Worldwide Remote
          </span>
        )}

        {job.employment_type && (
          <span className="badge badge-purple">
            <Layers className="w-3 h-3" />
            {job.employment_type}
          </span>
        )}

        {job.similarity_score !== undefined && (
          <span className="badge badge-amber">
            <Sparkles className="w-3 h-3" />
            {(job.similarity_score * 100).toFixed(0)}% Similar
          </span>
        )}
      </div>

      {/* Card Actions Footer */}
      <div className="pt-4 border-t border-white/5 flex items-center justify-between gap-2 mt-auto">
        {onViewSimilar && (
          <button
            onClick={() => onViewSimilar(job)}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-indigo-500/10 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Similar Jobs
          </button>
        )}

        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={() => onSelectJob(job)}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            Details
          </button>
          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="gradient-btn text-xs py-1.5 px-3.5 flex items-center gap-1"
          >
            Apply <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
};
