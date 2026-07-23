export function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-navy/10 p-4">
      <div className="text-xs uppercase tracking-wide text-navy/50">{label}</div>
      <div className="mt-1 text-2xl font-bold text-navy">{value}</div>
    </div>
  );
}

export function BarList({
  title,
  items,
}: {
  title: string;
  items: { key: string; count: number }[];
}) {
  const max = Math.max(1, ...items.map((i) => i.count));
  return (
    <div className="rounded-xl border border-navy/10 p-4">
      <h2 className="mb-3 text-sm font-semibold text-navy">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-navy/50">Belum ada data.</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.key} className="flex items-center gap-3 text-sm">
              <span className="w-40 shrink-0 truncate text-navy/70">{item.key}</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-navy/10">
                <div
                  className="h-full rounded-full bg-gold"
                  style={{ width: `${(item.count / max) * 100}%` }}
                />
              </div>
              <span className="w-8 text-right font-medium text-navy">{item.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
