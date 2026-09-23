import React, { useState } from 'react';
import { 
  Layers, Plus, Calendar, Utensils, Droplets, Activity, FileText, 
  X, CheckCircle2, AlertCircle, Feather, Wheat, Beef, RefreshCw 
} from 'lucide-react';
import { createBatch, addDailyLog, fetchLogs } from '../api';

export default function Batches({ batches, onBatchCreated, onLogAdded }) {
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [showLogModal, setShowLogModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  
  // Batch Form State
  const [newBatchName, setNewBatchName] = useState('');
  const [newBatchType, setNewBatchType] = useState('Poultry');
  const [newBatchQty, setNewBatchQty] = useState(500);

  // Daily Log Form State
  const [mortality, setMortality] = useState(0);
  const [feedKg, setFeedKg] = useState(0);
  const [waterL, setWaterL] = useState(0);
  const [logNotes, setLogNotes] = useState('');

  // Selected Batch Logs View
  const [activeLogs, setActiveLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  // Creation State
  const [isCreatingBatch, setIsCreatingBatch] = useState(false);
  const [batchError, setBatchError] = useState(null);

  const handleCreateBatch = async (e) => {
    e.preventDefault();
    const name = newBatchName.trim();
    const qty = parseInt(newBatchQty, 10);

    if (!name) {
      setBatchError('Please enter a valid batch name.');
      return;
    }
    if (isNaN(qty) || qty <= 0) {
      setBatchError('Please enter a positive initial quantity.');
      return;
    }

    setIsCreatingBatch(true);
    setBatchError(null);

    try {
      const created = await createBatch({
        name: name,
        batch_type: newBatchType,
        initial_quantity: qty,
        current_quantity: qty,
        status: 'Active'
      });
      
      if (onBatchCreated) onBatchCreated(created);
      setShowBatchModal(false);
      setNewBatchName('');
      setNewBatchQty(500);
    } catch (err) {
      console.error('Failed to create batch:', err);
      setBatchError('Failed to create batch. Please try again.');
    } finally {
      setIsCreatingBatch(false);
    }
  };

  const handleOpenLogModal = async (batch) => {
    setSelectedBatch(batch);
    setShowLogModal(true);
    setLoadingLogs(true);
    try {
      const logs = await fetchLogs(batch.id);
      setActiveLogs(logs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleAddLog = async (e) => {
    e.preventDefault();
    if (!selectedBatch) return;

    try {
      const newLog = await addDailyLog(selectedBatch.id, {
        batch_id: selectedBatch.id,
        mortality_count: parseInt(mortality, 10),
        feed_consumed_kg: parseFloat(feedKg),
        water_consumed_l: parseFloat(waterL),
        notes: logNotes
      });
      
      setActiveLogs([newLog, ...activeLogs]);
      if (onLogAdded) onLogAdded(selectedBatch.id, newLog);
      
      // Reset log form
      setMortality(0);
      setFeedKg(0);
      setWaterL(0);
      setLogNotes('');
      setShowLogModal(false);
    } catch (err) {
      console.error('Failed to add daily log:', err);
    }
  };

  const getBatchIcon = (type) => {
    switch (type) {
      case 'Poultry': return <Feather className="w-4 h-4 text-amber-400" />;
      case 'Crops': return <Wheat className="w-4 h-4 text-emerald-400" />;
      case 'Livestock': return <Beef className="w-4 h-4 text-rose-400" />;
      default: return <Layers className="w-4 h-4 text-agri-400" />;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Top Bar with Create Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-agri-800/40">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-agri-950 border border-agri-800 rounded-xl text-agri-400">
            <Layers className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold font-display text-white">Batch Management & Resource Telemetry</h1>
            <p className="text-sm text-slate-300">Track current inventory, daily mortality, feed & water consumption</p>
          </div>
        </div>

        <button
          onClick={() => setShowBatchModal(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-agri-600 to-emerald-500 hover:from-agri-500 hover:to-emerald-400 text-white font-bold text-sm shadow-lg shadow-agri-600/30 transition-all self-start sm:self-auto"
        >
          <Plus className="w-5 h-5" />
          <span>Add New Batch</span>
        </button>
      </div>

      {/* Batches Table Grid */}
      <div className="glass-panel rounded-2xl border border-agri-800/40 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-darkbg/90 border-b border-agri-900 text-slate-400 text-xs uppercase font-bold tracking-wider">
                <th className="py-4 px-6">Batch Identifier</th>
                <th className="py-4 px-6">Category</th>
                <th className="py-4 px-6">Current Stock</th>
                <th className="py-4 px-6">Initial Stock</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-agri-900/50">
              {batches.map((batch) => {
                const healthIndex = Math.round((batch.current_quantity / batch.initial_quantity) * 100);
                return (
                  <tr key={batch.id} className="hover:bg-darkcard/50 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-100">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-darkbg rounded-lg border border-agri-900">
                          {getBatchIcon(batch.batch_type)}
                        </div>
                        <span>{batch.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-2.5 py-1 rounded bg-darkbg text-slate-300 border border-agri-950 font-medium text-xs">
                        {batch.batch_type}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-bold text-emerald-400">
                      {batch.current_quantity} <span className="text-xs text-slate-400 font-normal">units</span>
                    </td>
                    <td className="py-4 px-6 text-slate-400">
                      {batch.initial_quantity}
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                        {batch.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => handleOpenLogModal(batch)}
                        className="px-3 py-1.5 rounded-lg bg-darkbg hover:bg-darkborder border border-agri-900 text-agri-400 hover:text-agri-300 font-semibold text-xs transition-all"
                      >
                        Log Daily Telemetry
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* New Batch Creation Modal */}
      {showBatchModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-agri-700/60 space-y-5 animate-fadeIn">
            <div className="flex items-center justify-between pb-3 border-b border-agri-900">
              <h3 className="text-lg font-bold font-display text-white">Create New Batch</h3>
              <button onClick={() => setShowBatchModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBatch} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">Batch Name</label>
                <input
                  type="text"
                  required
                  value={newBatchName}
                  onChange={(e) => setNewBatchName(e.target.value)}
                  placeholder="e.g. Broiler Flock Section D"
                  className="w-full bg-darkbg border border-agri-900 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-agri-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">Target Type</label>
                <select
                  value={newBatchType}
                  onChange={(e) => setNewBatchType(e.target.value)}
                  className="w-full bg-darkbg border border-agri-900 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-agri-500"
                >
                  <option value="Poultry">Poultry 🐔</option>
                  <option value="Crops">Crops 🌾</option>
                  <option value="Livestock">Livestock 🐮</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">Initial Quantity / Count</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={newBatchQty}
                  onChange={(e) => setNewBatchQty(e.target.value)}
                  className="w-full bg-darkbg border border-agri-900 rounded-xl px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-agri-500"
                />
              </div>

              {batchError && (
                <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  <span>{batchError}</span>
                </div>
              )}

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowBatchModal(false)}
                  className="px-4 py-2 rounded-xl bg-darkbg text-slate-300 text-xs font-semibold hover:bg-darkborder"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingBatch}
                  className="px-5 py-2 rounded-xl bg-agri-600 hover:bg-agri-500 text-white text-xs font-bold shadow-md shadow-agri-600/30 flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isCreatingBatch ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <span>Create Batch</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Daily Telemetry Modal */}
      {showLogModal && selectedBatch && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-xl p-6 rounded-2xl border border-agri-700/60 space-y-5 animate-fadeIn max-h-[90vh] overflow-y-auto">
            
            <div className="flex items-center justify-between pb-3 border-b border-agri-900">
              <div>
                <h3 className="text-lg font-bold font-display text-white">{selectedBatch.name}</h3>
                <p className="text-xs text-slate-400">Log daily mortality, feed intake, and hydration telemetry</p>
              </div>
              <button onClick={() => setShowLogModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Daily Log Form */}
            <form onSubmit={handleAddLog} className="space-y-4 bg-darkbg p-4 rounded-xl border border-agri-950">
              <h4 className="text-xs font-bold uppercase tracking-wider text-agri-400">New Daily Log Entry</h4>
              
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 mb-1 flex items-center gap-1">
                    <Activity className="w-3.5 h-3.5 text-rose-400" /> Mortality
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={mortality}
                    onChange={(e) => setMortality(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-agri-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-300 mb-1 flex items-center gap-1">
                    <Utensils className="w-3.5 h-3.5 text-amber-400" /> Feed (kg)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={feedKg}
                    onChange={(e) => setFeedKg(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-agri-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-300 mb-1 flex items-center gap-1">
                    <Droplets className="w-3.5 h-3.5 text-cyan-400" /> Water (L)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={waterL}
                    onChange={(e) => setWaterL(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-agri-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-300 mb-1">Notes / Behavioral Observation</label>
                <input
                  type="text"
                  value={logNotes}
                  onChange={(e) => setLogNotes(e.target.value)}
                  placeholder="e.g. Normal appetite, clear drinking water intake..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-agri-500"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-agri-600 hover:bg-agri-500 text-white text-xs font-bold shadow-md shadow-agri-600/30"
                >
                  Save Daily Log
                </button>
              </div>
            </form>

            {/* Existing Logs List */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Historical Telemetry Logs</h4>
              {loadingLogs ? (
                <div className="text-center py-4 text-slate-400 text-xs flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-agri-400" />
                  <span>Loading telemetry...</span>
                </div>
              ) : activeLogs.length === 0 ? (
                <p className="text-xs text-slate-400 italic text-center py-4">No daily logs recorded yet.</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {activeLogs.map((log) => (
                    <div key={log.id} className="bg-darkbg p-3 rounded-xl border border-agri-950 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-slate-200">{log.log_date}</span>
                        {log.notes && <p className="text-slate-400 mt-0.5">{log.notes}</p>}
                      </div>
                      <div className="flex items-center gap-3 font-semibold">
                        <span className="text-rose-400">-{log.mortality_count} mortality</span>
                        <span className="text-amber-400">{log.feed_consumed_kg} kg feed</span>
                        <span className="text-cyan-400">{log.water_consumed_l} L water</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
