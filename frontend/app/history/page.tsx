"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
const modeLabels: Record<string, string> = { polish: "润色", enhance: "增强" };

export default function HistoryPage() {
  const [cardKey, setCardKey] = useState("");
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const saved = localStorage.getItem("card_key");
    if (saved) setCardKey(saved);
  }, []);

  const fetchHistory = useCallback(async () => {
    if (!cardKey) return;
    const res = await fetch(`${API_URL}/api/v1/rewrite/history?card_key=${cardKey}&page=${page}&per_page=20`);
    if (res.ok) {
      const data = await res.json();
      setItems(data.items);
      setTotal(data.total);
    }
  }, [cardKey, page]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  if (!cardKey) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-16">
        <div className="text-center">
          <p className="text-muted mb-4">请先输入兑换码</p>
          <Link href="/workspace" className="text-primary text-sm hover:underline">前往工作台</Link>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="min-h-screen bg-surface pt-20 pb-10">
      <div className="max-w-[800px] mx-auto px-6">
        <h1 className="text-xl font-bold mb-6">历史记录</h1>
        {items.length === 0 ? (
          <div className="bg-white border border-border rounded-lg p-12 text-center text-sm text-muted shadow-card">暂无改写记录</div>
        ) : (
          <>
            <div className="space-y-3">
              {items.map(item => (
                <Link key={item.id} href={`/history/${item.id}?card_key=${cardKey}`}
                  className="block bg-white border border-border rounded-lg p-5 shadow-card hover:border-primary transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold">{modeLabels[item.mode] || item.mode} · {item.source_language === "zh" ? "中文" : "EN"}</span>
                    <span className="text-xs text-muted">{new Date(item.created_at).toLocaleString("zh-CN")}</span>
                  </div>
                  <p className="text-sm text-muted line-clamp-2">{item.input_text}</p>
                  <span className="text-xs text-lighter mt-2">{item.word_count} 字</span>
                </Link>
              ))}
            </div>
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-6">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button key={i} onClick={() => setPage(i + 1)}
                    className={`px-3 py-1 text-sm rounded ${page === i + 1 ? "bg-primary text-white" : "bg-white border border-border text-muted"}`}>
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
