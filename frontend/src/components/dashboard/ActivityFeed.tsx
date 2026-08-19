import React from 'react';
import { AlertTriangle, LogIn, UserPlus } from 'lucide-react';
import type { ActivityItem } from '@/lib/api';
import { formatRelativeTime, severityClasses } from '@/lib/format';

function iconFor(item: ActivityItem) {
  if (item.type === 'alert') {
    const color = severityClasses(item.severity);
    return <AlertTriangle className={`w-3.5 h-3.5 ${color.text}`} />;
  }
  if (item.type === 'login') return <LogIn className="w-3.5 h-3.5 text-blue-400" />;
  return <UserPlus className="w-3.5 h-3.5 text-emerald-400" />;
}

export function ActivityFeed({ items, loading }: { items: ActivityItem[]; loading: boolean }) {
  return (
    <div className="glass rounded-3xl p-8">
      <div className="font-medium mb-1">RECENT ACTIVITY</div>
      <div className="text-xs text-slate-400 mb-6">Alerts, sign-ins &amp; registrations</div>

      {!loading && items.length === 0 && (
        <div className="text-slate-400 text-sm py-8 text-center">No recent activity.</div>
      )}

      <div className="space-y-4 max-h-[360px] overflow-y-auto pr-1">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
              {iconFor(item)}
            </div>
            <div className="min-w-0">
              <div className="text-sm text-slate-200 truncate">{item.message}</div>
              <div className="text-[11px] text-slate-500">{formatRelativeTime(item.timestamp)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
