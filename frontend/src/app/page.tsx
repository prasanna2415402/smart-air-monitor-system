import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="industrial-bg min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center">
        <div className="mx-auto mb-8 flex justify-center">
          <div className="inline-flex items-center gap-4 bg-slate-900/70 px-8 py-5 rounded-3xl border border-blue-500/30">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-inner">
              <span className="text-5xl text-white font-black tracking-[-4px]">SA</span>
            </div>
          </div>
        </div>
        
        <h1 className="text-white text-6xl font-semibold tracking-tighter mb-3">Smart Air</h1>
        <div className="uppercase text-blue-400 text-sm tracking-[4px] mb-8">MONITOR SYSTEM</div>
        
        <p className="text-slate-400 max-w-xs mx-auto mb-12">
          Professional industrial air quality monitoring platform with secure registration, admin approval workflow and role based access control.
        </p>
        
        <div className="flex flex-col gap-4">
          <Link 
            href="/signup"
            className="block bg-white text-slate-950 py-4 rounded-2xl font-semibold hover:bg-slate-100 active:scale-[0.985] transition-all text-lg shadow-xl shadow-blue-950/40"
          >
            REGISTER NEW ACCOUNT
          </Link>
          
          <Link 
            href="/login"
            className="block border border-white/30 text-white py-4 rounded-2xl font-medium hover:bg-white/5 transition-all"
          >
            SIGN IN TO DASHBOARD
          </Link>
        </div>
        
        <div className="mt-16 text-xs text-slate-500 font-mono tracking-widest">
          NEXT.JS FRONTEND • DJANGO REST API • AI/ML PREDICTIONS<br />
          FULL AUTHENTICATION + APPROVAL WORKFLOW
        </div>
      </div>
    </div>
  );
}
