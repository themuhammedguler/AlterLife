"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import { getSimulationTree, branchSimulation, runStressTest, generateSimulation } from "@/lib/api";

interface NodeData {
  id: string;
  label: string;
  parent: string | null;
  metrics: { savings: number; stress: number; happiness: number; career: number };
  desc: string;
  color: string;
}

const DEFAULT_NODE: NodeData = {
  id: "node_root",
  label: "Başlangıç Durumu",
  parent: null,
  metrics: { savings: 500, stress: 30, happiness: 70, career: 20 },
  desc: "Yükleniyor...",
  color: "var(--accent-cyan)"
};

export default function SimulationsPage() {
  const [tree, setTree] = useState<NodeData[]>([DEFAULT_NODE]);
  const [selectedNode, setSelectedNode] = useState<NodeData>(DEFAULT_NODE);
  const [whatIfText, setWhatIfText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<{ optionA: string; optionB: string } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  // Load Tree from Backend
  const loadTree = async () => {
    setLoading(true);
    setError(null);
    try {
      let baseGoal: string | null = null;
      if (typeof window !== "undefined") {
        const params = new URLSearchParams(window.location.search);
        baseGoal = params.get("base_goal");
      }

      let data;
      if (baseGoal) {
        data = await generateSimulation(baseGoal);
        if (typeof window !== "undefined") {
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      } else {
        data = await getSimulationTree();
      }

      if (data && data.nodes) {
        const mapped: NodeData[] = data.nodes.map((n: any, idx: number) => {
          let nodeColor = "var(--accent-violet)";
          if (idx === 0) {
            nodeColor = "var(--accent-cyan)";
          } else if (n.node_id.includes("crisis")) {
            nodeColor = "var(--accent-pink)";
          } else if (n.node_id.includes("whatif")) {
            nodeColor = "var(--accent-green)";
          }
          
          return {
            id: n.node_id,
            label: n.decision_name,
            parent: n.parent,
            metrics: {
              savings: n.metrics.monthly_savings,
              stress: n.metrics.stress_level,
              happiness: n.metrics.happiness,
              career: n.metrics.career_progress
            },
            desc: n.description || "",
            color: nodeColor
          };
        });
        setTree(mapped);
        
        // Retain selection if valid, otherwise select root
        const found = mapped.find(n => n.id === selectedNode.id);
        setSelectedNode(found || mapped[0]);
      }
    } catch (err: any) {
      setError(err.message || "Simülasyon ağacı yüklenemedi.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  // Generate Suggestions based on Selected Node
  useEffect(() => {
    if (selectedNode.id === "node_root") {
      setAiSuggestions({
        optionA: "Yarı zamanlı freelance işlerle portfolyoyu büyütmek",
        optionB: "Mevcut işinde kalıp bulut sertifikaları almak",
      });
    } else if (selectedNode.id.includes("path_1")) {
      setAiSuggestions({
        optionA: "Berlin yerine yaşam maliyeti düşük Köln veya Münih'i seçmek",
        optionB: "Almanya öncesi 6 ay Polonya veya Estonya'da tecrübe kazanmak",
      });
    } else if (selectedNode.id.includes("path_2")) {
      setAiSuggestions({
        optionA: "Master yaparken yarı zamanlı çalışıp (Werkstudent) tecrübe kazanmak",
        optionB: "İngilizce eğitim veren devlet üniversitelerini araştırmak",
      });
    } else {
      setAiSuggestions({
        optionA: "Bu adımı 6 ay erteleyip bütçeyi %25 artırmak",
        optionB: "Alanın uzmanlarıyla LinkedIn'de networking yapmak",
      });
    }
  }, [selectedNode]);

  // Handle Add Branch (What If)
  const handleAddNewBranch = async (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const newNode = await branchSimulation(selectedNode.id, text);
      const mappedNode: NodeData = {
        id: newNode.node_id,
        label: newNode.decision_name,
        parent: newNode.parent,
        metrics: {
          savings: newNode.metrics.monthly_savings,
          stress: newNode.metrics.stress_level,
          happiness: newNode.metrics.happiness,
          career: newNode.metrics.career_progress
        },
        desc: newNode.description || "",
        color: "var(--accent-green)"
      };

      setTree(prev => [...prev, mappedNode]);
      setSelectedNode(mappedNode);
      setWhatIfText("");
    } catch (err: any) {
      setError(err.message || "Yeni dal oluşturulamadı.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Black Swan Stress Test
  const handleStressTest = async () => {
    setLoading(true);
    setError(null);
    try {
      const newNode = await runStressTest(selectedNode.id);
      const mappedNode: NodeData = {
        id: newNode.node_id,
        label: newNode.decision_name,
        parent: newNode.parent,
        metrics: {
          savings: newNode.metrics.monthly_savings,
          stress: newNode.metrics.stress_level,
          happiness: newNode.metrics.happiness,
          career: newNode.metrics.career_progress
        },
        desc: newNode.description || "",
        color: "var(--accent-pink)"
      };

      setTree(prev => [...prev, mappedNode]);
      setSelectedNode(mappedNode);
    } catch (err: any) {
      setError(err.message || "Stres testi çalıştırılamadı.");
    } finally {
      setLoading(false);
    }
  };

  // Breadcrumbs (Path from Root to Selected Node)
  const getPathBreadcrumbs = () => {
    const path: NodeData[] = [];
    let current: NodeData | undefined = selectedNode;
    while (current) {
      path.unshift(current);
      const parentId: string | null = current.parent;
      if (!parentId) break;
      current = tree.find((n) => n.id === parentId);
    }
    return path;
  };

  // Nodes at Depth in Tree
  const getNodesAtDepth = (depth: number): NodeData[] => {
    const path = getPathBreadcrumbs();
    if (depth === 0) {
      return tree.filter((n) => n.parent === null);
    }
    const ancestor = path[depth - 1];
    if (!ancestor) return [];
    return tree.filter((n) => n.parent === ancestor.id);
  };

  // Coordinates Layout Calculation
  const layoutData = useMemo(() => {
    const columns: NodeData[][] = [];
    const breadcrumbs = getPathBreadcrumbs();
    
    // Calculate how many columns we need
    const maxDepth = Math.max(1, breadcrumbs.length);
    for (let d = 0; d <= maxDepth; d++) {
      const nodes = getNodesAtDepth(d);
      if (nodes.length > 0) {
        columns.push(nodes);
      }
    }

    const nodeCoords: { [id: string]: { x: number; y: number } } = {};
    const colWidth = 260;
    const colGap = 80;
    
    columns.forEach((nodes, colIdx) => {
      const colX = colIdx * (colWidth + colGap) + 20;
      nodes.forEach((node, nodeIdx) => {
        // Space nodes vertically
        const nodeY = nodeIdx * 90 + 30;
        nodeCoords[node.id] = { x: colX, y: nodeY };
      });
    });

    // Find connections
    const connections: { id: string; from: { x: number; y: number }; to: { x: number; y: number }; color: string }[] = [];
    tree.forEach((node) => {
      if (node.parent && nodeCoords[node.parent] && nodeCoords[node.id]) {
        connections.push({
          id: `${node.parent}-${node.id}`,
          from: nodeCoords[node.parent],
          to: nodeCoords[node.id],
          color: node.color
        });
      }
    });

    // Find total height and width
    let totalHeight = 350;
    columns.forEach(nodes => {
      const h = nodes.length * 90 + 60;
      if (h > totalHeight) totalHeight = h;
    });

    const totalWidth = columns.length * (colWidth + colGap) + 100;

    return {
      columns,
      nodeCoords,
      connections,
      width: totalWidth,
      height: totalHeight
    };
  }, [tree, selectedNode]);

  return (
    <div className="page-container" style={{ maxWidth: "1400px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "32px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Karar Ağacı & Simülasyon</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          what if? — Hayatınızın tüm dallanmalarını ve alternatif yollarını zihin haritası olarak gözden geçirin
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "12px 16px",
            background: "rgba(255, 61, 0, 0.1)",
            border: "1px solid rgba(255, 61, 0, 0.3)",
            borderRadius: "var(--radius-md)",
            color: "#ff3d00",
            fontSize: "0.85rem",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      {/* ── ZİHİN HARİTASI PANELİ (SVG-Connected Mind Map) ────────────────── */}
      <div
        className="glass-card"
        style={{
          padding: "32px",
          marginBottom: "28px",
          overflowX: "auto",
          position: "relative"
        }}
      >
        <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "6px", color: "var(--text-primary)" }}>
          Zihin Haritası Görünümü (Mind Map)
        </h2>
        <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "24px" }}>
          Seçenekler soldan sağa doğru dallanarak ilerler. Bir adıma tıklayarak o yolu seçebilir ve sağa doğru yeni dallar üretebilirsiniz.
        </p>

        <div 
          ref={containerRef}
          style={{ 
            position: "relative", 
            width: `${layoutData.width}px`, 
            height: `${layoutData.height}px`,
            minHeight: "350px",
            transition: "all 0.3s ease"
          }}
        >
          {/* SVG Connector Lines Layer */}
          <svg 
            style={{ 
              position: "absolute", 
              top: 0, 
              left: 0, 
              width: "100%", 
              height: "100%",
              pointerEvents: "none",
              zIndex: 1
            }}
          >
            <defs>
              <linearGradient id="cyan-violet" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="var(--accent-cyan)" />
                <stop offset="100%" stopColor="var(--accent-violet)" />
              </linearGradient>
            </defs>
            {layoutData.connections.map((conn) => {
              const x1 = conn.from.x + 240;
              const y1 = conn.from.y + 22;
              const x2 = conn.to.x;
              const y2 = conn.to.y + 22;
              const midX = (x1 + x2) / 2;
              const d = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
              
              const isSelectedPath = getPathBreadcrumbs().some(n => n.id === conn.id.split("-")[1]);

              return (
                <path
                  key={conn.id}
                  d={d}
                  fill="none"
                  stroke={isSelectedPath ? conn.color : "rgba(255, 255, 255, 0.08)"}
                  strokeWidth={isSelectedPath ? 3.5 : 1.5}
                  strokeDasharray={conn.color.includes("pink") ? "4 4" : "none"}
                  style={{
                    filter: isSelectedPath ? `drop-shadow(0 0 4px ${conn.color})` : "none",
                    transition: "all 0.3s ease"
                  }}
                />
              );
            })}
          </svg>

          {/* HTML Nodes Layer */}
          <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", zIndex: 2 }}>
            {layoutData.columns.map((column, colIdx) => (
              <div key={colIdx}>
                {column.map((node) => {
                  const coords = layoutData.nodeCoords[node.id];
                  if (!coords) return null;
                  
                  const isSelected = selectedNode.id === node.id;
                  const isActivePath = getPathBreadcrumbs().some(n => n.id === node.id);

                  return (
                    <button
                      key={node.id}
                      type="button"
                      onClick={() => setSelectedNode(node)}
                      style={{
                        position: "absolute",
                        left: `${coords.x}px`,
                        top: `${coords.y}px`,
                        width: "240px",
                        height: "44px",
                        ...mindmapNodeStyle(isActivePath, isSelected, node.color)
                      }}
                    >
                      <strong>{node.label}</strong>
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "24px" }}>

        {/* Sol Sütun: Dallanmalar Ekleme ve AI Önerileri */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          <div className="glass-card" style={{ padding: "28px" }}>
            <div style={{ textAlign: "center", marginBottom: "32px" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Seçili Aktif Adım
              </div>
              <button
                type="button"
                style={{
                  ...nodeButtonStyle(true, selectedNode.color),
                  maxWidth: "280px",
                  display: "inline-block",
                  boxShadow: "var(--shadow-glow-cyan)",
                }}
              >
                {selectedNode.label}
              </button>
            </div>

            {/* AI Önerileri Panel */}
            {aiSuggestions && (
              <div
                style={{
                  padding: "20px",
                  background: "rgba(124,58,237,0.04)",
                  border: "1px solid rgba(124,58,237,0.15)",
                  borderRadius: "var(--radius-md)",
                  marginBottom: "24px",
                }}
              >
                <h3 style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--accent-cyan)", marginBottom: "8px" }}>
                  AI Gelişim Önerileri (Aktif Dala Göre)
                </h3>
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "14px" }}>
                  AI mevcut dalı gözden geçirdi ve bir sonraki adım için şu alternatif seçenekleri hazırladı. Tıklayarak alt dallar ekleyebilirsiniz:
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => handleAddNewBranch(aiSuggestions.optionA)}
                    style={suggestionButtonStyle}
                  >
                    {aiSuggestions.optionA}
                  </button>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => handleAddNewBranch(aiSuggestions.optionB)}
                    style={suggestionButtonStyle}
                  >
                    {aiSuggestions.optionB}
                  </button>
                </div>
              </div>
            )}

            {/* Custom Step Creator */}
            <div
              style={{
                padding: "20px",
                background: "rgba(0, 229, 255, 0.03)",
                border: "1px solid var(--glass-border)",
                borderRadius: "var(--radius-md)",
              }}
            >
              <h3 style={{ fontSize: "0.88rem", fontWeight: 600, marginBottom: "12px", color: "var(--accent-cyan)" }}>
                Aktif Dala Yeni Seçenek Ekle
              </h3>
              <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginBottom: "12px" }}>
                Seçili olan &ldquo;{selectedNode.label}&rdquo; adımından sonra dallanabilecek yeni bir yol yazın:
              </p>
              <div style={{ display: "flex", gap: "10px" }}>
                <input
                  id="input-what-if"
                  type="text"
                  value={whatIfText}
                  onChange={(e) => setWhatIfText(e.target.value)}
                  placeholder='Örn: "Yüksek Lisans sırasında staj yapmak"'
                  disabled={loading}
                  style={{
                    flex: 1, padding: "10px 14px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--text-primary)", fontSize: "0.85rem", outline: "none",
                    fontFamily: "'Inter', sans-serif",
                  }}
                />
                <button
                  id="btn-generate-branch"
                  className="btn-primary"
                  type="button"
                  disabled={loading}
                  style={{ whiteSpace: "nowrap", padding: "10px 18px", fontSize: "0.85rem" }}
                  onClick={() => handleAddNewBranch(whatIfText)}
                >
                  {loading ? "Ekleniyor..." : "Seçenek Ekle"}
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* Sağ Sütun: Düğüm Detayları */}
        <div className="glass-card" style={{ padding: "24px", height: "fit-content" }}>
          <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, marginBottom: "6px", fontSize: "1.1rem" }}>
            {selectedNode.label}
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "22px", lineHeight: 1.55 }}>
            {selectedNode.desc}
          </p>

          {[
            { label: "Aylık Tasarruf", value: `$${selectedNode.metrics.savings}`, positive: selectedNode.metrics.savings > 500 },
            { label: "Stres Seviyesi", value: `${selectedNode.metrics.stress}%`, positive: selectedNode.metrics.stress < 50 },
            { label: "Mutluluk Oranı", value: `${selectedNode.metrics.happiness}%`, positive: selectedNode.metrics.happiness > 60 },
            { label: "Kariyer Skoru", value: `${selectedNode.metrics.career}%`, positive: selectedNode.metrics.career > 40 },
          ].map((m) => (
            <div
              key={m.label}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 0",
                borderBottom: "1px solid var(--glass-border)",
              }}
            >
              <span style={{ fontSize: "0.83rem", color: "var(--text-secondary)" }}>{m.label}</span>
              <span style={{ fontWeight: 700, fontSize: "0.9rem", color: m.positive ? "var(--accent-green)" : "var(--accent-pink)" }}>
                {m.value}
              </span>
            </div>
          ))}

          {/* Black Swan Stress Test Button */}
          <button
            type="button"
            className="btn-primary"
            disabled={loading}
            style={{
              width: "100%",
              justifyContent: "center",
              marginTop: "20px",
              background: "rgba(236, 72, 153, 0.12)",
              border: "1px solid rgba(236, 72, 153, 0.3)",
              color: "var(--accent-pink)",
              fontSize: "0.85rem",
              fontWeight: 600
            }}
            onClick={handleStressTest}
          >
            {loading ? "Stres Testi Sürüyor..." : "⚡ Kara Kuğu Stres Testi"}
          </button>

          {selectedNode.parent && (
            <button
              type="button"
              className="btn-ghost"
              style={{ width: "100%", justifyContent: "center", marginTop: "14px" }}
              onClick={() => {
                const parentNode = tree.find((n) => n.id === selectedNode.parent);
                if (parentNode) setSelectedNode(parentNode);
              }}
            >
              ← Üst Adıma Geri Dön
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Yardımcı Stiller ──────────────────────────────────────────────────────────

function mindmapNodeStyle(isActivePath: boolean, isSelected: boolean, color: string): React.CSSProperties {
  return {
    padding: "10px 14px",
    background: isSelected ? "rgba(0, 229, 255, 0.08)" : "var(--glass-bg)",
    border: `1px solid ${isSelected ? "var(--accent-cyan)" : isActivePath ? color : "var(--glass-border)"}`,
    borderRadius: "var(--radius-md)",
    color: isSelected ? "var(--accent-cyan)" : isActivePath ? "var(--text-primary)" : "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "0.82rem",
    textAlign: "left",
    fontFamily: "'Inter', sans-serif",
    transition: "all 0.2s ease",
    boxShadow: isSelected ? "var(--shadow-glow-cyan)" : "none",
    opacity: isActivePath ? 1 : 0.4,
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    zIndex: 10
  };
}

function nodeButtonStyle(selected: boolean, color: string): React.CSSProperties {
  return {
    padding: "13px 18px",
    background: selected ? `${color}18` : "var(--glass-bg)",
    border: `1px solid ${selected ? color : "var(--glass-border)"}`,
    borderRadius: "var(--radius-md)",
    cursor: "pointer",
    color: selected ? color : "var(--text-primary)",
    fontFamily: "'Inter', sans-serif",
    fontWeight: selected ? 600 : 400,
    fontSize: "0.9rem",
    transition: "all 0.2s ease",
    textAlign: "center" as const,
    width: "100%",
  };
}

const suggestionButtonStyle: React.CSSProperties = {
  width: "100%",
  padding: "12px 16px",
  background: "rgba(255, 255, 255, 0.02)",
  border: "1px dashed rgba(0, 229, 255, 0.2)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-secondary)",
  cursor: "pointer",
  fontSize: "0.82rem",
  textAlign: "left",
  fontFamily: "'Inter', sans-serif",
  transition: "all 0.2s ease",
};
