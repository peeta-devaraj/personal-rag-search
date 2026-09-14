import { motion } from "framer-motion";
import { BarChart3, Library, MessageSquare, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { getHealth } from "../api/client";
import type { HealthResponse } from "../types";
import { cn } from "../lib/utils";

const NAV_ITEMS = [
  { to: "/library", label: "Library", icon: Library },
  { to: "/ask", label: "Ask", icon: MessageSquare },
  { to: "/eval", label: "Eval Dashboard", icon: BarChart3 },
];

export default function Layout() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState(false);
  const location = useLocation();

  useEffect(() => {
    let cancelled = false;
    const poll = () => {
      getHealth()
        .then((h) => {
          if (!cancelled) {
            setHealth(h);
            setHealthError(false);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setHealth(null);
            setHealthError(true);
          }
        });
    };
    poll();
    const id = setInterval(poll, 10000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const isOnline = !!health?.ollama_reachable;

  return (
    <div className="flex h-full bg-base-950">
      {/* ambient background glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 left-1/3 h-[480px] w-[480px] rounded-full bg-indigo-600/[0.06] blur-[120px]" />
        <div className="absolute -top-24 -right-20 h-[360px] w-[360px] rounded-full bg-fuchsia-600/[0.045] blur-[120px]" />
      </div>

      <nav className="relative z-10 flex w-64 flex-shrink-0 flex-col border-r border-white/[0.06] bg-base-900/60 px-3 py-5 backdrop-blur-xl">
        <div className="mb-8 flex items-center gap-2.5 px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient shadow-glow">
            <Sparkles size={16} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <div className="text-[13.5px] font-semibold leading-tight text-zinc-50">Personal RAG</div>
            <div className="text-[10.5px] font-medium leading-tight text-zinc-500">local &amp; private</div>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.to;
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className="relative block">
                {active && (
                  <motion.div
                    layoutId="nav-active-pill"
                    className="absolute inset-0 rounded-lg bg-white/[0.06] ring-1 ring-inset ring-white/10"
                    transition={{ type: "spring", stiffness: 500, damping: 40 }}
                  />
                )}
                <div
                  className={cn(
                    "relative flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-colors",
                    active ? "text-white" : "text-zinc-400 hover:text-zinc-100",
                  )}
                >
                  <Icon size={16} strokeWidth={2} className={active ? "text-indigo-300" : ""} />
                  {item.label}
                </div>
              </NavLink>
            );
          })}
        </div>

        <div className="flex-1" />

        <div className="glass-card flex items-center gap-2.5 rounded-lg px-3 py-2.5">
          <span className="relative flex h-2 w-2 flex-shrink-0">
            {isOnline && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            )}
            <span
              className={cn(
                "relative inline-flex h-2 w-2 rounded-full",
                isOnline ? "bg-emerald-400" : "bg-rose-500",
              )}
            />
          </span>
          <div className="min-w-0 flex-1">
            <div className="truncate text-[12px] font-medium text-zinc-200">
              {health ? health.model : healthError ? "Ollama unreachable" : "Checking..."}
            </div>
            <div className="text-[10.5px] text-zinc-500">{isOnline ? "Model ready" : "Start ollama serve"}</div>
          </div>
        </div>
      </nav>

      <main className="relative z-10 flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-10 py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
