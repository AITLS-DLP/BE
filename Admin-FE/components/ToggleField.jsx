'use client';

export default function ToggleField({label, description, checked, onChange, disabled = false}) {
  return (
    <label className="flex items-start gap-3">
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange?.(event.target.checked)}
      />
      <div>
        <p className="text-sm font-medium text-slate-900">{label}</p>
        {description ? <p className="text-xs text-slate-500">{description}</p> : null}
      </div>
    </label>
  );
}
