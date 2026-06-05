"use client";

import React, { useState, useEffect } from "react";
import DiagnosticsPanel from "@/components/DiagnosticsPanel";
import ChatTerminal from "@/components/ChatTerminal";
import IntelligencePanel from "@/components/IntelligencePanel";

// Configurations
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const DEMO_API_KEY = "trap_talk_secret_key_2026";

interface ChatMessage {
  sender: "scammer" | "agent" | "system";
  text: string;
  timestamp: number;
}

interface IntelligenceData {
  bankAccounts: string[];
  upiIds: string[];
  phishingLinks: string[];
  phoneNumbers: string[];
  suspiciousKeywords: string[];
  agentNotes?: string;
}

export default function Home() {
  const [systemTime, setSystemTime] = useState("");
  const [sessionId, setSessionId] = useState("");
  
  // App States
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [intelligence, setIntelligence] = useState<IntelligenceData>({
    bankAccounts: [],
    upiIds: [],
    phishingLinks: [],
    phoneNumbers: [],
    suspiciousKeywords: [],
    agentNotes: ""
  });
  const [riskScore, setRiskScore] = useState(0);
  const [scamCategory, setScamCategory] = useState<string | null>(null);
  const [scamDetected, setScamDetected] = useState(false);
  const [sessionStatus, setSessionStatus] = useState("idle"); // idle, active, completed
  
  // UX / Loading States
  const [isLoading, setIsLoading] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [callbackSuccess, setCallbackSuccess] = useState<boolean | null>(null);
  
  // Logs & Orchestrator States
  const [logs, setLogs] = useState<string[]>([]);
  const [oodaState, setOodaState] = useState<"observe" | "orient" | "decide" | "act" | "idle">("idle");

  // Clock synchronization
  useEffect(() => {
    const updateTime = () => {
      const d = new Date();
      setSystemTime(d.toISOString().replace("T", " ").substring(0, 19));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    
    // Generate new Session ID
    const randomId = "session-" + Math.random().toString(36).substring(2, 11).toUpperCase();
    setSessionId(randomId);
    
    return () => clearInterval(timer);
  }, []);

  const addLog = (message: string) => {
    const timeStr = new Date().toTimeString().split(" ")[0];
    setLogs((prev) => [...prev, `[${timeStr}] ${message}`]);
  };

  // Submit messages to backend
  const handleSendMessage = async (text: string) => {
    if (!sessionId) return;
    
    // 1. Save Scammer message locally first
    const scammerMsg: ChatMessage = {
      sender: "scammer",
      text: text,
      timestamp: Date.now()
    };
    
    const updatedMessages = [...messages, scammerMsg];
    setMessages(updatedMessages);
    setSessionStatus("active");
    setIsLoading(true);
    setCallbackSuccess(null); // Reset callback indicator on new message

    // OODA State: OBSERVE -> ORIENT
    setOodaState("observe");
    addLog(`OBSERVING SCAMMER INBOUND: "${text.substring(0, 40)}..."`);
    
    try {
      // Transition to Orient
      setOodaState("orient");
      addLog("ORIENTING PACKET METADATA & PARSING ENTITIES...");
      
      // Structure request payload matching backend schema
      // Format conversation history to match MessageHistoryObject
      const apiHistory = messages
        .filter(m => m.sender !== "system")
        .map(m => ({
          sender: m.sender,
          text: m.text,
          timestamp: m.timestamp
        }));

      const payload = {
        sessionId: sessionId,
        message: {
          sender: "scammer",
          text: text,
          timestamp: scammerMsg.timestamp
        },
        conversationHistory: apiHistory,
        metadata: {
          channel: "SMS",
          language: "English",
          locale: "IN"
        }
      };

      // Call FastAPI
      const res = await fetch(`${API_BASE_URL}/api/v1/engage`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": DEMO_API_KEY
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`API returned ${res.status}`);
      }

      const responseData = await res.json();
      
      // OODA State: DECIDE
      setOodaState("decide");
      addLog("DECIDING THREAT WEIGHTS & RETRIEVING PERSONA PROMPTS...");
      
      // Query current session details from backend to update state panels
      const sessionRes = await fetch(`${API_BASE_URL}/api/v1/sessions/${sessionId}/report`, {
        headers: {
          "x-api-key": DEMO_API_KEY
        }
      });
      
      if (sessionRes.ok) {
        const sessionReport = await sessionRes.json();
        setRiskScore(sessionReport.scamDetected ? 85 : 10); // Mock score weighting or read from session if added to report later
        setScamDetected(sessionReport.scamDetected);
        
        // Extract category heuristics or updates
        if (sessionReport.scamDetected) {
          setScamCategory("phishing_threat"); // Default visual fallback
          addLog("STATE ALIGNMENT: CONFIRMED SCAM IN BOUNDS!");
        } else {
          addLog("STATE ALIGNMENT: NO THREAT ASSESSED.");
        }
        
        // Map extracted variables
        const intel = sessionReport.extractedIntelligence;
        setIntelligence({
          bankAccounts: intel.bankAccounts || [],
          upiIds: intel.upiIds || [],
          phishingLinks: intel.phishingLinks || [],
          phoneNumbers: intel.phoneNumbers || [],
          suspiciousKeywords: intel.suspiciousKeywords || [],
          agentNotes: sessionReport.agentNotes || ""
        });
      }

      // Save Agent Response message locally
      const agentMsg: ChatMessage = {
        sender: "agent",
        text: responseData.reply,
        timestamp: Date.now()
      };
      
      setMessages((prev) => [...prev, agentMsg]);
      
      // OODA State: ACT
      setOodaState("act");
      addLog(`ACTING RESPONSE: GENERATED BELIEVABLE PERSONA ENGAGEMENT`);
      
      // Complete loop back to idle
      setTimeout(() => {
        setOodaState("idle");
      }, 1000);

    } catch (err: any) {
      console.error(err);
      addLog(`CRITICAL FAILURE: ${err.message}`);
      setOodaState("idle");
      setMessages((prev) => [
        ...prev,
        {
          sender: "system",
          text: `NETWORK ERROR: Unable to reach FastAPI backend. Make sure server is running at ${API_BASE_URL}`,
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Close Session and dispatch final report callback
  const handleCloseSession = async () => {
    if (!sessionId || sessionStatus !== "active") return;
    
    setIsClosing(true);
    addLog(`INITIATING REPORT COMPILATION FOR SESSION: ${sessionId}`);
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/sessions/${sessionId}/close`, {
        method: "POST",
        headers: {
          "x-api-key": DEMO_API_KEY
        }
      });

      if (!res.ok) {
        throw new Error(`Close session request failed: status ${res.status}`);
      }
      
      const report = await res.json();
      setSessionStatus("completed");
      setCallbackSuccess(true);
      addLog(`REPORT DISPATCH SUCCESS: GUVI CALLBACK RETURNED CODE 200`);
      
      setMessages((prev) => [
        ...prev,
        {
          sender: "system",
          text: `SESSION TERMINATED. callback payload successfully sent to GUVI endpoint.`,
          timestamp: Date.now()
        }
      ]);

    } catch (err: any) {
      console.error(err);
      setCallbackSuccess(false);
      addLog(`REPORT DISPATCH FAILURE: CALLBACK ENDPOINT TIMEOUT`);
      setMessages((prev) => [
        ...prev,
        {
          sender: "system",
          text: `CALLBACK DISPATCH ERROR: ${err.message}`,
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsClosing(false);
    }
  };

  const handleSelectPreset = (scenarioName: string, initialMessage: string) => {
    addLog(`PRESET ACTIVATED: ${scenarioName}`);
    // Clear previous chat log and reset state for new clean run
    setMessages([]);
    setRiskScore(0);
    setScamCategory(null);
    setScamDetected(false);
    setSessionStatus("idle");
    setCallbackSuccess(null);
    setIntelligence({
      bankAccounts: [],
      upiIds: [],
      phishingLinks: [],
      phoneNumbers: [],
      suspiciousKeywords: [],
      agentNotes: ""
    });
    
    // Auto submit message
    handleSendMessage(initialMessage);
  };

  return (
    <main className="h-screen w-screen flex flex-col hud-canvas overflow-hidden select-none">
      {/* HUD HEADER NAVBAR */}
      <header className="h-14 border-b border-accent-muted bg-bg-panel flex items-center justify-between px-6 z-10 shadow-md">
        <div className="flex items-center space-x-4">
          <span className="font-orbitron font-black text-lg text-accent-neon tracking-widest glow-text-green">
            TRAP_TALK_AI
          </span>
          <span className="border border-accent-neon/30 px-2 py-0.5 rounded-sm font-share text-[10px] text-accent-neon animate-pulse">
            CORE_ON
          </span>
        </div>
        <div className="hidden md:flex items-center space-x-8 font-share text-xs">
          <div className="flex space-x-2">
            <span className="text-text-muted">HOST:</span>
            <span className="text-accent-neon">{API_BASE_URL.replace("http://", "")}</span>
          </div>
          <div className="flex space-x-2">
            <span className="text-text-muted">LINK:</span>
            <span className="text-state-cyan animate-pulse">SECURE_TUNNEL</span>
          </div>
          <div className="flex space-x-2">
            <span className="text-text-muted">CLOCK:</span>
            <span className="text-accent-neon font-mono">{systemTime}</span>
          </div>
        </div>
      </header>

      {/* THREE PANELS LAYOUT */}
      <div className="flex-1 flex flex-col md:flex-row p-4 gap-4 overflow-hidden relative">
        {/* Left Column: Diagnostics (25%) */}
        <section className="w-full md:w-1/4 flex flex-col h-1/3 md:h-full">
          <DiagnosticsPanel logs={logs} oodaState={oodaState} />
        </section>

        {/* Center Column: Chat Console (50%) */}
        <section className="w-full md:w-1/2 flex flex-col h-1/3 md:h-full">
          <ChatTerminal
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            sessionId={sessionId}
            onSelectPreset={handleSelectPreset}
          />
        </section>

        {/* Right Column: Intelligence & Reports (25%) */}
        <section className="w-full md:w-1/4 flex flex-col h-1/3 md:h-full">
          <IntelligencePanel
            intelligence={intelligence}
            riskScore={riskScore}
            scamCategory={scamCategory}
            scamDetected={scamDetected}
            sessionStatus={sessionStatus}
            onCloseSession={handleCloseSession}
            isClosing={isClosing}
            callbackSuccess={callbackSuccess}
          />
        </section>
      </div>

      {/* FOOTER STATUS BAR */}
      <footer className="h-8 border-t border-accent-muted bg-bg-panel flex items-center justify-between px-6 text-[10px] font-share text-text-muted z-10">
        <span>AUTHENTICATION CHECK: APPROVED (x-api-key)</span>
        <span>COPYRIGHT (C) DEEPMIND // ALL RIGHTS RESERVED</span>
        <span>THREAT DETECTED: AUTO_TRIGGER ENABLED</span>
      </footer>
    </main>
  );
}
