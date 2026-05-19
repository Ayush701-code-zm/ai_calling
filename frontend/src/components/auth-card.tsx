import { ReactNode } from "react";

type AuthCardProps = {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: ReactNode;
  footer?: ReactNode;
};

export function AuthCard({ eyebrow, title, subtitle, children, footer }: AuthCardProps) {
  return (
    <div className="relative w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur">
      <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">{eyebrow}</p>
      <h1 className="mt-2 text-2xl font-bold text-white">{title}</h1>
      <p className="mt-2 text-sm text-slate-400">{subtitle}</p>
      <div className="mt-6">{children}</div>
      {footer && <div className="mt-6 text-center text-sm text-slate-400">{footer}</div>}
    </div>
  );
}
