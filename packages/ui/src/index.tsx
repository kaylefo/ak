import type { ReactNode, HTMLAttributes, ButtonHTMLAttributes } from "react";

export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  narrow?: boolean;
}

export function Container({ children, narrow, className, ...props }: ContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full px-6",
        narrow ? "max-w-3xl" : "max-w-6xl",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  eyebrow?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, eyebrow, actions }: PageHeaderProps) {
  return (
    <header className="mb-10 border-b border-stone-200 pb-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          {eyebrow ? (
            <p className="mb-2 font-mono text-xs uppercase tracking-[0.2em] text-stone-500">
              {eyebrow}
            </p>
          ) : null}
          <h1 className="font-serif text-3xl font-light tracking-tight text-stone-900 sm:text-4xl">
            {title}
          </h1>
          {subtitle ? (
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-stone-600">
              {subtitle}
            </p>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 gap-2">{actions}</div> : null}
      </div>
    </header>
  );
}

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: "default" | "outline" | "muted";
}

export function Card({ children, variant = "default", className, ...props }: CardProps) {
  const variants = {
    default: "bg-white border border-stone-200 shadow-sm",
    outline: "bg-transparent border border-stone-200",
    muted: "bg-stone-50 border border-stone-100",
  };

  return (
    <div className={cn("rounded-sm p-5", variants[variant], className)} {...props}>
      {children}
    </div>
  );
}

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
}

export function Badge({ children, tone = "neutral", className, ...props }: BadgeProps) {
  const tones = {
    neutral: "bg-stone-100 text-stone-700 border-stone-200",
    success: "bg-emerald-50 text-emerald-800 border-emerald-200",
    warning: "bg-amber-50 text-amber-800 border-amber-200",
    danger: "bg-rose-50 text-rose-800 border-rose-200",
    info: "bg-sky-50 text-sky-800 border-sky-200",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider",
        tones[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonProps) {
  const variants = {
    primary: "bg-stone-900 text-stone-50 hover:bg-stone-800",
    secondary: "bg-white text-stone-900 border border-stone-300 hover:bg-stone-50",
    ghost: "bg-transparent text-stone-700 hover:bg-stone-100",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-sm font-medium transition-colors disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export interface StatProps {
  label: string;
  value: string | number;
  hint?: string;
}

export function Stat({ label, value, hint }: StatProps) {
  return (
    <div className="border-l-2 border-stone-300 pl-4">
      <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500">
        {label}
      </p>
      <p className="mt-1 font-serif text-2xl font-light text-stone-900">{value}</p>
      {hint ? <p className="mt-1 text-xs text-stone-500">{hint}</p> : null}
    </div>
  );
}

export interface DataTableProps {
  headers: string[];
  rows: (string | ReactNode)[][];
  emptyMessage?: string;
}

export function DataTable({ headers, rows, emptyMessage = "No data" }: DataTableProps) {
  if (rows.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-stone-500">{emptyMessage}</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-stone-200">
            {headers.map((header) => (
              <th
                key={header}
                className="px-4 py-3 font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-stone-100 hover:bg-stone-50/50">
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-3 text-stone-700">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-sm border border-dashed border-stone-300 bg-stone-50/50 px-8 py-16 text-center">
      <h3 className="font-serif text-lg font-light text-stone-800">{title}</h3>
      {description ? (
        <p className="mt-2 max-w-md text-sm text-stone-500">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}

export interface SectionProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  title?: string;
  id?: string;
}

export function Section({ children, title, id, className, ...props }: SectionProps) {
  return (
    <section id={id} className={cn("mb-10", className)} {...props}>
      {title ? (
        <h2 className="mb-4 font-mono text-xs uppercase tracking-[0.2em] text-stone-500">
          {title}
        </h2>
      ) : null}
      {children}
    </section>
  );
}
