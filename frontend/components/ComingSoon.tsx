export default function ComingSoon({ title, phase }: { title: string; phase: string }) {
  return (
    <div>
      <h1 className="mb-2 text-2xl font-semibold">{title}</h1>
      <p className="text-gray-600">This screen is built in {phase}.</p>
    </div>
  );
}