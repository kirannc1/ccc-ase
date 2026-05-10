"use client";

import * as echarts from "echarts";
import { useEffect, useMemo, useRef } from "react";

export type EChartsOption = echarts.EChartsOption;

export function ChartWrapper({ option, height = 280 }: { option: EChartsOption; height?: number }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const stableOption = useMemo(() => option, [option]);

  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    chart.setOption(stableOption, { notMerge: true });
    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [stableOption]);

  return <div ref={ref} style={{ width: "100%", height }} />;
}

