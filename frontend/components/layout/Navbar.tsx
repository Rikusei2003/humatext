"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Navbar() {
  const [cardKey, setCardKey] = useState<string | null>(null);

  useEffect(() => {
    setCardKey(localStorage.getItem("card_key"));
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur border-b border-border-light">
      <div className="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-foreground">
          HumaText
        </Link>
        <div className="flex items-center gap-4 text-sm">
          {cardKey ? (
            <>
              <Link href="/workspace" className="text-muted hover:text-foreground transition-colors">
                工作台
              </Link>
              <Link href="/history" className="text-muted hover:text-foreground transition-colors">
                历史记录
              </Link>
              <button
                onClick={() => { localStorage.removeItem("card_key"); setCardKey(null); window.location.href = "/"; }}
                className="text-xs text-lighter hover:text-muted"
              >
                退出
              </button>
            </>
          ) : (
            <Link href="/workspace" className="px-4 py-2 bg-primary text-white rounded-md font-medium text-sm hover:shadow-button transition-shadow">
              开始使用
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
