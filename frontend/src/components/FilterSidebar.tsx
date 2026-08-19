import React from 'react';
import {
  Search,
  Filter,
  RotateCcw,
  Sparkles,
  DollarSign,
  Building2,
  Layers,
  MapPin,
} from 'lucide-react';
import { FilterOptions } from '../types/api';

interface FilterSidebarProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  useFTS: boolean;
  setUseFTS: (use: boolean) => void;
  selectedCategories: string[];
  setSelectedCategories: React.Dispatch<React.SetStateAction<string[]>>;
  selectedLocations: string[];
  setSelectedLocations: React.Dispatch<React.SetStateAction<string[]>>;
  selectedSeniority: string[];
  setSelectedSeniority: React.Dispatch<React.SetStateAction<string[]>>;
  selectedEmpType: string[];
  setSelectedEmpType: React.Dispatch<React.SetStateAction<string[]>>;
  minSalary: number;
  setMinSalary: (sal: number) => void;
  filterOptions: FilterOptions | null;
  onReset: () => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  searchQuery,
  setSearchQuery,
  useFTS,
  setUseFTS,
  selectedCategories,
  setSelectedCategories,
  selectedLocations,
  setSelectedLocations,
  selectedSeniority,
  setSelectedSeniority,
  selectedEmpType,
  setSelectedEmpType,
  minSalary,
  setMinSalary,
  filterOptions,
  onReset,
}) => {
  const toggleSelection = (
    value: string,
    state: string[],
    setState: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    if (state.includes(value)) {
      setState(state.filter((item) => item !== value));
    } else {
      setState([...state, value]);
    }
  };

  return (
    <aside className="glass-panel p-6 space-y-6 shrink-0 w-full lg:w-80">
      {/* Sidebar Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <h3 className="font-bold text-white flex items-center gap-2">
          <Filter className="w-4 h-4 text-cyan-400" />
          Filter Jobs
        </h3>
        <button
          onClick={onReset}
          className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3 h-3" /> Reset
        </button>
      </div>

      {/* Search Input & FTS Toggle */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Search Keywords
        </label>
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none z-10" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder='e.g. "Senior Python"'
            className="w-full bg-slate-900/90 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* FTS Toggle */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" /> SQLite FTS5 Engine
          </span>
          <button
            onClick={() => setUseFTS(!useFTS)}
            className={`w-9 h-5 rounded-full p-0.5 transition-colors ${
              useFTS ? 'bg-cyan-500' : 'bg-slate-700'
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-white transition-transform ${
                useFTS ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Minimum Salary Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <label className="font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Minimum Salary
          </label>
          <span className="text-emerald-400 font-bold">
            ${(minSalary / 1000).toFixed(0)}k+
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={200000}
          step={5000}
          value={minSalary}
          onChange={(e) => setMinSalary(Number(e.target.value))}
          className="w-full accent-cyan-500 cursor-pointer"
        />
      </div>

      {/* Employment Types */}
      {filterOptions?.employment_types && filterOptions.employment_types.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-purple-400" /> Employment Type
          </label>
          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
            {filterOptions.employment_types.map((type) => (
              <label
                key={type}
                className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer hover:text-white"
              >
                <input
                  type="checkbox"
                  checked={selectedEmpType.includes(type)}
                  onChange={() =>
                    toggleSelection(type, selectedEmpType, setSelectedEmpType)
                  }
                  className="rounded border-white/20 bg-slate-900 text-cyan-500 focus:ring-0"
                />
                <span className="capitalize">{type}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Seniority Levels */}
      {filterOptions?.seniorities && filterOptions.seniorities.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Seniority Level
          </label>
          <div className="flex flex-wrap gap-1.5">
            {filterOptions.seniorities.map((sen) => {
              const isSelected = selectedSeniority.includes(sen);
              return (
                <button
                  key={sen}
                  onClick={() =>
                    toggleSelection(sen, selectedSeniority, setSelectedSeniority)
                  }
                  className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                    isSelected
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 font-semibold'
                      : 'bg-slate-900/60 border-white/5 text-slate-400 hover:text-white'
                  }`}
                >
                  {sen}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Locations */}
      {filterOptions?.locations && filterOptions.locations.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" /> Location / Region
          </label>
          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
            {filterOptions.locations.slice(0, 15).map((loc) => (
              <label
                key={loc}
                className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer hover:text-white"
              >
                <input
                  type="checkbox"
                  checked={selectedLocations.includes(loc)}
                  onChange={() =>
                    toggleSelection(loc, selectedLocations, setSelectedLocations)
                  }
                  className="rounded border-white/20 bg-slate-900 text-cyan-500 focus:ring-0"
                />
                <span className="truncate">{loc}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Categories */}
      {filterOptions?.categories && filterOptions.categories.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1">
            <Building2 className="w-3.5 h-3.5 text-indigo-400" /> Categories
          </label>
          <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
            {filterOptions.categories.slice(0, 20).map((cat) => (
              <label
                key={cat}
                className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer hover:text-white"
              >
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(cat)}
                  onChange={() =>
                    toggleSelection(cat, selectedCategories, setSelectedCategories)
                  }
                  className="rounded border-white/20 bg-slate-900 text-cyan-500 focus:ring-0"
                />
                <span className="truncate">{cat}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
};
