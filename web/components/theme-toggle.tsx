"use client";
import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [m, setM] = useState(false);
  useEffect(() => setM(true), []);
  const dark = resolvedTheme === "dark";
  return (
    <button className="btn btn-ghost btn-sm" aria-label="Toggle theme"
      onClick={() => setTheme(dark ? "light" : "dark")}>
      {m ? (dark ? <Sun /> : <Moon />) : <Sun />}
      <span className="fz-xs">{m ? (dark ? "Light" : "Dark") : ""}</span>
    </button>
  );
}
