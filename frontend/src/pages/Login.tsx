import { motion } from 'framer-motion';
import { CheckCircle, Eye, EyeOff, Server, ShieldCheck } from 'lucide-react';
import { useEffect, useMemo, useState, type FormEvent, type KeyboardEvent } from 'react';
import { useLocation } from 'wouter';

const capabilityCards = [
  {
    title: 'Crime Pattern Intelligence',
    description: 'Analyze emerging threats with precision.',
  },
  {
    title: 'Investigation Knowledge Graph',
    description: 'Link cases, actors, and evidence seamlessly.',
  },
  {
    title: 'Predictive Crime Analytics',
    description: 'Anticipate risks with machine intelligence.',
  },
  {
    title: 'Digital Evidence Analysis',
    description: 'Securely process intelligence-grade evidence.',
  },
];

const systemStatusItems = [
  { label: 'Backend', value: 'Connected' },
  { label: 'Ledger', value: 'Synced' },
  { label: 'Environment', value: 'Production' },
  { label: 'Threat Alerts', value: 'No alerts' },
  { label: 'Current Time', value: '' },
];

const authMessages = [
  'Verifying Officer Identity...',
  'Checking Device Trust...',
  'Establishing Secure Session...',
  'Loading Intelligence Workspace...',
];

const identityLines = [
  'Government of Karnataka',
  'Karnataka State Police',
  'Crime Intelligence Division',
  'Powered by Zoho Catalyst Native',
];

const footerLines = [
  'Government of Karnataka',
  'Karnataka State Police',
  'Crime Intelligence Division',
  'Powered by Zoho Catalyst',
  '© 2026 Government of Karnataka',
];

const threatNotices = [
  'Authorized personnel only. Access is monitored and audited.',
  'Watch for unusual login attempts on this network.',
  'Zero Trust policies apply for every request.',
  'Classified portal activity is reviewed continuously.',
];

export function Login() {
  const [, setLocation] = useLocation();
  const [officerId, setOfficerId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberDevice, setRememberDevice] = useState(true);
  const [capsLockOn, setCapsLockOn] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [authStep, setAuthStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [noticeIndex, setNoticeIndex] = useState(0);
  const [timeText, setTimeText] = useState(() => {
    const now = new Date();
    return now.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  });

  const threatNotice = useMemo(() => threatNotices[noticeIndex], [noticeIndex]);

  useEffect(() => {
    const storedOfficer = window.localStorage.getItem('ksp-last-officer');
    if (storedOfficer) {
      setOfficerId(storedOfficer);
    }
  }, []);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setNoticeIndex((current) => (current + 1) % threatNotices.length);
    }, 6000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      const now = new Date();
      setTimeText(
        now.toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false,
        })
      );
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const handleLogin = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError(null);
    setIsSubmitting(true);
    setAuthStep(1);

    window.setTimeout(() => setAuthStep(2), 400);
    window.setTimeout(() => setAuthStep(3), 800);
    window.setTimeout(() => {
      setAuthStep(4);
      if (rememberDevice) {
        window.localStorage.setItem('ksp-last-officer', officerId);
      }
      window.setTimeout(() => setLocation('/dashboard'), 600);
    }, 1300);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    setCapsLockOn(event.getModifierState('CapsLock'));
    if (event.key === 'Enter') {
      event.preventDefault();
    }
  };

  return (
    <motion.div
      className="relative min-h-screen overflow-hidden bg-slate-50 text-slate-950"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="pointer-events-none absolute inset-0 opacity-5">
        <div className="absolute left-10 top-20 h-[1px] w-[320px] bg-slate-400" />
        <div className="absolute left-44 top-44 h-[280px] w-[280px] rounded-full border border-slate-400" />
        <div className="absolute right-10 top-40 h-[320px] w-px bg-slate-400" />
        <div className="absolute left-20 bottom-28 h-[1px] w-[240px] bg-slate-400" />
        <div className="absolute right-28 bottom-24 h-[240px] w-px bg-slate-400" />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col px-5 py-8 lg:px-10">
        <div className="flex flex-1 flex-col gap-8 lg:flex-row lg:items-stretch">
          <section className="relative flex-1 rounded-[32px] border border-slate-200 bg-white p-8 lg:max-w-[45%] lg:p-10">
            <div className="relative z-10 flex h-full flex-col justify-between gap-10">
              <div>
                <div className="mb-8 flex items-center gap-4">
                  <div className="flex h-20 w-20 items-center justify-center rounded-[24px] border border-slate-200 bg-slate-950 text-white">
                    <ShieldCheck className="h-8 w-8" />
                  </div>
                  <div>
                    <p className="text-[12px] uppercase tracking-[0.32em] text-slate-500">Karnataka State Police</p>
                    <h1 className="mt-3 max-w-[460px] text-[30px] font-semibold leading-[1.05] text-slate-950 sm:text-[34px]">
                      AI Crime Intelligence & Investigation Platform
                    </h1>
                    <p className="mt-3 max-w-[520px] text-[15px] leading-7 text-slate-600">
                      Advanced Investigation Intelligence powered by Artificial Intelligence and Zoho Catalyst.
                    </p>
                  </div>
                </div>

                <div className="grid gap-4">
                  {capabilityCards.map((card) => (
                    <button
                      key={card.title}
                      type="button"
                      className="group relative overflow-hidden rounded-[20px] border border-slate-200 bg-white pl-5 pr-4 py-4 text-left transition duration-150 hover:border-slate-400"
                    >
                      <div className="absolute left-0 top-0 h-full w-1 bg-slate-950 transition duration-150 group-hover:bg-slate-700" />
                      <div className="relative flex items-start gap-4">
                        <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-slate-950">
                          <CheckCircle className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-950">{card.title}</p>
                          <p className="mt-1 text-sm leading-6 text-slate-600">{card.description}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid gap-5 text-sm text-slate-600">
                <div className="rounded-[20px] border border-slate-200 bg-slate-50 p-5">
                  {identityLines.map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </div>
                <div className="rounded-[20px] border border-slate-200 bg-slate-50 p-5">
                  <p className="font-semibold text-slate-950">Internal Government Network</p>
                  <p>Authorized Personnel Only</p>
                  <p>Version 2.0</p>
                </div>
              </div>
            </div>
          </section>

          <main className="flex-1 lg:max-w-[55%]">
            <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
              <div className="rounded-[32px] border border-slate-200 bg-white p-8 lg:p-10">
                <div className="flex flex-col gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-slate-950">
                    <ShieldCheck className="h-5 w-5" />
                  </div>
                  <p className="text-[11px] uppercase tracking-[0.34em] text-slate-500">Secure Officer Access</p>
                  <h2 className="text-[36px] font-semibold tracking-[-0.03em] text-slate-950">Welcome Back</h2>
                  <p className="max-w-[520px] text-sm leading-7 text-slate-600">
                    Authenticate using your official Karnataka State Police credentials.
                  </p>
                </div>

                <form className="space-y-6 mt-8" onSubmit={handleLogin}>
                  <div className="space-y-4 rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                    <div className="relative">
                      <input
                        id="officer-id"
                        autoFocus
                        value={officerId}
                        onChange={(event) => setOfficerId(event.target.value)}
                        onKeyDown={handleKeyDown}
                        className="peer h-[52px] w-full rounded-[16px] border border-slate-200 bg-white px-4 pt-5 text-sm text-slate-950 outline-none transition duration-150 focus:border-slate-700 focus:ring-1 focus:ring-slate-300"
                        placeholder=" "
                        aria-label="Officer ID"
                      />
                      <label
                        htmlFor="officer-id"
                        className="pointer-events-none absolute left-4 top-4 text-sm text-slate-500 transition-all duration-150 peer-placeholder-shown:top-[18px] peer-placeholder-shown:text-base peer-focus:top-3 peer-focus:text-sm"
                      >
                        Officer ID
                      </label>
                    </div>

                    <div className="relative">
                      <input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        onKeyDown={handleKeyDown}
                        className="peer h-[52px] w-full rounded-[16px] border border-slate-200 bg-white px-4 pr-12 pt-5 text-sm text-slate-950 outline-none transition duration-150 focus:border-slate-700 focus:ring-1 focus:ring-slate-300"
                        placeholder=" "
                        aria-label="Password"
                      />
                      <label
                        htmlFor="password"
                        className="pointer-events-none absolute left-4 top-4 text-sm text-slate-500 transition-all duration-150 peer-placeholder-shown:top-[18px] peer-placeholder-shown:text-base peer-focus:top-3 peer-focus:text-sm"
                      >
                        Password
                      </label>
                      <button
                        type="button"
                        onClick={() => setShowPassword((value) => !value)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 transition duration-150 hover:text-slate-950"
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>

                    {capsLockOn ? <p className="text-[13px] text-amber-700">Caps Lock is enabled.</p> : null}

                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <label className="flex items-center gap-3 text-sm text-slate-600">
                        <input
                          type="checkbox"
                          checked={rememberDevice}
                          onChange={(event) => setRememberDevice(event.target.checked)}
                          className="h-4 w-4 rounded border border-slate-300 bg-white text-slate-950"
                        />
                        Remember this device
                      </label>
                      <button type="button" className="text-sm font-semibold text-slate-950 transition duration-150 hover:text-slate-700">
                        Forgot Password?
                      </button>
                    </div>

                    {error ? (
                      <div className="rounded-[16px] border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-slate-900">
                        <p className="font-semibold">Authentication Failed</p>
                        <p className="mt-1 text-slate-700">Officer credentials could not be verified. Please verify your Officer ID and password or contact your administrator.</p>
                      </div>
                    ) : null}

                    <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
                      <button
                        type="submit"
                        disabled={isSubmitting}
                        className="flex h-[52px] items-center justify-center rounded-[16px] bg-slate-950 px-5 text-sm font-semibold uppercase tracking-[0.14em] text-white transition duration-150 disabled:cursor-not-allowed disabled:opacity-70"
                      >
                        {isSubmitting ? 'Authenticating...' : 'Secure Sign In'}
                      </button>
                      <button
                        type="button"
                        className="flex h-[52px] items-center justify-center gap-2 rounded-[16px] border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-950 transition duration-150 hover:border-slate-400"
                      >
                        <Server className="h-4 w-4" />
                        Government SSO Login
                        <span className="rounded-full border border-slate-300 bg-slate-100 px-2 py-0.5 text-[11px] uppercase tracking-[0.24em] text-slate-600">
                          Recommended
                        </span>
                      </button>
                    </div>
                  </div>
                </form>

                <div className="rounded-[20px] border border-slate-200 bg-slate-50 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Authentication sequence</p>
                      <p className="mt-2 text-[16px] font-semibold text-slate-950">Secure Login Flow</p>
                    </div>
                    <div className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[12px] uppercase tracking-[0.2em] text-slate-500">
                      {isSubmitting ? 'Authenticating' : 'Ready'}
                    </div>
                  </div>
                  <div className="mt-5 grid gap-3">
                    {authMessages.map((message, index) => (
                      <div key={message} className="flex items-center gap-3 rounded-[14px] bg-white px-4 py-3 text-sm text-slate-700">
                        <span className={`inline-flex h-3.5 w-3.5 rounded-full ${authStep > index ? 'bg-slate-950' : 'bg-slate-300'}`} />
                        <span className={authStep === index + 1 ? 'font-semibold text-slate-950' : 'text-slate-600'}>{message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <aside className="hidden xl:flex flex-col gap-4 rounded-[28px] border border-slate-200 bg-slate-50 p-5 text-[12px] text-slate-600">
                <p className="text-[11px] uppercase tracking-[0.32em] text-slate-500">System status</p>
                <div className="grid gap-4">
                  {systemStatusItems.map((item) => (
                    <div key={item.label} className="rounded-[18px] border border-slate-200 bg-white p-4">
                      <p className="text-[9px] uppercase tracking-[0.32em] text-slate-500">{item.label}</p>
                      <p className="mt-1 font-mono text-sm text-slate-950">{item.label === 'Current Time' ? timeText : item.value}</p>
                    </div>
                  ))}
                </div>
                <div className="rounded-[18px] border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700">
                  {threatNotice}
                </div>
              </aside>
            </div>

            <footer className="mt-7 rounded-[24px] border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
              <div className="grid gap-2">
                {footerLines.map((line) => (
                  <p key={line}>{line}</p>
                ))}
              </div>
            </footer>
          </main>
        </div>
      </div>
    </motion.div>
  );
}

