import React, { useState } from 'react';
import { 
  UploadCloud, Stethoscope, Sparkles, Feather, Wheat, Beef, 
  CheckCircle2, AlertTriangle, ShieldAlert, Pill, RefreshCw, 
  Droplets, Utensils, FileText, ArrowRight, Camera 
} from 'lucide-react';
import { submitAIDiagnosis } from '../api';

export default function Diagnostics({ batches, onDiagnosticCreated }) {
  const [targetType, setTargetType] = useState('Poultry');
  const [selectedBatchId, setSelectedBatchId] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [notes, setNotes] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState(null);
  const [error, setError] = useState(null);

  const targetTypes = [
    { id: 'Poultry', label: 'Poultry 🐔', icon: Feather, color: 'hover:border-amber-500' },
    { id: 'Crops', label: 'Crops 🌾', icon: Wheat, color: 'hover:border-emerald-500' },
    { id: 'Livestock', label: 'Livestock 🐮', icon: Beef, color: 'hover:border-rose-500' },
  ];

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) {
      setError('Please upload a specimen or leaf photo to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('batch_type', targetType);
    if (selectedBatchId) formData.append('batch_id', selectedBatchId);
    formData.append('notes', notes);

    try {
      const result = await submitAIDiagnosis(formData);
      setDiagnosticResult(result);
      if (onDiagnosticCreated) onDiagnosticCreated(result);
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError('AI diagnostic engine failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'Critical':
        return <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-rose-950 text-rose-400 border border-rose-800 animate-pulse flex items-center gap-1.5"><ShieldAlert className="w-4 h-4"/> CRITICAL SEVERITY</span>;
      case 'High':
        return <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-amber-950 text-amber-400 border border-amber-800 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4"/> HIGH RISK</span>;
      case 'Medium':
        return <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-yellow-950 text-yellow-400 border border-yellow-800">MEDIUM RISK</span>;
      default:
        return <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-950 text-emerald-400 border border-emerald-800">LOW RISK</span>;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-agri-800/40">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-agri-950 border border-agri-800 rounded-xl text-agri-400">
            <Stethoscope className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold font-display text-white">Multimodal AI Health Diagnostic Engine</h1>
            <p className="text-sm text-slate-300">Powered by Gemini 2.5 Flash • Instant pathogen detection & actionable treatment protocol</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Form Controls & Image Upload (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-2xl space-y-5">
            
            {/* Target Type Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                1. Select Target Category
              </label>
              <div className="grid grid-cols-3 gap-2">
                {targetTypes.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => {
                      setTargetType(t.id);
                      setSelectedBatchId('');
                    }}
                    className={`py-3 px-2 rounded-xl text-xs font-bold transition-all border flex flex-col items-center gap-1.5 ${
                      targetType === t.id
                        ? 'bg-agri-800 text-white border-agri-500 shadow-md'
                        : 'bg-darkbg text-slate-400 border-agri-950 hover:bg-darkborder'
                    }`}
                  >
                    <span className="text-base">{t.label.split(' ')[1]}</span>
                    <span>{t.id}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Batch Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                2. Associate with Active Batch (Optional)
              </label>
              <select
                value={selectedBatchId}
                onChange={(e) => setSelectedBatchId(e.target.value)}
                className="w-full bg-darkbg border border-agri-900 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-agri-500"
              >
                <option value="">-- Unassigned (General Inspection) --</option>
                {batches
                  .filter((b) => b.batch_type === targetType)
                  .map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} ({b.current_quantity} units)
                    </option>
                  ))}
              </select>
            </div>

            {/* Image Upload Area */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                3. Upload Specimen / Symptom Photo
              </label>
              
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${
                  imagePreview
                    ? 'border-agri-500 bg-agri-950/20'
                    : 'border-agri-900 hover:border-agri-600 bg-darkbg/50'
                }`}
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
                />

                {imagePreview ? (
                  <div className="space-y-3">
                    <img
                      src={imagePreview}
                      alt="Uploaded Specimen"
                      className="max-h-56 mx-auto rounded-lg object-contain border border-agri-800 shadow-md"
                    />
                    <p className="text-xs text-agri-400 font-medium">Click or drag another image to replace</p>
                  </div>
                ) : (
                  <div className="space-y-3 py-4">
                    <div className="w-12 h-12 rounded-full bg-agri-950 border border-agri-800 flex items-center justify-center mx-auto text-agri-400">
                      <Camera className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-200">Drag & drop photo here</p>
                      <p className="text-xs text-slate-400 mt-1">or click to browse from device</p>
                    </div>
                    <span className="inline-block text-[10px] px-2.5 py-1 bg-slate-900 text-slate-400 rounded-full border border-slate-800">
                      Supports JPG, PNG, WEBP (Up to 10MB)
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* User Notes */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                4. Field Symptoms / Notes (Optional)
              </label>
              <textarea
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Observed 5 birds with lethargy and ruffled feathers since morning..."
                className="w-full bg-darkbg border border-agri-900 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-agri-500 placeholder-slate-600"
              />

              {/* Quick Field Symptom Helper Chips */}
              <div className="mt-2.5 space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-400">Quick Observation Presets:</span>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { label: '🌿 Healthy Check', note: 'Healthy specimen routine inspection' },
                    { label: '🟡 Yellowing Leaves', note: 'Yellowing leaves and chlorosis at tips' },
                    { label: '🐛 Armyworm Holes', note: 'Whorl leaf holes and caterpillar damage' },
                    { label: '🐔 Bloody Droppings', note: 'Bloody droppings and pale comb' },
                    { label: '😮 Gasping / Coughing', note: 'Respiratory gasping, coughing and nasal discharge' },
                    { label: '🐮 Udder Swelling', note: 'Udder quarter swelling and milk clots' },
                  ].map((chip, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setNotes(chip.note)}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-darkbg hover:bg-agri-950 border border-agri-900 text-slate-300 hover:text-white transition-all"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Run AI Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-agri-600 to-emerald-500 hover:from-agri-500 hover:to-emerald-400 text-white font-bold text-sm shadow-lg shadow-agri-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Gemini 2.5 Flash Inspecting Image...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Run Multimodal AI Diagnostics</span>
                </>
              )}
            </button>

          </form>
        </div>

        {/* Right Column: Diagnostic Results Dashboard (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {loading ? (
            <div className="glass-panel p-12 rounded-2xl border border-agri-800/40 text-center space-y-6">
              <div className="relative w-20 h-20 mx-auto">
                <div className="absolute inset-0 rounded-full border-4 border-agri-500/20 border-t-agri-500 animate-spin"></div>
                <div className="absolute inset-3 rounded-full bg-agri-950 flex items-center justify-center text-agri-400">
                  <Sparkles className="w-8 h-8 animate-pulse" />
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold font-display text-white">Analyzing Specimen Micro-Features</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Gemini 2.5 Flash vision model is inspecting leaf/skin tissue patterns, lesion geometry, and physical symptom markers...
                </p>
              </div>
            </div>
          ) : diagnosticResult ? (
            <div className="glass-panel p-6 rounded-2xl space-y-6 border border-agri-700/60 animate-fadeIn">
              
              {/* Header: Issue & Severity */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-agri-900">
                <div>
                  <div className="flex items-center gap-2 text-xs font-bold text-agri-400 uppercase tracking-wider mb-1">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>AI Pathology Inspection Result</span>
                  </div>
                  <h2 className="text-2xl font-extrabold font-display text-white">{diagnosticResult.detected_issue}</h2>
                </div>
                {getSeverityBadge(diagnosticResult.severity)}
              </div>

              {/* Confidence Meter Bar */}
              <div className="space-y-2 bg-darkbg p-4 rounded-xl border border-agri-950">
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-slate-400">AI Diagnostic Confidence Score</span>
                  <span className="text-emerald-400">{diagnosticResult.confidence_score}%</span>
                </div>
                <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                  <div
                    className="bg-gradient-to-r from-emerald-500 to-agri-400 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${diagnosticResult.confidence_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Identified Symptoms list */}
              {diagnosticResult.treatment_plan?.symptom_analysis && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Visual Symptoms Identified</h3>
                  <div className="flex flex-wrap gap-2">
                    {diagnosticResult.treatment_plan.symptom_analysis.map((symptom, i) => (
                      <span key={i} className="text-xs px-3 py-1 bg-darkbg text-slate-200 rounded-lg border border-agri-900 font-medium">
                        • {symptom}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Immediate Actions */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Immediate Action Plan</span>
                </h3>
                <ul className="space-y-1.5">
                  {diagnosticResult.treatment_plan?.immediate_actions?.map((act, i) => (
                    <li key={i} className="text-xs text-slate-200 bg-rose-950/30 p-2.5 rounded-lg border border-rose-900/40 flex items-start gap-2">
                      <span className="font-bold text-rose-400">{i + 1}.</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Medications & Inputs */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                  <Pill className="w-4 h-4" />
                  <span>Recommended Treatment / Medications</span>
                </h3>
                <ul className="space-y-1.5">
                  {diagnosticResult.treatment_plan?.medication_or_inputs?.map((med, i) => (
                    <li key={i} className="text-xs text-slate-200 bg-amber-950/30 p-2.5 rounded-lg border border-amber-900/40 flex items-start gap-2">
                      <span className="font-bold text-amber-400">•</span>
                      <span>{med}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Resource Adjustments Grid (Feed & Water) */}
              {diagnosticResult.treatment_plan?.resource_adjustments && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="bg-darkbg p-4 rounded-xl border border-amber-900/40 space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                      <Utensils className="w-4 h-4" />
                      <span>Feed Telemetry Adjustment</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {diagnosticResult.treatment_plan.resource_adjustments.feed_recommendation}
                    </p>
                  </div>

                  <div className="bg-darkbg p-4 rounded-xl border border-cyan-900/40 space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                      <Droplets className="w-4 h-4" />
                      <span>Water Telemetry Adjustment</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {diagnosticResult.treatment_plan.resource_adjustments.water_recommendation}
                    </p>
                  </div>
                </div>
              )}

            </div>
          ) : (
            /* Idle Placeholder */
            <div className="glass-panel p-12 rounded-2xl border border-agri-800/40 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-agri-950 border border-agri-800 flex items-center justify-center mx-auto text-agri-400">
                <Sparkles className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-bold font-display text-white">Ready for Visual Diagnostics</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                  Upload an image of your crop leaf, poultry flock, or livestock specimen to receive an instant multimodal AI pathology report.
                </p>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
