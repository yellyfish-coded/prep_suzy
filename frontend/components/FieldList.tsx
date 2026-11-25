"use client";

type Field = { key: string; label: string; multiline?: boolean };

type Props = {
  title: string;
  items: Record<string, string>[];
  fields: Field[];
  onChange: (items: Record<string, string>[]) => void;
  addLabel: string;
  max: number;
};

export default function FieldList({ title, items, fields, onChange, addLabel, max }: Props) {
  function update(index: number, key: string, value: string) {
    onChange(items.map((item, i) => (i === index ? { ...item, [key]: value } : item)));
  }

  function remove(index: number) {
    onChange(items.filter((_, i) => i !== index));
  }

  function add() {
    onChange([...items, Object.fromEntries(fields.map((f) => [f.key, ""]))]);
  }

  return (
    <section className="mb-8">
      <h2 className="mb-2 text-lg font-semibold">
        {title} <span className="text-sm font-normal text-gray-500">({items.length})</span>
      </h2>

      {items.length === 0 && <p className="mb-2 text-sm text-gray-500">Nothing here yet.</p>}

      <div className="space-y-3">
        {items.map((item, i) => (
          <div key={i} className="rounded border bg-white p-3">
            <div className="grid gap-2 sm:grid-cols-2">
              {fields.map((f) => {
                const id = `${title}-${i}-${f.key}`;
                return (
                  <div key={f.key} className={f.multiline ? "sm:col-span-2" : ""}>
                    <label htmlFor={id} className="mb-1 block text-xs font-medium text-gray-600">
                      {f.label}
                    </label>
                    {f.multiline ? (
                      <textarea
                        id={id}
                        rows={3}
                        value={item[f.key] ?? ""}
                        onChange={(e) => update(i, f.key, e.target.value)}
                        className="w-full rounded border p-2 text-sm"
                      />
                    ) : (
                      <input
                        id={id}
                        value={item[f.key] ?? ""}
                        onChange={(e) => update(i, f.key, e.target.value)}
                        className="w-full rounded border p-2 text-sm"
                      />
                    )}
                  </div>
                );
              })}
            </div>
            <button
              type="button"
              onClick={() => remove(i)}
              className="mt-2 text-sm text-red-700 hover:underline"
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      {items.length < max && (
        <button
          type="button"
          onClick={add}
          className="mt-3 rounded border bg-white px-3 py-1 text-sm hover:bg-gray-100"
        >
          {addLabel}
        </button>
      )}
    </section>
  );
}