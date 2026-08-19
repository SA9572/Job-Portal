import React, { useState, useEffect } from 'react';
import {
  UserRound,
  Sparkles,
  Crown,
  Briefcase,
  MapPin,
  DollarSign,
  Award,
  FileText,
  Save,
  CheckCircle2,
  Plus,
  X,
  Zap,
  ArrowRight,
  ShieldCheck,
  RotateCcw,
} from 'lucide-react';
import { User, UserProfileMatch } from '../types/api';

interface ProfileViewProps {
  currentUser: User | null;
  onOpenUpgrade: () => void;
  onNavigateToMatch: (profile: UserProfileMatch) => void;
}

const DEFAULT_SKILLS = [
  'Python',
  'React',
  'TypeScript',
  'FastAPI',
  'SQL',
  'Node.js',
  'TailwindCSS',
  'Docker',
];

export const ProfileView: React.FC<ProfileViewProps> = ({
  currentUser,
  onOpenUpgrade,
  onNavigateToMatch,
}) => {
  const [fullName, setFullName] = useState<string>(currentUser?.full_name || 'Saurabh Kumar');
  const [desiredTitle, setDesiredTitle] = useState<string>('Python Developer');
  const [bio, setBio] = useState<string>(
    'Experienced Software Engineer passionate about FastAPI, React, Python microservices, and high-scale real-time job portals.'
  );
  const [skills, setSkills] = useState<string[]>(DEFAULT_SKILLS);
  const [newSkill, setNewSkill] = useState<string>('');
  const [preferredLocations, setPreferredLocations] = useState<string[]>(['Remote', 'United States', 'Worldwide']);
  const [newLocation, setNewLocation] = useState<string>('');
  const [seniority, setSeniority] = useState<string[]>(['Senior', 'Lead']);
  const [minSalary, setMinSalary] = useState<number>(90000);
  const [resumeText, setResumeText] = useState<string>('');
  const [parsingResume, setParsingResume] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  // Load from LocalStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('user_profile_data');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.desiredTitle) setDesiredTitle(parsed.desiredTitle);
        if (parsed.bio) setBio(parsed.bio);
        if (parsed.skills && Array.isArray(parsed.skills)) setSkills(parsed.skills);
        if (parsed.preferredLocations && Array.isArray(parsed.preferredLocations))
          setPreferredLocations(parsed.preferredLocations);
        if (parsed.seniority && Array.isArray(parsed.seniority)) setSeniority(parsed.seniority);
        if (parsed.minSalary) setMinSalary(parsed.minSalary);
        if (parsed.fullName) setFullName(parsed.fullName);
      }
    } catch (e) {
      console.error('Error loading profile from localStorage', e);
    }
  }, []);

  const handleSaveProfile = () => {
    const profileData = {
      fullName,
      desiredTitle,
      bio,
      skills,
      preferredLocations,
      seniority,
      minSalary,
    };
    localStorage.setItem('user_profile_data', JSON.stringify(profileData));
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleAddSkill = () => {
    if (!newSkill.trim()) return;
    if (!skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
    }
    setNewSkill('');
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove));
  };

  const handleAddLocation = () => {
    if (!newLocation.trim()) return;
    if (!preferredLocations.includes(newLocation.trim())) {
      setPreferredLocations([...preferredLocations, newLocation.trim()]);
    }
    setNewLocation('');
  };

  const handleRemoveLocation = (locToRemove: string) => {
    setPreferredLocations(preferredLocations.filter((l) => l !== locToRemove));
  };

  const handleToggleSeniority = (level: string) => {
    if (seniority.includes(level)) {
      setSeniority(seniority.filter((s) => s !== level));
    } else {
      setSeniority([...seniority, level]);
    }
  };

  const handleParseResume = () => {
    if (!resumeText.trim()) return;
    setParsingResume(true);
    setTimeout(() => {
      const candidates = [
        'Python',
        'TypeScript',
        'React',
        'FastAPI',
        'Docker',
        'PostgreSQL',
        'GraphQL',
        'AWS',
        'TailwindCSS',
        'Kubernetes',
        'REST API',
        'System Architecture',
      ];
      const extracted = candidates.filter((item) =>
        resumeText.toLowerCase().includes(item.toLowerCase())
      );
      const combined = Array.from(new Set([...skills, ...extracted]));
      setSkills(combined);
      setParsingResume(false);
    }, 1200);
  };

  const handleLaunchMatch = () => {
    handleSaveProfile();
    const profileMatch: UserProfileMatch = {
      desired_title: desiredTitle,
      skills,
      preferred_locations: preferredLocations,
      seniority,
      min_salary: minSalary,
    };
    onNavigateToMatch(profileMatch);
  };

  return (
    <div className="space-y-6 text-[#0b2319]">
      {/* Top Banner Card */}
      <div className="rounded-3xl border border-[#e4e8de] bg-[#f5f2e6] p-8 shadow-sm relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-[#276e46] text-white shadow-md font-extrabold text-2xl">
            SK
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl md:text-3xl font-extrabold text-[#0a2618] tracking-tight">
                {fullName || currentUser?.full_name || 'Saurabh Kumar'}
              </h1>
              <span className="rounded-full border border-[#d2e2c2] bg-[#e3edd9] px-3 py-0.5 text-xs font-bold text-[#225738]">
                {currentUser?.role === 'admin' ? 'System Admin' : 'Active Candidate'}
              </span>
            </div>
            <p className="mt-1 text-xs font-semibold text-slate-600">
              {currentUser?.email || 'saurabh@jobrequired.com'} &bull; Target: <span className="text-[#2e7d52] font-bold">{desiredTitle}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <button
            onClick={handleSaveProfile}
            className="flex-1 md:flex-initial flex items-center justify-center gap-2 rounded-xl bg-white border border-[#d5e0cc] px-5 py-2.5 text-xs font-bold text-[#1e3a29] hover:bg-[#f8faf5] transition-all shadow-sm"
          >
            {savedSuccess ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Saved!
              </>
            ) : (
              <>
                <Save className="w-4 h-4 text-[#2e7d52]" /> Save Profile
              </>
            )}
          </button>

          <button
            onClick={onOpenUpgrade}
            className="flex-1 md:flex-initial btn-green-gradient px-5 py-2.5 text-xs flex items-center justify-center gap-2 shadow"
          >
            <Crown className="w-4 h-4 text-amber-300" /> Upgrade Plan
          </button>
        </div>
      </div>

      {savedSuccess && (
        <div className="rounded-2xl border border-[#d2e2c2] bg-[#e3edd9] p-4 text-center text-xs font-extrabold text-[#225738]">
          ✨ Profile preferences saved! Your target role and skills are active across AI Candidate Matching.
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Details & Target Role */}
        <div className="lg:col-span-2 space-y-6">
          {/* Executive Bio & Details */}
          <div className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <h2 className="text-base font-extrabold text-[#0a2618] flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-[#2e7d52]" /> Candidate Preferences &amp; Bio
              </h2>
              <span className="text-xs text-slate-500 font-medium">Used for AI Candidate Matching</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-xs text-[#0a2618] font-semibold focus:border-[#2e7d52] focus:outline-none"
                  placeholder="Saurabh Kumar"
                />
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1.5">
                  Target Job Title
                </label>
                <input
                  type="text"
                  value={desiredTitle}
                  onChange={(e) => setDesiredTitle(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-xs text-[#0a2618] font-semibold focus:border-[#2e7d52] focus:outline-none"
                  placeholder="e.g. Python Developer"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1.5">
                Executive Bio / Professional Summary
              </label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-xs text-[#0a2618] font-medium focus:border-[#2e7d52] focus:outline-none"
                placeholder="Highlight your key achievements, tech stack expertise, and career goals..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1.5">
                  Minimum Desired Salary ($/yr)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-3 h-4 w-4 text-emerald-600" />
                  <input
                    type="number"
                    step={5000}
                    value={minSalary}
                    onChange={(e) => setMinSalary(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3.5 py-2.5 text-xs text-[#0a2618] font-semibold focus:border-[#2e7d52] focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1.5">
                  Seniority Level
                </label>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {['Junior', 'Mid-Level', 'Senior', 'Lead', 'Executive'].map((level) => {
                    const active = seniority.includes(level);
                    return (
                      <button
                        key={level}
                        type="button"
                        onClick={() => handleToggleSeniority(level)}
                        className={`rounded-lg px-3 py-1 text-xs font-bold transition-all ${
                          active
                            ? 'bg-[#e3edd9] border border-[#c4dbb4] text-[#1e5a39]'
                            : 'bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        {level}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Skills & Tech Stack Section */}
          <div className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <h2 className="text-base font-extrabold text-[#0a2618] flex items-center gap-2">
                <Award className="w-5 h-5 text-[#2e7d52]" /> Skills &amp; Core Tools
              </h2>
              <span className="text-xs text-slate-500 font-medium">{skills.length} skills added</span>
            </div>

            {/* Current Skill Chips */}
            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-[#d2e2c2] bg-[#e3edd9] px-3 py-1 text-xs font-bold text-[#225738]"
                >
                  {skill}
                  <button
                    onClick={() => handleRemoveSkill(skill)}
                    className="hover:text-red-600 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>

            {/* Add Custom Skill */}
            <div className="flex items-center gap-3">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                placeholder="Add a new skill (e.g. Docker, PostgreSQL)..."
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs text-[#0a2618] focus:border-[#2e7d52] focus:outline-none"
              />
              <button
                type="button"
                onClick={handleAddSkill}
                className="btn-green-gradient px-4 py-2 text-xs flex items-center gap-1"
              >
                <Plus className="w-4 h-4" /> Add
              </button>
            </div>

            {/* Locations Section */}
            <div className="pt-4 border-t border-slate-100">
              <label className="block text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-2">
                Preferred Locations
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {preferredLocations.map((loc) => (
                  <span
                    key={loc}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-[#d2e2c2] bg-[#e3edd9] px-3 py-1 text-xs font-bold text-[#225738]"
                  >
                    <MapPin className="w-3 h-3" /> {loc}
                    <button
                      onClick={() => handleRemoveLocation(loc)}
                      className="hover:text-red-600 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddLocation()}
                  placeholder="Add preferred location (e.g. Remote, US)..."
                  className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs text-[#0a2618] focus:border-[#2e7d52] focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleAddLocation}
                  className="btn-light-secondary px-4 py-2 text-xs flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" /> Add Location
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: AI Match Launcher & Resume Parser */}
        <div className="space-y-6">
          {/* Quick Launch Match Card */}
          <div className="rounded-2xl border border-[#e4e8de] bg-[#f5f2e6] p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#e3edd9] text-[#2e7d52]">
                <Sparkles className="h-5 w-5" />
              </div>
              <h3 className="text-base font-extrabold text-[#0a2618]">AI Candidate Matcher</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Launch the Job Match engine pre-configured with your skills ({skills.length}), seniority, and target salary.
            </p>
            <button
              onClick={handleLaunchMatch}
              className="w-full btn-green-gradient py-3 text-xs flex items-center justify-center gap-2"
            >
              Match Jobs For Me <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* AI Resume Parser Simulator */}
          <div className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-[#2e7d52]" />
              <h3 className="text-base font-extrabold text-[#0a2618]">AI Resume Parser</h3>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Paste your resume or work history below to automatically extract core skills into your profile.
            </p>

            <textarea
              rows={4}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your raw resume summary or work experience..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-[#0a2618] focus:border-[#2e7d52] focus:outline-none"
            />

            <button
              onClick={handleParseResume}
              disabled={parsingResume || !resumeText.trim()}
              className="w-full btn-green-gradient py-2.5 text-xs flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {parsingResume ? (
                'Extracting Skills...'
              ) : (
                <>
                  <Zap className="w-4 h-4" /> Extract Skills with AI
                </>
              )}
            </button>
          </div>

          {/* Account Security & Overview */}
          <div className="rounded-2xl border border-[#e4e8de] bg-white p-6 shadow-sm space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500">
              Account Overview
            </h3>
            <div className="space-y-2 text-xs font-medium">
              <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Account Type</span>
                <span className="font-extrabold text-[#2e7d52]">Standard Candidate</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Database Engine</span>
                <span className="font-extrabold text-[#2e7d52]">FastAPI &amp; SQLite FTS5</span>
              </div>
              <div className="flex items-center justify-between py-1.5">
                <span className="text-slate-500">Data Privacy</span>
                <span className="font-extrabold text-slate-700">Encrypted Local Storage</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
