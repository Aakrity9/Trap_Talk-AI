"use client";

import React from "react";
import { ShieldAlert, AlertCircle, CheckCircle, FileText, Ban } from "lucide-react";

interface IntelligenceData {
  bankAccounts: string[];
  upiIds: string[];
  phishingLinks: string[];
  phoneNumbers: string[];
  suspiciousKeywords: string[];
  agentNotes?: string;
}

interface IntelligencePanelProps {
  intelligence: IntelligenceData;
  riskScore: number;
  scamCategory: string | null;
  scamDetected: boolean;
  sessionStatus: string;
  onCloseSession: () => void;
  isClosing: boolean;
  callbackSuccess: boolean | null;
}

export default function IntelligencePanel({
  intelligence,
  riskScore,
  scamCategory,
  scamDetected,
  sessionStatus,
  onCloseSession,
  isClosing,
  callbackSuccess
}: IntelligencePanelProps) {
  
  // Format risk score style
  const getRiskColorClass = () => {
    if (riskScore < 30) return "text-accent-neon glow-text-green";
    if (riskScore < 70) return "text-state-amber";
    return "text-state-red glow-text-red";
  };

  const getRiskLevelName = () => {
    if (riskScore === 0) return "CLEAN";
    if (riskScore < 30) return "LOW RISK";
    if (riskScore < 70) return "SUSPICIOUS";
    return "CRITICAL FRAUD THREAT";
  };

  return (
    <div className="flex-1 flex flex-col border border-accent-muted bg-bg-panel shadow-lg glow-border-green rounded-sm overflow-hidden h-full">
      {/* Panel Header */}
      <div className="bg-bg-panel-header border-b border-accent-muted px-4 py-2 flex justify-between items-center font-share text-xs text-accent-neon">
        <span className="flex items-center space-x-2">
          <ShieldAlert size={12} className="text-accent-neon animate-pulse" />
          <span>[03] SCAM INTEL FIELD REPORT</span>
        </span>
        <span className="text-[10px] text-text-white uppercase font-bold">
          STATUS: {sessionStatus}
        </span>
      </div>

      <div className="p-4 flex-1 flex flex-col space-y-4 overflow-y-auto font-mono text-[11px] text-text-secondary select-none">
        
        {/* Risk Level Dashboard */}
        <div className="border border-accent-muted/30 bg-bg-secondary/40 p-3 rounded-sm flex items-center justify-between">
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">Scam Risk Assessment</div>
            <div className="text-sm font-share font-bold uppercase tracking-widest flex items-center space-x-2">
              <span className={getRiskColorClass()}>{getRiskLevelName()}</span>
            </div>
            {scamDetected && scamCategory && (
              <div className="text-[10px] text-text-white uppercase">
                CATEGORY: <span className="text-state-cyan">{scamCategory}</span>
              </div>
            )}
          </div>
          <div className="text-center font-share">
            <div className="text-[9px] text-text-muted uppercase">Risk Score</div>
            <div className={`text-2xl font-bold ${getRiskColorClass()}`}>{riskScore.toFixed(0)}</div>
          </div>
        </div>

        {/* Extracted Entities List */}
        <div className="flex-1 space-y-3 overflow-y-auto pr-1">
          {/* UPI Handles */}
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">UPI Handles ({intelligence.upiIds.length})</div>
            <div className="min-h-[30px] border border-accent-muted/20 bg-black/20 p-2 rounded-sm space-y-1">
              {intelligence.upiIds.length === 0 ? (
                <span className="text-[10px] text-text-muted italic">NONE DETECTED</span>
              ) : (
                intelligence.upiIds.map((val, idx) => (
                  <div key={idx} className="text-state-cyan break-all select-all font-bold">&gt; {val}</div>
                ))
              )}
            </div>
          </div>

          {/* Phishing Links */}
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">Phishing Links ({intelligence.phishingLinks.length})</div>
            <div className="min-h-[30px] border border-accent-muted/20 bg-black/20 p-2 rounded-sm space-y-1">
              {intelligence.phishingLinks.length === 0 ? (
                <span className="text-[10px] text-text-muted italic">NONE DETECTED</span>
              ) : (
                intelligence.phishingLinks.map((val, idx) => (
                  <div key={idx} className="text-state-red break-all select-all font-bold">&gt; {val}</div>
                ))
              )}
            </div>
          </div>

          {/* Phone Numbers */}
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">Contact Numbers ({intelligence.phoneNumbers.length})</div>
            <div className="min-h-[30px] border border-accent-muted/20 bg-black/20 p-2 rounded-sm space-y-1">
              {intelligence.phoneNumbers.length === 0 ? (
                <span className="text-[10px] text-text-muted italic">NONE DETECTED</span>
              ) : (
                intelligence.phoneNumbers.map((val, idx) => (
                  <div key={idx} className="text-text-white break-all select-all">&gt; {val}</div>
                ))
              )}
            </div>
          </div>

          {/* Bank Accounts */}
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">Bank Accounts ({intelligence.bankAccounts.length})</div>
            <div className="min-h-[30px] border border-accent-muted/20 bg-black/20 p-2 rounded-sm space-y-1">
              {intelligence.bankAccounts.length === 0 ? (
                <span className="text-[10px] text-text-muted italic">NONE DETECTED</span>
              ) : (
                intelligence.bankAccounts.map((val, idx) => (
                  <div key={idx} className="text-text-white break-all select-all">&gt; {val}</div>
                ))
              )}
            </div>
          </div>

          {/* Suspicious Keywords */}
          <div className="space-y-1">
            <div className="text-[9px] text-text-muted font-share uppercase tracking-wider">Trigger Keywords ({intelligence.suspiciousKeywords.length})</div>
            <div className="flex flex-wrap gap-1">
              {intelligence.suspiciousKeywords.length === 0 ? (
                <span className="text-[10px] text-text-muted italic">NONE</span>
              ) : (
                intelligence.suspiciousKeywords.map((val, idx) => (
                  <span key={idx} className="text-[9px] px-1.5 py-0.5 border border-accent-muted/40 bg-accent-dark/20 text-text-secondary rounded-sm uppercase">
                    {val}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Agent Notes / Tactics Summary */}
        <div className="border border-accent-muted/20 bg-bg-secondary/20 p-3 rounded-sm">
          <div className="text-[9px] text-text-muted font-share uppercase tracking-wider mb-1 flex items-center space-x-1">
            <FileText size={10} />
            <span>Agent Tactical Summary</span>
          </div>
          <p className="text-[10px] leading-relaxed italic text-text-secondary">
            {intelligence.agentNotes || "Awaiting scam engagement diagnostics..."}
          </p>
        </div>

        {/* Callback Dispatched Logger */}
        {callbackSuccess !== null && (
          <div className={`flex items-center space-x-2 border p-2 rounded-sm text-[10px] uppercase font-share ${
            callbackSuccess 
              ? "bg-accent-neon/10 border-accent-neon/30 text-accent-neon"
              : "bg-state-red/10 border-state-red/30 text-state-red"
          }`}>
            {callbackSuccess ? (
              <>
                <CheckCircle size={12} className="animate-pulse" />
                <span>GUVI Callback Dispatched successfully</span>
              </>
            ) : (
              <>
                <Ban size={12} />
                <span>GUVI Callback failed after max retries</span>
              </>
            )}
          </div>
        )}

        {/* Closing Action Panel */}
        <div className="pt-2">
          <button
            onClick={onCloseSession}
            disabled={sessionStatus !== "active" || isClosing}
            className="hud-button w-full flex items-center justify-center space-x-2 py-3 border border-accent-neon text-accent-neon bg-transparent hover:bg-accent-neon hover:text-bg-primary active:scale-95 disabled:border-accent-muted/30 disabled:text-text-muted disabled:hover:bg-transparent font-share font-bold uppercase tracking-widest text-xs rounded-sm cursor-pointer transition-all duration-200"
          >
            {isClosing ? "COMPILE & POSTING REPORT..." : "[+ CLOSE_SESSION & COMPILE REPORT ]"}
          </button>
        </div>

      </div>
    </div>
  );
}
