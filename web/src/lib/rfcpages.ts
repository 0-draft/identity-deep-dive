import { landscape, type Spec } from "./landscape";
import { rfcNumbers } from "./rfc";

/** Specs on the map whose RFC text is in data/rfc, so they get a bilingual page. */
export function rfcSpecs(): (Spec & { rfcNumber: number })[] {
  const have = new Set(rfcNumbers());
  return landscape()
    .specs.map((s) => {
      const n = s.ietf?.rfc ?? (s.status.stage === "rfc" ? Number(/RFC (\d+)/.exec(s.status.label)?.[1]) : undefined);
      return n && have.has(n) ? { ...s, rfcNumber: n } : null;
    })
    .filter((s): s is Spec & { rfcNumber: number } => s !== null);
}
