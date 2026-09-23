import React from 'react';
import { Sprout, Cpu, LayoutDashboard, Stethoscope, Layers, LineChart, AlertTriangle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats }) {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'diagnostics', label: 'AI Health Diagnostic', icon: Stethoscope },
    { id: 'batches', label: 'Batches & Telemetry', icon: Layers },
    { id: 'analytics', label: 'Resource Analytics', icon: LineChart },
  ];

  return (
    <header className="sticky top-0 z-40 bg-darkbg/90 backdrop-blur-md border-b border-agri-900/60 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Brand Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="p-2.5 bg-gradient-to-tr from-agri-800 to-emerald-500 rounded-xl shadow-lg shadow-agri-500/20 text-white">
              <Sprout className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display font-extrabold text-2xl tracking-tight text-white">Agri<span className="text-agri-500">Mind</span></span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-agri-950 text-agri-400 border border-agri-800">
                  v1.0 AI Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden sm:block">Smart Agricultural Resource Engine & Multimodal AI</p>
            </div>
          </div>

          {/* Quick Critical Alert Banner for mobile */}
          {stats?.critical_alerts > 0 && (
            <div className="md:hidden flex items-center gap-1.5 px-3 py-1 bg-rose-950/80 border border-rose-800/80 rounded-full text-rose-400 text-xs font-semibold">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-500 animate-bounce" />
              <span>{stats.critical_alerts} Alert</span>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-darkcard/80 p-1.5 rounded-xl border border-agri-900/50 overflow-x-auto scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 whitespace-nowrap ${
                  isActive
                    ? 'bg-gradient-to-r from-agri-700 to-agri-600 text-white shadow-md shadow-agri-900/50'
                    : 'text-slate-400 hover:text-white hover:bg-darkborder/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.id === 'diagnostics' && (
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* AI Engine Status & Quick Metrics */}
        <div className="hidden lg:flex items-center gap-4 text-xs font-medium text-slate-300">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <div>
              <span className="text-[10px] block text-slate-400 uppercase font-semibold">AI Diagnostic Core</span>
              <span className="text-emerald-400 font-bold">Gemini 2.5 Flash</span>
            </div>
          </div>
        </div>

      </div>
    </header>
  );
}
