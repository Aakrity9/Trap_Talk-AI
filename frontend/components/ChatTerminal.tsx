"use client";

import React, { useState, useEffect, useRef } from "react";
import { MessageSquare, Send, AlertTriangle, ShieldCheck } from "lucide-react";

interface ChatMessage {
  sender: "scammer" | "agent" | "system";
  text: string;
  timestamp: number;
}

interface ChatTerminalProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  sessionId: string;
  onSelectPreset: (scenarioName: string, initialMessage: string) => void;
}

const PRESETS = [
  {
    name: "BANK THREAT",
    text: "Your account is blocked. Verify card immediately at http://verify-block.alert/login",
  },
  {
    name: "UPI PAYMENT FRAUD",
    text: "Congratulations! You earned a cashback reward. Please scan and pay 5000 INR to upi@reward",
  },
  {
    name: "FAKE PRIZE DRAW",
    text: "Dear customer, you won a lottery prize of 1 crore. Click http://prize-crore.info/claim to pay fees",
  }
];

export default function ChatTerminal({
  messages,
  onSendMessage,
  isLoading,
  sessionId,
  onSelectPreset
}: ChatTerminalProps) {
  const [inputText, setInputText] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Typewriter effect state
  const [displayedTextMap, setDisplayedTextMap] = useState<Record<number, string>>({});

  useEffect(() => {
    // Scroll to bottom on new messages
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });

    // Handle streaming/typewriter effect for latest agent message
    if (messages.length > 0) {
      const latestMsgIdx = messages.length - 1;
      const latestMsg = messages[latestMsgIdx];
      
      if (latestMsg.sender === "agent" && !displayedTextMap[latestMsg.timestamp]) {
        let currentText = "";
        let charIdx = 0;
        
        const timer = setInterval(() => {
          if (charIdx < latestMsg.text.length) {
            currentText += latestMsg.text[charIdx];
            setDisplayedTextMap(prev => ({
              ...prev,
              [latestMsg.timestamp]: currentText
            }));
            charIdx++;
          } else {
            clearInterval(timer);
          }
        }, 15); // Typewriter speed
        
        return () => clearInterval(timer);
      }
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText("");
  };

  const formatTimestamp = (ts: number) => {
    const d = new Date(ts);
    return d.toTimeString().split(" ")[0];
  };

  return (
    <div className="flex-1 flex flex-col border border-accent-muted bg-bg-panel shadow-lg glow-border-green rounded-sm overflow-hidden h-full">
      {/* Panel Header */}
      <div className="bg-bg-panel-header border-b border-accent-muted px-4 py-2 flex justify-between items-center font-share text-xs text-accent-neon">
        <span className="flex items-center space-x-2">
          <MessageSquare size={12} className="text-accent-neon animate-pulse" />
          <span>[02] NEURAL LINK CONSOLE (SIMULATOR)</span>
        </span>
        <span className="text-[10px] text-text-muted">SESSION_ID: {sessionId || "N/A"}</span>
      </div>

      {/* Preset Scenario Injectors */}
      <div className="bg-bg-secondary/30 border-b border-accent-muted/20 p-2 flex flex-wrap gap-2 justify-center">
        <span className="text-[9px] text-text-muted font-share flex items-center pr-1 uppercase tracking-wider">
          Scenarios:
        </span>
        {PRESETS.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPreset(preset.name, preset.text)}
            className="text-[9px] font-share px-2 py-1 border border-accent-muted text-text-secondary rounded-sm hover:border-accent-neon hover:text-accent-neon hover:bg-accent-neon/5 active:scale-95 transition-all duration-150 uppercase"
            disabled={isLoading}
          >
            {preset.name}
          </button>
        ))}
      </div>

      {/* Chat Messages Feed Container */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin bg-black/40">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-text-muted space-y-2 font-share text-xs select-none">
            <ShieldCheck size={28} className="text-text-muted animate-pulse" />
            <p className="uppercase tracking-widest text-[11px]">Neural console connection idle</p>
            <p className="text-[9px]">Select a scenario above or input a scam message below to engage</p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isScammer = msg.sender === "scammer";
            const isSystem = msg.sender === "system";
            
            if (isSystem) {
              return (
                <div key={index} className="flex justify-center text-[10px] text-state-cyan font-share uppercase border-y border-state-cyan/10 py-1 tracking-wider bg-state-cyan/5">
                  [SYSTEM // {formatTimestamp(msg.timestamp)}] {msg.text}
                </div>
              );
            }

            // Get text to display (regular or typewriter for latest agent message)
            const textToDisplay = msg.sender === "agent" 
              ? (displayedTextMap[msg.timestamp] || msg.text)
              : msg.text;

            return (
              <div
                key={index}
                className={`flex flex-col border ${
                  isScammer
                    ? "border-state-red/40 bg-state-red/5 rounded-r-md rounded-bl-md ml-4 mr-12"
                    : "border-accent-muted/40 bg-accent-dark/10 rounded-l-md rounded-br-md mr-4 ml-12"
                }`}
              >
                {/* Message Meta Info Header */}
                <div
                  className={`px-3 py-1 border-b text-[9px] font-share flex justify-between uppercase ${
                    isScammer
                      ? "border-state-red/20 text-state-red bg-state-red/10"
                      : "border-accent-muted/20 text-accent-neon bg-accent-neon/5"
                  }`}
                >
                  <span className="font-bold tracking-wider flex items-center space-x-1">
                    {isScammer ? (
                      <>
                        <AlertTriangle size={9} />
                        <span>SCAMMER_IN</span>
                      </>
                    ) : (
                      <span>AGENT_OUT (RAMESH PERSONA)</span>
                    )}
                  </span>
                  <span className="text-[8px] text-text-muted">{formatTimestamp(msg.timestamp)}</span>
                </div>
                {/* Message Content Body */}
                <div className={`p-3 text-xs leading-relaxed font-mono ${
                  isScammer ? "text-text-white" : "text-accent-neon glow-text-green"
                }`}>
                  {textToDisplay}
                  {msg.sender === "agent" && textToDisplay.length < msg.text.length && (
                    <span className="ml-0.5 text-accent-neon caret-blink">_</span>
                  )}
                </div>
              </div>
            );
          })
        )}
        {isLoading && (
          <div className="flex items-center space-x-2 text-[10px] text-accent-neon font-share uppercase tracking-widest pl-4">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-neon animate-ping" />
            <span>AI Processing neural response...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Terminal Input Bar */}
      <form onSubmit={handleSubmit} className="border-t border-accent-muted bg-bg-secondary p-3 flex items-center">
        <span className="text-accent-neon font-bold text-sm select-none mr-2 font-share">&gt;</span>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Input scam message..."
          className="flex-1 bg-transparent border-none outline-none text-accent-neon placeholder-text-muted/60 font-mono text-xs"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isLoading}
          className="p-1.5 border border-accent-muted text-accent-neon rounded-sm hover:border-accent-neon hover:bg-accent-neon/10 disabled:border-accent-muted/30 disabled:text-text-muted transition-all duration-150 active:scale-90"
        >
          <Send size={12} />
        </button>
      </form>
    </div>
  );
}
