import { useEffect, useRef } from "react";
import embed from "vega-embed";

export function VegaChart({ spec }: { spec: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    let parsed: any;
    try {
      parsed = JSON.parse(spec);
    } catch {
      return;
    }
    parsed.width = "container";
    parsed.autosize = { type: "fit", contains: "padding" };
    parsed.config = {
      ...(parsed.config || {}),
      background: "transparent",
      font: "Arial",
      range: { category: ["#29B5E8", "#11567F", "#FF9F36", "#7D44CF", "#D45B90", "#75CDD7"] },
      mark: { color: "#29B5E8" },
    };
    const result = embed(ref.current, parsed, { actions: false, renderer: "svg" });
    return () => {
      result.then((r) => r.finalize()).catch(() => undefined);
    };
  }, [spec]);
  return <div className="chart" ref={ref} />;
}
