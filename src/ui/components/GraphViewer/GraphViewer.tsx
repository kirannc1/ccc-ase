"use client";

import cytoscape, { Core } from "cytoscape";
import { useEffect, useRef } from "react";

export type GraphNode = { id: string; label: string; status?: "default" | "highlight" | "risk" };
export type GraphEdge = { id: string; source: string; target: string; label?: string };

export function GraphViewer({
  nodes,
  edges,
  height = 320
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  height?: number;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const coreRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map((node) => ({ data: { id: node.id, label: node.label, status: node.status ?? "default" } })),
        ...edges.map((edge) => ({ data: { id: edge.id, source: edge.source, target: edge.target, label: edge.label ?? "" } }))
      ],
      style: [
        { selector: "node", style: { label: "data(label)", "text-wrap": "wrap", "text-max-width": "140px", "background-color": "#4F6BED", color: "#111" } },
        { selector: 'node[status = "risk"]', style: { "background-color": "#D13438" } },
        { selector: 'node[status = "highlight"]', style: { "background-color": "#00B7C3" } },
        { selector: "edge", style: { width: 2, "line-color": "#bbb", "target-arrow-color": "#bbb", "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(label)" } }
      ],
      layout: { name: "cose", animate: false }
    });
    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      cy.elements().removeClass("selected");
      node.addClass("selected");
      cy.center(node);
    });
    coreRef.current = cy;
    return () => {
      cy.destroy();
      coreRef.current = null;
    };
  }, [nodes, edges]);

  return <div ref={containerRef} style={{ width: "100%", height }} aria-label="graph viewer" />;
}

