export default function FeaturesSection() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-[30px] font-bold text-center mb-3">核心功能</h2>
        <p className="text-base text-lighter text-center mb-14">专为学术写作场景打造的改写引擎</p>
        <div className="grid grid-cols-3 gap-7">
          <div className="bg-surface rounded-lg p-9 border border-border-light">
            <div className="w-11 h-11 bg-primary-light rounded-xl flex items-center justify-center mb-5 text-lg">
              &#9733;
            </div>
            <h3 className="text-[17px] font-semibold mb-2">双模式引擎</h3>
            <p className="text-sm text-muted leading-relaxed">
              Polish 精修润色与 Enhance 去 AI 化增强，两种策略覆盖从初稿打磨到终稿优化的完整流程。
            </p>
          </div>
          <div className="bg-surface rounded-lg p-9 border border-border-light">
            <div className="w-11 h-11 bg-primary-light rounded-xl flex items-center justify-center mb-5 text-lg">
              &#9745;
            </div>
            <h3 className="text-[17px] font-semibold mb-2">术语零丢失</h3>
            <p className="text-sm text-muted leading-relaxed">
              核心技术术语、数据、引用格式完全锁定。改写过程绝不触碰学术内容的严谨性。
            </p>
          </div>
          <div className="bg-surface rounded-lg p-9 border border-border-light">
            <div className="w-11 h-11 bg-primary-light rounded-xl flex items-center justify-center mb-5 text-lg">
              &#9889;
            </div>
            <h3 className="text-[17px] font-semibold mb-2">流式实时输出</h3>
            <p className="text-sm text-muted leading-relaxed">
              点击即开始，逐字实时呈现改写结果。无需漫长等待，所见即所得。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
