import React, { useState } from 'react';
import { ChevronDown, LogOut, ShieldCheck, UserCircle } from 'lucide-react';
import type { ApiUser } from '@/lib/api';
import { roleClasses } from '@/lib/format';

export function UserMenu({ user, onLogout }: { user: ApiUser; onLogout: () => void }) {
  const [open, setOpen] = useState(false);
  const color = roleClasses(user.role);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-3 bg-slate-800 hover:bg-slate-700 rounded-2xl px-4 py-2 transition-colors"
      >
        <div className={`w-7 h-7 rounded-full ${color.bg} ${color.text} flex items-center justify-center text-xs font-semibold`}>
          {user.full_name?.charAt(0)?.toUpperCase() || <UserCircle className="w-4 h-4" />}
        </div>
        <div className="text-left hidden sm:block">
          <div className="text-xs font-medium leading-tight">{user.full_name}</div>
          <div className={`text-[10px] ${color.text} leading-tight`}>{user.role}</div>
        </div>
        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 glass rounded-2xl p-4 z-20 border border-slate-700/50">
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className={`w-4 h-4 ${color.text}`} />
              <div className="text-sm font-medium">{user.full_name}</div>
            </div>
            <div className="text-xs text-slate-400 space-y-1 mb-4">
              <div>{user.email}</div>
              <div>@{user.username}</div>
              <div>
                Role: <span className={color.text}>{user.role}</span>
              </div>
              <div>Status: {user.account_status}</div>
            </div>
            <button
              onClick={onLogout}
              className="w-full flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs px-4 py-2 rounded-xl transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" /> SIGN OUT
            </button>
          </div>
        </>
      )}
    </div>
  );
}
