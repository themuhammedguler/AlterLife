"use client";

import { useEffect, useState } from "react";

interface NodeData {
  id: string;
  label: string;
  parent: string | null;
  metrics: { savings: number; stress: number; happiness: number; career: number };
  desc: string;
  color: string;
}

// ── Çok Seviyeli Derin Karar Ağaçları ──────────────────────────────────────────

const INITIAL_TREES: Record<string, NodeData[]> = {
  software: [
    {
      id: "node_root",
      label: "Şu An (Yazılımcı)",
      parent: null,
      metrics: { savings: 500, stress: 30, happiness: 70, career: 20 },
      desc: "Türkiye'de yazılım geliştirici olarak çalışıyorsunuz.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_germany",
      label: "Almanya'ya Git",
      parent: "node_root",
      metrics: { savings: 1200, stress: 55, happiness: 75, career: 50 },
      desc: "Avrupa pazarında yazılım kariyeri hedefiyle Almanya'ya geçiş.",
      color: "var(--accent-violet)",
    },
    {
      id: "node_remote",
      label: "Yurt Dışı Remote Çalış",
      parent: "node_root",
      metrics: { savings: 2800, stress: 40, happiness: 80, career: 55 },
      desc: "Türkiye'den ayrılmadan yabancı firmalara uzaktan çalışma.",
      color: "var(--accent-green)",
    },
    {
      id: "node_germany_job",
      label: "Almanya'da İş Bul",
      parent: "node_germany",
      metrics: { savings: 3300, stress: 60, happiness: 75, career: 70 },
      desc: "Mavi Kart (Blue Card) ile Almanya'da doğrudan yazılımcı olarak işe başlamak.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_germany_master",
      label: "Almanya'da Yüksek Lisans Yap",
      parent: "node_germany",
      metrics: { savings: -1000, stress: 50, happiness: 80, career: 60 },
      desc: "Öğrenci vizesiyle gidip Alman üniversitelerinde yüksek lisans (Master) yapmak.",
      color: "var(--accent-pink)",
    },
    {
      id: "node_germany_job_cloud",
      label: "Cloud & DevOps Pozisyonları",
      parent: "node_germany_job",
      metrics: { savings: 4000, stress: 65, happiness: 75, career: 85 },
      desc: "Büyük ölçekli bulut mimarileri (AWS/Azure) ve Kubernetes odaklı roller.",
      color: "var(--accent-amber)",
    },
    {
      id: "node_germany_job_ai",
      label: "Yapay Zeka (AI) Pozisyonları",
      parent: "node_germany_job",
      metrics: { savings: 4500, stress: 70, happiness: 80, career: 90 },
      desc: "Almanya'daki yapay zeka araştırma ve makine öğrenimi takımları.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_germany_master_cs",
      label: "Bilgisayar Bilimleri (CS) Master",
      parent: "node_germany_master",
      metrics: { savings: -800, stress: 55, happiness: 85, career: 75 },
      desc: "Yazılım mühendisliği teorisine ve dağıtık sistemlere odaklanma.",
      color: "var(--accent-violet)",
    },
    {
      id: "node_germany_master_ds",
      label: "Veri Bilimi (Data Science) Master",
      parent: "node_germany_master",
      metrics: { savings: -500, stress: 60, happiness: 80, career: 80 },
      desc: "Büyük veri, istatistik ve veri analitiği üzerine uzmanlaşma.",
      color: "var(--accent-pink)",
    },
  ],
  design: [
    {
      id: "node_root",
      label: "Şu An (Tasarımcı)",
      parent: null,
      metrics: { savings: 400, stress: 25, happiness: 75, career: 15 },
      desc: "Yerel bir ajansta grafik / UI/UX tasarımcısı olarak çalışıyorsunuz.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_global_agency",
      label: "Uluslararası Ajansa Gir",
      parent: "node_root",
      metrics: { savings: 2500, stress: 65, happiness: 70, career: 65 },
      desc: "Küresel markalarla çalışarak büyük portfolyo oluşturma.",
      color: "var(--accent-violet)",
    },
    {
      id: "node_freelance",
      label: "Freelance Tasarımcı Ol",
      parent: "node_root",
      metrics: { savings: 2000, stress: 35, happiness: 85, career: 50 },
      desc: "Kendi müşteri ağını kurarak yer bağımsız tasarım yapmak.",
      color: "var(--accent-green)",
    },
    {
      id: "node_ui_ux",
      label: "UI/UX Tasarımı Alanı",
      parent: "node_global_agency",
      metrics: { savings: 3200, stress: 60, happiness: 75, career: 75 },
      desc: "Ürün geliştirme takımlarında kullanıcı deneyimine odaklanma.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_art_dir",
      label: "Sanat Yönetmenliği (Art Direction)",
      parent: "node_global_agency",
      metrics: { savings: 3500, stress: 70, happiness: 70, career: 80 },
      desc: "Yaratıcı kampanyaları ve görsel dili yöneten lider rolü.",
      color: "var(--accent-pink)",
    },
  ],
  startup: [
    {
      id: "node_root",
      label: "Şu An (Girişimci Adayı)",
      parent: null,
      metrics: { savings: 800, stress: 35, happiness: 65, career: 25 },
      desc: "Yeni bir girişim fikri üzerinde çalışan bağımsız kurucusunuz.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_bootstrap",
      label: "Bootstrapped Hızlı MVP",
      parent: "node_root",
      metrics: { savings: 200, stress: 55, happiness: 75, career: 50 },
      desc: "Hiç yatırım almadan kendi imkanlarınızla MVP üretmek.",
      color: "var(--accent-violet)",
    },
    {
      id: "node_vc_funding",
      label: "Melek Yatırım Bul",
      parent: "node_root",
      metrics: { savings: 3000, stress: 75, happiness: 70, career: 70 },
      desc: "Yatırımcılardan fon alarak hızlı büyüme yolunu seçmek.",
      color: "var(--accent-green)",
    },
    {
      id: "node_b2b_saas",
      label: "B2B SaaS Projesi",
      parent: "node_bootstrap",
      metrics: { savings: 1000, stress: 65, happiness: 75, career: 70 },
      desc: "Şirketlerin iş problemlerini çözen aylık abonelikli yazılım.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_b2c_app",
      label: "B2C Mobil Uygulama",
      parent: "node_bootstrap",
      metrics: { savings: 500, stress: 60, happiness: 80, career: 65 },
      desc: "Doğrudan son tüketiciye hitap eden mobil uygulama projesi.",
      color: "var(--accent-pink)",
    },
  ],
  default: [
    {
      id: "node_root",
      label: "Şu An",
      parent: null,
      metrics: { savings: 450, stress: 30, happiness: 70, career: 20 },
      desc: "Gelecek hedeflerini araştıran bir kaşifsiniz.",
      color: "var(--accent-cyan)",
    },
    {
      id: "node_industry_change",
      label: "Sektör Değiştir (Yazılım)",
      parent: "node_root",
      metrics: { savings: 1200, stress: 55, happiness: 75, career: 60 },
      desc: "Yazılım veya teknoloji alanına yönelme kararı.",
      color: "var(--accent-violet)",
    },
    {
      id: "node_stay_put",
      label: "Mevcut Alanda Uzmanlaş",
      parent: "node_root",
      metrics: { savings: 900, stress: 40, happiness: 70, career: 50 },
      desc: "Mevcut mesleğinizde kalıp dikey uzmanlık kazanmak.",
      color: "var(--accent-green)",
    },
  ],
};

export default function SimulationsPage() {
  const [tree, setTree] = useState<NodeData[]>(INITIAL_TREES.default);
  const [selectedNode, setSelectedNode] = useState<NodeData>(INITIAL_TREES.default[0]);
  const [whatIfText, setWhatIfText] = useState("");
  const [aiSuggestions, setAiSuggestions] = useState<{ optionA: string; optionB: string } | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const data = localStorage.getItem("alterlife_onboarding");
      if (data) {
        try {
          const profile = JSON.parse(data);
          const field = profile.field;
          if (INITIAL_TREES[field]) {
            setTree(INITIAL_TREES[field]);
            setSelectedNode(INITIAL_TREES[field][0]);
          }
        } catch (e) {
          console.error("Onboarding verisi yuklenemedi", e);
        }
      }
    }
  }, []);

  // Seçilen Düğüm Değiştiğinde AI Önerilerini Tetikle
  useEffect(() => {
    generateAiSuggestions(selectedNode);
  }, [selectedNode]);

  // AI Öneri Motoru (Simüle Edilmiş Karar Ajanı)
  const generateAiSuggestions = (node: NodeData) => {
    if (node.id === "node_root") {
      setAiSuggestions({
        optionA: "Şöyle de olabilir: Yarı zamanlı freelance işlerle portfolyoyu büyütmek",
        optionB: "Böyle de olabilir: Mevcut işinde kalıp maaş artışı talep etmek",
      });
    } else if (node.id === "node_germany") {
      setAiSuggestions({
        optionA: "Şöyle de olabilir: Berlin yerine yaşam maliyeti daha düşük olan Köln veya Münih'i seçmek",
        optionB: "Böyle de olabilir: Almanya öncesi 6 ay Polonya veya Estonya'da tecrübe kazanmak",
      });
    } else if (node.id === "node_germany_job") {
      setAiSuggestions({
        optionA: "Şöyle de olabilir: Doğrudan Full-Stack veya Backend rollerini denemek",
        optionB: "Böyle de olabilir: Startup yerine daha stabil olan kurumsal Alman firmalarını hedeflemek",
      });
    } else if (node.id === "node_germany_master") {
      setAiSuggestions({
        optionA: "Şöyle de olabilir: Master yaparken yarı zamanlı çalışıp (Werkstudent) tecrübe kazanmak",
        optionB: "Böyle de olabilir: İngilizce eğitim veren devlet üniversitelerini araştırmak",
      });
    } else {
      setAiSuggestions({
        optionA: `Şöyle de olabilir: Bu adımı (${node.label}) 6 ay erteleyip birikimi %25 artırmak`,
        optionB: "Böyle de olabilir: Sürece alanında uzman bir mentordan destek alarak başlamak",
      });
    }
  };

  // Yeni Dal/Seçenek Ekleme Fonksiyonu (Çocuk düğüm olarak ekler)
  const handleAddNewBranch = (label: string, customDesc?: string) => {
    if (!label.trim()) return;

    const newId = `node_custom_${Date.now()}`;
    const newBranch: NodeData = {
      id: newId,
      label: label.replace("Şöyle de olabilir: ", "").replace("Böyle de olabilir: ", ""),
      parent: selectedNode.id,
      metrics: {
        savings: Math.floor(selectedNode.metrics.savings * 1.1),
        stress: Math.min(100, Math.floor(selectedNode.metrics.stress * 1.05)),
        happiness: Math.min(100, Math.floor(selectedNode.metrics.happiness * 1.1)),
        career: Math.min(100, Math.floor(selectedNode.metrics.career * 1.15)),
      },
      desc: customDesc || `AI ve sizin tarafınızdan ortaklaşa kurgulanan "${label}" dallanma senaryosu.`,
      color: "var(--accent-pink)",
    };

    setTree((prev) => [...prev, newBranch]);
    setSelectedNode(newBranch);
    setWhatIfText("");
  };

  // Aktif Seçili Yolun Breadcrumb Listesini Çıkarma (Şu An -> Almanya -> Master...)
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

  // Seçili düğümün doğrudan alt seçenekleri
  const getNextOptions = () => {
    return tree.filter((n) => n.parent === selectedNode.id);
  };

  // Zihin Haritası İçin İlgili Derinlikteki Düğümleri Getir
  const getNodesAtDepth = (depth: number): NodeData[] => {
    const path = getPathBreadcrumbs();
    if (depth === 0) {
      return tree.filter((n) => n.parent === null);
    }
    const ancestor = path[depth - 1];
    if (!ancestor) return [];
    return tree.filter((n) => n.parent === ancestor.id);
  };

  return (
    <div className="page-container" style={{ maxWidth: "1400px" }}>
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Karar Ağacı & Simülasyon</span>
        </h1>
        <p className="page-subtitle">
          what if? — Hayatınızın tüm dallanmalarını ve alternatif yollarını zihin haritası olarak gözden geçirin
        </p>
      </div>

      {/* ── ZİHİN HARİTASI PANELİ (Mind Map Horizonal Progressive View) ────────────────── */}
      <div
        className="glass-card"
        style={{
          padding: "32px",
          marginBottom: "28px",
          overflowX: "auto",
        }}
      >
        <h2 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "12px", color: "var(--text-primary)" }}>
          Zihin Haritası Görünümü (Mind Map)
        </h2>
        <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "24px" }}>
          Seçenekler soldan sağa doğru dallanarak ilerler. Bir adıma tıklayarak o yolu seçebilir ve sağa doğru yeni dallar üretebilirsiniz.
        </p>

        <div style={{ display: "flex", gap: "40px", alignItems: "flex-start", minWidth: "800px" }}>
          {/* Sütun 1: Başlangıç (Seviye 0) */}
          <div style={mindmapColumnStyle}>
            <div style={columnTitleStyle}>1. Adım (Başlangıç)</div>
            {getNodesAtDepth(0).map((node) => (
              <button
                key={node.id}
                type="button"
                onClick={() => setSelectedNode(node)}
                style={mindmapNodeStyle(selectedNode.id === node.id || getPathBreadcrumbs().some(n => n.id === node.id), selectedNode.id === node.id, node.color)}
              >
                <strong>{node.label}</strong>
              </button>
            ))}
          </div>

          {/* Sütun 2: Seviye 1 Dallanmalar */}
          {getPathBreadcrumbs().length > 0 && getNodesAtDepth(1).length > 0 && (
            <>
              <div style={connectorStyle}>──&gt;</div>
              <div style={mindmapColumnStyle}>
                <div style={columnTitleStyle}>2. Adım Tercihleri</div>
                {getNodesAtDepth(1).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => setSelectedNode(node)}
                    style={mindmapNodeStyle(selectedNode.id === node.id || getPathBreadcrumbs().some(n => n.id === node.id), selectedNode.id === node.id, node.color)}
                  >
                    <strong>{node.label}</strong>
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Sütun 3: Seviye 2 Dallanmalar */}
          {getPathBreadcrumbs().length > 1 && getNodesAtDepth(2).length > 0 && (
            <>
              <div style={connectorStyle}>──&gt;</div>
              <div style={mindmapColumnStyle}>
                <div style={columnTitleStyle}>3. Adım Tercihleri</div>
                {getNodesAtDepth(2).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => setSelectedNode(node)}
                    style={mindmapNodeStyle(selectedNode.id === node.id || getPathBreadcrumbs().some(n => n.id === node.id), selectedNode.id === node.id, node.color)}
                  >
                    <strong>{node.label}</strong>
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Sütun 4: Seviye 3 Dallanmalar */}
          {getPathBreadcrumbs().length > 2 && getNodesAtDepth(3).length > 0 && (
            <>
              <div style={connectorStyle}>──&gt;</div>
              <div style={mindmapColumnStyle}>
                <div style={columnTitleStyle}>4. Adım Tercihleri</div>
                {getNodesAtDepth(3).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => setSelectedNode(node)}
                    style={mindmapNodeStyle(selectedNode.id === node.id || getPathBreadcrumbs().some(n => n.id === node.id), selectedNode.id === node.id, node.color)}
                  >
                    <strong>{node.label}</strong>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "24px" }}>

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
                    onClick={() => handleAddNewBranch(aiSuggestions.optionA)}
                    style={suggestionButtonStyle}
                  >
                    {aiSuggestions.optionA}
                  </button>
                  <button
                    type="button"
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
                  style={{ whiteSpace: "nowrap", padding: "10px 18px", fontSize: "0.85rem" }}
                  onClick={() => handleAddNewBranch(whatIfText, `Kullanıcı tarafından eklenen '${whatIfText}' alt dalı.`)}
                >
                  Seçenek Ekle
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* Sağ Sütun: Düğüm Detayları */}
        <div className="glass-card" style={{ padding: "24px", height: "fit-content" }}>
          <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, marginBottom: "6px", fontSize: "1rem" }}>
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

          {selectedNode.parent && (
            <button
              type="button"
              className="btn-ghost"
              style={{ width: "100%", justifyContent: "center", marginTop: "18px" }}
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

const mindmapColumnStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  minWidth: "220px",
};

const columnTitleStyle: React.CSSProperties = {
  fontSize: "0.75rem",
  color: "var(--text-muted)",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  marginBottom: "4px",
  fontWeight: 600,
};

const connectorStyle: React.CSSProperties = {
  alignSelf: "center",
  color: "var(--text-muted)",
  fontSize: "1.2rem",
  fontWeight: "bold",
  opacity: 0.5,
  paddingTop: "24px",
};

function mindmapNodeStyle(isActivePath: boolean, isSelected: boolean, color: string): React.CSSProperties {
  return {
    padding: "12px 16px",
    background: isSelected ? "rgba(0, 229, 255, 0.08)" : "var(--glass-bg)",
    border: `1px solid ${isSelected ? "var(--accent-cyan)" : isActivePath ? color : "var(--glass-border)"}`,
    borderRadius: "var(--radius-md)",
    color: isSelected ? "var(--accent-cyan)" : isActivePath ? "var(--text-primary)" : "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "0.85rem",
    textAlign: "left",
    fontFamily: "'Inter', sans-serif",
    transition: "all 0.2s ease",
    boxShadow: isSelected ? "var(--shadow-glow-cyan)" : "none",
    opacity: isActivePath ? 1 : 0.4,
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
