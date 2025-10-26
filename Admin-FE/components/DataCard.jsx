'use client';

import clsx from 'clsx';

export default function DataCard({title, value, description, tone = 'default'}) {
  const toneClass = {
    default: 'bg-white text-slate-900',
    success: 'bg-emerald-600 text-white',
    danger: 'bg-rose-600 text-white',
    info: 'bg-slate-900 text-white'
  }[tone] ?? 'bg-white text-slate-900';

  return (
    <section className={clsx('card space-y-2 shadow-sm', toneClass)}>
      <p className="text-sm font-medium opacity-75">{title}</p>
      <p className="text-3xl font-semibold">{value}</p>
      {description ? <p className="text-sm opacity-80">{description}</p> : null}
    </section>
  );
}
