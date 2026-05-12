export default function ModesSection() {
  return (
    <section className="py-20 bg-surface">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="grid grid-cols-2 gap-7">
          <div className="bg-white border border-border rounded-lg p-10 shadow-card border-t-[3px] border-t-primary">
            <h3 className="text-[22px] font-bold mb-3">&#9998; Polish 润色模式</h3>
            <p className="text-muted leading-relaxed mb-5 text-[15px]">
              保留原意，逐句精修。提升词汇层次、优化句式结构，让学术表达更专业流畅。
            </p>
            <span className="inline-block px-3.5 py-1.5 bg-border-light text-[13px] rounded-sm text-muted font-medium">
              保守型改写
            </span>
          </div>
          <div className="bg-white border border-border rounded-lg p-10 shadow-card border-t-[3px] border-t-enhance">
            <h3 className="text-[22px] font-bold mb-3">&#128640; Enhance 增强模式</h3>
            <p className="text-muted leading-relaxed mb-5 text-[15px]">
              深度重组句子，消除 AI 写作痕迹。两轮改写流程确保输出文本自然、有人味。
            </p>
            <span className="inline-block px-3.5 py-1.5 bg-border-light text-[13px] rounded-sm text-muted font-medium">
              激进型改写
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
