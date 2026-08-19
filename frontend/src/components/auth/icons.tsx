import type { SVGProps } from "react";
import { cn } from "@/utils/cn";

type IconProps = SVGProps<SVGSVGElement>;

export function LogoMark({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 48 48" fill="none" className={cn("drop-shadow-[0_0_18px_rgba(103,232,249,0.32)]", className)} {...props}>
      <rect x="8" y="8" width="32" height="32" rx="12" fill="currentColor" opacity="0.12" />
      <path d="M16 27c5.3-6.5 10.8 4.8 16-1.7" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" />
      <path d="M16 20c5.3-6.5 10.8 4.8 16-1.7" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" opacity="0.7" />
      <circle cx="24" cy="24" r="17" stroke="currentColor" strokeWidth="1.5" opacity="0.38" />
      <circle cx="34" cy="14" r="3" fill="currentColor" />
    </svg>
  );
}

export function SensorIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 64 64" fill="none" className={className} {...props}>
      <rect x="18" y="13" width="28" height="38" rx="11" stroke="currentColor" strokeWidth="3" />
      <path d="M25 24h14M25 32h14M25 40h8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" opacity="0.76" />
      <path d="M10 25c-4 4-4 10 0 14M54 25c4 4 4 10 0 14" stroke="currentColor" strokeWidth="3" strokeLinecap="round" opacity="0.55" />
      <path d="M5 18c-8 8-8 20 0 28M59 18c8 8 8 20 0 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity="0.35" />
    </svg>
  );
}

export function MailIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <rect x="3" y="5" width="18" height="14" rx="3" />
      <path d="m4 7 8 6 8-6" />
    </svg>
  );
}

export function LockIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <rect x="4" y="10" width="16" height="10" rx="3" />
      <path d="M8 10V8a4 4 0 0 1 8 0v2" />
      <path d="M12 14v2" />
    </svg>
  );
}

export function UserIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="M20 21a8 8 0 0 0-16 0" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

export function TerminalIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <rect x="3" y="4" width="18" height="16" rx="3" />
      <path d="m8 9 3 3-3 3" />
      <path d="M13 15h3" />
    </svg>
  );
}

export function PhoneIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="M4 5c0-.6.4-1 1-1h3.2c.5 0 .9.3 1 .8l.9 3.6c.1.4 0 .9-.3 1.2l-1.6 1.6a15.5 15.5 0 0 0 6.6 6.6l1.6-1.6c.3-.3.8-.4 1.2-.3l3.6.9c.5.1.8.5.8 1V21c0 .6-.4 1-1 1h-1.5C10.9 22 2 13.1 2 2.5V5z" />
    </svg>
  );
}

export function IdCardIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <rect x="2" y="5" width="20" height="14" rx="3" />
      <circle cx="8" cy="12" r="2" />
      <path d="M5 17c.5-1.6 1.7-2.5 3-2.5s2.5.9 3 2.5" />
      <path d="M14 10h5M14 14h3" />
    </svg>
  );
}

export function ShieldIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="M12 22s8-3.8 8-10V5l-8-3-8 3v7c0 6.2 8 10 8 10Z" />
      <path d="m9 12 2 2 4-5" />
    </svg>
  );
}

export function EyeIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export function EyeOffIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="m3 3 18 18" />
      <path d="M10.7 5.2A10.8 10.8 0 0 1 12 5c6.5 0 10 7 10 7a17.8 17.8 0 0 1-3 4.1" />
      <path d="M6.6 6.6C3.7 8.5 2 12 2 12s3.5 7 10 7a10.5 10.5 0 0 0 4.1-.8" />
      <path d="M9.9 9.9A3 3 0 0 0 14.1 14" />
    </svg>
  );
}

export function AlertIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
    </svg>
  );
}

export function InfoIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5" />
      <path d="M12 8h.01" />
    </svg>
  );
}

export function SpinnerIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} {...props}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2.4" opacity="0.25" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

export function CheckIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className={className} {...props}>
      <path d="m5 12 4.2 4.2L19 6.8" />
    </svg>
  );
}
