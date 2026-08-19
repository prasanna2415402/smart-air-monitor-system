'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Activity,
  AlertTriangle,
  Building2,
  Gauge,
  RefreshCw,
  Users,
  Wind,
} from 'lucide-react';
import Link from 'next/link';

import {
  acknowledgeAlert,
  approveUser,
  getDashboardSummary,
  getReadingsReport,
  isAuthenticated,
  logoutUser,
  rejectUser,
  ApiError,
  type DashboardSummary,
  type ReportBucket,
} from '@/lib/api';

import { alertLevelClasses } from '@/lib/format';

import {
  StatCardGrid,
  type StatCardData,
} from '@/components/dashboard/StatCard';

import { AlertPanel } from '@/components/dashboard/AlertPanel';
import { StationStatusGrid } from '@/components/dashboard/StationStatusGrid';
import { LiveChart } from '@/components/dashboard/LiveChart';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { UserMenu } from '@/components/dashboard/UserMenu';
import { PendingRegistrations } from '@/components/dashboard/PendingRegistrations';
import { LiveReadings } from '@/components/dashboard/LiveReadings';

const REFRESH_SECONDS = 15;

export default function DashboardPage() {
  const router = useRouter();

  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  const [chart, setChart] = useState<ReportBucket[]>([]);

  const [period, setPeriod] = useState<
    'daily' | 'weekly' | 'monthly'
  >('daily');

  const [loading, setLoading] = useState(true);

  const [chartLoading, setChartLoading] = useState(true);

  const [error, setError] = useState('');

  const [autoRefresh, setAutoRefresh] = useState(true);

  const [countdown, setCountdown] =
    useState(REFRESH_SECONDS);

  const countdownRef =
    useRef<ReturnType<typeof setInterval> | null>(null);

  // ------------------------------------------------------------
  // LOAD SUMMARY
  // ------------------------------------------------------------

  const loadSummary = useCallback(async () => {
    try {
      const data = await getDashboardSummary();

      setSummary(data);
      setError('');
    } catch (err) {
      if (
        err instanceof ApiError &&
        err.status === 401
      ) {
        router.push('/login');
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load dashboard data.'
      );
    } finally {
      setLoading(false);
      setCountdown(REFRESH_SECONDS);
    }
  }, [router]);

  // ------------------------------------------------------------
  // LOAD CHART
  // ------------------------------------------------------------

  const loadChart = useCallback(
    async (
      selectedPeriod:
        | 'daily'
        | 'weekly'
        | 'monthly'
    ) => {
      setChartLoading(true);

      try {
        const data =
          await getReadingsReport(selectedPeriod);

        setChart(data);
      } catch {
        setChart([]);
      } finally {
        setChartLoading(false);
      }
    },
    []
  );

  // ------------------------------------------------------------
  // INITIAL LOAD
  // ------------------------------------------------------------

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadSummary();
  }, [router, loadSummary]);

  // ------------------------------------------------------------
  // LOAD CHART WHEN PERIOD CHANGES
  // ------------------------------------------------------------

  useEffect(() => {
    if (!isAuthenticated()) {
      return;
    }

    loadChart(period);
  }, [period, loadChart]);

  // ------------------------------------------------------------
  // AUTO REFRESH
  // ------------------------------------------------------------

  useEffect(() => {
    if (!autoRefresh) {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
        countdownRef.current = null;
      }

      return;
    }

    countdownRef.current = setInterval(() => {
      setCountdown((current) => {
        if (current <= 1) {
          loadSummary();
          return REFRESH_SECONDS;
        }

        return current - 1;
      });
    }, 1000);

    return () => {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
        countdownRef.current = null;
      }
    };
  }, [autoRefresh, loadSummary]);

  // ------------------------------------------------------------
  // LOGOUT
  // ------------------------------------------------------------

  const handleLogout = async () => {
    await logoutUser();
    router.push('/login');
  };

  // ------------------------------------------------------------
  // ACKNOWLEDGE ALERT
  // ------------------------------------------------------------

  const handleAcknowledge = async (id: number) => {
    try {
      await acknowledgeAlert(id);
      await loadSummary();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to acknowledge alert.'
      );
    }
  };

  // ------------------------------------------------------------
  // APPROVE USER
  // ------------------------------------------------------------

  const handleApprove = async (id: string) => {
    try {
      await approveUser(id);
      await loadSummary();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to approve user.'
      );
    }
  };

  // ------------------------------------------------------------
  // REJECT USER
  // ------------------------------------------------------------

  const handleReject = async (
    id: string,
    reason: string
  ) => {
    try {
      await rejectUser(id, reason);
      await loadSummary();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to reject user.'
      );
    }
  };

  // ------------------------------------------------------------
  // DASHBOARD VALUES
  // ------------------------------------------------------------

  const aqiColor = alertLevelClasses(
    summary?.current_alert_level ?? null
  );

  const role =
    summary?.current_user?.role;

  const isAdmin =
    role === 'ADMIN';

  const canAcknowledge =
    role === 'ADMIN' ||
    role === 'OPERATOR';

  // ------------------------------------------------------------
  // SAFE STAT VALUES
  // ------------------------------------------------------------

  const stationsOnline =
    summary?.stats?.stations_online ?? 0;

  const stationsTotal =
    summary?.stats?.stations_total ?? 0;

  const sensorsOnline =
    summary?.stats?.sensors_online ?? 0;

  const sensorsTotal =
    summary?.stats?.sensors_total ?? 0;

  const usersTotal =
    summary?.stats?.users_total ?? 0;

  const pendingApprovals =
    summary?.stats?.pending_approvals ?? 0;

  const activeAlerts =
    summary?.stats?.active_alerts ?? 0;

  const criticalAlerts =
    summary?.stats?.alerts_critical ?? 0;

  const avgAqi =
    summary?.stats?.avg_aqi_24h ?? '—';

  const todayReadings =
    summary?.stats?.today_readings ?? 0;

  // ------------------------------------------------------------
  // STAT CARDS
  // ------------------------------------------------------------

  const stats: StatCardData[] = [
  {
    label: 'Stations Online',
    value:
      String(stationsOnline) +
      '/' +
      String(stationsTotal),
    icon: <Building2 className="w-5 h-5" />,
    color: 'sky',
  },

  {
    label: 'Sensors Online',
    value:
      String(sensorsOnline) +
      '/' +
      String(sensorsTotal),
    icon: <Activity className="w-5 h-5" />,
    color: 'emerald',
  },

  {
    label: 'Users',
    value: String(usersTotal),
    sub:
      String(pendingApprovals) +
      ' pending',
    icon: <Users className="w-5 h-5" />,
    color: 'amber',
  },

  {
    label: 'Active Alerts',
    value: String(activeAlerts),
    sub:
      String(criticalAlerts) +
      ' critical',
    icon: (
      <AlertTriangle className="w-5 h-5" />
    ),
    color: 'red',
  },

  {
    label: 'Avg AQI (24h)',
    value: String(avgAqi),
    icon: <Gauge className="w-5 h-5" />,
    color: 'violet',
  },

  {
    label: "Today's Readings",
    value: String(todayReadings),
    icon: <Wind className="w-5 h-5" />,
    color: 'teal',
  },
];
  // ------------------------------------------------------------
  // UI
  // ------------------------------------------------------------

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* TOP NAVIGATION */}

      <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">

        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between gap-6">

          <div className="flex items-center gap-4">

            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center font-bold">
              A
            </div>

            <div>

              <div className="font-semibold tracking-wider text-sm">
                SMART AIR MONITOR
              </div>

              <div className="text-[10px] text-slate-400 tracking-[2px]">
                LIVE INDUSTRIAL DASHBOARD
              </div>

            </div>

          </div>

          <div className="flex items-center gap-3 md:gap-6 text-sm flex-wrap">

            <button
              type="button"
              onClick={() => {
                setAutoRefresh(
                  (current) => !current
                );
              }}
              className="flex items-center gap-2 text-slate-400 hover:text-slate-200 text-xs"
              title="Toggle auto-refresh"
            >

              <span
                className={
                  'w-2 h-2 rounded-full ' +
                  (autoRefresh
                    ? 'bg-emerald-400 animate-pulse'
                    : 'bg-slate-600')
                }
              />

              {autoRefresh
                ? 'AUTO ' +
                  String(countdown) +
                  's'
                : 'PAUSED'}

            </button>

            <button
              type="button"
              onClick={loadSummary}
              className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300"
            >

              <RefreshCw
                className={
                  'w-3.5 h-3.5 ' +
                  (loading
                    ? 'animate-spin'
                    : '')
                }
              />

              {error
                ? 'RETRY'
                : 'REFRESH'}

            </button>

            <Link
              href="/signup"
              className="hidden md:flex items-center gap-2 px-5 py-2 bg-slate-800 hover:bg-slate-700 rounded-2xl text-xs tracking-wider transition-colors"
            >

              <Users className="w-4 h-4" />

              ADD USER

            </Link>

            {summary?.current_user && (
              <UserMenu
                user={summary.current_user}
                onLogout={handleLogout}
              />
            )}

          </div>

        </div>

      </header>

      {/* MAIN */}

      <main className="max-w-7xl mx-auto px-6 py-8">

        {/* ERROR */}

        {error && (
          <div className="mb-8 flex items-center gap-3 bg-red-500/10 border border-red-500/30 text-red-400 px-5 py-4 rounded-2xl text-sm">

            <AlertTriangle className="w-5 h-5 flex-shrink-0" />

            {error}

          </div>
        )}

        {/* PAGE HEADER */}

        <div className="flex flex-wrap justify-between items-end gap-6 mb-8">

          <div>

            <div className="uppercase text-blue-400 text-xs tracking-[2px] font-medium">

              WELCOME BACK

              {summary?.current_user
                ? ', ' +
                  summary.current_user.full_name
                    .split(' ')[0]
                    .toUpperCase()
                : ''}

            </div>

            <h1 className="text-4xl md:text-5xl font-semibold tracking-tighter text-white">
              Facility Overview
            </h1>

          </div>

          <div className="text-right">

            <div className="text-xs text-slate-400">
              CURRENT AIR QUALITY INDEX
            </div>

            <div
              className={
                'text-5xl md:text-6xl font-mono font-semibold ' +
                aqiColor.text +
                ' tracking-tighter'
              }
            >
              {loading
                ? '—'
                : summary?.current_aqi ?? '—'}
            </div>

            <div
              className={
                'text-xs ' +
                aqiColor.text
              }
            >

              {summary?.current_alert_level
                ? summary.current_alert_level.replace(
                    '_',
                    ' '
                  ) +
                  ' • ' +
                  String(activeAlerts) +
                  ' ALERT' +
                  (activeAlerts === 1
                    ? ''
                    : 'S')
                : 'NO DATA YET'}

            </div>

          </div>

        </div>

        {/* STAT CARDS */}

        <StatCardGrid
          stats={stats}
          loading={loading}
        />

        {/* CONTENT GRID */}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

          {/* LEFT */}

          <div className="lg:col-span-7 space-y-6">

            {/* LIVE READINGS */}

            <LiveReadings
              readings={
                summary?.live_readings ?? []
              }
              loading={loading}
            />

            {/* CHART */}

            <div className="glass rounded-3xl p-8">

              <div className="flex justify-between items-center mb-4 gap-4 flex-wrap">

                <div>

                  <div className="font-medium">
                    AIR QUALITY TREND
                  </div>

                  <div className="text-xs text-slate-400">
                    AQI &amp; PM2.5 from historical database readings
                  </div>

                </div>

                <div className="flex gap-1 bg-slate-900/60 rounded-xl p-1">

                  {(
                    [
                      'daily',
                      'weekly',
                      'monthly',
                    ] as const
                  ).map((p) => (

                    <button
                      type="button"
                      key={p}
                      onClick={() => {
                        setPeriod(p);
                      }}
                      className={
                        'text-[11px] uppercase px-3 py-1.5 rounded-lg transition-colors ' +
                        (period === p
                          ? 'bg-blue-600 text-white'
                          : 'text-slate-400 hover:text-slate-200')
                      }
                    >
                      {p}
                    </button>

                  ))}

                </div>

              </div>

              <LiveChart
                data={chart}
                loading={chartLoading}
              />

            </div>

            {/* STATION STATUS */}

            <StationStatusGrid
              stations={
                summary?.station_status ?? []
              }
              loading={loading}
            />

          </div>

          {/* RIGHT */}

          <div className="lg:col-span-5 space-y-6">

            {/* ALERTS */}

            <AlertPanel
              alerts={
                summary?.alerts ?? []
              }
              canAcknowledge={
                canAcknowledge
              }
              onAcknowledge={
                handleAcknowledge
              }
            />

            {/* ACTIVITY */}

            <ActivityFeed
              items={
                summary?.recent_activity ?? []
              }
              loading={loading}
            />

            {/* PENDING USERS */}

            <PendingRegistrations
              users={
                summary?.pending_registrations ?? []
              }
              loading={loading}
              isAdmin={isAdmin}
              onApprove={handleApprove}
              onReject={handleReject}
            />

          </div>

        </div>

        {/* REGISTER USER */}

        <div className="flex justify-center">

          <Link
            href="/signup"
            className="text-xs flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-3xl text-slate-300 transition-colors"
          >

            <Users className="w-3.5 h-3.5" />

            REGISTER ANOTHER USER

          </Link>

        </div>

      </main>

    </div>
  );
}