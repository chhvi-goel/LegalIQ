import React from 'react';
import { Info, AlertTriangle, BookOpen, CheckCircle, Scale } from 'lucide-react';

interface RichResponseRendererProps {
  content: string;
}

export const RichResponseRenderer: React.FC<RichResponseRendererProps> = ({ content }) => {
  if (!content) return null;

  // Split lines and parse blocks
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];

  let inList = false;
  let listItems: string[] = [];

  const flushList = (keyPrefix: string) => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`${keyPrefix}_ul`} className="space-y-1.5 my-2 pl-2">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex items-start space-x-2 text-xs leading-relaxed text-slate-200">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
              <span>{renderInlineFormatting(item)}</span>
            </li>
          ))}
        </ul>
      );
      listItems = [];
    }
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushList(`flush_${idx}`);
      return;
    }

    // Headings (e.g. #, ##, ### or bold titles)
    if (trimmed.startsWith('#') || (trimmed.startsWith('**') && trimmed.endsWith('**') && trimmed.length < 60)) {
      flushList(`h_flush_${idx}`);
      const text = trimmed.replace(/^#+\s*/, '').replace(/^\*\*/, '').replace(/\*\*$/, '').trim();
      elements.push(
        <div key={idx} className="mt-3 mb-2 flex items-center space-x-2 pb-1 border-b border-slate-700/60">
          <Scale className="h-4 w-4 text-indigo-400 shrink-0" />
          <h4 className="text-xs font-extrabold text-indigo-300 uppercase tracking-wide">{text}</h4>
        </div>
      );
      return;
    }

    // Warnings / Alerts
    if (trimmed.toLowerCase().includes('warning') || trimmed.toLowerCase().includes('caution') || trimmed.startsWith('> [!WARNING]')) {
      flushList(`warn_flush_${idx}`);
      const text = trimmed.replace(/^>\s*\[!WARNING\]/i, '').replace(/^warning:/i, '').trim();
      elements.push(
        <div key={idx} className="my-2 p-3 bg-amber-950/40 border-l-4 border-amber-500 rounded-r-xl flex items-start space-x-2.5 text-xs text-amber-200">
          <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
          <div>{renderInlineFormatting(text)}</div>
        </div>
      );
      return;
    }

    // Important Notes / Statutory Highlights
    if (trimmed.toLowerCase().includes('note:') || trimmed.startsWith('> [!NOTE]') || trimmed.startsWith('> [!IMPORTANT]')) {
      flushList(`note_flush_${idx}`);
      const text = trimmed.replace(/^>\s*\[!(NOTE|IMPORTANT)\]/i, '').replace(/^note:/i, '').trim();
      elements.push(
        <div key={idx} className="my-2 p-3 bg-indigo-950/40 border-l-4 border-indigo-500 rounded-r-xl flex items-start space-x-2.5 text-xs text-indigo-200">
          <Info className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
          <div>{renderInlineFormatting(text)}</div>
        </div>
      );
      return;
    }

    // Bullet or Numbered Lists
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || /^\d+\.\s/.test(trimmed)) {
      const itemText = trimmed.replace(/^[-*]\s*/, '').replace(/^\d+\.\s*/, '');
      listItems.push(itemText);
      return;
    }

    // Standard Paragraph
    flushList(`p_flush_${idx}`);
    elements.push(
      <p key={idx} className="text-xs leading-relaxed text-slate-200 my-1.5">
        {renderInlineFormatting(trimmed)}
      </p>
    );
  });

  flushList('final_flush');

  return <div className="space-y-1">{elements}</div>;
};

// Inline helper to convert Section/Act references into chips & bold text into clean tags
function renderInlineFormatting(text: string): React.ReactNode {
  // Replace section references with badges
  const parts = text.split(/(\*\*[^*]+\*\*|Section \d+[A-Z]*|Article \d+|BNS 2023|IPC|BNSS|CrPC)/gi);

  return parts.map((part, i) => {
    if (!part) return null;
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-extrabold text-slate-100">{part.slice(2, -2)}</strong>;
    }
    if (/^(Section \d+[A-Z]*|Article \d+|BNS 2023|IPC|BNSS|CrPC)/i.test(part)) {
      return (
        <span key={i} className="inline-flex items-center px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 text-[10px] font-mono font-bold mx-0.5">
          {part}
        </span>
      );
    }
    return part;
  });
}
