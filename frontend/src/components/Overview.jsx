import React from 'react';
import { 
  Layers, AlertTriangle, Droplets, Utensils, Activity, ArrowUpRight, 
  Stethoscope, CheckCircle2, ChevronRight, Sparkles, Feather, Wheat, Beef 
} from 'lucide-react';

export default function Overview({ stats, diagnostics, batches, setActiveTab, onSelectDiagnostic }) {
  const getBatchIcon = (type) => {
    switch (type) {
      case 'Poultry': return <Feather className="w-4 h-4 text-amber-400" />;
      case 'Crops': return <Wheat className="w-4 h-4 text-emerald-400" />;
      case 'Livestock': return <Beef className="w-4 h-4 text-rose-400" />;
      default: return <Layers className="w-4 h-4 text-agri-400" />;
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'Critical':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800 animate-pulse">Critical</span>;
      case 'High':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-950 text-amber-400 border border-amber-800">High Severity</span>;
      case 'Medium':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-yellow-950 text-yellow-400 border border-yellow-800">Medium</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">Low Risk</span>;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Top Welcome & Quick AI Action Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel p-6 lg:p-8 border border-agri-800/40">
        <div className="absolute -right-10 -bottom-10 w-80 h-80 bg-agri-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-agri-400 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-agri-400 animate-spin" />
              <span>Smart Agricultural Intelligence Active</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold font-display text-white tracking-tight">
              Farm Health & Telemetry Hub
            </h1>
            <p className="text-slate-300 text-sm max-w-2xl leading-relaxed">
              Real-time monitoring for your crops, poultry, and livestock. Run instant multimodal AI health diagnostics to prevent disease outbreaks and optimize feed & water consumption.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-agri-600 to-emerald-500 hover:from-agri-500 hover:to-emerald-400 text-white font-bold text-sm shadow-lg shadow-agri-600/30 transition-all hover:scale-105"
            >
              <Stethoscope className="w-5 h-5" />
              <span>Run Visual AI Diagnosis</span>
            </button>
            <button
              onClick={() => setActiveTab('batches')}
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-darkcard hover:bg-darkborder/70 border border-agri-800/60 text-slate-200 font-semibold text-sm transition-all"
            >
              <Layers className="w-5 h-5 text-agri-400" />
              <span>Manage Batches & Telemetry</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Active Batches */}
        <div className="glass-panel glass-panel-hover p-5 rounded-xl flex items-start justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Batches</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-display text-white">{stats?.active_batches || 0}</span>
              <span className="text-xs text-emerald-400 font-medium">/ {stats?.total_batches || 0} Total</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Poultry, Crops, Livestock</p>
          </div>
          <div className="p-3 bg-agri-950/80 border border-agri-800/60 rounded-xl text-agri-400">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        {/* Total Mortality */}
        <div className="glass-panel glass-panel-hover p-5 rounded-xl flex items-start justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Mortality Logged</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-display text-rose-400">{stats?.total_mortality || 0}</span>
              <span className="text-xs text-slate-400">units</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Controlled flock loss index</p>
          </div>
          <div className="p-3 bg-rose-950/80 border border-rose-800/60 rounded-xl text-rose-400">
            <Activity className="w-6 h-6" />
          </div>
        </div>

        {/* Feed Consumed */}
        <div className="glass-panel glass-panel-hover p-5 rounded-xl flex items-start justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Feed Consumed</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-display text-amber-400">{stats?.total_feed_consumed_kg || 0}</span>
              <span className="text-xs text-slate-400">kg</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Cumulative feed input</p>
          </div>
          <div className="p-3 bg-amber-950/80 border border-amber-800/60 rounded-xl text-amber-400">
            <Utensils className="w-6 h-6" />
          </div>
        </div>

        {/* Water Consumed */}
        <div className="glass-panel glass-panel-hover p-5 rounded-xl flex items-start justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Water Telemetry</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-display text-cyan-400">{stats?.total_water_consumed_l || 0}</span>
              <span className="text-xs text-slate-400">L</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Hydration tracking</p>
          </div>
          <div className="p-3 bg-cyan-950/80 border border-cyan-800/60 rounded-xl text-cyan-400">
            <Droplets className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* Main Grid: Batches Health Overview & Recent AI Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left 2 Cols: Active Farm Batches */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold font-display text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-agri-400" />
              <span>Active Resource Batches</span>
            </h2>
            <button
              onClick={() => setActiveTab('batches')}
              className="text-xs font-semibold text-agri-400 hover:text-agri-300 flex items-center gap-1"
            >
              <span>Manage All</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3">
            {batches.map((batch) => {
              const survivalRate = Math.round((batch.current_quantity / batch.initial_quantity) * 100);
              return (
                <div key={batch.id} className="glass-panel p-5 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2.5 bg-darkbg rounded-lg border border-agri-900/80">
                      {getBatchIcon(batch.batch_type)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-white text-base">{batch.name}</h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-darkbg text-slate-400 border border-agri-950 font-medium">
                          {batch.batch_type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        Stock: <span className="text-slate-200 font-semibold">{batch.current_quantity}</span> / {batch.initial_quantity} units
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 w-full sm:w-auto justify-between">
                    <div className="text-right sm:min-w-[120px]">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-400">Health Index</span>
                        <span className="font-bold text-emerald-400">{survivalRate}%</span>
                      </div>
                      <div className="w-full sm:w-28 bg-darkbg h-2 rounded-full overflow-hidden border border-agri-950">
                        <div
                          className="bg-gradient-to-r from-emerald-500 to-agri-400 h-full rounded-full"
                          style={{ width: `${survivalRate}%` }}
                        ></div>
                      </div>
                    </div>

                    <button
                      onClick={() => setActiveTab('batches')}
                      className="p-2 rounded-lg bg-darkbg hover:bg-darkborder text-slate-300 hover:text-white transition-all"
                      title="Log Telemetry"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 1 Col: Recent AI Diagnostics */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold font-display text-white flex items-center gap-2">
              <Stethoscope className="w-5 h-5 text-agri-400" />
              <span>Recent Diagnostics</span>
            </h2>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className="text-xs font-semibold text-agri-400 hover:text-agri-300"
            >
              New Scan
            </button>
          </div>

          <div className="glass-panel p-5 rounded-xl space-y-4">
            {diagnostics.length === 0 ? (
              <div className="text-center py-8 text-slate-400 space-y-2">
                <CheckCircle2 className="w-10 h-10 text-slate-600 mx-auto" />
                <p className="text-sm">No diagnostic issues recorded.</p>
              </div>
            ) : (
              diagnostics.slice(0, 3).map((diag) => (
                <div
                  key={diag.id}
                  onClick={() => onSelectDiagnostic(diag)}
                  className="p-4 rounded-lg bg-darkbg/70 hover:bg-darkborder/50 border border-agri-900/60 cursor-pointer transition-all space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-bold text-sm text-slate-100">{diag.detected_issue}</h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Confidence: <span className="text-emerald-400 font-semibold">{diag.confidence_score}%</span>
                      </p>
                    </div>
                    {getSeverityBadge(diag.severity)}
                  </div>

                  {diag.treatment_plan?.symptom_analysis && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {diag.treatment_plan.symptom_analysis.slice(0, 2).map((symptom, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-800">
                          • {symptom}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="pt-1 flex justify-end">
                    <span className="text-[11px] font-semibold text-agri-400 flex items-center gap-1 hover:underline">
                      <span>View Action Plan</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
