interface SkeletonProps {
  variant?: "page" | "grid" | "list";
}

export function SkeletonGrid() {
  return (
    <div className="metric-grid">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="skeleton-block">
          <div className="skeleton-line short" />
          <div className="skeleton-line h2" />
          <div className="skeleton-line med" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonList({ rows = 5 }: { rows?: number }) {
  return (
    <div className="skeleton-block">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ marginBottom: i === rows - 1 ? 0 : undefined }}>
          <div className="skeleton-line wide" />
          <div className="skeleton-line short" />
        </div>
      ))}
    </div>
  );
}

export default function Skeleton({ variant = "page" }: SkeletonProps) {
  if (variant === "grid") return <SkeletonGrid />;
  if (variant === "list") return <SkeletonList />;
  return (
    <div className="stack">
      <SkeletonGrid />
      <div className="skeleton-block">
        <div className="skeleton-line short" />
        <div className="skeleton-line wide" />
        <div className="skeleton-line wide" />
        <div className="skeleton-line med" />
      </div>
    </div>
  );
}