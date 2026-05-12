import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="pt-32 pb-20 text-center bg-gradient-to-b from-surface to-white">
      <div className="max-w-[1200px] mx-auto px-6">
        <h1 className="text-[52px] font-extrabold leading-tight text-[#0f172a] tracking-tight mb-4">
          让学术表达<span className="text-primary">更精准、更自然</span>
        </h1>
        <p className="text-lg text-muted max-w-[540px] mx-auto mb-10 leading-relaxed">
          基于 AI 的双模式学术文本改写 — 润色与去 AI 化增强，保持学术严谨的同时让文字焕发生命力
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            href="/register"
            className="inline-block px-10 py-3.5 bg-primary text-white font-semibold rounded-md hover:shadow-button transition-shadow"
          >
            开始改写
          </Link>
          <Link
            href="/pricing"
            className="inline-block px-10 py-3.5 bg-white text-foreground font-semibold rounded-md border-2 border-border hover:border-primary transition-colors"
          >
            了解更多
          </Link>
        </div>
      </div>
    </section>
  );
}
