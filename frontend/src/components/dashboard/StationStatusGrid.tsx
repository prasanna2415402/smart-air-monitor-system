import React from 'react';
import { Radio, WifiOff } from 'lucide-react';
import type { StationStatus } from '@/lib/api';
import { formatRelativeTime, alertLevelClasses } from '@/lib/format';

export function StationStatusGrid({ stations, loading }: { stations: StationStatus[]; loading: boolean }) {
  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="font-medium">STATION STATUS</div>
          <div className="text-xs text-slate-400">Online/offline health &amp; sensor coverage</div>
        </div>
      </div>

      {!loading && stations.length === 0 && (
        <div className="text-slate-400 text-sm py-10 text-center">No stations configured yet.</div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {stations.map((station) => {
          const color = alertLevelClasses(station.last_alert_level);
          return (
            <div key={station.id} className="bg-slate-950/60 border border-slate-700 rounded-2xl p-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-sm font-medium">{station.name}</div>
                  <div className="text-xs text-slate-500 font-mono">{station.code}</div>
                </div>
                <div
                  className={`flex items-center gap-1.5 text-[10px] uppercase px-2 py-1 rounded-full ${
                    station.is_online
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'bg-slate-700/50 text-slate-400'
                  }`}
                >
                  {station.is_online ? <Radio className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                  {station.is_online ? 'Online' : 'Offline'}
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between text-xs">
                <div className="text-slate-400">
                  Sensors{' '}
                  <span className="text-slate-200 font-mono">
                    {station.online_sensor_count}/{station.sensor_count}
                  </span>{' '}
                  online
                </div>
                {station.last_alert_level && (
                  <div className={color.text}>{station.last_alert_level.replace('_', ' ')}</div>
                )}
              </div>

              <div className="mt-2 text-[11px] text-slate-500">
                Last updated {formatRelativeTime(station.last_reading_at)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
