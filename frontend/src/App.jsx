import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Overview from './components/Overview';
import Diagnostics from './components/Diagnostics';
import Batches from './components/Batches';
import Analytics from './components/Analytics';
import DiagnosticModal from './components/DiagnosticModal';
import { fetchStats, fetchBatches, fetchDiagnostics, fetchHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [batches, setBatches] = useState([]);
  const [diagnostics, setDiagnostics] = useState([]);
  const [selectedDiagnostic, setSelectedDiagnostic] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [statsData, batchesData, diagData] = await Promise.all([
        fetchStats(),
        fetchBatches(),
        fetchDiagnostics()
      ]);
      setStats(statsData);
      setBatches(batchesData);
      setDiagnostics(diagData);
    } catch (err) {
      console.error('Error loading initial farm data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    fetchHealth();
  }, []);

  const handleBatchCreated = (newBatch) => {
    setBatches([newBatch, ...batches]);
    loadData();
  };

  const handleLogAdded = (batchId, newLog) => {
    // Update local batch stock
    setBatches(batches.map(b => {
      if (b.id === batchId && newLog.mortality_count > 0) {
        return { ...b, current_quantity: Math.max(0, b.current_quantity - newLog.mortality_count) };
      }
      return b;
    }));
    loadData();
  };

  const handleDiagnosticCreated = (newDiag) => {
    setDiagnostics([newDiag, ...diagnostics]);
    loadData();
  };

  return (
    <div className="min-h-screen flex flex-col bg-darkbg text-slate-100 font-sans selection:bg-agri-500 selection:text-white">
      
      {/* Navigation & Header */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />

      {/* Main App Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-4 text-slate-400">
            <div className="w-12 h-12 rounded-full border-4 border-agri-500/20 border-t-agri-500 animate-spin"></div>
            <p className="text-sm font-semibold">Connecting to AgriMind Engine...</p>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <Overview
                stats={stats}
                diagnostics={diagnostics}
                batches={batches}
                setActiveTab={setActiveTab}
                onSelectDiagnostic={(diag) => setSelectedDiagnostic(diag)}
              />
            )}

            {activeTab === 'diagnostics' && (
              <Diagnostics
                batches={batches}
                onDiagnosticCreated={handleDiagnosticCreated}
              />
            )}

            {activeTab === 'batches' && (
              <Batches
                batches={batches}
                onBatchCreated={handleBatchCreated}
                onLogAdded={handleLogAdded}
              />
            )}

            {activeTab === 'analytics' && (
              <Analytics
                stats={stats}
                batches={batches}
                diagnostics={diagnostics}
              />
            )}
          </>
        )}
      </main>

      {/* Modal for detailed Diagnostic Report */}
      {selectedDiagnostic && (
        <DiagnosticModal
          diagnostic={selectedDiagnostic}
          onClose={() => setSelectedDiagnostic(null)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-agri-950 py-6 px-4 text-center text-xs text-slate-500">
        <p>AgriMind Engine • AI-Powered Smart Agricultural Resource Engine & Visual Pathology Diagnostics</p>
      </footer>

    </div>
  );
}
