import React from 'react';
import { statColorClasses } from '@/lib/format';

export interface StatCardData {
  label: string;
  value: React.ReactNode;
  unit?: string;
  icon: React.ReactNode;
  color: string;
  sub?: string;
}

export function StatCardGrid({ stats, loading }: { stats: StatCardData[]; loading: boolean }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-10">
      {stats.map((stat, index) => (
        <div key={index} className="glass rounded-3xl p-5 flex flex-col">
          <div className={statColorClasses(stat.color).text}>{stat.icon}</div>
          <div className="mt-auto">
            <div className="text-3xl font-semibold tabular-nums tracking-tighter mt-4">
              {loading ? '—' : stat.value}
              {stat.unit && !loading && <span className="text-sm text-slate-400 ml-1">{stat.unit}</span>}
            </div>
            <div className="text-[11px] text-slate-400 mt-1 uppercase tracking-wider">{stat.label}</div>
            {stat.sub && <div className="text-[10px] text-slate-500 mt-0.5">{stat.sub}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}
