import { useMemo, useState } from "react";

interface Point {
  label: string;
  value: number;
  color?: string;
}

const PALETTE = ["var(--indigo)", "var(--blue)", "var(--green)", "var(--amber)", "var(--rose)"];

interface Tip {
  x: number;
  y: number;
  title: string;
  sub?: string;
}

function ChartTip({ tip }: { tip: Tip | null }) {
  if (!tip) return null;
  return (
    <div className="chart-tooltip" style={{ left: tip.x, top: tip.y }}>
      <div className="tt-title">{tip.title}</div>
      {tip.sub && <div className="tt-sub">{tip.sub}</div>}
    </div>
  );
}

function useTip() {
  const [tip, setTip] = useState<Tip | null>(null);
  function show(e: React.MouseEvent, title: string, sub?: string) {
    setTip({ x: e.clientX + 14, y: e.clientY - 10, title, sub });
  }
  function hide() {
    setTip(null);
  }
  return { tip, show, hide };
}

export function AreaChart({ data, height = 220 }: { data: Point[]; height?: number }) {
  const { tip, show, hide } = useTip();
  const W = 720;
  const H = height;
  const padX = 8;
  const padTop = 16;
  const padBottom = 26;
  const max = Math.max(...data.map((d) => d.value), 1);
  const min = 0;
  const span = max - min || 1;
  const stepX = (W - padX * 2) / Math.max(data.length - 1, 1);
  const x = (i: number) => padX + i * stepX;
  const y = (v: number) => padTop + (H - padTop - padBottom) * (1 - (v - min) / span);
  const path = useMemo(() => {
    const pts = data.map((d, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(d.value)}`);
    return pts.join(" ");
  }, [data]);
  const area = `${path} L ${x(data.length - 1)} ${H - padBottom} L ${x(0)} ${H - padBottom} Z`;
  const gridLines = 4;

  return (
    <div style={{ position: "relative" }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }} role="img" aria-label="Trend chart">
        <defs>
          <linearGradient id="area-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.28" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {Array.from({ length: gridLines + 1 }).map((_, gi) => {
          const gy = padTop + ((H - padTop - padBottom) / gridLines) * gi;
          return (
            <g key={gi}>
              <line x1={padX} x2={W - padX} y1={gy} y2={gy} stroke="var(--border)" strokeDasharray="3 4" />
              <text x={padX} y={gy - 5} fontSize="10" fill="var(--text-faint)">
                {Math.round(max - (max / gridLines) * gi)}
              </text>
            </g>
          );
        })}
        <path d={area} fill="url(#area-fill)" />
        <path d={path} fill="none" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" />
        {data.map((d, i) => (
          <circle
            key={`${d.label}-${i}`}
            cx={x(i)}
            cy={y(d.value)}
            r="4"
            fill="var(--surface)"
            stroke="var(--primary)"
            strokeWidth="2.5"
            onMouseEnter={(e) => show(e, d.label, String(d.value))}
            onMouseMove={(e) => show(e, d.label, String(d.value))}
            onMouseLeave={hide}
            style={{ cursor: "pointer" }}
          />
        ))}
        {data.map((d, i) => (
          <text
            key={`x-${d.label}-${i}`}
            x={x(i)}
            y={H - 8}
            fontSize="10"
            fill="var(--text-faint)"
            textAnchor={i === 0 ? "start" : i === data.length - 1 ? "end" : "middle"}
          >
            {d.label}
          </text>
        ))}
      </svg>
      <ChartTip tip={tip} />
    </div>
  );
}

export function BarChart({ data, height = 220, money = false }: { data: Point[]; height?: number; money?: boolean }) {
  const { tip, show, hide } = useTip();
  const W = 720;
  const H = height;
  const max = Math.max(...data.map((d) => d.value), 1);
  const slotW = W / data.length;
  const barW = Math.min(slotW * 0.5, 56);
  const base = H - 26;
  const fmt = (v: number) => (money ? `$${v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v}` : String(v));

  return (
    <div style={{ position: "relative" }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }} role="img" aria-label="Bar chart">
        <line x1="0" x2={W} y1={base} y2={base} stroke="var(--border)" />
        {data.map((d, i) => {
          const barH = Math.max((d.value / max) * (base - 14), 4);
          const cx = slotW * i + slotW / 2;
          return (
            <g key={`${d.label}-${i}`}>
              <rect
                x={cx - barW / 2}
                y={base - barH}
                width={barW}
                height={barH}
                rx="6"
                fill={d.color ?? PALETTE[i % PALETTE.length]}
                onMouseEnter={(e) => show(e, d.label, fmt(d.value))}
                onMouseMove={(e) => show(e, d.label, fmt(d.value))}
                onMouseLeave={hide}
                style={{ cursor: "pointer" }}
              />
              <text x={cx} y={base + 16} fontSize="10" fill="var(--text-faint)" textAnchor="middle">
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
      <ChartTip tip={tip} />
    </div>
  );
}

export function DonutChart({
  data,
  size = 190,
  centerLabel,
  centerValue,
}: {
  data: Point[];
  size?: number;
  centerLabel?: string;
  centerValue?: string;
}) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const r = 80;
  const cx = size / 2;
  const cy = size / 2;
  const C = 2 * Math.PI * r;
  let acc = 0;

  return (
    <div className="donut-wrap" style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap" }}>
      <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
        <svg width={size} height={size}>
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--surface-3)" strokeWidth="18" />
          {data.map((d, i) => {
            const frac = d.value / total;
            const dash = frac * C;
            const offset = -acc * C;
            acc += frac;
            const el = (
              <circle
                key={`${d.label}-${i}`}
                cx={cx}
                cy={cy}
                r={r}
                fill="none"
                stroke={d.color ?? PALETTE[i % PALETTE.length]}
                strokeWidth="18"
                strokeDasharray={`${dash} ${C - dash}`}
                strokeDashoffset={offset}
                transform={`rotate(-90 ${cx} ${cy})`}
                style={{ transition: "stroke-dasharray 0.5s ease" }}
              />
            );
            return el;
          })}
          <text x={cx} y={cy - 2} textAnchor="middle" fontSize="22" fontWeight="800" fill="var(--text)">
            {centerValue}
          </text>
          {centerLabel && (
            <text x={cx} y={cy + 16} textAnchor="middle" fontSize="11" fill="var(--text-muted)">
              {centerLabel}
            </text>
          )}
        </svg>
      </div>
      <div className="donut-legend">
        {data.map((d, i) => (
          <div key={`${d.label}-${i}`} className="donut-legend-item">
            <span className="donut-legend-swatch" style={{ background: d.color ?? PALETTE[i % PALETTE.length] }} />
            <span className="lbl">{d.label}</span>
            <span className="val">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FunnelBars({ data }: { data: Point[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {data.map((d, i) => {
        const prev = i === 0 ? d.value : data[i - 1].value;
        const pct = i === 0 || prev <= 0 ? (d.value > 0 ? 100 : 0) : Math.round((d.value / prev) * 100);
        const share = Math.round((d.value / max) * 100);
        return (
          <div key={`${d.label}-${i}`} className="funnel-step">
            <div className="funnel-label">
              {d.label}
              {i > 0 && <span className="muted"> · {pct}% of previous</span>}
            </div>
            <div className="funnel-track">
              <div className="funnel-bar" style={{ width: `${share}%`, background: "var(--primary-grad)" }} />
            </div>
            <div className="funnel-value">{d.value}</div>
          </div>
        );
      })}
    </div>
  );
}

export function MiniBars({ data }: { data: Point[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <ul className="source-list">
      {data.map((d, i) => (
        <li key={`${d.label}-${i}`} className="source-row">
          <span className="source-name">{d.label}</span>
          <span className="mini-track">
            <span className="mini-fill" style={{ width: `${Math.max((d.value / max) * 100, 3)}%` }} />
          </span>
          <span className="source-count">{d.value}</span>
        </li>
      ))}
    </ul>
  );
}