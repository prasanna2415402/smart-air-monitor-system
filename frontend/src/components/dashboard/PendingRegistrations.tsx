import React, { useState } from 'react';
import { Check, X } from 'lucide-react';
import type { ApiUser } from '@/lib/api';

interface Props {
  users: ApiUser[];
  loading: boolean;
  isAdmin: boolean;
  onApprove: (id: string) => Promise<void>;
  onReject: (id: string, reason: string) => Promise<void>;
}

export function PendingRegistrations({ users, loading, isAdmin, onApprove, onReject }: Props) {
  const [busyId, setBusyId] = useState<string | null>(null);

  const approve = async (id: string) => {
    setBusyId(id);
    try {
      await onApprove(id);
    } finally {
      setBusyId(null);
    }
  };

  const reject = async (id: string) => {
    const reason = window.prompt('Reason for rejection?') || 'Not specified';
    setBusyId(id);
    try {
      await onReject(id, reason);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="glass rounded-3xl p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="font-medium flex items-center gap-2">
            PENDING REGISTRATIONS
            <span className="bg-amber-400 text-amber-950 text-[10px] px-2 py-px rounded">
              {users.length}
            </span>
          </div>
          <div className="text-xs text-slate-400">Awaiting admin approval</div>
        </div>
      </div>

      {!loading && users.length === 0 && (
        <div className="text-slate-400 text-sm py-6 text-center">No pending registrations.</div>
      )}

      <div className="space-y-4">
        {users.map((user, index) => (
          <div
            key={user.id}
            className="flex justify-between bg-slate-900/60 rounded-2xl p-4 items-center border border-slate-700"
          >
            <div className="flex items-center gap-4 min-w-0">
              <div className="w-9 h-9 bg-slate-700 rounded-2xl flex items-center justify-center text-xs font-mono text-slate-400 flex-shrink-0">
                P{index + 1}
              </div>
              <div className="min-w-0">
                <div className="font-medium text-sm truncate">{user.full_name}</div>
                <div className="text-xs text-slate-400 truncate">{user.email}</div>
              </div>
            </div>

            {isAdmin ? (
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => approve(user.id)}
                  disabled={busyId === user.id}
                  title="Approve"
                  className="w-8 h-8 flex items-center justify-center rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors disabled:opacity-50"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={() => reject(user.id)}
                  disabled={busyId === user.id}
                  title="Reject"
                  className="w-8 h-8 flex items-center justify-center rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors disabled:opacity-50"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="text-right flex-shrink-0">
                <div className="text-[10px] uppercase tracking-widest text-amber-400 mb-px">PENDING</div>
                <div className="text-xs text-slate-500">{user.role}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
