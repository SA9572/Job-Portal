import React, { useState, useEffect } from 'react';
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
  Bookmark,
  ExternalLink,
  UserRound,
  Crown,
} from 'lucide-react';
import { UserProfileMatch, MatchedJob } from '../types/api';
import { matchingApi } from '../services/api';

interface MatchEngineViewProps {
  onSelectJob: (job: MatchedJob) => void;
  savedJobIds: number[];
  onToggleSave: (jobId: number) => void;
  initialProfile?: UserProfileMatch | null;
  onOpenUpgrade?: () => void;
}

export const MatchEngineView: React.FC<MatchEngineViewProps> = ({
  onSelectJob,
  savedJobIds,
  onToggleSave,
  initialProfile,
  onOpenUpgrade,
}) => {
  const [desiredTitle, setDesiredTitle] = useState('Python Developer');
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState<string[]>(['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'React']);
  const [preferredLocations, setPreferredLocations] = useState<string[]>(['Remote']);
  const [locationInput, setLocationInput] = useState('');
  const [seniority, setSeniority] = useState<string[]>(['Senior']);
  const [minSalary, setMinSalary] = useState<number>(90000);

  const [matchedJobs, setMatchedJobs] = useState<MatchedJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  useEffect(() => {
    if (initialProfile) {
      if (initialProfile.desired_title) setDesiredTitle(initialProfile.desired_title);
      if (initialProfile.skills) setSkills(initialProfile.skills);
      if (initialProfile.preferred_locations) setPreferredLocations(initialProfile.preferred_locations);
      if (initialProfile.seniority) setSeniority(initialProfile.seniority);
      if (initialProfile.min_salary) setMinSalary(initialProfile.min_salary);
      handleRunMatchWithProfile(initialProfile);
    } else {
      const saved = localStorage.getItem('user_profile_data');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (parsed.desiredTitle) setDesiredTitle(parsed.desiredTitle);
          if (parsed.skills && Array.isArray(parsed.skills)) setSkills(parsed.skills);
          if (parsed.preferredLocations && Array.isArray(parsed.preferredLocations))
            setPreferredLocations(parsed.preferredLocations);
          if (parsed.seniority && Array.isArray(parsed.seniority)) setSeniority(parsed.seniority);
          if (parsed.minSalary) setMinSalary(parsed.minSalary);
        } catch (e) {
          console.error(e);
        }
      }
    }
  }, [initialProfile]);

  const handleSyncFromProfile = () => {
    const saved = localStorage.getItem('user_profile_data');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.desiredTitle) setDesiredTitle(parsed.desiredTitle);
        if (parsed.skills && Array.isArray(parsed.skills)) setSkills(parsed.skills);
        if (parsed.preferredLocations && Array.isArray(parsed.preferredLocations))
          setPreferredLocations(parsed.preferredLocations);
        if (parsed.seniority && Array.isArray(parsed.seniority)) setSeniority(parsed.seniority);
        if (parsed.minSalary) setMinSalary(parsed.minSalary);
      } catch (e) {
        console.error(e);
      }
    }
  };

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

  const handleRunMatchWithProfile = async (prof: UserProfileMatch) => {
    setLoading(true);
    setHasRun(true);
    try {
      const res = await matchingApi.matchJobs(prof, 20, 0.05);
      setMatchedJobs(res.jobs);
    } catch (err) {
      console.error('Match engine error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunMatch = async () => {
    const profile: UserProfileMatch = {
      desired_title: desiredTitle || undefined,
      skills,
      preferred_locations: preferredLocations,
      seniority,
      min_salary: minSalary || undefined,
    };
    await handleRunMatchWithProfile(profile);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner (IMAGE 2 REPLICA) */}
      <div className="rounded-3xl border border-[#e4e8de] bg-[#f5f2e6] p-8 shadow-sm relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#e3edd9] border border-[#d2e2c2] text-[#225738] text-[11px] font-extrabold mb-3">
            <Sparkles className="w-3.5 h-3.5 text-[#2e7d52]" /> AI CANDIDATE MATCH ENGINE
          </div>
          <h2 className="text-3xl font-extrabold text-[#0a2618] tracking-tight mb-2">
            Multi-Attribute Candidate Role Scoring
          </h2>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            Our intelligent matching algorithm evaluates Title Keyword Overlap, Skill Coverage, Location Restrictions, Seniority Alignment, and Salary Proximity in real time.
          </p>
        </div>

        <button
          onClick={onOpenUpgrade}
          className="btn-light-secondary px-4 py-2.5 text-xs flex items-center gap-1.5 shrink-0"
        >
          <Crown className="w-4 h-4 text-emerald-700" /> Upgrade Plan
        </button>
      </div>

      {/* Main Grid: Parameters Card + Results View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Match Parameters (White Card) */}
        <div className="rounded-2xl border border-[#e4e8de] bg-white p-6 space-y-5 shadow-sm lg:col-span-1 text-[#0b2319]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-extrabold text-sm text-[#0a2618] flex items-center gap-2">
              <Sliders className="w-4 h-4 text-[#2e7d52]" /> Match Parameters
            </h3>
            <button
              onClick={handleSyncFromProfile}
              className="text-[11px] font-bold text-[#2e7d52] hover:underline flex items-center gap-1"
            >
              <UserRound className="w-3 h-3" /> Sync Profile
            </button>
          </div>

          {/* TARGET JOB TITLE */}
          <div>
            <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
              TARGET JOB TITLE
            </label>
            <input
              type="text"
              value={desiredTitle}
              onChange={(e) => setDesiredTitle(e.target.value)}
              placeholder="e.g. Python Developer"
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-xs text-[#0a2618] font-semibold focus:outline-none focus:border-[#2e7d52]"
            />
          </div>

          {/* CORE SKILLS & TOOLS */}
          <div>
            <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
              CORE SKILLS &amp; TOOLS ({skills.length})
            </label>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {skills.map((s) => (
                <span
                  key={s}
                  className="rounded-lg border border-[#dce8d2] bg-[#f2f7ec] text-[#1e5a39] text-[11px] py-1 px-2.5 flex items-center gap-1 font-bold"
                >
                  {s}
                  <X
                    className="w-3 h-3 cursor-pointer hover:text-red-600"
                    onClick={() => removeSkill(s)}
                  />
                </span>
              ))}
              <button
                type="button"
                onClick={addSkill}
                className="rounded-lg border border-slate-200 bg-slate-100 p-1 text-slate-600 hover:bg-slate-200"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Add skill..."
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-[#2e7d52]"
              />
            </div>
          </div>

          {/* PREFERRED LOCATIONS */}
          <div>
            <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block mb-1.5">
              PREFERRED LOCATIONS
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLocation())}
                placeholder="Add location (e.g. Remote, US)"
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-[#2e7d52]"
              />
              <button
                type="button"
                onClick={addLocation}
                className="rounded-xl border border-slate-200 bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {preferredLocations.map((loc) => (
                <span
                  key={loc}
                  className="rounded-lg border border-[#dce8d2] bg-[#f2f7ec] text-[#1e5a39] text-[11px] py-1 px-2.5 flex items-center gap-1 font-bold"
                >
                  {loc}
                  <X
                    className="w-3 h-3 cursor-pointer hover:text-red-600"
                    onClick={() => removeLocation(loc)}
                  />
                </span>
              ))}
            </div>
          </div>

          {/* TARGET MIN SALARY */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <label className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">
                TARGET MIN SALARY
              </label>
              <span className="text-[#2e7d52] font-extrabold">${(minSalary / 1000).toFixed(0)}k/yr</span>
            </div>
            <input
              type="range"
              min={0}
              max={250000}
              step={10000}
              value={minSalary}
              onChange={(e) => setMinSalary(Number(e.target.value))}
              className="w-full accent-[#2e7d52] cursor-pointer"
            />
          </div>

          <button
            onClick={handleRunMatch}
            disabled={loading}
            className="w-full btn-green-gradient py-3 text-xs flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? 'Evaluating...' : 'Run Candidate Matcher'}
          </button>
        </div>

        {/* Right Column: Empty State or Ranked Results (IMAGE 2 RIGHT CARD) */}
        <div className="lg:col-span-2 space-y-4">
          {!hasRun ? (
            <div className="rounded-2xl border border-[#e4e8de] bg-[#fbf8ee] p-12 text-center text-[#0b2319] space-y-4 shadow-sm flex flex-col items-center justify-center min-h-[380px]">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#e3edd9] text-[#2e7d52] border border-[#cbe0bc] shadow-sm">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-extrabold text-[#0a2618]">Ready to Match Candidates</h3>
              <p className="text-xs text-slate-600 max-w-md leading-relaxed font-medium">
                Configure your target title, skills, and compensation on the left, then click 'Run Candidate Matcher' to compute multi-factor scores.
              </p>
              <button
                onClick={handleRunMatch}
                className="btn-green-gradient px-6 py-3 text-xs flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" /> Start Matching Now
              </button>
            </div>
          ) : loading ? (
            <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-600 space-y-3 shadow-sm">
              <div className="w-8 h-8 border-2 border-[#2e7d52] border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs font-semibold">Evaluating candidate criteria &amp; computing weighted match scores...</p>
            </div>
          ) : matchedJobs.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">
                  Matched Positions ({matchedJobs.length} results)
                </h3>
                <span className="text-xs text-[#2e7d52] font-bold">Sorted by Match Score</span>
              </div>

              {matchedJobs.map((mJob) => {
                const isSaved = savedJobIds.includes(mJob.id);
                const scorePercent = (mJob.match_score * 100).toFixed(0);

                return (
                  <div
                    key={mJob.id}
                    className="rounded-2xl border border-[#e4e8de] bg-white p-5 space-y-4 shadow-sm hover:border-[#2e7d52] transition-all text-[#0b2319]"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#388e5c] to-[#1f5e3b] p-[2px] shrink-0">
                          <div className="w-full h-full bg-[#f2f8ef] rounded-[14px] flex items-center justify-center font-extrabold text-sm text-[#1f5e3b]">
                            {scorePercent}%
                          </div>
                        </div>
                        <div>
                          <h4
                            onClick={() => onSelectJob(mJob)}
                            className="text-base font-extrabold text-[#0a2618] hover:text-[#2e7d52] cursor-pointer transition-colors"
                          >
                            {mJob.title}
                          </h4>
                          <p className="text-xs font-semibold text-slate-500">{mJob.company}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => onToggleSave(mJob.id)}
                          className={`flex items-center gap-1 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all ${
                            isSaved
                              ? 'bg-[#e3edd9] border-[#c4dbb4] text-[#1e5a39]'
                              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                          }`}
                        >
                          <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-[#1e5a39]' : ''}`} />
                          {isSaved ? 'Saved' : 'Save Job'}
                        </button>

                        <a
                          href={mJob.application_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-green-gradient px-4 py-2 text-xs flex items-center gap-1"
                        >
                          Apply Now &rarr;
                        </a>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-100 text-[11px]">
                      <div>
                        <span className="text-slate-500 font-semibold block">Title Match</span>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-[#2e7d52] h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.title_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 font-semibold block">Skills Match</span>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-[#48a670] h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.skill_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 font-semibold block">Location Match</span>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-[#2e7d52] h-full rounded-full"
                            style={{ width: `${mJob.match_breakdown.location_match * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 font-semibold block">Salary Match</span>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 mt-1 overflow-hidden">
                          <div
                            className="bg-[#e6ad35] h-full rounded-full"
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
            <div className="rounded-2xl border border-[#e4e8de] bg-white p-12 text-center text-slate-500">
              No matching jobs met the minimum score threshold. Try expanding your skills or location criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
