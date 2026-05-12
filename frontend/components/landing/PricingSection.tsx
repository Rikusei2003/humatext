import Link from "next/link";

export default function PricingSection() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-[30px] font-bold text-center mb-14">定价方案</h2>
        <div className="flex justify-center gap-7 flex-wrap">
          <div className="flex-1 min-w-[260px] max-w-[340px] bg-white border border-border rounded-lg p-10 text-center shadow-card">
            <h3 className="text-xl font-bold mb-2">免费入门</h3>
            <div className="text-[40px] font-extrabold my-4">
              &#165;0 <span className="text-base font-normal text-muted">/ 月</span>
            </div>
            <ul className="list-none p-0 mb-7 text-left text-sm">
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">每日 2 次改写</li>
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">Polish 模式可用</li>
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">单次最多 500 字</li>
            </ul>
            <Link
              href="/register"
              className="block w-full py-3 text-sm font-semibold text-foreground border-2 border-border rounded-md hover:border-primary transition-colors"
            >
              免费开始
            </Link>
          </div>

          <div className="flex-1 min-w-[260px] max-w-[340px] bg-white border-2 border-primary rounded-lg p-10 text-center shadow-featured">
            <h3 className="text-xl font-bold mb-2">专业会员</h3>
            <div className="text-[40px] font-extrabold my-4">
              &#165;29 <span className="text-base font-normal text-muted">/ 月</span>
            </div>
            <ul className="list-none p-0 mb-7 text-left text-sm">
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">无限次改写</li>
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">全部模式可用</li>
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">单次最多 5000 字</li>
              <li className="py-2 text-muted before:content-['✓_'] before:text-primary">优先处理队列</li>
            </ul>
            <Link
              href="/register"
              className="block w-full py-3 text-sm font-semibold text-white bg-primary rounded-md hover:shadow-button transition-shadow"
            >
              订阅会员
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
