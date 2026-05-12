"use client";

import { useState, useEffect } from "react";
import { useParams, useSearchParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function HistoryDetailPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const cardKey = searchParams.get("card_key") || "";
  const [job, setJob] = useState<any>(null);

  useEffect(() => {
    if (!cardKey) return;
    fetch(`${API_URL}/api/v1/rewrite/history/${id}?card_key=${cardKey}`).then(r => r.json()).then(setJob);
  }, [id, cardKey]);

  if (!job) return <div className="min-h-screen flex items-center justify-center pt-16"><div className="text-muted text-sm">加载中...</div></div>;

  return (
    <div className="min-h-screen bg-surface pt-20 pb-10">
      <div className="max-w-[900px] mx-auto px-6">
        <h1 className="text-xl font-bold mb-2">改写详情</h1>
        <div className="flex items-center gap-4 text-xs text-muted mb-6">
          <span>{job.mode === "polish" ? "Polish 润色" : "Enhance 增强"}</span>
          <span>{job.source_language === "zh" ? "中文" : "English"}</span>
          <span>{job.word_count} 字</span>
          <span>{new Date(job.created_at).toLocaleString("zh-CN")}</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-semibold mb-2 text-muted">原文</h3>
            <div className="bg-white border border-border rounded-lg p-5 shadow-card text-sm leading-relaxed whitespace-pre-wrap min-h-[300px]">{job.input_text}</div>
          </div>
          <div>
            <h3 className="text-sm font-semibold mb-2 text-muted">改写结果</h3>
            <div className="bg-white border border-border rounded-lg p-5 shadow-card text-sm leading-relaxed whitespace-pre-wrap min-h-[300px]">{job.output_text || "(空)"}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
