import React from 'react';
import { 
  X, CheckCircle2, AlertTriangle, ShieldAlert, Pill, 
  Utensils, Droplets, Stethoscope, Calendar, Share2, Printer 
} from 'lucide-react';

export default function DiagnosticModal({ diagnostic, onClose }) {
  if (!diagnostic) return null;

  const { detected_issue, severity, confidence_score, treatment_plan, image_url, created_at } = diagnostic;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-3xl p-6 sm:p-8 rounded-2xl border border-agri-700/60 space-y-6 max-h-[90vh] overflow-y-auto animate-fadeIn shadow-2xl">
        
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-agri-900">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-agri-400 uppercase tracking-wider mb-1">
              <Stethoscope className="w-4 h-4 text-emerald-400" />
              <span>Diagnostic Pathology Report</span>
            </div>
            <h2 className="text-2xl font-extrabold font-display text-white">{detected_issue}</h2>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
              <Calendar className="w-3.5 h-3.5" />
              <span>Report Date: {created_at ? new Date(created_at).toLocaleDateString() : 'Today'}</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="p-2 rounded-lg bg-darkbg hover:bg-darkborder text-slate-300 hover:text-white border border-agri-900"
              title="Print Action Card"
            >
              <Printer className="w-4 h-4" />
            </button>
            <button onClick={onClose} className="p-2 rounded-lg bg-darkbg hover:bg-darkborder text-slate-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Confidence & Severity Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-darkbg p-4 rounded-xl border border-agri-950 space-y-2">
            <div className="flex justify-between text-xs font-bold">
              <span className="text-slate-400">Pathology Confidence Score</span>
              <span className="text-emerald-400 font-extrabold">{confidence_score}%</span>
            </div>
            <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
              <div
                className="bg-gradient-to-r from-emerald-500 to-agri-400 h-full rounded-full"
                style={{ width: `${confidence_score}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-darkbg p-4 rounded-xl border border-agri-950 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase">Severity Level</span>
              <p className="text-sm font-extrabold text-white mt-0.5">{severity}</p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              severity === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
              severity === 'High' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
              'bg-emerald-950 text-emerald-400 border border-emerald-800'
            }`}>
              {severity} Priority
            </span>
          </div>
        </div>

        {/* Image Preview if available */}
        {image_url && (
          <div className="rounded-xl overflow-hidden border border-agri-900 max-h-60 bg-darkbg flex justify-center">
            <img src={image_url} alt="Diagnostic Specimen" className="object-contain max-h-60 w-full" />
          </div>
        )}

        {/* Symptoms */}
        {treatment_plan?.symptom_analysis && (
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Key Visual Symptoms</h3>
            <div className="flex flex-wrap gap-2">
              {treatment_plan.symptom_analysis.map((symptom, i) => (
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
            <span>Immediate Actions Required</span>
          </h3>
          <ul className="space-y-1.5">
            {treatment_plan?.immediate_actions?.map((act, i) => (
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
            <span>Recommended Medication & Input Protocols</span>
          </h3>
          <ul className="space-y-1.5">
            {treatment_plan?.medication_or_inputs?.map((med, i) => (
              <li key={i} className="text-xs text-slate-200 bg-amber-950/30 p-2.5 rounded-lg border border-amber-900/40 flex items-start gap-2">
                <span className="font-bold text-amber-400">•</span>
                <span>{med}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Resource Telemetry Recommendations */}
        {treatment_plan?.resource_adjustments && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-darkbg p-4 rounded-xl border border-amber-900/40 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                <Utensils className="w-4 h-4" />
                <span>Feed Adjustment</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {treatment_plan.resource_adjustments.feed_recommendation}
              </p>
            </div>

            <div className="bg-darkbg p-4 rounded-xl border border-cyan-900/40 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                <Droplets className="w-4 h-4" />
                <span>Water Adjustment</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {treatment_plan.resource_adjustments.water_recommendation}
              </p>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
