"use client";

import { useEffect, useRef } from "react";

const FALLBACK = {
  moss: "rgb(78 122 68)",
  blue: "rgb(74 95 138)",
  stone: "rgb(138 130 114)",
  brass: "rgb(176 135 47)",
  gold: "rgb(201 154 58)",
  snow: "rgb(201 211 224)",
  ink: "rgb(42 47 58)",
  rule: "rgba(18, 21, 27, 0.1)",
  reproducedLine: "rgba(78, 122, 68, 0.34)",
  refutedLine: "rgba(176, 67, 44, 0.34)",
};

function token(name: string, fallback: string) {
  if (typeof document === "undefined") return fallback;
  const probe = document.createElement("span");
  probe.style.color = `var(${name}, ${fallback})`;
  document.body.appendChild(probe);
  const color = getComputedStyle(probe).color || fallback;
  probe.remove();
  return color;
}

function graphPalette(dark: boolean) {
  return {
    moss: token("--graph-moss", FALLBACK.moss),
    blue: token("--graph-blue", FALLBACK.blue),
    stone: token("--graph-stone", FALLBACK.stone),
    brass: token("--graph-brass", FALLBACK.brass),
    gold: token("--graph-focus", FALLBACK.gold),
    upEdge: token("--graph-up-edge", FALLBACK.reproducedLine),
    downEdge: token("--graph-down-edge", FALLBACK.refutedLine),
    label: token("--graph-label", dark ? FALLBACK.snow : FALLBACK.ink),
    defaultEdge: token("--graph-edge", FALLBACK.rule),
  };
}

const classColor = (cls: string, pal: ReturnType<typeof graphPalette>) =>
  cls === "constitutive_regulator" ? pal.moss
  : cls === "condition_specific_regulator" ? pal.blue
  : cls === "unverifiable_no_kd" ? pal.brass
  : pal.stone;

type GData = {
  atlas: { g: string; cls: string; od: number; id: number }[];
  out: Record<string, { t: string; d: string; e: number }[]>;
  in: Record<string, { s: string; d: string; e: number }[]>;
};

export function GraphView({
  data, focus, onFocus, dark,
}: { data: GData; focus: string; onFocus: (g: string) => void; dark: boolean }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let renderer: any, cancelled = false;
    (async () => {
      const Graph = (await import("graphology")).default;
      const Sigma = (await import("sigma")).default;
      const forceAtlas2 = (await import("graphology-layout-forceatlas2")).default;
      if (cancelled || !ref.current) return;

      const meta = new Map(data.atlas.map((n) => [n.g, n]));
      const out = data.out[focus] || [], inn = data.in[focus] || [];
      const ids = new Set<string>([focus, ...out.map((x) => x.t), ...inn.map((x) => x.s)]);
      const pal = graphPalette(dark);

      const g = new Graph();
      for (const id of ids) {
        const m = meta.get(id);
        const isFocus = id === focus;
        g.addNode(id, {
          label: id,
          x: Math.random(), y: Math.random(),
          size: isFocus ? 13 : Math.max(4, Math.min(11, 4 + (m ? Math.log((m.od || 0) + 1) * 1.4 : 0))),
          color: isFocus ? pal.gold : m ? classColor(m.cls, pal) : pal.stone,
        });
      }
      const addEdge = (s: string, t: string, d: string) => {
        if (s !== t && g.hasNode(s) && g.hasNode(t) && !g.hasEdge(s, t))
          g.addEdgeWithKey(`${s}>${t}`, s, t, { size: 1.1, color: d === "up" ? pal.upEdge : pal.downEdge });
      };
      for (const x of out) addEdge(focus, x.t, x.d);
      for (const x of inn) addEdge(x.s, focus, x.d);
      // second-hop links among the neighborhood - reveals the local module
      for (const id of ids) for (const x of data.out[id] || []) if (ids.has(x.t)) addEdge(id, x.t, x.d);

      forceAtlas2.assign(g, {
        iterations: 300,
        settings: { gravity: 1.1, scalingRatio: 9, barnesHutOptimize: true, adjustSizes: true, slowDown: 2 },
      });

      renderer = new Sigma(g, ref.current, {
        labelColor: { color: pal.label },
        labelSize: 11,
        labelFont: "var(--font-mono), ui-monospace, monospace",
        labelDensity: 0.7, labelGridCellSize: 60,
        defaultEdgeColor: pal.defaultEdge,
        zIndex: true,
      });
      renderer.on("clickNode", ({ node }: any) => onFocus(node));
      renderer.on("enterNode", () => { if (ref.current) ref.current.style.cursor = "pointer"; });
      renderer.on("leaveNode", () => { if (ref.current) ref.current.style.cursor = "default"; });
    })();
    return () => { cancelled = true; try { renderer?.kill?.(); } catch {} };
  }, [data, focus, dark, onFocus]);

  return <div ref={ref} style={{ width: "100%", height: 540, borderRadius: "var(--radius)",
    background: "var(--paper-recessed)", border: "1px solid var(--rule)" }} />;
}
