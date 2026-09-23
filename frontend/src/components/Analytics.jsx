import React from 'react';
import { 
  LineChart, Activity, Utensils, Droplets, TrendingUp, 
  ShieldCheck, AlertTriangle, PieChart, BarChart2 
} from 'lucide-react';

export default function Analytics({ stats, batches, diagnostics }) {
  const totalStock = batches.reduce((acc, b) => acc + b.initial_quantity, 0);
  const currentStock = batches.reduce((acc, b) => acc + b.current_quantity, 0);
  const overallMortalityRate = totalStock > 0 ? (((totalStock - currentStock) / totalStock) * 100).toFixed(1) : 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Analytics Header */}
      <div className="glass-panel p-6 rounded-2xl border border-agri-800/40">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-agri-950 border border-agri-800 rounded-xl text-agri-400">
            <LineChart className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold font-display text-white">Resource Analytics & Mortality Trends</h1>
            <p className="text-sm text-slate-300">Biometric feed conversion, water consumption ratios, and flock health indexes</p>
          </div>
        </div>
      </div>

      {/* Analytics Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div className="glass-panel p-6 rounded-2xl border border-agri-800/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Flock Survival Index</span>
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold font-display text-emerald-400">{100 - overallMortalityRate}%</span>
            <span className="text-xs text-slate-400">survival rate</span>
          </div>
          <p className="text-xs text-slate-400">Overall flock retention across all active batches.</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-agri-800/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Mortality Loss Rate</span>
            <Activity className="w-5 h-5 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold font-display text-rose-400">{overallMortalityRate}%</span>
            <span className="text-xs text-slate-400">mortality rate</span>
          </div>
          <p className="text-xs text-slate-400">Within standard threshold (&lt;3.5% target).</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-agri-800/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Feed Conversion Ratio</span>
            <Utensils className="w-5 h-5 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold font-display text-amber-400">1.62</span>
            <span className="text-xs text-slate-400">FCR Index</span>
          </div>
          <p className="text-xs text-slate-400">Kilograms feed per kilogram live weight gain.</p>
        </div>

      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Resource Ratios */}
        <div className="glass-panel p-6 rounded-2xl border border-agri-800/40 space-y-4">
          <h3 className="text-lg font-bold font-display text-white flex items-center gap-2">
            <Droplets className="w-5 h-5 text-cyan-400" />
            <span>Water-to-Feed Consumption Ratio</span>
          </h3>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span className="text-slate-300">Poultry Flock A (Hydration Target 2.2:1)</span>
                <span className="text-cyan-400">2.3 : 1 Ratio</span>
              </div>
              <div className="w-full bg-darkbg h-3 rounded-full overflow-hidden border border-agri-950">
                <div className="bg-cyan-500 h-full rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span className="text-slate-300">Maize Plot #3 (Soil Moisture Retention)</span>
                <span className="text-emerald-400">Optimal (82%)</span>
              </div>
              <div className="w-full bg-darkbg h-3 rounded-full overflow-hidden border border-agri-950">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '82%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span className="text-slate-300">Dairy Herd B (Lactation Water Demand)</span>
                <span className="text-amber-400">Sub-optimal (68%)</span>
              </div>
              <div className="w-full bg-darkbg h-3 rounded-full overflow-hidden border border-agri-950">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: '68%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Pathology Risk Distribution */}
        <div className="glass-panel p-6 rounded-2xl border border-agri-800/40 space-y-4">
          <h3 className="text-lg font-bold font-display text-white flex items-center gap-2">
            <PieChart className="w-5 h-5 text-agri-400" />
            <span>Pathogen & Risk Distribution</span>
          </h3>

          <div className="space-y-3">
            <div className="p-3 bg-darkbg rounded-xl border border-rose-900/50 flex items-center justify-between text-xs">
              <span className="font-bold text-slate-200">Parasitic / Coccidiosis Risk</span>
              <span className="px-2.5 py-0.5 rounded bg-rose-950 text-rose-400 font-bold border border-rose-800">45% Incidents</span>
            </div>
            <div className="p-3 bg-darkbg rounded-xl border border-amber-900/50 flex items-center justify-between text-xs">
              <span className="font-bold text-slate-200">Fungal / Leaf Blight Issues</span>
              <span className="px-2.5 py-0.5 rounded bg-amber-950 text-amber-400 font-bold border border-amber-800">35% Incidents</span>
            </div>
            <div className="p-3 bg-darkbg rounded-xl border border-emerald-900/50 flex items-center justify-between text-xs">
              <span className="font-bold text-slate-200">Nutritional Deficiencies</span>
              <span className="px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-bold border border-emerald-800">20% Incidents</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
