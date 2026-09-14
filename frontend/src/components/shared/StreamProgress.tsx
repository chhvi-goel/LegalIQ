import React from 'react';
import { Loader2, CheckCircle2, Cpu, ShieldCheck } from 'lucide-react';

interface StreamProgressProps {
  currentStage: string;
  stageMessage: string;
}

export const StreamProgress: React.FC<StreamProgressProps> = ({ currentStage, stageMessage }) => {
  const stages = [
    'Input Guardrails',
    'Intent Classification',
    'Searching Legal Knowledge',
    'Ranking Evidence',
    'Citation Validation',
    'Generating Response'
  ];

  const getStageIndex = (stage: string) => {
    return stages.findIndex(s => s.toLowerCase() === stage.toLowerCase());
  };

  const currentIndex = getStageIndex(currentStage);

  return (
    <div className="w-full bg-slate-900/90 text-white rounded-xl p-4 border border-sky-500/30 shadow-xl my-4 backdrop-blur-md transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-4 w-4 text-sky-400 animate-spin" />
          <span className="text-xs font-semibold uppercase tracking-wider text-sky-400">
            Multi-Agent Orchestration Active
          </span>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {currentIndex >= 0 ? `${currentIndex + 1} / ${stages.length}` : 'Processing'}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-800 rounded-full h-1.5 mb-3 overflow-hidden">
        <div
          className="bg-gradient-to-r from-sky-500 to-indigo-500 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${Math.max(15, ((currentIndex + 1) / stages.length) * 100)}%` }}
        />
      </div>

      <div className="text-sm font-medium text-slate-200 flex items-center justify-between">
        <span>{stageMessage || 'Initializing legal pipeline...'}</span>
        <span className="text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-mono border border-sky-800/50">
          {currentStage}
        </span>
      </div>
    </div>
  );
};
