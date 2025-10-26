'use client';

export default function Section({title, description, children, actions}) {
  return (
    <section className="card space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          {description ? <p className="text-sm text-slate-600">{description}</p> : null}
        </div>
        {actions ? <div className="flex gap-2">{actions}</div> : null}
      </header>
      <div className="space-y-4">{children}</div>
    </section>
  );
}
