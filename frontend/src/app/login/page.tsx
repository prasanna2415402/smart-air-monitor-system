'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { loginUser, ApiError } from '@/lib/api';
import {
  AuthShell,
  AuthCard,
  AuthHeader,
  FormMessage,
  FieldError,
  AuthSwitch,
  SubmitButton,
  PasswordToggle,
  SuccessOverlay,
  inputClass,
} from '@/components/auth/AuthUI';
import { MailIcon, LockIcon } from '@/components/auth/icons';

type LoginForm = {
  identifier: string;
  password: string;
  remember: boolean;
};

type LoginErrors = Partial<Record<'identifier' | 'password', string>>;

function validateLogin(values: LoginForm): LoginErrors {
  const errors: LoginErrors = {};

  if (!values.identifier.trim()) {
    errors.identifier = 'Enter your email or username.';
  }

  if (!values.password) {
    errors.password = 'Enter your password.';
  }

  return errors;
}

export default function LoginPage() {
  const router = useRouter();

  const [form, setForm] = useState<LoginForm>({ identifier: '', password: '', remember: true });
  const [touched, setTouched] = useState<Partial<Record<keyof LoginForm, boolean>>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [notice, setNotice] = useState('');

  const errors = validateLogin(form);

  function updateField<K extends keyof LoginForm>(field: K, value: LoginForm[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function markTouched(field: keyof LoginForm) {
    setTouched((current) => ({ ...current, [field]: true }));
  }

  function shouldShowError(field: 'identifier' | 'password') {
    return Boolean(touched[field] || form[field].length > 0);
  }

  function handleForgotPassword() {
    setSubmitError('');
    setNotice('Password recovery requires administrator assistance. Please contact your Smart Air Monitor admin.');
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError('');
    setNotice('');
    setTouched({ identifier: true, password: true });

    const currentErrors = validateLogin(form);
    if (Object.keys(currentErrors).length > 0) {
      setSubmitError('Check the highlighted fields before signing in.');
      return;
    }

    setIsSubmitting(true);

    try {
      await loginUser(form.identifier.trim(), form.password);
      setSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 1200);
    } catch (err) {
      if (err instanceof ApiError) {
        setSubmitError(err.message);
      } else {
        setSubmitError('Unable to reach the server. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <AuthCard>
        <AuthHeader
          eyebrow="Secure console"
          title="Welcome back"
          subtitle="Access live air quality readings, alert status, and sensor health with role-based permissions."
        />

        <FormMessage type="error" message={submitError} />
        <FormMessage type="notice" message={notice} />

        <div className="auth-form-motion">
          <form className="space-y-5" noValidate aria-busy={isSubmitting} onSubmit={handleSubmit}>
            <div>
              <label className="text-sm font-medium text-cyan-50" htmlFor="login-identifier">
                Email / Username
              </label>
              <div className="relative mt-2">
                <MailIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                <input
                  id="login-identifier"
                  name="identifier"
                  type="text"
                  autoComplete="username"
                  value={form.identifier}
                  onChange={(event) => updateField('identifier', event.target.value)}
                  onBlur={() => markTouched('identifier')}
                  aria-invalid={Boolean(shouldShowError('identifier') && errors.identifier)}
                  aria-describedby="login-identifier-error"
                  disabled={isSubmitting || success}
                  placeholder="admin@smartair.com"
                  className={inputClass(shouldShowError('identifier') && errors.identifier, 'pl-12')}
                />
              </div>
              <FieldError id="login-identifier-error" message={shouldShowError('identifier') ? errors.identifier : undefined} />
            </div>

            <div>
              <div className="flex items-center justify-between gap-3">
                <label className="text-sm font-medium text-cyan-50" htmlFor="login-password">
                  Password
                </label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  disabled={isSubmitting || success}
                  className="text-xs font-semibold text-cyan-200/80 transition hover:text-cyan-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200/30"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative mt-2">
                <LockIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                <input
                  id="login-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={form.password}
                  onChange={(event) => updateField('password', event.target.value)}
                  onBlur={() => markTouched('password')}
                  aria-invalid={Boolean(shouldShowError('password') && errors.password)}
                  aria-describedby="login-password-error"
                  disabled={isSubmitting || success}
                  placeholder="Enter your password"
                  className={inputClass(shouldShowError('password') && errors.password, 'pl-12 pr-12')}
                />
                <PasswordToggle
                  visible={showPassword}
                  disabled={isSubmitting || success}
                  onClick={() => setShowPassword((current) => !current)}
                  label={showPassword ? 'Hide password' : 'Show password'}
                />
              </div>
              <FieldError id="login-password-error" message={shouldShowError('password') ? errors.password : undefined} />
            </div>

            <div className="flex items-center justify-between gap-4">
              <label className="group flex cursor-pointer items-center gap-3 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={form.remember}
                  onChange={(event) => updateField('remember', event.target.checked)}
                  disabled={isSubmitting || success}
                  className="h-4 w-4 rounded border-white/20 bg-slate-950/60 accent-cyan-300 focus:ring-2 focus:ring-cyan-200/30"
                />
                <span className="transition group-hover:text-white">Remember Me</span>
              </label>
              <span className="text-xs text-slate-400">RBAC enabled</span>
            </div>

            <SubmitButton loading={isSubmitting} loadingText="Verifying secure session">
              Sign In
            </SubmitButton>

            <AuthSwitch disabled={isSubmitting || success} onClick={() => router.push('/signup')}>
              Don&apos;t have an account? <span>Register now</span>
            </AuthSwitch>
          </form>
        </div>

        {success ? (
          <SuccessOverlay
            title="Secure session approved"
            message="Opening the Smart Air Monitor dashboard with your account permissions."
            actionLabel="Continue"
            onAction={() => router.push('/dashboard')}
          />
        ) : null}
      </AuthCard>

      <div className="mt-8 text-center text-xs font-mono tracking-widest text-slate-500">
        RBAC ENABLED &bull; APPROVAL REQUIRED FOR NEW USERS
      </div>
    </AuthShell>
  );
}
