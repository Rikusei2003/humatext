"use client";

import { useState, useEffect, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [tab, setTab] = useState<"cards" | "create">("cards");
  const [cards, setCards] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [newLimit, setNewLimit] = useState(10);
  const [newCount, setNewCount] = useState(1);
  const [newNote, setNewNote] = useState("");
  const [createdCards, setCreatedCards] = useState<any[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("admin_token");
    if (saved) { setToken(saved); fetchData(saved); }
  }, []);

  const fetchData = async (t: string) => {
    const headers = { Authorization: `Bearer ${t}` };
    const [cRes, sRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/admin/cards?per_page=100`, { headers }),
      fetch(`${API_URL}/api/v1/admin/stats`, { headers }),
    ]);
    if (cRes.ok) { const d = await cRes.json(); setCards(d.items); }
    if (sRes.ok) setStats(await sRes.json());
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    const res = await fetch(`${API_URL}/api/v1/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("admin_token", data.token);
      setToken(data.token);
      fetchData(data.token);
    } else {
      setLoginError("用户名或密码错误");
    }
  };

  const handleCreate = async () => {
    const res = await fetch(`${API_URL}/api/v1/admin/cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ usage_limit: newLimit, count: newCount, note: newNote || null }),
    });
    if (res.ok) {
      const data = await res.json();
      setCreatedCards(data.cards);
      fetchData(token);
      setTab("cards");
    }
  };

  const handleUpdate = async (id: string, limit: number, active: boolean) => {
    await fetch(`${API_URL}/api/v1/admin/cards/${id}?usage_limit=${limit}&is_active=${active}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchData(token);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定删除？")) return;
    await fetch(`${API_URL}/api/v1/admin/cards/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchData(token);
  };

  const copyLink = (key: string) => {
    navigator.clipboard.writeText(`${window.location.origin}/workspace?code=${key}`);
    alert("链接已复制");
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="bg-white border border-border rounded-lg p-8 shadow-card w-full max-w-[360px]">
          <h1 className="text-xl font-bold text-center mb-6">管理后台</h1>
          {loginError && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-md mb-4">{loginError}</div>}
          <form onSubmit={handleLogin} className="space-y-4">
            <input type="text" value={username} onChange={e => setUsername(e.target.value)}
              placeholder="用户名" className="w-full px-3.5 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-primary" />
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="密码" className="w-full px-3.5 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-primary" />
            <button type="submit" className="w-full py-2.5 bg-primary text-white font-semibold rounded-md hover:shadow-button transition-shadow">
              登录
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface pt-20 pb-10">
      <div className="max-w-[1100px] mx-auto px-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold">管理后台</h1>
          <button onClick={() => { localStorage.removeItem("admin_token"); setToken(""); }}
            className="text-xs text-muted hover:text-red-500">退出登录</button>
        </div>

        {stats && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[["总码数", stats.total_cards], ["活跃码", stats.active_cards], ["总改写", stats.total_rewrites], ["今日改写", stats.today_rewrites]].map(([label, val]) => (
              <div key={label} className="bg-white border border-border rounded-lg p-4 text-center shadow-card">
                <div className="text-2xl font-extrabold text-primary">{val}</div>
                <div className="text-xs text-muted mt-1">{label}</div>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2 mb-6">
          <button onClick={() => setTab("cards")}
            className={`px-4 py-2 text-sm rounded-md font-medium ${tab === "cards" ? "bg-primary text-white" : "bg-white border border-border text-muted"}`}>
            码列表
          </button>
          <button onClick={() => { setTab("create"); setCreatedCards([]); }}
            className={`px-4 py-2 text-sm rounded-md font-medium ${tab === "create" ? "bg-primary text-white" : "bg-white border border-border text-muted"}`}>
            生成新码
          </button>
        </div>

        {tab === "create" && (
          <div className="bg-white border border-border rounded-lg p-6 shadow-card max-w-[500px]">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">可用次数</label>
                <input type="number" value={newLimit} onChange={e => setNewLimit(parseInt(e.target.value) || 0)}
                  className="w-full px-3.5 py-2.5 border border-border rounded-md text-sm mt-1" min={1} />
              </div>
              <div>
                <label className="text-sm font-medium">生成数量</label>
                <input type="number" value={newCount} onChange={e => setNewCount(parseInt(e.target.value) || 1)}
                  className="w-full px-3.5 py-2.5 border border-border rounded-md text-sm mt-1" min={1} max={100} />
              </div>
              <div>
                <label className="text-sm font-medium">备注</label>
                <input type="text" value={newNote} onChange={e => setNewNote(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-border rounded-md text-sm mt-1" placeholder="可选" />
              </div>
              <button onClick={handleCreate}
                className="w-full py-2.5 bg-primary text-white font-semibold rounded-md hover:shadow-button transition-shadow">
                生成 {newCount} 个兑换码
              </button>
            </div>
            {createdCards.length > 0 && (
              <div className="mt-6 p-4 bg-green-50 rounded-md">
                <div className="text-sm font-semibold text-green-700 mb-2">生成成功！</div>
                {createdCards.map((c: any) => (
                  <div key={c.card_key} className="text-xs text-green-800 mb-1 flex items-center gap-2">
                    <code className="bg-white px-2 py-0.5 rounded">{c.card_key}</code>
                    <span>×{c.usage_limit}次</span>
                    <button onClick={() => copyLink(c.card_key)} className="text-green-600 underline">复制链接</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "cards" && (
          <div className="bg-white border border-border rounded-lg shadow-card overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border-light text-muted text-left">
                  <th className="p-3 font-medium">兑换码</th>
                  <th className="p-3 font-medium">用量</th>
                  <th className="p-3 font-medium">状态</th>
                  <th className="p-3 font-medium">备注</th>
                  <th className="p-3 font-medium">创建</th>
                  <th className="p-3 font-medium text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                {cards.map(c => (
                  <tr key={c.id} className="border-b border-border-light last:border-0">
                    <td className="p-3"><code className="bg-surface px-1.5 py-0.5 rounded text-xs">{c.card_key}</code></td>
                    <td className="p-3">
                      <span className={c.remaining <= 3 && c.remaining > 0 ? "text-enhance" : c.remaining <= 0 ? "text-red-500" : ""}>
                        {c.usage_count}/{c.usage_limit}
                      </span>
                    </td>
                    <td className="p-3">
                      {c.is_active ? <span className="text-green-600 text-xs">● 激活</span> : <span className="text-red-500 text-xs">● 冻结</span>}
                    </td>
                    <td className="p-3 text-xs text-muted">{c.note || "-"}</td>
                    <td className="p-3 text-xs text-muted">{new Date(c.created_at).toLocaleDateString("zh-CN")}</td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => copyLink(c.card_key)} className="text-xs px-2 py-1 text-primary hover:bg-primary-light rounded">复制</button>
                        <button onClick={() => handleUpdate(c.id, c.usage_limit + 10, c.is_active)}
                          className="text-xs px-2 py-1 text-muted hover:bg-surface rounded">+10次</button>
                        <button onClick={() => handleUpdate(c.id, c.usage_limit, !c.is_active)}
                          className={`text-xs px-2 py-1 rounded ${c.is_active ? "text-enhance hover:bg-yellow-50" : "text-green-600 hover:bg-green-50"}`}>
                          {c.is_active ? "冻结" : "激活"}
                        </button>
                        <button onClick={() => handleDelete(c.id)} className="text-xs px-2 py-1 text-red-400 hover:bg-red-50 rounded">删</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
