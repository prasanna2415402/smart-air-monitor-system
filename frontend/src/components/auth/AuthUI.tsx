'use client';

import type { CSSProperties, ReactNode } from 'react';
import { cn } from '@/utils/cn';
import {
  LogoMark,
  SensorIcon,
  ShieldIcon,
  EyeIcon,
  EyeOffIcon,
  AlertIcon,
  InfoIcon,
  SpinnerIcon,
  CheckIcon,
} from './icons';

const PARTICLES = [
  { x: '12%', y: '18%', size: '5px', delay: '-1s', duration: '8s' },
  { x: '23%', y: '72%', size: '3px', delay: '-4s', duration: '10s' },
  { x: '31%', y: '34%', size: '4px', delay: '-2s', duration: '7s' },
  { x: '41%', y: '82%', size: '6px', delay: '-6s', duration: '12s' },
  { x: '52%', y: '16%', size: '3px', delay: '-3s', duration: '9s' },
  { x: '62%', y: '63%', size: '5px', delay: '-5s', duration: '11s' },
  { x: '72%', y: '29%', size: '4px', delay: '-2.5s', duration: '8.5s' },
  { x: '83%', y: '54%', size: '3px', delay: '-7s', duration: '13s' },
  { x: '18%', y: '48%', size: '4px', delay: '-3.5s', duration: '9.5s' },
  { x: '76%', y: '78%', size: '5px', delay: '-1.5s', duration: '10.5s' },
] as const;

type ParticleStyle = CSSProperties & {
  '--x': string;
  '--y': string;
  '--size': string;
  '--delay': string;
  '--duration': string;
};

export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#020817] text-white">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(20,184,166,0.16),transparent_30%),radial-gradient(circle_at_82%_8%,rgba(59,130,246,0.18),transparent_28%),linear-gradient(135deg,#020817_0%,#07182f_48%,#03111f_100%)]" />
      <div className="pointer-events-none absolute -right-28 bottom-0 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="relative grid min-h-screen lg:grid-cols-[1.06fr_0.94fr]">
        <BrandPanel />
        <section className="relative flex min-h-screen items-center justify-center px-4 py-8 sm:px-6 lg:px-10">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(2,8,23,0.2),rgba(15,23,42,0.7))]" />
          <div className="relative z-10 w-full max-w-[470px]">
            <div className="mb-7 flex items-center gap-3 lg:hidden">
              <LogoMark className="h-11 w-11 text-cyan-200" />
              <div>
                <p className="text-base font-semibold tracking-tight text-white">Smart Air Monitor</p>
                <p className="text-xs text-cyan-100/60">Breathe Smarter. Monitor Better.</p>
              </div>
            </div>
            {children}
          </div>
        </section>
      </div>
    </main>
  );
}

export function AuthCard({ children }: { children: ReactNode }) {
  return (
    <div className="relative overflow-hidden rounded-[2rem] border border-white/12 bg-white/[0.075] p-5 shadow-[0_32px_100px_rgba(0,0,0,0.45)] backdrop-blur-2xl sm:p-8">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-200/70 to-transparent" />
      <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-cyan-300/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-20 left-8 h-48 w-48 rounded-full bg-blue-500/10 blur-3xl" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}

export function AuthHeader({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle: string }) {
  return (
    <div className="mb-7">
      <p className="text-xs font-semibold uppercase tracking-[0.32em] text-cyan-200/70">{eyebrow}</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-white sm:text-4xl">{title}</h2>
      <p className="mt-3 max-w-sm text-sm leading-6 text-slate-300/78">{subtitle}</p>
    </div>
  );
}

function BrandPanel() {
  return (
    <section className="relative isolate flex min-h-[48vh] overflow-hidden border-b border-white/10 bg-[#031021] px-6 py-8 sm:px-8 lg:min-h-screen lg:border-b-0 lg:border-r lg:border-white/10 lg:px-14 lg:py-12">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_22%,rgba(45,212,191,0.18),transparent_32%),radial-gradient(circle_at_72%_28%,rgba(96,165,250,0.16),transparent_30%),linear-gradient(160deg,rgba(2,6,23,0.12),rgba(15,23,42,0.88))]" />
      <div className="sensor-grid-bg" aria-hidden="true" />
      <div className="ambient-cloud ambient-cloud-one" aria-hidden="true" />
      <div className="ambient-cloud ambient-cloud-two" aria-hidden="true" />

      <div className="relative z-10 flex w-full flex-col justify-between gap-10">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <LogoMark className="h-12 w-12 text-cyan-200" />
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-100/75">IoT Air Intelligence</p>
              <p className="mt-1 text-xs text-slate-400">Encrypted environmental monitoring</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 text-xs font-medium text-emerald-100/80 sm:flex">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-50" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-300" />
            </span>
            Sensor link active
          </div>
        </div>

        <div className="grid flex-1 items-center gap-8 py-3 lg:py-8">
          <AirQualityVisual />
          <div className="max-w-2xl">
            <p className="mb-3 text-sm font-semibold uppercase tracking-[0.35em] text-cyan-200/75">Smart Air Monitor</p>
            <h1 className="max-w-xl text-5xl font-semibold tracking-[-0.07em] text-white sm:text-6xl lg:text-7xl">
              Smart Air Monitor
            </h1>
            <p className="mt-5 text-xl font-medium text-cyan-100 sm:text-2xl">Breathe Smarter. Monitor Better.</p>
            <p className="mt-4 max-w-md text-sm leading-6 text-slate-300/75">
              Role-based access to live CO2, VOC, humidity, and particulate data across every monitored room, with
              instant alerting when thresholds are crossed.
            </p>
          </div>
        </div>

        <div className="hidden flex-wrap gap-x-6 gap-y-2 text-xs font-medium uppercase tracking-[0.28em] text-cyan-100/45 sm:flex">
          <span>AQI</span>
          <span>CO2</span>
          <span>VOC</span>
          <span>Humidity</span>
          <span>Alerts</span>
        </div>
      </div>
    </section>
  );
}

function AirQualityVisual() {
  return (
    <div className="sensor-stage mx-auto h-[260px] w-[260px] sm:h-[340px] sm:w-[340px] lg:h-[410px] lg:w-[410px]" aria-hidden="true">
      <svg className="absolute inset-0 h-full w-full" viewBox="0 0 410 410" fill="none">
        <defs>
          <linearGradient id="airflow-gradient" x1="40" y1="80" x2="360" y2="330" gradientUnits="userSpaceOnUse">
            <stop stopColor="#67e8f9" stopOpacity="0" />
            <stop offset="0.5" stopColor="#5eead4" />
            <stop offset="1" stopColor="#60a5fa" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          className="airflow-line airflow-line-one"
          d="M38 245C93 178 152 300 205 211C260 119 318 206 371 142"
          stroke="url(#airflow-gradient)"
        />
        <path
          className="airflow-line airflow-line-two"
          d="M42 166C101 86 143 231 209 158C276 84 307 181 372 101"
          stroke="url(#airflow-gradient)"
        />
        <path
          className="airflow-line airflow-line-three"
          d="M38 303C99 247 142 342 205 274C266 208 318 283 371 226"
          stroke="url(#airflow-gradient)"
        />
      </svg>

      <div className="sensor-orbit sensor-orbit-one" />
      <div className="sensor-orbit sensor-orbit-two" />
      <div className="sensor-orbit sensor-orbit-three" />

      {PARTICLES.map((particle) => (
        <span
          key={`${particle.x}-${particle.y}`}
          className="air-particle"
          style={
            {
              '--x': particle.x,
              '--y': particle.y,
              '--size': particle.size,
              '--delay': particle.delay,
              '--duration': particle.duration,
            } as ParticleStyle
          }
        />
      ))}

      <div className="sensor-core">
        <SensorIcon className="h-20 w-20 text-cyan-50" />
        <span className="sensor-core-dot sensor-core-dot-one" />
        <span className="sensor-core-dot sensor-core-dot-two" />
        <span className="sensor-core-dot sensor-core-dot-three" />
      </div>
    </div>
  );
}

export type RoleOption = { id: string; label: string; cue: string; description: string };

export function RoleSelector({
  name,
  roles,
  value,
  compact = false,
  disabled = false,
  onChange,
}: {
  name: string;
  roles: readonly RoleOption[];
  value: string;
  compact?: boolean;
  disabled?: boolean;
  onChange: (role: string) => void;
}) {
  return (
    <div className={cn('grid gap-2', compact ? 'grid-cols-2' : 'sm:grid-cols-2')} role="radiogroup" aria-label="Access role">
      {roles.map((role) => (
        <label key={role.id} className="group cursor-pointer">
          <input
            className="peer sr-only"
            type="radio"
            name={name}
            value={role.id}
            checked={value === role.id}
            disabled={disabled}
            onChange={() => onChange(role.id)}
          />
          <span
            className={cn(
              'flex min-h-[54px] flex-col justify-center rounded-2xl border border-white/10 bg-white/[0.045] px-3 text-left transition duration-300 hover:border-cyan-200/40 hover:bg-cyan-200/8 peer-focus-visible:ring-2 peer-focus-visible:ring-cyan-200/35 peer-disabled:cursor-not-allowed peer-disabled:opacity-60 peer-checked:border-cyan-200/55 peer-checked:bg-cyan-300/12 peer-checked:shadow-[0_12px_30px_rgba(45,212,191,0.12)]',
              compact ? 'items-center text-center' : '',
            )}
          >
            <span className="text-sm font-semibold text-white">{role.label}</span>
            {compact ? null : <span className="mt-1 text-[11px] leading-4 text-slate-400">{role.cue}</span>}
          </span>
        </label>
      ))}
    </div>
  );
}

export function PasswordStrengthBar({ id, password }: { id: string; password: string }) {
  const checks = [
    password.length >= 8,
    /[a-z]/.test(password),
    /[A-Z]/.test(password),
    /\d/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ];
  const score = checks.filter(Boolean).length;

  const strength = !password
    ? { label: 'Start with 8+ characters', tone: 'bg-white/15', text: 'text-slate-400' }
    : score <= 2
      ? { label: 'Weak password', tone: 'bg-rose-400', text: 'text-rose-200' }
      : score <= 4
        ? { label: 'Good password', tone: 'bg-cyan-300', text: 'text-cyan-100' }
        : { label: 'Excellent password', tone: 'bg-emerald-300', text: 'text-emerald-100' };

  const criteria = [
    { label: '8+ chars', pass: password.length >= 8 },
    { label: 'Lowercase', pass: /[a-z]/.test(password) },
    { label: 'Uppercase', pass: /[A-Z]/.test(password) },
    { label: 'Number', pass: /\d/.test(password) },
  ];

  return (
    <div id={id} className="mt-3 space-y-2" aria-live="polite">
      <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
        <div
          className={cn('h-full rounded-full transition-all duration-500', strength.tone)}
          style={{ width: `${Math.max(score, password ? 1 : 0) * 20}%` }}
        />
      </div>
      <div className="flex items-center justify-between gap-4 text-xs">
        <span className={cn('font-medium', strength.text)}>{strength.label}</span>
        <span className="text-slate-500">{score}/5</span>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11px] text-slate-400 sm:grid-cols-4">
        {criteria.map((criterion) => (
          <span key={criterion.label} className="flex items-center gap-1.5">
            <span className={cn('h-1.5 w-1.5 rounded-full', criterion.pass ? 'bg-cyan-300' : 'bg-white/20')} />
            {criterion.label}
          </span>
        ))}
      </div>
    </div>
  );
}

export function SubmitButton({ loading, loadingText, children }: { loading: boolean; loadingText: string; children: string }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="group relative flex h-12 w-full items-center justify-center overflow-hidden rounded-2xl bg-cyan-300 px-5 text-sm font-bold text-slate-950 shadow-[0_16px_42px_rgba(45,212,191,0.28)] transition duration-300 hover:-translate-y-0.5 hover:bg-cyan-200 hover:shadow-[0_18px_48px_rgba(45,212,191,0.36)] focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200/55 disabled:translate-y-0 disabled:cursor-wait disabled:opacity-75"
    >
      <span className="absolute inset-0 -translate-x-full bg-[linear-gradient(110deg,transparent,rgba(255,255,255,0.6),transparent)] transition duration-700 group-hover:translate-x-full" />
      <span className="relative flex items-center gap-2">
        {loading ? <SpinnerIcon className="h-4 w-4 animate-spin" /> : <ShieldIcon className="h-4 w-4" />}
        {loading ? loadingText : children}
      </span>
    </button>
  );
}

export function PasswordToggle({ visible, disabled, label, onClick }: { visible: boolean; disabled: boolean; label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className="absolute right-3 top-1/2 -translate-y-1/2 rounded-xl p-2 text-cyan-100/55 transition hover:bg-white/8 hover:text-cyan-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200/35 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {visible ? <EyeOffIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
    </button>
  );
}

export function AuthSwitch({ disabled, onClick, children }: { disabled: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <p className="text-center text-sm text-slate-400">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        className="font-medium transition hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200/35 disabled:cursor-not-allowed disabled:opacity-60 [&_span]:font-bold [&_span]:text-cyan-200"
      >
        {children}
      </button>
    </p>
  );
}

export function FormMessage({ type, message }: { type: 'error' | 'notice'; message: string }) {
  if (!message) {
    return null;
  }

  return (
    <div
      role={type === 'error' ? 'alert' : 'status'}
      className={cn(
        'mb-5 flex items-start gap-3 rounded-2xl border px-4 py-3 text-sm leading-5',
        type === 'error'
          ? 'border-rose-300/30 bg-rose-500/10 text-rose-100'
          : 'border-cyan-300/25 bg-cyan-300/10 text-cyan-50',
      )}
    >
      {type === 'error' ? <AlertIcon className="mt-0.5 h-4 w-4 shrink-0" /> : <InfoIcon className="mt-0.5 h-4 w-4 shrink-0" />}
      <span>{message}</span>
    </div>
  );
}

export function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) {
    return null;
  }

  return (
    <p id={id} role="alert" className="mt-2 flex items-center gap-2 text-xs font-medium text-rose-200">
      <AlertIcon className="h-3.5 w-3.5" />
      {message}
    </p>
  );
}

export function SuccessOverlay({ title, message, actionLabel, onAction }: { title: string; message: string; actionLabel: string; onAction: () => void }) {
  return (
    <div className="auth-success absolute inset-0 z-30 flex items-center justify-center rounded-[2rem] border border-cyan-200/20 bg-slate-950/82 p-8 text-center backdrop-blur-2xl" aria-live="polite">
      <div className="max-w-xs">
        <div className="success-mark mx-auto flex h-20 w-20 items-center justify-center rounded-full border border-cyan-200/25 bg-cyan-300/12 text-cyan-100 shadow-[0_0_48px_rgba(45,212,191,0.28)]">
          <CheckIcon className="check-draw h-10 w-10" />
        </div>
        <h3 className="mt-6 text-2xl font-semibold tracking-[-0.04em] text-white">{title}</h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">{message}</p>
        <button
          type="button"
          onClick={onAction}
          className="mt-7 rounded-2xl border border-white/12 bg-white/8 px-5 py-2.5 text-sm font-semibold text-cyan-50 transition hover:border-cyan-200/40 hover:bg-cyan-200/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200/35"
        >
          {actionLabel}
        </button>
      </div>
    </div>
  );
}

export function inputClass(hasError: string | false | undefined, spacing: string) {
  return cn(
    'h-12 w-full rounded-2xl border bg-slate-950/45 px-4 text-sm text-white outline-none transition duration-300 placeholder:text-slate-500 hover:border-cyan-200/35 focus:border-cyan-200/70 focus:bg-slate-950/65 focus:ring-4 focus:ring-cyan-300/12 disabled:cursor-not-allowed disabled:opacity-65',
    spacing,
    hasError ? 'border-rose-300/60 focus:border-rose-300 focus:ring-rose-300/16' : 'border-white/10',
  );
}
