/**
 * HazardBadge — small label that displays a hazard with an icon.
 * Severity colors map to the SafeLab semantic risk scale.
 */

import type { ReactElement } from "react";
import {
  Flame,
  TestTube,
  Skull,
  Droplets,
  AlertOctagon,
  AlertTriangle,
  Biohazard,
  Leaf,
  Wind,
} from "lucide-react";
import type { Hazard } from "@/lib/types";

const ICONS: Record<string, ReactElement> = {
  flame:           <Flame className="h-3 w-3" />,
  "test-tube":     <TestTube className="h-3 w-3" />,
  skull:           <Skull className="h-3 w-3" />,
  "droplet-off":   <Droplets className="h-3 w-3" />,
  "alert-octagon": <AlertOctagon className="h-3 w-3" />,
  "alert-triangle":<AlertTriangle className="h-3 w-3" />,
  biohazard:       <Biohazard className="h-3 w-3" />,
  leaf:            <Leaf className="h-3 w-3" />,
  wind:            <Wind className="h-3 w-3" />,
};

const SEVERITY_STYLES: Record<string, string> = {
  low:    "badge-safe",
  medium: "badge-unknown",
  high:   "badge-unsafe",
};

export default function HazardBadge({ hazard }: { hazard: Hazard }) {
  const icon = ICONS[hazard.pictogram] ?? <AlertTriangle className="h-3 w-3" />;
  const style = SEVERITY_STYLES[hazard.default_severity] ?? SEVERITY_STYLES.medium;
  return (
    <span className={`badge ${style}`} title={hazard.description}>
      {icon}
      {hazard.name}
    </span>
  );
}
