import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Mic, Download, ShieldAlert, Sparkles, CheckCircle,
  Globe, PhoneCall, History, Plus, Trash2, MessageSquare, ChevronLeft,
  Pin, Edit3, Search, FileText, Share2, HelpCircle
} from 'lucide-react';
import {
  subscribeChatStream, generatePDFReport, downloadReportFile,
  fetchUserSessions, fetchSessionHistory, deleteSession,
  pinSession, renameSession, exportSession, searchSessions
} from '@/lib/api';
import { StreamProgress } from '../shared/StreamProgress';
import { RichResponseRenderer } from '../shared/RichResponseRenderer';

interface CitizenChatProps {
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
}

export const CitizenChat: React.FC<CitizenChatProps> = ({ sessionId, setSessionId }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamStage, setStreamStage] = useState('');
  const [streamMessage, setStreamMessage] = useState('');
  const [activePipeline, setActivePipeline] = useState<string>('');
  const [currentResponse, setCurrentResponse] = useState('');
  const [currentMetadata, setCurrentMetadata] = useState<any>(null);
  const [selectedLang, setSelectedLang] = useState('English');
  const [isRecording, setIsRecording] = useState(false);
  const [showEmergency, setShowEmergency] = useState(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  // Sidebar & Search State
  const [sessions, setSessions] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse, streamStage]);

  // Load sessions list
  const loadSessions = async () => {
    try {
      if (searchQuery.trim()) {
        const data = await searchSessions(searchQuery);
        setSessions(data);
      } else {
        const data = await fetchUserSessions('citizen');
        setSessions(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadSessions();
  }, [sessionId, searchQuery]);

  // Restore history when session ID changes or on page load
  useEffect(() => {
    if (sessionId) {
      handleSelectSession(sessionId);
    }
  }, [sessionId]);

  const handleSelectSession = async (sId: string) => {
    setSessionId(sId);
    try {
      const history = await fetchSessionHistory(sId);
      const formatted = history.map((h: any) => ({
        id: `msg_${h.id}`,
        role: h.role,
        content: h.content,
        confidence_score: h.confidence_score,
        citations: h.citations || [],
        pipeline_used: h.pipeline_used,
        timestamp: new Date(h.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }));
      setMessages(formatted);
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewChat = () => {
    setSessionId(null);
    setMessages([]);
    setCurrentResponse('');
    setCurrentMetadata(null);
  };

  const handlePin = async (sId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await pinSession(sId);
      loadSessions();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRename = async (sId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!editingTitle.trim()) return;
    try {
      await renameSession(sId, editingTitle);
      setEditingSessionId(null);
      loadSessions();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteSession = async (sId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteSession(sId);
      if (sessionId === sId) {
        handleNewChat();
      }
      loadSessions();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExportChat = async (sId: string, format: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await exportSession(sId, format);
    } catch (err) {
      console.error(err);
    }
  };

  // Dynamic Suggestion Cards
  const getDynamicSuggestions = () => {
    if (messages.length === 0) {
      return [
        { title: "Cyber Fraud Recovery", prompt: "I was scammed online and lost ₹50,000 via UPI. What legal action can I take under Section 66D IT Act?" },
        { title: "Tenant Deposit Dispute", prompt: "My landlord refuses to return my ₹60,000 security deposit without 30 days written notice." },
        { title: "Defective Laptop Replacement", prompt: "Bought a laptop with a faulty motherboard, seller refuses refund. How to file on e-Daakhil?" },
        { title: "Illegal Detention Rights", prompt: "What are my legal rights if someone is detained without a warrant under BNSS 2023?" }
      ];
    }
    return [
      { title: "Statutory Notice", prompt: "Can you help me draft a formal 15-day statutory legal notice for this issue?" },
      { title: "Relevant Landmark Judgments", prompt: "What are the key Supreme Court precedents governing this type of dispute?" },
      { title: "Limitation Period", prompt: "What is the limitation period for filing a complaint in this matter?" }
    ];
  };

  const handleSend = async (customQuery?: string) => {
    const textToSend = customQuery || query;
    if (!textToSend.trim() || isLoading) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    if (!customQuery) setQuery('');
    setIsLoading(true);
    setCurrentResponse('');
    setCurrentMetadata(null);
    setStreamStage('Initializing Orchestrator');

    await subscribeChatStream(
      textToSend,
      sessionId,
      'citizen',
      (stageData) => {
        setStreamStage(stageData.stage);
        setStreamMessage(stageData.message);
        if (stageData.pipeline) setActivePipeline(stageData.pipeline);
      },
      (meta) => {
        setCurrentMetadata(meta);
        if (meta.emergency_data?.is_emergency) {
          setShowEmergency(true);
        }
      },
      (tokenChunk) => {
        setCurrentResponse(prev => prev + tokenChunk);
      },
      (doneData) => {
        if (doneData.session_id) {
          setSessionId(doneData.session_id);
          loadSessions();
        }
        setIsLoading(false);
        setStreamStage('');
      },
      (errorData) => {
        setIsLoading(false);
        setStreamStage('');
        setMessages(prev => [
          ...prev,
          {
            id: `err_${Date.now()}`,
            role: 'assistant',
            content: errorData.message || "I'm having trouble accessing the legal knowledge base right now. Please try again in a moment.",
            confidence_score: 0,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
      }
    );
  };

  useEffect(() => {
    if (!isLoading && currentResponse) {
      setMessages(prev => [
        ...prev,
        {
          id: `asst_${Date.now()}`,
          role: 'assistant',
          content: currentResponse,
          confidence_score: currentMetadata?.confidence_score || 1.0,
          citations: currentMetadata?.citations || [],
          action_steps: currentMetadata?.action_steps || [],
          guided_questions: currentMetadata?.guided_questions || [],
          pipeline_used: currentMetadata?.pipeline_used || activePipeline || 'direct_ai',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      setCurrentResponse('');
    }
  }, [isLoading, currentResponse, currentMetadata]);

  const handleDownloadPDF = async () => {
    if (!sessionId && messages.length === 0) {
      alert("No conversation available to generate PDF report.");
      return;
    }
    setIsGeneratingPdf(true);
    try {
      const targetSessionId = sessionId || `session_temp_${Date.now()}`;
      const res = await generatePDFReport(targetSessionId, 'citizen_legal_advice');
      if (res.report_id) {
        await downloadReportFile(res.report_id);
      } else {
        alert("Report generation failed.");
      }
    } catch (e) {
      alert('Failed to generate PDF report.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const toggleVoiceInput = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setTimeout(() => {
        setQuery("What is the legal punishment for online cheating and financial fraud under Bharatiya Nyaya Sanhita?");
        setIsRecording(false);
      }, 2000);
    }
  };

  // Group sessions into Pinned, Today, Yesterday, Older
  const pinnedSessions = sessions.filter(s => s.is_pinned);
  const unpinnedSessions = sessions.filter(s => !s.is_pinned);

  return (
    <div className="flex h-[calc(100vh-65px)] max-w-7xl mx-auto px-2 py-3 overflow-hidden font-sans">
      {/* ChatGPT-Style Sidebar */}
      <div className={`transition-all duration-300 flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 rounded-2xl mr-3 p-3 ${isSidebarOpen ? 'w-72' : 'w-14 items-center'}`}>
        <div className="flex items-center justify-between mb-3 w-full">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors"
            title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
          >
            {isSidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <History className="h-5 w-5" />}
          </button>

          {isSidebarOpen && (
            <button
              onClick={handleNewChat}
              className="flex items-center space-x-1.5 text-xs font-bold px-3 py-1.5 bg-gradient-to-r from-sky-500 to-indigo-600 text-white rounded-xl hover:opacity-90 shadow-md transition-all"
            >
              <Plus className="h-4 w-4" />
              <span>New Chat</span>
            </button>
          )}
        </div>

        {isSidebarOpen ? (
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Search sessions input */}
            <div className="relative mb-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats..."
                className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none text-slate-800 dark:text-slate-200"
              />
              <Search className="h-3.5 w-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1">
              {/* Pinned Section */}
              {pinnedSessions.length > 0 && (
                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-500 flex items-center space-x-1 px-2 mb-1">
                    <Pin className="h-3 w-3" />
                    <span>Pinned ({pinnedSessions.length})</span>
                  </span>
                  {pinnedSessions.map((s) => (
                    <div
                      key={s.id}
                      onClick={() => handleSelectSession(s.id)}
                      className={`group flex items-center justify-between p-2 rounded-xl text-xs cursor-pointer transition-all ${
                        sessionId === s.id
                          ? 'bg-amber-50 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200 font-bold'
                          : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      <div className="flex items-center space-x-2 truncate flex-1">
                        <MessageSquare className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                        <span className="truncate">{s.title}</span>
                      </div>
                      <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={(e) => handlePin(s.id, e)} title="Unpin" className="p-1 hover:text-amber-600">
                          <Pin className="h-3 w-3 fill-amber-500 text-amber-500" />
                        </button>
                        <button onClick={(e) => handleDeleteSession(s.id, e)} title="Delete" className="p-1 hover:text-rose-500">
                          <Trash2 className="h-3 w-3 text-slate-400 hover:text-rose-500" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* All / Recent Sessions */}
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block px-2 mb-1">
                  Recent Conversations ({unpinnedSessions.length})
                </span>
                {unpinnedSessions.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => handleSelectSession(s.id)}
                    className={`group flex items-center justify-between p-2 rounded-xl text-xs cursor-pointer transition-all ${
                      sessionId === s.id
                        ? 'bg-sky-50 dark:bg-sky-950/60 border border-sky-300 dark:border-sky-800 text-sky-800 dark:text-sky-200 font-bold'
                        : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2 truncate flex-1">
                      <MessageSquare className="h-3.5 w-3.5 shrink-0 text-sky-500" />
                      {editingSessionId === s.id ? (
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && handleRename(s.id, e as any)}
                          onClick={(e) => e.stopPropagation()}
                          className="text-xs p-1 bg-white dark:bg-slate-800 border rounded w-full text-slate-900 dark:text-slate-100"
                          autoFocus
                        />
                      ) : (
                        <span className="truncate">{s.title}</span>
                      )}
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={(e) => handlePin(s.id, e)} title="Pin Chat" className="p-1 text-slate-400 hover:text-amber-500">
                        <Pin className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingSessionId(s.id);
                          setEditingTitle(s.title);
                        }}
                        title="Rename Chat"
                        className="p-1 text-slate-400 hover:text-sky-500"
                      >
                        <Edit3 className="h-3 w-3" />
                      </button>
                      <button onClick={(e) => handleExportChat(s.id, 'markdown', e)} title="Export Markdown" className="p-1 text-slate-400 hover:text-emerald-500">
                        <FileText className="h-3 w-3" />
                      </button>
                      <button onClick={(e) => handleDeleteSession(s.id, e)} title="Delete Chat" className="p-1 text-slate-400 hover:text-rose-500">
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={handleNewChat}
            className="p-2.5 bg-sky-500 text-white rounded-xl hover:bg-sky-600 shadow-md mt-2"
            title="Start New Chat"
          >
            <Plus className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Main Chat Workspace Area */}
      <div className="flex-1 flex flex-col h-full max-w-4xl mx-auto overflow-hidden">
        {/* Top Controls Bar */}
        <div className="flex items-center justify-between mb-3 bg-slate-100 dark:bg-slate-900/80 p-2.5 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center space-x-2">
            <Globe className="h-4 w-4 text-sky-500" />
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Language:</span>
            <select
              value={selectedLang}
              onChange={(e) => setSelectedLang(e.target.value)}
              className="text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-2 py-1 font-medium focus:outline-none text-slate-800 dark:text-slate-200"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Marathi">Marathi (मराठी)</option>
              <option value="Tamil">Tamil (தமிழ்)</option>
              <option value="Bengali">Bengali (বাংলা)</option>
            </select>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowEmergency(!showEmergency)}
              className="flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all"
            >
              <ShieldAlert className="h-3.5 w-3.5 animate-pulse" />
              <span>Emergency Helplines</span>
            </button>

            {messages.length > 0 && (
              <button
                onClick={handleDownloadPDF}
                disabled={isGeneratingPdf}
                className="flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-sky-500 text-white hover:bg-sky-600 shadow-sm transition-all disabled:opacity-50"
              >
                <Download className="h-3.5 w-3.5" />
                <span>{isGeneratingPdf ? 'Generating PDF...' : 'Download PDF Advice'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Emergency Drawer */}
        {showEmergency && (
          <div className="mb-3 bg-gradient-to-r from-rose-900/90 to-red-950 text-white p-4 rounded-xl border border-rose-500/40 shadow-xl animate-fade-in">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <PhoneCall className="h-5 w-5 text-rose-400 animate-bounce" />
                <h4 className="font-bold text-sm text-rose-200">Official Indian Legal & Safety Helplines</h4>
              </div>
              <button onClick={() => setShowEmergency(false)} className="text-xs text-rose-300 hover:text-white">
                ✕ Close
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              <div className="bg-rose-950/60 p-2 rounded border border-rose-800/50">
                <span className="text-rose-400 font-bold block">National Emergency</span>
                <span className="text-base font-mono font-bold">112</span>
              </div>
              <div className="bg-rose-950/60 p-2 rounded border border-rose-800/50">
                <span className="text-rose-400 font-bold block">National Cyber Crime</span>
                <span className="text-base font-mono font-bold">1930</span>
              </div>
              <div className="bg-rose-950/60 p-2 rounded border border-rose-800/50">
                <span className="text-rose-400 font-bold block">NALSA Free Legal Aid</span>
                <span className="text-base font-mono font-bold">15100</span>
              </div>
              <div className="bg-rose-950/60 p-2 rounded border border-rose-800/50">
                <span className="text-rose-400 font-bold block">Women Helpline</span>
                <span className="text-base font-mono font-bold">1091</span>
              </div>
            </div>
          </div>
        )}

        {/* Chat Messages Body */}
        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center py-10">
              <div className="h-14 w-14 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white mb-3 shadow-xl shadow-sky-500/20">
                <Sparkles className="h-7 w-7" />
              </div>
              <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100 mb-2">
                LegalIQ AI Intelligence Platform
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-6">
                Ask general or legal questions. The Intelligent Query Orchestrator automatically selects between Direct AI and Legal Intelligence pipelines.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {getDynamicSuggestions().map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(item.prompt)}
                    className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-sky-500 dark:hover:border-sky-500 text-left transition-all group shadow-sm"
                  >
                    <span className="text-xs font-bold text-sky-600 dark:text-sky-400 block mb-1">
                      {item.title}
                    </span>
                    <span className="text-xs text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white line-clamp-2">
                      "{item.prompt}"
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={msg.id || idx}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-center space-x-2 mb-1 text-[11px] text-slate-400">
                <span className="font-semibold">{msg.role === 'user' ? 'You' : 'LegalIQ Assistant'}</span>
                <span>•</span>
                {msg.pipeline_used && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${msg.pipeline_used === 'direct_ai' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'}`}>
                    {msg.pipeline_used === 'direct_ai' ? 'Direct AI' : 'Legal Intelligence RAG'}
                  </span>
                )}
                <span>•</span>
                <span>{msg.timestamp}</span>
              </div>

              <div
                className={`max-w-3xl rounded-2xl p-4 shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-sky-600 text-white rounded-tr-none'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none'
                }`}
              >
                <div className="text-sm leading-relaxed">
                  {msg.role === 'user' ? (
                    msg.content
                  ) : (
                    <RichResponseRenderer content={msg.content} />
                  )}
                </div>

                {msg.role === 'assistant' && (
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 space-y-3">
                    {msg.confidence_score !== undefined && msg.pipeline_used === 'legal_ai' && (
                      <div className="flex items-center space-x-1.5">
                        <ShieldAlert className="h-4 w-4 text-emerald-500" />
                        <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                          Evidence Verification:
                        </span>
                        <span className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                          {Math.round(msg.confidence_score * 100)}% Verified
                        </span>
                      </div>
                    )}

                    {msg.citations && msg.citations.length > 0 && (
                      <div>
                        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                          📚 Legal Citations & Statutory Evidence:
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {msg.citations.map((cit: any, cIdx: number) => (
                            <div key={cIdx} className="bg-slate-50 dark:bg-slate-800/50 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700/60 text-xs">
                              <span className="font-bold text-sky-600 dark:text-sky-400 block">{cit.title}</span>
                              <span className="text-[11px] text-slate-500 font-mono block">{cit.act_or_court} • {cit.section_or_year}</span>
                              <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">{cit.snippet}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {msg.guided_questions && msg.guided_questions.length > 0 && (
                      <div>
                        <span className="text-[11px] font-bold text-slate-500 block mb-1 flex items-center space-x-1">
                          <HelpCircle className="h-3.5 w-3.5 text-sky-500" />
                          <span>You May Also Ask:</span>
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.guided_questions.map((gq: string, gIdx: number) => (
                            <button
                              key={gIdx}
                              onClick={() => handleSend(gq)}
                              className="text-xs bg-slate-100 hover:bg-sky-100 text-sky-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-sky-300 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700 transition-colors"
                            >
                              + {gq}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="max-w-3xl">
              <StreamProgress currentStage={streamStage} stageMessage={streamMessage} />
              {currentResponse && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-sm text-sm whitespace-pre-wrap leading-relaxed animate-pulse-light">
                  {currentResponse}
                </div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="relative flex items-center bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-2xl shadow-md p-2 focus-within:ring-2 focus-within:ring-sky-500"
          >
            <button
              type="button"
              onClick={toggleVoiceInput}
              className={`p-2.5 rounded-xl transition-colors ${
                isRecording
                  ? 'bg-rose-500 text-white animate-bounce'
                  : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
              }`}
              title="Voice Input"
            >
              <Mic className="h-5 w-5" />
            </button>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={isRecording ? 'Listening to voice...' : 'Ask general or legal questions in plain language...'}
              disabled={isLoading}
              className="flex-1 bg-transparent px-3 py-2 text-sm focus:outline-none text-slate-800 dark:text-slate-100 placeholder-slate-400"
            />

            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="p-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-600 hover:to-indigo-700 disabled:opacity-50 text-white rounded-xl shadow-md transition-all ml-1"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
