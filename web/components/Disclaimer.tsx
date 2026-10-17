export function Disclaimer({ text }: { text?: string }) {
  return (
    <div className="disclaimer">
      {text ||
        "Exploratory only. Not medical advice, not a clinical diagnosis, and not proof of descent from any named historical person. Files stay on this machine."}
    </div>
  );
}
