"use client";

import React, { useState, useEffect, useRef } from "react";
import { Terminal, Cpu, HardDrive, Wifi, Activity } from "lucide-react";

interface DiagnosticsPanelProps {
  logs?: string[];
  oodaState?: "observe" | "orient" | "decide" | "act" | "idle";
}

export default function DiagnosticsPanel({ logs = [], oodaState = "idle" }: DiagnosticsPanelProps) {
  const [cpu, setCpu] = useState(12);
  const [memory, setMemory] = useState(48.2);
  const [latency, setLatency] = useState(24);
  const [systemLogs, setSystemLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Fluctuating metrics simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setCpu((prev) => {
        const delta = Math.floor(Math.random() * 5) - 2;
        return Math.max(5, Math.min(45, prev + delta));
      });
      setMemory((prev) => {
        const delta = Number((Math.random() * 0.4 - 0.2).toFixed(2));
        return Math.max(40, Math.min(60, prev + delta));
      });
      setLatency((prev) => {
        const delta = Math.floor(Math.random() * 10) - 5;
        return Math.max(10, Math.min(80, prev + delta));
      });
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  // Sync parent logs and add some baseline system boot logs
  useEffect(() => {
    const bootLogs = [
      "SYSTEM RUNNING: OK",
      "CORE INTERFACES INITIALIZED",
      "LISTENING ON PORT 8000...",
      "DATABASE READY: sqlite:///./traptalk.db"
    ];
    
    if (logs.length === 0) {
      setSystemLogs(bootLogs);
    } else {
      setSystemLogs([...bootLogs, ...logs]);
    }
  }, [logs]);

  // Auto-scroll logs to bottom
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [systemLogs]);

  return (
    <div className="flex-1 flex flex-col border border-accent-muted bg-bg-panel shadow-lg glow-border-green rounded-sm overflow-hidden h-full">
      {/* Panel Header */}
      <div className="bg-bg-panel-header border-b border-accent-muted px-4 py-2 flex justify-between items-center font-share text-xs text-accent-neon">
        <span className="flex items-center space-x-2">
          <Terminal size={12} className="text-accent-neon animate-pulse" />
          <span>[01] DIAGNOSTICS & METRICS</span>
        </span>
        <span className="flex items-center space-x-1">
          <Activity size={10} className="text-accent-neon animate-pulse" />
          <span className="text-[10px]">OS_KERN: OK</span>
        </span>
      </div>

      <div className="p-4 flex-1 flex flex-col space-y-6 overflow-y-auto font-mono text-[11px] text-text-secondary select-none">
        
        {/* Fluctuating System Metrics */}
        <div className="space-y-3">
          {/* CPU Indicator */}
          <div className="space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center space-x-1">
                <Cpu size={11} className="text-text-muted" />
                <span>CPU_LOAD</span>
              </span>
              <span className="text-accent-neon font-bold">{cpu}%</span>
            </div>
            <div className="w-full h-2 bg-accent-dark border border-accent-muted/40 relative">
              <div
                className="h-full bg-accent-neon shadow-[0_0_8px_var(--accent-glow-green)] transition-all duration-500"
                style={{ width: `${cpu}%` }}
              />
            </div>
          </div>

          {/* Memory Indicator */}
          <div className="space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span className="flex items-center space-x-1">
                <HardDrive size={11} className="text-text-muted" />
                <span>MEM_ALLOC</span>
              </span>
              <span className="text-accent-neon font-bold">{memory.toFixed(1)}%</span>
            </div>
            <div className="w-full h-2 bg-accent-dark border border-accent-muted/40 relative">
              <div
                className="h-full bg-accent-neon shadow-[0_0_8px_var(--accent-glow-green)] transition-all duration-500"
                style={{ width: `${memory}%` }}
              />
            </div>
          </div>

          {/* Latency / Network */}
          <div className="flex justify-between items-center border border-accent-muted/20 bg-accent-dark/30 p-2 rounded-sm text-xs">
            <span className="flex items-center space-x-1 text-text-muted">
              <Wifi size={11} />
              <span>NET_LATENCY</span>
            </span>
            <span className="text-state-cyan font-bold">{latency}ms</span>
          </div>
        </div>

        {/* OODA LOOP Orchestrator UI */}
        <div className="border border-accent-muted/30 p-3 bg-bg-secondary/40 rounded-sm space-y-2">
          <div className="text-[10px] text-text-muted font-share uppercase tracking-widest text-center border-b border-accent-muted/20 pb-1">
            Agentic OODA Loop Orchestrator
          </div>
          <div className="grid grid-cols-4 gap-1 text-center text-[10px] font-share font-bold">
            <div
              className={`p-1 border rounded-sm transition-all duration-300 ${
                oodaState === "observe"
                  ? "bg-accent-neon text-bg-primary border-accent-neon glow-border-green scale-105"
                  : "border-accent-muted/30 text-text-muted bg-transparent"
              }`}
            >
              OBSERVE
            </div>
            <div
              className={`p-1 border rounded-sm transition-all duration-300 ${
                oodaState === "orient"
                  ? "bg-state-cyan text-bg-primary border-state-cyan scale-105"
                  : "border-accent-muted/30 text-text-muted bg-transparent"
              }`}
            >
              ORIENT
            </div>
            <div
              className={`p-1 border rounded-sm transition-all duration-300 ${
                oodaState === "decide"
                  ? "bg-state-amber text-bg-primary border-state-amber scale-105"
                  : "border-accent-muted/30 text-text-muted bg-transparent"
              }`}
            >
              DECIDE
            </div>
            <div
              className={`p-1 border rounded-sm transition-all duration-300 ${
                oodaState === "act"
                  ? "bg-state-red text-bg-primary border-state-red scale-105 animate-pulse"
                  : "border-accent-muted/30 text-text-muted bg-transparent"
              }`}
            >
              ACT
            </div>
          </div>
        </div>

        {/* Scrolling Event Log Console */}
        <div className="flex-1 flex flex-col border border-accent-muted/25 bg-bg-primary/60 rounded-sm overflow-hidden min-h-[150px]">
          <div className="bg-bg-panel-header border-b border-accent-muted/20 px-2 py-1 font-share text-[9px] text-text-muted tracking-wider flex justify-between">
            <span>CONSOLE LOG AUDIT FEED</span>
            <span>LIVE</span>
          </div>
          <div className="p-2 flex-1 overflow-y-auto font-mono text-[9px] text-text-secondary space-y-1.5 scrollbar-thin">
            {systemLogs.map((log, idx) => (
              <div key={idx} className="flex space-x-1.5 border-b border-accent-muted/5 pb-1">
                <span className="text-text-muted font-bold select-none">&gt;&gt;</span>
                <span className="break-all">{log}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

      </div>
    </div>
  );
}
