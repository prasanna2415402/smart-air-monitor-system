/**
 * src/lib/format.ts
 * Small formatting helpers shared across dashboard components.
 *
 * IMPORTANT: Tailwind's compiler only generates classes it can see as
 * literal strings in the source. Building class names with template
 * literals like `text-${color}-400` silently produces no CSS. Every color
 * variant below is therefore spelled out in full so Tailwind picks it up.
 */

export function formatRelativeTime(iso: string | null): string {
  if (!iso) return 'never';
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

export interface ColorClasses {
  text: string;
  bg: string;
  border: string;
}

const PALETTE: Record<string, ColorClasses> = {
  emerald: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
  amber: { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30' },
  orange: { text: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/30' },
  red: { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30' },
  slate: { text: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/30' },
  blue: { text: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
  sky: { text: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/30' },
  violet: { text: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/30' },
  teal: { text: 'text-teal-400', bg: 'bg-teal-500/10', border: 'border-teal-500/30' },
};

export function alertLevelClasses(level: string | null | undefined): ColorClasses {
  switch (level) {
    case 'GOOD':
      return PALETTE.emerald;
    case 'MODERATE':
      return PALETTE.amber;
    case 'POOR':
    case 'VERY_POOR':
      return PALETTE.orange;
    case 'HAZARDOUS':
      return PALETTE.red;
    default:
      return PALETTE.slate;
  }
}

export function severityClasses(severity: string | null | undefined): ColorClasses {
  switch (severity) {
    case 'CRITICAL':
      return PALETTE.red;
    case 'WARNING':
      return PALETTE.amber;
    default:
      return PALETTE.slate;
  }
}

export function roleClasses(role: string | null | undefined): ColorClasses {
  switch (role) {
    case 'ADMIN':
      return PALETTE.red;
    case 'OPERATOR':
      return PALETTE.blue;
    default:
      return PALETTE.slate;
  }
}

export function statColorClasses(name: string): ColorClasses {
  return PALETTE[name] ?? PALETTE.slate;
}
