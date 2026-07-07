"use client";

import { useEffect, useRef } from "react";

// hex approximations of the observatory materials (sigma renders to canvas, so
// it needs real colors, not CSS vars). Mid-tones that read on paper and night.
const PAL = {
  moss: "#4e7a44", blue: "#4a5f8a", stone: "#8a8272", brass: "#b0872f",
  gold: "#c99a3a", cinnabar: "#b0432c",
};
const classColor = (cls: string) =>
  cls === "constitutive_regulator" ? PAL.moss
  : cls === "condition_specific_regulator" ? PAL.blue
  : cls === "unverifiable_no_kd" ? PAL.brass
  : PAL.stone;

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

      const g = new Graph();
      for (const id of ids) {
        const m = meta.get(id);
        const isFocus = id === focus;
        g.addNode(id, {
          label: id,
          x: Math.random(), y: Math.random(),
          size: isFocus ? 13 : Math.max(4, Math.min(11, 4 + (m ? Math.log((m.od || 0) + 1) * 1.4 : 0))),
          color: isFocus ? PAL.gold : m ? classColor(m.cls) : PAL.stone,
        });
      }
      const addEdge = (s: string, t: string, d: string) => {
        if (s !== t && g.hasNode(s) && g.hasNode(t) && !g.hasEdge(s, t))
          g.addEdgeWithKey(`${s}>${t}`, s, t, { size: 1.1, color: d === "up" ? "#4e7a4455" : "#b0432c55" });
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
        labelColor: { color: dark ? "#c9d3e0" : "#2a2f3a" },
        labelSize: 11,
        labelFont: "var(--font-mono), ui-monospace, monospace",
        labelDensity: 0.7, labelGridCellSize: 60,
        defaultEdgeColor: dark ? "#ffffff20" : "#0000001a",
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
