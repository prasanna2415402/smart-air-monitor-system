import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import type { AlertLogItem } from '@/lib/api';
import { formatRelativeTime, severityClasses } from '@/lib/format';

interface Props {
  alerts: AlertLogItem[];
  canAcknowledge: boolean;
  onAcknowledge: (id: number) => Promise<void>;
}

export function AlertPanel({ alerts, canAcknowledge, onAcknowledge }: Props) {
  const [acking, setAcking] = useState<number | null>(null);

  const handleAck = async (id: number) => {
    setAcking(id);
    try {
      await onAcknowledge(id);
    } finally {
      setAcking(null);
    }
  };

  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="font-medium flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            ACTIVE ALERTS
            <span className="bg-red-500/20 text-red-400 text-[10px] px-2 py-px rounded">
              {alerts.length}
            </span>
          </div>
          <div className="text-xs text-slate-400">Unacknowledged threshold breaches</div>
        </div>
      </div>

      {alerts.length === 0 && (
        <div className="flex items-center gap-2 text-emerald-400 text-sm py-10 justify-center">
          <CheckCircle2 className="w-5 h-5" /> All clear — no active alerts.
        </div>
      )}

      <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
        {alerts.map((alert) => {
          const color = severityClasses(alert.severity);
          return (
            <div
              key={alert.id}
              className={`bg-slate-950/60 border ${color.border} rounded-2xl p-4`}
            >
              <div className="flex justify-between items-start gap-3">
                <div className="flex gap-3">
                  <AlertTriangle className={`w-4 h-4 mt-0.5 ${color.text} flex-shrink-0`} />
                  <div>
                    <div className="text-sm font-medium">{alert.message}</div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      {alert.station_name} • {alert.parameter}
                    </div>
                    {alert.recommendation && (
                      <div className="text-xs text-slate-500 mt-1">{alert.recommendation}</div>
                    )}
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className={`text-[10px] uppercase px-2 py-0.5 rounded ${color.bg} ${color.text}`}>
                    {alert.severity}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">{formatRelativeTime(alert.created_at)}</div>
                </div>
              </div>
              {canAcknowledge && (
                <button
                  onClick={() => handleAck(alert.id)}
                  disabled={acking === alert.id}
                  className="mt-3 text-[11px] bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-xl transition-colors disabled:opacity-50"
                >
                  {acking === alert.id ? 'ACKNOWLEDGING…' : 'ACKNOWLEDGE'}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
