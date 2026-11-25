export function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div role="status" className="p-6 text-gray-500">
      {label}
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div role="alert" className="rounded border border-red-300 bg-red-50 p-4 text-red-800">
      {message}
    </div>
  );
}

export function Empty({ message }: { message: string }) {
  return <div className="rounded border border-dashed p-6 text-center text-gray-500">{message}</div>;
}