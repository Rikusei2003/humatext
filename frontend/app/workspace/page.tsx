"use client";

import { useState, useCallback, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

type Mode = "polish" | "enhance";

export default function WorkspacePage() {
  const [cardKey, setCardKey] = useState("");
  const [cardInfo, setCardInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<Mode>("polish");
  const [lang, setLang] = useState<"zh" | "en">("zh");
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [phase, setPhase] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("card_key");
    if (saved) setCardKey(saved);
    setLoading(false);
  }, []);

  const verifyCard = useCallback(async (key: string) => {
    if (!key) return;
    const res = await fetch(`${API_URL}/api/v1/card/verify/${key}`);
    const data = await res.json();
    if (data.valid) {
      localStorage.setItem("card_key", key);
      setCardInfo(data);
      setError("");
    } else {
      setCardInfo(null);
      if (cardKey) setError("兑换码无效");
    }
    setLoading(false);
  }, [cardKey]);

  useEffect(() => {
    if (cardKey) { setLoading(true); verifyCard(cardKey); }
    else { setCardInfo(null); setLoading(false); }
  }, [cardKey, verifyCard]);

  const handleSubmitKey = (e: React.FormEvent) => {
    e.preventDefault();
    const input = (e.target as any).card_input.value.trim();
    if (input) setCardKey(input);
  };

  const handleRewrite = useCallback(async () => {
    if (!input.trim() || !cardKey) return;
    setOutput("");
    setError("");
    setStreaming(true);
    setPhase("");

    try {
      const res = await fetch(`${API_URL}/api/v1/card/rewrite/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_key: cardKey, mode, source_language: lang, input_text: input }),
      });
      if (!res.ok) {
        setError(`请求失败: ${res.status}`);
        setStreaming(false);
        return;
      }
      const reader = res.body?.getReader();
      if (!reader) { setError("Stream not available"); setStreaming(false); return; }

      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.phase) setPhase(data.phase);
              if (data.text) setOutput(prev => prev + data.text);
              if (data.message) setPhase(data.message);
              if (data.code) setError(data.message || data.code);
              if (data.remaining !== undefined) {
                setCardInfo((prev: any) => ({ ...prev, usage_count: (prev?.usage_limit || 0) - data.remaining, remaining: data.remaining }));
              }
            } catch {}
          }
        }
      }
    } catch (e: any) { setError(e.message || "网络错误"); }
    setStreaming(false);
    setPhase("");
    verifyCard(cardKey);
  }, [input, mode, lang, cardKey, verifyCard]);

  const charCount = input.replace(/\s/g, "").length;

  if (loading) return <div className="min-h-screen flex items-center justify-center pt-16"><div className="text-muted">加载中...</div></div>;

  return (
    <div className="min-h-screen bg-surface pt-20 pb-10">
      <div className="max-w-[960px] mx-auto px-6">
        {!cardInfo ? (
          <div className="max-w-[400px] mx-auto mt-20">
            <div className="bg-white border border-border rounded-lg p-8 shadow-card text-center">
              <h1 className="text-xl font-bold mb-2">欢迎使用 HumaText</h1>
              <p className="text-sm text-muted mb-6">请输入您的兑换码开始使用</p>
              {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-md mb-4">{error}</div>}
              <form onSubmit={handleSubmitKey}>
                <input
                  name="card_input"
                  placeholder="兑换码"
                  className="w-full px-4 py-3 border border-border rounded-md text-sm text-center tracking-widest focus:outline-none focus:border-primary mb-4"
                  autoFocus
                />
                <button type="submit" className="w-full py-2.5 bg-primary text-white font-semibold rounded-md hover:shadow-button transition-shadow">
                  验证兑换码
                </button>
              </form>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-4 mb-6 flex-wrap">
              <div className="flex bg-white border border-border rounded-md p-1">
                <button onClick={() => setMode("polish")} className={`px-4 py-2 text-sm font-medium rounded transition-colors ${mode === "polish" ? "bg-primary text-white" : "text-muted hover:text-foreground"}`}>Polish 润色</button>
                <button onClick={() => setMode("enhance")} className={`px-4 py-2 text-sm font-medium rounded transition-colors ${mode === "enhance" ? "bg-enhance text-white" : "text-muted hover:text-foreground"}`}>Enhance 增强</button>
              </div>
              <select value={lang} onChange={e => setLang(e.target.value as "zh" | "en")} className="px-3 py-2 border border-border rounded-md text-sm bg-white">
                <option value="zh">中文</option>
                <option value="en">English</option>
              </select>
              <span className="text-xs text-muted">{charCount} 字</span>
              <div className="ml-auto flex items-center gap-3 text-xs">
                <span className="text-muted">码: <code className="bg-surface px-1.5 py-0.5 rounded">{cardKey}</code></span>
                <span className={`font-semibold ${cardInfo.remaining <= 3 ? "text-red-500" : "text-primary"}`}>
                  剩余 {cardInfo.remaining}/{cardInfo.usage_limit} 次
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white border border-border rounded-lg p-6 shadow-card">
                <textarea
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder={lang === "zh" ? "在此粘贴要改写的学术文本..." : "Paste academic text here..."}
                  className="w-full h-[400px] text-sm leading-relaxed resize-none focus:outline-none"
                  disabled={streaming}
                />
              </div>
              <div className="bg-white border border-border rounded-lg p-6 shadow-card relative">
                <div className="h-[400px] overflow-auto">
                  {error ? <div className="text-red-500 text-sm">{error}</div>
                    : output ? <div className="text-sm leading-relaxed whitespace-pre-wrap">{output}</div>
                    : <div className="text-sm text-lighter italic">{streaming ? "正在改写..." : "改写结果将在这里实时显示"}</div>}
                </div>
                {streaming && phase && <div className="absolute bottom-4 left-6 right-6"><span className="text-xs text-muted bg-surface px-2 py-1 rounded">{phase}</span></div>}
              </div>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={handleRewrite}
                disabled={streaming || !input.trim() || cardInfo.remaining <= 0}
                className="px-12 py-3 bg-primary text-white font-semibold rounded-md hover:shadow-button transition-shadow disabled:opacity-50"
              >
                {cardInfo.remaining <= 0 ? "次数已用完" : streaming ? "改写中..." : mode === "polish" ? "开始润色" : "开始增强改写"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
