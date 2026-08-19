import React, { useState } from 'react';
import {
  Sparkles,
  Search,
  Plus,
  X,
  Sliders,
  DollarSign,
  MapPin,
  Briefcase,
  Layers,
} from 'lucide-react';
import { UserProfileMatch, MatchedJob } from '../types/api';
import { matchingApi } from '../services/api';
import { JobCard } from './JobCard';

interface MatchEngineViewProps {
  onSelectJob: (job: MatchedJob) => void;
  savedJobIds: number[];
  onToggleSave: (jobId: number) => void;
}

export const MatchEngineView: React.FC<MatchEngineViewProps> = ({
  onSelectJob,
  savedJobIds,
  onToggleSave,
}) => {
  const [desiredTitle, setDesiredTitle] = useState('Python Developer');
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState<string[]>(['Python', 'FastAPI', 'PostgreSQL', 'Docker']);
  const [preferredLocations, setPreferredLocations] = useState<string[]>(['Remote']);
  const [locationInput, setLocationInput] = useState('');
  const [seniority, setSeniority] = useState<string[]>(['Senior']);
  const [minSalary, setMinSalary] = useState<number>(100000);

  const [matchedJobs, setMatchedJobs] = useState<MatchedJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const addSkill = () => {
    if (skillInput.trim() && !skills.includes(skillInput.trim())) {
      setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const removeSkill = (s: string) => {
    setSkills(skills.filter((item) => item !== s));
  };

  const addLocation = () => {
    if (locationInput.trim() && !preferredLocations.includes(locationInput.trim())) {
      setPreferredLocations([...preferredLocations, locationInput.trim()]);
      setLocationInput('');
    }
  };

  const removeLocation = (loc: string) => {
    setPreferredLocations(preferredLocations.filter((item) => item !== loc));
  };

  const handleRunMatch = async () => {
    setLoading(true);
    setHasRun(true);
    try {
      const profile: UserProfileMatch = {
        desired_title: desiredTitle || undefined,
        skills,
        preferred_locations: preferredLocations,
        seniority,
        min_salary: minSalary || undefined,
      };

      const res = await matchingApi.matchJobs(profile, 20, 0.05);
      setMatchedJobs(res.jobs);
    } catch (err) {
      console.error('Match engine error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <div className="glass-panel p-8 relative overflow-hidden bg-gradient-to-br from-indigo-950/60 via-slate-900/80 to-purple-950/60">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold mb-4">
            <Sparkles className="w-4 h-4" /> AI Candidate Match Engine
          </div>
          <h2 className="text-3xl font-extrabold text-white mb-2">
            Find Your Perfectly Matched Role
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Build your skill profile below. Our multi-attribute recommendation engine evaluates
            Title Keyword Overlap, Skill Coverage, Location Restrictions, Seniority Alignment, and
            Salary Proximity in real-time.
          </p>
        </div>
      </div>

      {/* Skill Profile Builder & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 space-y-6 lg:col-span-1 border-indigo-500/20">
          <h3 className="font-bold text-white flex items-center gap-2 pb-3 border-b border-white/10">
            <Sliders className="w-4 h-4 text-cyan-400" /> Skill & Profile Criteria
          </h3>

          {/* Desired Title */}
          <div>
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1.5">
              Target Job Title
            </label>
            <div className="relative">
              <Briefcase className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                value={desiredTitle}
                onChange={(e) => setDesiredTitle(e.target.value)}
                placeholder="e.g. Senior Backend Engineer"
                className="w-full bg-slate-900/80 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Skill Chips Builder */}
          <div>
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1.5">
              Core Skills & Tools
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Add skill (e.g. React, Python)"
                className="flex-1 bg-slate-900/80 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={addSkill}
                className="btn-secondary px-3 py-2 text-xs flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {skills.map((s) => (
                <span
                  key={s}
                  className="badge badge-cyan text-xs py-1 px-2.5 flex items-center gap-1.5"
                >
                  {s}
                  <X
                    className="w-3 h-3 cursor-pointer hover:text-white"
                    onClick={() => removeSkill(s)}
                  />
                </span>
              ))}
            </div>
          </div>

          {/* Preferred Locations */}
          <div>
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1.5">
              Preferred Locations
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                placeholder="Add location (e.g. Remote, US)"
                className="flex-1 bg-slate-900/80 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={addLocation}
                className="btn-secondary px-3 py-2 text-xs flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {preferredLocations.map((loc) => (
                <span
                  key={loc}
                  className="badge badge-purple text-xs py-1 px-2.5 flex items-center gap-1.5"
                >
                  {loc}
                  <X
                    className="w-3 h-3 cursor-pointer hover:text-white"
                    onClick={() => removeLocation(loc)}
                  />
                </span>
              ))}
            </div>
          </div>

          {/* Min Salary Expectation */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <label className="font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Target Min Salary
              </label>
              <span className="text-emerald-400 font-bold">${(minSalary / 1000).toFixed(0)}k/yr</span>
            </div>
            <input
              type="range"
              min={0}
              max={250000}
              step={10000}
              value={minSalary}
              onChange={(e) => setMinSalary(Number(e.target.value))}
              className="w-full accent-cyan-500 cursor-pointer"
            />
          </div>

          <button
            onClick={handleRunMatch}
            disabled={loading}
            className="gradient-btn w-full py-3 text-sm flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? 'Evaluating Candidates...' : 'Run Matching Engine'}
          </button>
        </div>

        {/* Results Ranking View */}
        <div className="lg:col-span-2 space-y-4">
          {!hasRun ? (
            <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
              <Sparkles className="w-12 h-12 text-amber-400/40 mx-auto animate-pulse" />
              <h3 className="text-lg font-bold text-white">Ready to Match</h3>
              <p className="text-xs max-w-md mx-auto">
                Configure your title, skills, and target compensation on the left, then click
                "Run Matching Engine" to compute your personalized match scores.
              </p>
            </div>
          ) : loading ? (
            <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
              <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs">Analyzing job criteria & computing weighted match scores...</p>
            </div>
          ) : matchedJobs.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                Ranked Candidates ({matchedJobs.length} matches found)
              </h3>

              {matchedJobs.map((mJob) => {
                const isSaved = savedJobIds.includes(mJob.id);
                const scorePercent = (mJob.match_score * 100).toFixed(0);

                return (
                  <div key={mJob.id} className="glass-panel p-5 space-y-3 border-indigo-500/20">
                    {/* Header: Score Gauge */}
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-amber-500 to-emerald-500 p-[2px] shrink-0">
                          <div className="w-full h-full bg-[#090D16] rounded-[10px] flex items-center justify-center font-extrabold text-sm text-emerald-400">
                            {scorePercent}%
                          </div>
                        </div>
                        <div>
                          <h4
                            onClick={() => onSelectJob(mJob)}
                            className="text-base font-bold text-white hover:text-cyan-400 cursor-pointer transition-colors"
                          >
                            {mJob.title}
                          </h4>
                          <p className="text-xs text-slate-400">{mJob.company}</p>
                        </div>
                      </div>

                      <button
                        onClick={() => onToggleSave(mJob.id)}
                        className={`p-2 rounded-xl border ${
                          isSaved
                            ? 'bg-purple-500/20 border-purple-500/50 text-purple-400'
                            : 'bg-slate-800 border-white/5 text-slate-400 hover:text-white'
                        }`}
                      >
                        <Sparkles className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Breakdown Score Bars */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-white/5 text-[11px]">
                      <div>
                        <span className="text-slate-500 block">Title Match</span>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-cyan-400 h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.title_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 block">Skills Match</span>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-purple-400 h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.skill_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 block">Location Match</span>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-emerald-400 h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.location_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 block">Salary Match</span>
                        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-amber-400 h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.salary_match * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-slate-400">
              No matching jobs met the minimum score threshold. Try expanding your skills or location criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
