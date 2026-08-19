import React, { useMemo } from 'react';
import type { ReportBucket } from '@/lib/api';

interface Series {
  key: keyof ReportBucket;
  label: string;
  color: string; // hex, used directly in the SVG (not a Tailwind class)
}

const SERIES: Series[] = [
  { key: 'avg_aqi', label: 'AQI', color: '#38bdf8' },
  { key: 'avg_pm25', label: 'PM2.5', color: '#f59e0b' },
];

const WIDTH = 640;
const HEIGHT = 220;
const PAD_LEFT = 36;
const PAD_RIGHT = 12;
const PAD_TOP = 16;
const PAD_BOTTOM = 28;

export function LiveChart({ data, loading }: { data: ReportBucket[]; loading: boolean }) {
  const { paths, maxVal, points } = useMemo(() => {
    if (!data || data.length === 0) return { paths: [], maxVal: 0, points: [] as ReportBucket[] };

    const innerW = WIDTH - PAD_LEFT - PAD_RIGHT;
    const innerH = HEIGHT - PAD_TOP - PAD_BOTTOM;
    const allValues = data.flatMap((d) => SERIES.map((s) => Number(d[s.key]) || 0));
    const max = Math.max(10, ...allValues) * 1.15;

    const step = data.length > 1 ? innerW / (data.length - 1) : 0;

    const computed = SERIES.map((s) => {
      const coords = data.map((d, i) => {
        const x = PAD_LEFT + i * step;
        const val = Number(d[s.key]) || 0;
        const y = PAD_TOP + innerH - (val / max) * innerH;
        return `${x},${y}`;
      });
      return { series: s, d: `M${coords.join(' L')}` };
    });

    return { paths: computed, maxVal: max, points: data };
  }, [data]);

  if (loading) {
    return (
      <div className="h-[220px] flex items-center justify-center text-slate-500 text-sm">
        Loading chart data…
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-[220px] flex items-center justify-center text-slate-500 text-sm text-center px-6">
        No historical readings yet for this period.
      </div>
    );
  }

  const gridLines = 4;

  return (
    <div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full h-[220px]" preserveAspectRatio="none">
        {/* grid */}
        {Array.from({ length: gridLines + 1 }).map((_, i) => {
          const y = PAD_TOP + (i * (HEIGHT - PAD_TOP - PAD_BOTTOM)) / gridLines;
          const val = Math.round(maxVal - (i * maxVal) / gridLines);
          return (
            <g key={i}>
              <line x1={PAD_LEFT} y1={y} x2={WIDTH - PAD_RIGHT} y2={y} stroke="#334155" strokeWidth={0.5} />
              <text x={2} y={y + 3} fontSize={9} fill="#64748b">
                {val}
              </text>
            </g>
          );
        })}

        {/* series lines */}
        {paths.map(({ series, d }) => (
          <path key={series.key} d={d} fill="none" stroke={series.color} strokeWidth={2} />
        ))}
      </svg>

      <div className="flex items-center gap-5 mt-2">
        {SERIES.map((s) => (
          <div key={s.key} className="flex items-center gap-1.5 text-xs text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: s.color }} />
            {s.label}
          </div>
        ))}
        <div className="ml-auto text-[11px] text-slate-500">
          {points.length} buckets · {points[0]?.n_readings ?? 0}–{points[points.length - 1]?.n_readings ?? 0} readings/bucket
        </div>
      </div>
    </div>
  );
}
