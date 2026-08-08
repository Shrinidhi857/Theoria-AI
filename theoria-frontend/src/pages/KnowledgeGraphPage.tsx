import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Network,
  Search,
  CheckCircle2,
  Sparkles,
  BookOpen,
  ArrowRight,
  RefreshCw,
  Zap,
  Info,
  Layers,
  Award
} from "lucide-react";
import {
  getGraphVisualization,
  getLearningPath,
  getRelatedConcepts,
  getUserRecommendations,
  markConceptCompleted,
} from "@/services/graphService";
import type {
  GraphNode,
  GraphEdge,
  LearningPathResponse,
  RelatedConceptsResponse,
  ConceptRecommendation,
} from "@/services/graphService";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const NODE_COLORS: Record<string, { bg: string; border: string; text: string; dot: string }> = {
  Concept: { bg: "bg-cyan-500/10", border: "border-cyan-500/40", text: "text-cyan-400", dot: "#06b6d4" },
  Algorithm: { bg: "bg-indigo-500/10", border: "border-indigo-500/40", text: "text-indigo-400", dot: "#6366f1" },
  DataStructure: { bg: "bg-amber-500/10", border: "border-amber-500/40", text: "text-amber-400", dot: "#f59e0b" },
  Complexity: { bg: "bg-emerald-500/10", border: "border-emerald-500/40", text: "text-emerald-400", dot: "#10b981" },
  Lesson: { bg: "bg-rose-500/10", border: "border-rose-500/40", text: "text-rose-400", dot: "#f43f5e" },
};

export const KnowledgeGraphPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const [learningPath, setLearningPath] = useState<LearningPathResponse | null>(null);
  const [relatedData, setRelatedData] = useState<RelatedConceptsResponse | null>(null);
  const [recommendations, setRecommendations] = useState<ConceptRecommendation[]>([]);
  const [completing, setCompleting] = useState<boolean>(false);

  // Load graph visualization data
  const fetchGraph = async (center?: string) => {
    setLoading(true);
    try {
      const data = await getGraphVisualization(center);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      if (data.nodes.length > 0 && !selectedNode) {
        setSelectedNode(data.nodes[0]);
      }
    } catch (err) {
      console.error("Failed to load graph visualization:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
    if (isAuthenticated) {
      getUserRecommendations()
        .then(setRecommendations)
        .catch(() => setRecommendations([]));
    }
  }, [isAuthenticated]);

  // Load details when selected node changes
  useEffect(() => {
    if (selectedNode) {
      getLearningPath(selectedNode.label)
        .then(setLearningPath)
        .catch(() => setLearningPath(null));

      getRelatedConcepts(selectedNode.label)
        .then(setRelatedData)
        .catch(() => setRelatedData(null));
    }
  }, [selectedNode]);

  const handleMarkCompleted = async () => {
    if (!selectedNode || !isAuthenticated) return;
    setCompleting(true);
    try {
      await markConceptCompleted(selectedNode.label);
      setSelectedNode({ ...selectedNode, completed: true });
      setNodes((prev) =>
        prev.map((n) => (n.id === selectedNode.id ? { ...n, completed: true } : n))
      );
    } catch (err) {
      console.error("Failed to mark concept completed:", err);
    } finally {
      setCompleting(false);
    }
  };

  // Node position calculation for SVG visualization (Balanced Radial Layout)
  const nodePositions = useMemo(() => {
    const posMap: Record<string, { x: number; y: number }> = {};
    const count = nodes.length;
    if (count === 0) return posMap;

    const centerX = 400;
    const centerY = 280;
    const radius = Math.min(220, 100 + count * 8);

    nodes.forEach((node, i) => {
      if (selectedNode && node.id === selectedNode.id) {
        posMap[node.id] = { x: centerX, y: centerY };
      } else {
        const angle = (2 * Math.PI * i) / (selectedNode ? count - 1 : count);
        posMap[node.id] = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        };
      }
    });

    return posMap;
  }, [nodes, selectedNode]);

  const filteredNodes = useMemo(() => {
    if (!searchQuery.trim()) return nodes;
    const q = searchQuery.toLowerCase();
    return nodes.filter(
      (n) =>
        n.label.toLowerCase().includes(q) ||
        n.type.toLowerCase().includes(q) ||
        (n.description && n.description.toLowerCase().includes(q))
    );
  }, [nodes, searchQuery]);

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-5">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <Network className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Computer Science Knowledge Graph</h1>
            <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 text-xs">
              Persistent & Evolving
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Explore interconnected algorithms, data structures, complexity, prerequisites, and personalized learning paths.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search concepts or algos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-muted/60 border border-border rounded-lg pl-9 pr-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchGraph(selectedNode?.label)}
            className="gap-2"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Center Graph
          </Button>
        </div>
      </div>

      {/* Main Grid: Left Visualizer + Right Details Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: SVG Canvas (2 cols) */}
        <div className="lg:col-span-2 bg-card border border-border/60 rounded-2xl p-4 shadow-sm flex flex-col justify-between min-h-[560px] relative overflow-hidden">
          {/* Graph Legend */}
          <div className="flex flex-wrap items-center gap-2 mb-3 z-10">
            {Object.entries(NODE_COLORS).map(([type, colors]) => (
              <div
                key={type}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${colors.bg} ${colors.border} ${colors.text}`}
              >
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: colors.dot }} />
                {type}
              </div>
            ))}
          </div>

          {/* SVG Canvas */}
          <div className="flex-1 w-full h-full relative flex items-center justify-center">
            {loading ? (
              <div className="flex flex-col items-center gap-2 text-muted-foreground">
                <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                <span className="text-sm">Loading Knowledge Subgraph...</span>
              </div>
            ) : nodes.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No graph nodes found matching filter.</p>
              </div>
            ) : (
              <svg viewBox="0 0 800 560" className="w-full h-[480px] select-none">
                <defs>
                  <marker
                    id="arrowhead"
                    markerWidth="8"
                    markerHeight="6"
                    refX="18"
                    refY="3"
                    orient="auto"
                  >
                    <polygon points="0 0, 8 3, 0 6" fill="currentColor" className="text-muted-foreground/60" />
                  </marker>
                </defs>

                {/* Edges */}
                {edges.map((edge, i) => {
                  const src = nodePositions[edge.source];
                  const tgt = nodePositions[edge.target];
                  if (!src || !tgt) return null;

                  return (
                    <g key={`edge-${i}`}>
                      <line
                        x1={src.x}
                        y1={src.y}
                        x2={tgt.x}
                        y2={tgt.y}
                        stroke="currentColor"
                        className="text-border/80"
                        strokeWidth="1.5"
                        strokeDasharray={edge.type === "PREREQUISITE_FOR" ? "4 4" : undefined}
                        markerEnd="url(#arrowhead)"
                      />
                      <text
                        x={(src.x + tgt.x) / 2}
                        y={(src.y + tgt.y) / 2 - 4}
                        fill="currentColor"
                        className="text-[9px] font-mono text-muted-foreground fill-muted-foreground"
                        textAnchor="middle"
                      >
                        {edge.type.replace("_", " ")}
                      </text>
                    </g>
                  );
                })}

                {/* Nodes */}
                {filteredNodes.map((node) => {
                  const pos = nodePositions[node.id] || { x: 400, y: 280 };
                  const isSelected = selectedNode?.id === node.id;
                  const colorConfig = NODE_COLORS[node.type] || NODE_COLORS.Concept;

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onClick={() => setSelectedNode(node)}
                      className="cursor-pointer group"
                    >
                      {/* Glow outline on selected */}
                      {isSelected && (
                        <circle r="32" fill="none" stroke={colorConfig.dot} strokeWidth="3" strokeOpacity="0.4" className="animate-pulse" />
                      )}

                      <circle
                        r="24"
                        fill="#0f172a"
                        stroke={colorConfig.dot}
                        strokeWidth={isSelected ? "2.5" : "1.5"}
                        className="transition-all duration-200 group-hover:scale-110"
                      />

                      {/* Node Center Dot or Checkmark */}
                      {node.completed ? (
                        <CheckCircle2 x="-8" y="-8" className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <circle r="5" fill={colorConfig.dot} />
                      )}

                      {/* Label Text */}
                      <text
                        y="38"
                        textAnchor="middle"
                        fill="currentColor"
                        className={`text-xs font-semibold tracking-tight transition-colors ${
                          isSelected ? "fill-foreground font-bold text-sm" : "fill-muted-foreground group-hover:fill-foreground"
                        }`}
                      >
                        {node.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            )}
          </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border/40 pt-2 z-10">
            <span>Showing {nodes.length} concepts & {edges.length} relationships</span>
            <span>Click any node to inspect details</span>
          </div>
        </div>

        {/* Right: Selected Node Detail & Learning Path Drawer */}
        <div className="space-y-6">
          {/* Node Details Card */}
          <div className="bg-card border border-border/60 rounded-2xl p-5 shadow-sm space-y-4">
            {selectedNode ? (
              <>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Badge
                        variant="outline"
                        className={`text-xs ${NODE_COLORS[selectedNode.type]?.bg} ${NODE_COLORS[selectedNode.type]?.text} ${NODE_COLORS[selectedNode.type]?.border}`}
                      >
                        {selectedNode.type}
                      </Badge>
                      {selectedNode.completed && (
                        <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs gap-1">
                          <CheckCircle2 className="h-3 w-3" /> Completed
                        </Badge>
                      )}
                    </div>
                    <h2 className="text-xl font-bold tracking-tight">{selectedNode.label}</h2>
                  </div>

                  <Button
                    size="sm"
                    className="gap-1.5 bg-primary text-primary-foreground hover:bg-primary/90"
                    onClick={() => navigate(`/new?topic=${encodeURIComponent(`Explain ${selectedNode.label}`)}`)}
                  >
                    <Zap className="h-3.5 w-3.5" />
                    Teach Me
                  </Button>
                </div>

                {selectedNode.description && (
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {selectedNode.description}
                  </p>
                )}

                {/* Mark Completed Action */}
                {isAuthenticated && !selectedNode.completed && (
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={completing}
                    onClick={handleMarkCompleted}
                    className="w-full gap-2 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    {completing ? "Marking Completed..." : "Mark Concept as Completed"}
                  </Button>
                )}

                <div className="border-t border-border/60 my-3" />

                {/* Learning Path Breakdown */}
                {learningPath && (
                  <div className="space-y-3">
                    <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="h-3.5 w-3.5 text-primary" /> Learning Path Breakdown
                    </h3>

                    {/* Prerequisites */}
                    <div>
                      <span className="text-xs font-medium text-foreground block mb-1">Prerequisites Needed:</span>
                      {learningPath.prerequisites.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                          {learningPath.prerequisites.map((p) => (
                            <Badge
                              key={p}
                              variant="secondary"
                              className="text-xs cursor-pointer hover:bg-muted"
                              onClick={() => {
                                const match = nodes.find((n) => n.label.toLowerCase() === p.toLowerCase());
                                if (match) setSelectedNode(match);
                                else fetchGraph(p);
                              }}
                            >
                              {p}
                            </Badge>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground italic">None (Foundational concept)</span>
                      )}
                    </div>

                    {/* Next Concepts */}
                    <div>
                      <span className="text-xs font-medium text-foreground block mb-1">Unlocks Next:</span>
                      {learningPath.next_concepts.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                          {learningPath.next_concepts.map((nxt) => (
                            <Badge
                              key={nxt}
                              variant="outline"
                              className="text-xs border-primary/30 text-primary cursor-pointer hover:bg-primary/10"
                              onClick={() => {
                                const match = nodes.find((n) => n.label.toLowerCase() === nxt.toLowerCase());
                                if (match) setSelectedNode(match);
                                else fetchGraph(nxt);
                              }}
                            >
                              {nxt} <ArrowRight className="h-2.5 w-2.5 ml-1" />
                            </Badge>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground italic">Advanced concept</span>
                      )}
                    </div>
                  </div>
                )}

                {/* Related Data */}
                {relatedData && (relatedData.complexity.length > 0 || relatedData.data_structures.length > 0) && (
                  <div className="space-y-2 border-t border-border/60 pt-3">
                    {relatedData.complexity.length > 0 && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-muted-foreground">Complexity:</span>
                        {relatedData.complexity.map((cx) => (
                          <Badge key={cx} className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-mono">
                            {cx}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {relatedData.data_structures.length > 0 && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-muted-foreground">Uses Data Structures:</span>
                        {relatedData.data_structures.map((ds) => (
                          <Badge key={ds} variant="secondary" className="text-xs">
                            {ds}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Select any concept node in the graph to view details and learning paths.</p>
              </div>
            )}
          </div>

          {/* Recommendations Card if Authenticated */}
          {isAuthenticated && recommendations.length > 0 && (
            <div className="bg-gradient-to-br from-primary/5 via-violet-500/5 to-transparent border border-primary/20 rounded-2xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-primary font-semibold text-sm">
                <Sparkles className="h-4 w-4" />
                <span>Recommended Next Concepts</span>
              </div>
              <div className="space-y-2">
                {recommendations.slice(0, 3).map((rec) => (
                  <div
                    key={rec.normalized_name}
                    onClick={() => fetchGraph(rec.concept)}
                    className="p-2.5 rounded-lg border border-border/60 bg-card/60 hover:bg-card hover:border-primary/40 cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div>
                      <span className="text-xs font-bold block">{rec.concept}</span>
                      <span className="text-[10px] text-muted-foreground">{rec.reason}</span>
                    </div>
                    <ArrowRight className="h-3.5 w-3.5 text-primary opacity-70" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
