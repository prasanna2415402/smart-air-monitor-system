'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { registerUser, ApiError } from '@/lib/api';
import {
  AuthShell,
  AuthCard,
  AuthHeader,
  FormMessage,
  FieldError,
  AuthSwitch,
  SubmitButton,
  PasswordToggle,
  PasswordStrengthBar,
  RoleSelector,
  SuccessOverlay,
  inputClass,
  type RoleOption,
} from '@/components/auth/AuthUI';
import { MailIcon, LockIcon, UserIcon, TerminalIcon, PhoneIcon, IdCardIcon, ShieldIcon } from '@/components/auth/icons';

const ROLES: RoleOption[] = [
  { id: 'Operator', label: 'Operator', cue: 'Live response', description: 'Monitor alerts, validate readings, and respond to room-level events.' },
  { id: 'Viewer', label: 'Viewer', cue: 'Read only', description: 'View dashboards, historical trends, and environmental reports.' },
];

type SignupForm = {
  fullName: string;
  username: string;
  email: string;
  mobileNumber: string;
  employeeId: string;
  password: string;
  confirmPassword: string;
  role: 'Operator' | 'Viewer';
  terms: boolean;
};

type SignupErrors = Partial<Record<keyof SignupForm, string>> & { general?: string };

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateSignup(values: SignupForm): SignupErrors {
  const errors: SignupErrors = {};

  if (values.fullName.trim().length < 2) {
    errors.fullName = 'Enter your full name.';
  }

  if (values.username.trim().length < 3) {
    errors.username = 'Username must be at least 3 characters.';
  }

  if (!emailPattern.test(values.email.trim())) {
    errors.email = 'Use a valid email address.';
  }

  if (!/^[0-9+\-\s()]{10,}$/.test(values.mobileNumber.trim())) {
    errors.mobileNumber = 'Enter a valid mobile number.';
  }

  if (values.password.length < 8) {
    errors.password = 'Password must be at least 8 characters.';
  } else if (!/[A-Z]/.test(values.password) || !/[a-z]/.test(values.password) || !/\d/.test(values.password)) {
    errors.password = 'Use upper, lower case letters and a number.';
  }

  if (!values.confirmPassword) {
    errors.confirmPassword = 'Confirm your password.';
  } else if (values.confirmPassword !== values.password) {
    errors.confirmPassword = 'Passwords do not match.';
  }

  if (!values.terms) {
    errors.terms = 'Accept the terms to create an account.';
  }

  return errors;
}

const fieldMap: Record<string, keyof SignupForm> = {
  full_name: 'fullName',
  username: 'username',
  email: 'email',
  mobile_number: 'mobileNumber',
  employee_id: 'employeeId',
  password: 'password',
  confirm_password: 'confirmPassword',
  terms_accepted: 'terms',
};

export default function SignUpPage() {
  const router = useRouter();

  const [form, setForm] = useState<SignupForm>({
    fullName: '',
    username: '',
    email: '',
    mobileNumber: '',
    employeeId: '',
    password: '',
    confirmPassword: '',
    role: 'Viewer',
    terms: false,
  });
  const [touched, setTouched] = useState<Partial<Record<keyof SignupForm, boolean>>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<SignupErrors>({});

  const errors = { ...validateSignup(form), ...fieldErrors };

  function updateField<K extends keyof SignupForm>(field: K, value: SignupForm[K]) {
    setForm((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => {
      const updated = { ...current };
      delete updated[field];
      return updated;
    });
  }

  function markTouched(field: keyof SignupForm) {
    setTouched((current) => ({ ...current, [field]: true }));
  }

  function shouldShowError(field: keyof SignupForm) {
    const value = form[field];
    return Boolean(touched[field] || (typeof value === 'string' && value.length > 0));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError('');
    setTouched({
      fullName: true,
      username: true,
      email: true,
      mobileNumber: true,
      password: true,
      confirmPassword: true,
      terms: true,
    });

    const currentErrors = validateSignup(form);
    if (Object.keys(currentErrors).length > 0) {
      setSubmitError('Resolve the validation messages to create your account.');
      return;
    }

    setIsSubmitting(true);

    try {
      await registerUser({
        fullName: form.fullName.trim(),
        username: form.username.trim().toLowerCase(),
        email: form.email.trim().toLowerCase(),
        mobileNumber: form.mobileNumber.trim(),
        employeeId: form.employeeId.trim() || undefined,
        password: form.password,
        confirmPassword: form.confirmPassword,
        role: form.role,
        termsAccepted: form.terms,
      });

      setSuccess(true);

      setTimeout(() => {
        router.push('/login');
      }, 2200);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.errors && typeof err.errors === 'object' && !Array.isArray(err.errors)) {
          const mapped: SignupErrors = {};
          for (const [key, value] of Object.entries(err.errors)) {
            const formKey = fieldMap[key] ?? (key as keyof SignupForm);
            mapped[formKey] = Array.isArray(value) ? value[0] : String(value);
          }
          setFieldErrors(mapped);
          setSubmitError(Object.keys(mapped).length ? 'Resolve the validation messages to create your account.' : err.message);
        } else {
          setSubmitError(err.message);
        }
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
          eyebrow="Create workspace access"
          title="Join the monitoring network"
          subtitle="Set up a verified account for your air monitoring site. New accounts require admin approval before login."
        />

        <FormMessage type="error" message={submitError} />

        <div className="auth-form-motion">
          <form className="space-y-5" noValidate aria-busy={isSubmitting} onSubmit={handleSubmit}>
            <div>
              <label className="text-sm font-medium text-cyan-50" htmlFor="signup-full-name">
                Full Name
              </label>
              <div className="relative mt-2">
                <UserIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                <input
                  id="signup-full-name"
                  name="fullName"
                  type="text"
                  autoComplete="name"
                  value={form.fullName}
                  onChange={(event) => updateField('fullName', event.target.value)}
                  onBlur={() => markTouched('fullName')}
                  aria-invalid={Boolean(shouldShowError('fullName') && errors.fullName)}
                  aria-describedby="signup-full-name-error"
                  disabled={isSubmitting || success}
                  placeholder="John Smith"
                  className={inputClass(shouldShowError('fullName') && errors.fullName, 'pl-12')}
                />
              </div>
              <FieldError id="signup-full-name-error" message={shouldShowError('fullName') ? errors.fullName : undefined} />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-cyan-50" htmlFor="signup-email">
                  Email
                </label>
                <div className="relative mt-2">
                  <MailIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                  <input
                    id="signup-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={(event) => updateField('email', event.target.value)}
                    onBlur={() => markTouched('email')}
                    aria-invalid={Boolean(shouldShowError('email') && errors.email)}
                    aria-describedby="signup-email-error"
                    disabled={isSubmitting || success}
                    placeholder="john.smith@company.com"
                    className={inputClass(shouldShowError('email') && errors.email, 'pl-12')}
                  />
                </div>
                <FieldError id="signup-email-error" message={shouldShowError('email') ? errors.email : undefined} />
              </div>

              <div>
                <label className="text-sm font-medium text-cyan-50" htmlFor="signup-username">
                  Username
                </label>
                <div className="relative mt-2">
                  <TerminalIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                  <input
                    id="signup-username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    value={form.username}
                    onChange={(event) => updateField('username', event.target.value)}
                    onBlur={() => markTouched('username')}
                    aria-invalid={Boolean(shouldShowError('username') && errors.username)}
                    aria-describedby="signup-username-error"
                    disabled={isSubmitting || success}
                    placeholder="jsmith"
                    className={inputClass(shouldShowError('username') && errors.username, 'pl-12')}
                  />
                </div>
                <FieldError id="signup-username-error" message={shouldShowError('username') ? errors.username : undefined} />
              </div>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-cyan-50" htmlFor="signup-mobile">
                  Mobile Number
                </label>
                <div className="relative mt-2">
                  <PhoneIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                  <input
                    id="signup-mobile"
                    name="mobileNumber"
                    type="tel"
                    autoComplete="tel"
                    value={form.mobileNumber}
                    onChange={(event) => updateField('mobileNumber', event.target.value)}
                    onBlur={() => markTouched('mobileNumber')}
                    aria-invalid={Boolean(shouldShowError('mobileNumber') && errors.mobileNumber)}
                    aria-describedby="signup-mobile-error"
                    disabled={isSubmitting || success}
                    placeholder="+1 (555) 123-4567"
                    className={inputClass(shouldShowError('mobileNumber') && errors.mobileNumber, 'pl-12')}
                  />
                </div>
                <FieldError id="signup-mobile-error" message={shouldShowError('mobileNumber') ? errors.mobileNumber : undefined} />
              </div>

              <div>
                <label className="text-sm font-medium text-cyan-50" htmlFor="signup-employee-id">
                  Employee ID <span className="font-normal text-slate-500">(optional)</span>
                </label>
                <div className="relative mt-2">
                  <IdCardIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                  <input
                    id="signup-employee-id"
                    name="employeeId"
                    type="text"
                    value={form.employeeId}
                    onChange={(event) => updateField('employeeId', event.target.value)}
                    disabled={isSubmitting || success}
                    placeholder="EMP-39281"
                    className={inputClass(false, 'pl-12')}
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-cyan-50" htmlFor="signup-password">
                Password
              </label>
              <div className="relative mt-2">
                <LockIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                <input
                  id="signup-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.password}
                  onChange={(event) => updateField('password', event.target.value)}
                  onBlur={() => markTouched('password')}
                  aria-invalid={Boolean(shouldShowError('password') && errors.password)}
                  aria-describedby="signup-password-error signup-password-strength"
                  disabled={isSubmitting || success}
                  placeholder="Create a strong password"
                  className={inputClass(shouldShowError('password') && errors.password, 'pl-12 pr-12')}
                />
                <PasswordToggle
                  visible={showPassword}
                  disabled={isSubmitting || success}
                  onClick={() => setShowPassword((current) => !current)}
                  label={showPassword ? 'Hide password' : 'Show password'}
                />
              </div>
              <PasswordStrengthBar id="signup-password-strength" password={form.password} />
              <FieldError id="signup-password-error" message={shouldShowError('password') ? errors.password : undefined} />
            </div>

            <div>
              <label className="text-sm font-medium text-cyan-50" htmlFor="signup-confirm-password">
                Confirm Password
              </label>
              <div className="relative mt-2">
                <LockIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-cyan-100/45" />
                <input
                  id="signup-confirm-password"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.confirmPassword}
                  onChange={(event) => updateField('confirmPassword', event.target.value)}
                  onBlur={() => markTouched('confirmPassword')}
                  aria-invalid={Boolean(shouldShowError('confirmPassword') && errors.confirmPassword)}
                  aria-describedby="signup-confirm-password-error"
                  disabled={isSubmitting || success}
                  placeholder="Re-enter password"
                  className={inputClass(shouldShowError('confirmPassword') && errors.confirmPassword, 'pl-12 pr-12')}
                />
                <PasswordToggle
                  visible={showConfirmPassword}
                  disabled={isSubmitting || success}
                  onClick={() => setShowConfirmPassword((current) => !current)}
                  label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                />
              </div>
              <FieldError id="signup-confirm-password-error" message={shouldShowError('confirmPassword') ? errors.confirmPassword : undefined} />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-cyan-50">Role selection</span>
                <ShieldIcon className="h-4 w-4 text-cyan-200/70" />
              </div>
              <RoleSelector name="signup-role" roles={ROLES} value={form.role} disabled={isSubmitting || success} onChange={(role) => updateField('role', role as SignupForm['role'])} />
              <p className="mt-2 text-xs leading-5 text-slate-400">
                Admin accounts are provisioned separately by an existing administrator.
              </p>
            </div>

            <div>
              <label className="group flex cursor-pointer items-start gap-3 text-sm leading-6 text-slate-300">
                <input
                  type="checkbox"
                  checked={form.terms}
                  onChange={(event) => updateField('terms', event.target.checked)}
                  onBlur={() => markTouched('terms')}
                  aria-invalid={Boolean(touched.terms && errors.terms)}
                  aria-describedby="signup-terms-error"
                  disabled={isSubmitting || success}
                  className="mt-1 h-4 w-4 rounded border-white/20 bg-slate-950/60 accent-cyan-300 focus:ring-2 focus:ring-cyan-200/30"
                />
                <span className="transition group-hover:text-white">
                  I agree to the Terms of Service and Privacy Policy. I understand my account will be pending admin
                  approval.
                </span>
              </label>
              <FieldError id="signup-terms-error" message={touched.terms ? errors.terms : undefined} />
            </div>

            <SubmitButton loading={isSubmitting} loadingText="Creating encrypted profile">
              Create Account
            </SubmitButton>

            <AuthSwitch disabled={isSubmitting || success} onClick={() => router.push('/login')}>
              Already have an account? <span>Login</span>
            </AuthSwitch>
          </form>
        </div>

        {success ? (
          <SuccessOverlay
            title="Account created"
            message="Your registration was submitted for review. An administrator will approve your access before you can log in."
            actionLabel="Back to login"
            onAction={() => router.push('/login')}
          />
        ) : null}
      </AuthCard>

      <div className="mt-8 text-center text-xs font-mono tracking-widest text-slate-500">
        SECURE REGISTRATION &bull; PENDING APPROVAL WORKFLOW
      </div>
    </AuthShell>
  );
}
