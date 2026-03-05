"use client";

/**
 * SVG circle gauge for match score display.
 */

interface ScoreGaugeProps {
  /** Match score 0-100. */
  score: number;
}

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/** Get color class based on score. */
function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-500";
  if (score >= 60) return "text-yellow-500";
  return "text-red-500";
}

/** Get stroke color for SVG. */
function getStrokeColor(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#eab308";
  return "#ef4444";
}

export function ScoreGauge({ score }: ScoreGaugeProps) {
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-[140px] w-[140px]">
        <svg width="140" height="140" className="-rotate-90">
          <circle
            cx="70"
            cy="70"
            r={RADIUS}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-muted"
          />
          <circle
            cx="70"
            cy="70"
            r={RADIUS}
            fill="none"
            stroke={getStrokeColor(score)}
            strokeWidth="10"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-3xl font-bold ${getScoreColor(score)}`}>
            {score}
          </span>
        </div>
      </div>
      <p className="text-sm text-muted-foreground">Match Score</p>
    </div>
  );
}
