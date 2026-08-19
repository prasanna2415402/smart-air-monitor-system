import React from 'react';
import type { DashboardSummary } from '@/lib/api';
import { alertLevelClasses, formatRelativeTime } from '@/lib/format';

type LiveReading = DashboardSummary['live_readings'][number];

function Metric({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-400">{label}</span>
      <span className="font-medium font-mono">
        {value}
        {unit && <span className="text-slate-500 ml-0.5">{unit}</span>}
      </span>
    </div>
  );
}

export function LiveReadings({ readings, loading }: { readings: LiveReading[]; loading: boolean }) {
  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex justify-between mb-6">
        <div className="font-medium">LIVE SENSOR READINGS</div>
        <div className="text-xs bg-slate-800 px-4 flex items-center rounded-3xl">
          {loading ? 'LOADING…' : `${readings.length} STATION${readings.length === 1 ? '' : 'S'} REPORTING`}
        </div>
      </div>

      {!loading && readings.length === 0 && (
        <div className="text-slate-400 text-sm py-10 text-center">
          No stations with recent readings yet. Ingest data via{' '}
          <code className="text-slate-300">POST /api/sensors/ingest/</code>, or run{' '}
          <code className="text-slate-300">python manage.py simulate_live_data</code> to see live cards here.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {readings.map(({ station, reading }) => {
          const color = alertLevelClasses(reading.alert_level);
          return (
            <div key={station.id} className="bg-slate-950/60 border border-slate-700 rounded-2xl p-5">
              <div className="flex justify-between items-center mb-4">
                <div className="text-xs text-slate-400">{station.name}</div>
                <div className="text-[10px] text-slate-500">{formatRelativeTime(reading.timestamp)}</div>
              </div>

              <div className="flex justify-between items-center mb-5">
                <div>
                  <div className={`flex items-center gap-2 ${color.text}`}>
                    <span className="font-mono text-2xl font-medium">{reading.temperature.toFixed(1)}°C</span>
                  </div>
                  <div className="text-xs text-slate-500">TEMPERATURE</div>
                </div>
                <div className={`px-3 py-1 text-xs rounded-3xl ${color.bg} ${color.text}`}>
                  {(reading.alert_level ?? 'UNKNOWN').replace('_', ' ')} · AQI {reading.aqi_score ?? '—'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                <Metric label="CO₂" value={Math.round(reading.co2_ppm).toString()} unit="ppm" />
                <Metric label="CO" value={reading.co_ppm.toFixed(1)} unit="ppm" />
                <Metric label="PM 2.5" value={reading.pm25.toFixed(1)} unit="µg/m³" />
                <Metric label="PM 10" value={reading.pm10.toFixed(1)} unit="µg/m³" />
                <Metric label="VOC" value={Math.round(reading.voc_index).toString()} unit="idx" />
                <Metric label="Humidity" value={reading.humidity.toFixed(0)} unit="%" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
