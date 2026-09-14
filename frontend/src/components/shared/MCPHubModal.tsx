import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, Play, Terminal, X } from 'lucide-react';
import { getMCPServers, executeMCPTool } from '@/lib/api';

interface MCPHubModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MCPHubModal: React.FC<MCPHubModalProps> = ({ isOpen, onClose }) => {
  const [servers, setServers] = useState<any[]>([]);
  const [selectedServer, setSelectedServer] = useState<any>(null);
  const [selectedTool, setSelectedTool] = useState('');
  const [toolOutput, setToolOutput] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      getMCPServers()
        .then((data) => {
          setServers(data);
          if (data.length > 0) {
            setSelectedServer(data[0]);
            if (data[0].available_tools?.length > 0) {
              setSelectedTool(data[0].available_tools[0]);
            }
          }
        })
        .catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleTestTool = async () => {
    if (!selectedServer || !selectedTool) return;
    setIsExecuting(true);
    try {
      const res = await executeMCPTool(selectedServer.name, selectedTool, { test_param: "sample_value" });
      setToolOutput(res);
    } catch (e) {
      setToolOutput({ error: "Failed to execute tool" });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 text-slate-100 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-fade-in">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2">
            <Cpu className="h-5 w-5 text-emerald-400" />
            <h3 className="text-sm font-extrabold text-white">Model Context Protocol (MCP) Server Hub</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              7 Servers Connected
            </span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="grid grid-cols-1 md:grid-cols-12 flex-1 overflow-hidden">
          {/* Server List (5 cols) */}
          <div className="md:col-span-5 border-r border-slate-800 p-3 space-y-2 overflow-y-auto bg-slate-900">
            {servers.map((s, idx) => (
              <div
                key={idx}
                onClick={() => {
                  setSelectedServer(s);
                  if (s.available_tools?.length > 0) setSelectedTool(s.available_tools[0]);
                  setToolOutput(null);
                }}
                className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                  selectedServer?.name === s.name
                    ? 'border-emerald-500 bg-emerald-500/10 text-white'
                    : 'border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-emerald-400">{s.display_name}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 uppercase font-mono">
                    {s.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2">{s.description}</p>
              </div>
            ))}
          </div>

          {/* Tool Inspector (7 cols) */}
          <div className="md:col-span-7 p-5 flex flex-col justify-between overflow-y-auto bg-slate-950/40">
            {selectedServer ? (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-bold text-emerald-400 mb-1">{selectedServer.display_name}</h4>
                  <p className="text-xs text-slate-300">{selectedServer.description}</p>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-1">Available MCP Tools:</label>
                  <select
                    value={selectedTool}
                    onChange={(e) => setSelectedTool(e.target.value)}
                    className="w-full text-xs p-2 bg-slate-900 border border-slate-700 rounded-xl text-slate-200"
                  >
                    {selectedServer.available_tools?.map((tool: string, tIdx: number) => (
                      <option key={tIdx} value={tool}>
                        {tool}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleTestTool}
                  disabled={isExecuting}
                  className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition-all"
                >
                  <Play className="h-3.5 w-3.5" />
                  <span>{isExecuting ? 'Executing Tool...' : 'Execute Tool Call'}</span>
                </button>

                {toolOutput && (
                  <div className="mt-3">
                    <span className="text-xs font-mono text-slate-400 block mb-1 flex items-center space-x-1">
                      <Terminal className="h-3.5 w-3.5 text-emerald-400" />
                      <span>Tool Execution Result:</span>
                    </span>
                    <pre className="p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono text-emerald-300 overflow-x-auto">
                      {JSON.stringify(toolOutput, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};
