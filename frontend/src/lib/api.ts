import Cookies from "js-cookie";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

const ACCESS_TOKEN_COOKIE = "sam_access_token";
const REFRESH_TOKEN_COOKIE = "sam_refresh_token";

// ----------------------------------------------------------------
// TYPES
// ----------------------------------------------------------------

export interface ApiUser {
  id: string;
  full_name: string;
  username: string;
  email: string;
  mobile_number: string;
  employee_id: string | null;
  role: "ADMIN" | "OPERATOR" | "VIEWER";
  account_status: "PENDING" | "APPROVED" | "REJECTED" | "SUSPENDED";
  is_active: boolean;
  profile_photo: string | null;
  registration_date: string;
  last_updated: string;
}

export interface ApiEnvelope<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, string[] | string> | string[] | null;
}

// ----------------------------------------------------------------
// API ERROR
// ----------------------------------------------------------------

export class ApiError extends Error {
  errors: Record<string, string[] | string> | string[] | null;
  status: number;

  constructor(
    message: string,
    status: number,
    errors: Record<string, string[] | string> | string[] | null = null
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errors = errors;
  }
}

// ----------------------------------------------------------------
// TOKENS
// ----------------------------------------------------------------

export function setTokens(access: string, refresh: string) {
  Cookies.set(ACCESS_TOKEN_COOKIE, access, {
    expires: 1,
    sameSite: "lax",
  });

  Cookies.set(REFRESH_TOKEN_COOKIE, refresh, {
    expires: 7,
    sameSite: "lax",
  });
}

export function getAccessToken(): string | undefined {
  return Cookies.get(ACCESS_TOKEN_COOKIE);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(REFRESH_TOKEN_COOKIE);
}

export function clearTokens() {
  Cookies.remove(ACCESS_TOKEN_COOKIE);
  Cookies.remove(REFRESH_TOKEN_COOKIE);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

// ----------------------------------------------------------------
// CORE REQUEST
// ----------------------------------------------------------------

async function request<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const { auth = true, headers, ...rest } = options;

  const finalHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string> | undefined),
  };

  if (auth) {
    const token = getAccessToken();

    if (token) {
      finalHeaders["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
  });

  let body: ApiEnvelope<T> | undefined;

  try {
    body = await response.json();
  } catch {
    // Backend returned non-JSON response
  }

  if (!response.ok || !body?.success) {
    throw new ApiError(
      body?.message || `Request failed with status ${response.status}`,
      response.status,
      body?.errors ?? null
    );
  }

  return body.data as T;
}

// ----------------------------------------------------------------
// AUTH
// ----------------------------------------------------------------

export interface RegisterPayload {
  fullName: string;
  username: string;
  email: string;
  mobileNumber: string;
  employeeId?: string;
  password: string;
  confirmPassword: string;
  role: "Operator" | "Viewer";
  termsAccepted: boolean;
}

export async function registerUser(payload: RegisterPayload) {
  return request<{ user_id: string }>("/api/auth/register/", {
    method: "POST",
    auth: false,
    body: JSON.stringify({
      full_name: payload.fullName,
      username: payload.username,
      email: payload.email,
      mobile_number: payload.mobileNumber,
      employee_id: payload.employeeId || undefined,
      password: payload.password,
      confirm_password: payload.confirmPassword,
      role: payload.role.toUpperCase(),
      terms_accepted: payload.termsAccepted,
    }),
  });
}

export interface LoginResult {
  access: string;
  refresh: string;
  user: ApiUser;
}

export async function loginUser(
  identifier: string,
  password: string
): Promise<LoginResult> {
  const data = await request<LoginResult>("/api/auth/login/", {
    method: "POST",
    auth: false,
    body: JSON.stringify({
      identifier,
      password,
    }),
  });

  setTokens(data.access, data.refresh);

  return data;
}

export async function logoutUser() {
  const refresh = getRefreshToken();

  try {
    if (refresh) {
      await request("/api/auth/logout/", {
        method: "POST",
        body: JSON.stringify({
          refresh,
        }),
      });
    }
  } finally {
    clearTokens();
  }
}

export async function getProfile() {
  return request<ApiUser>("/api/profile/me/");
}

// ----------------------------------------------------------------
// SENSOR DATA
// ----------------------------------------------------------------

export interface SensorReading {
  id: number;
  station: number;
  station_name: string;
  sensor: number | null;
  timestamp: string;

  co2_ppm: number;
  co_ppm: number;
  voc_index: number;

  temperature: number;
  humidity: number;

  pm25: number;
  pm10: number;
  pressure: number;

  aqi_score: number | null;
  alert_level: string | null;

  fan_state: boolean;
}

export interface StationStatus {
  id: number;
  name: string;
  code: string;

  status: "ACTIVE" | "INACTIVE" | "MAINTENANCE";

  is_online: boolean;

  sensor_count: number;
  online_sensor_count: number;

  last_reading_at: string | null;
  last_alert_level: string | null;
}

export interface AlertLogItem {
  id: number;
  station: number;
  station_name: string;

  reading: number | null;
  parameter: string;

  severity: "WARNING" | "CRITICAL";

  message: string;
  recommendation: string;

  is_acknowledged: boolean;

  acknowledged_by: string | null;
  acknowledged_by_name: string | null;
  acknowledged_at: string | null;

  created_at: string;
}

export interface ActivityItem {
  type: "alert" | "registration" | "login";
  message: string;
  severity: string | null;
  timestamp: string;
}

// ----------------------------------------------------------------
// DASHBOARD
// ----------------------------------------------------------------

export interface DashboardSummary {
  current_aqi: number | null;
  current_alert_level: string | null;

  current_user: ApiUser;

  stats: {
    sensors_online: number;
    sensors_total: number;

    stations_online: number;
    stations_total: number;
    stations_active: number;

    pending_approvals: number;

    users_total: number;
    users_active: number;

    active_alerts: number;
    alerts_critical: number;
    alerts_warning: number;

    avg_pm25: number | null;
    avg_aqi_24h: number | null;

    today_readings: number;
  };

  live_readings: Array<{
    station: {
      id: number;
      name: string;
      code: string;
      status: string;
    };

    reading: SensorReading;
  }>;

  station_status: StationStatus[];

  alerts: AlertLogItem[];

  recent_activity: ActivityItem[];

  pending_registrations: ApiUser[];

  generated_at: string;
}

export async function getDashboardSummary() {
  return request<DashboardSummary>("/api/dashboard/summary/");
}

// ----------------------------------------------------------------
// ALERTS
// ----------------------------------------------------------------

export async function acknowledgeAlert(id: number) {
  return request(`/api/sensors/alerts/${id}/acknowledge/`, {
    method: "POST",
  });
}

// ----------------------------------------------------------------
// REPORTS / CHARTS
// ----------------------------------------------------------------

export interface ReportBucket {
  bucket: string;

  avg_co2: number;
  avg_co: number;
  avg_voc: number;

  avg_temp: number;
  avg_hum: number;

  avg_pm25: number;
  avg_pm10: number;

  avg_pressure: number;

  avg_aqi: number | null;

  n_readings: number;
}

export async function getReadingsReport(
  period: "daily" | "weekly" | "monthly" = "daily",
  station?: number
) {
  const params = new URLSearchParams({
    period,
  });

  if (station) {
    params.set("station", String(station));
  }

  return request<ReportBucket[]>(
    `/api/sensors/readings/report/?${params.toString()}`
  );
}

// ----------------------------------------------------------------
// USER MANAGEMENT
// ----------------------------------------------------------------

export async function approveUser(id: string) {
  return request(`/api/users/${id}/approve/`, {
    method: "POST",
  });
}

export async function rejectUser(id: string, reason: string) {
  return request(`/api/users/${id}/reject/`, {
    method: "POST",
    body: JSON.stringify({
      reason,
    }),
  });
}

export async function suspendUser(id: string) {
  return request(`/api/users/${id}/suspend/`, {
    method: "POST",
  });
}

// ----------------------------------------------------------------
// AI
// ----------------------------------------------------------------

export interface AIPrediction {
  station: number;

  predicted_class: string | null;
  confidence: number | null;

  co2_forecast: number | null;

  trend: string;

  is_anomaly: boolean;

  method: "ml" | "rule-based";

  recommendations: string[];

  rows_available: number;
  rows_required_for_ml: number;

  model_trained?: boolean;
}

export async function getAIPrediction(stationId: number) {
  return request<AIPrediction>(
    `/api/ai/predict/?station=${stationId}`
  );
}