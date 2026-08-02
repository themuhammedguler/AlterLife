"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import { branchSimulation, generateSimulation, getBranchActionPlan, getSimulationTree, runStressTest, saveSimulationViewState, setActiveGoal } from "@/lib/api";
import styles from "./page.module.css";

interface NodeData {
  id: string;
  label: string;
  parent: string | null;
  metrics: { savings: number; stress: number; happiness: number; career: number };
  desc: string;
  color: string;
  isSuggestion?: boolean;
  suggestionText?: string;
}

type ActionPlan = {
  selected_goal: string;
  summary: string;
  realism_score: number;
  fun_angle: string;
  steps: { title: string; description: string; duration: string; proof: string }[];
  resources: { title: string; platform: string; url: string; reason: string }[];
  done_so_far: string[];
  shared_path: {
    code: string;
    common_until: string;
    together: string[];
    divergence_options: string[];
  };
  research_note: string;
};

const DEFAULT_NODE: NodeData = {
  id: "node_root",
  label: "Başlangıç Durumu",
  parent: null,
  metrics: { savings: 500, stress: 30, happiness: 70, career: 20 },
  desc: "Yükleniyor...",
  color: "var(--accent-cyan)"
};

function getCompleteDecisionLabel(node: { decision_name: string; description?: string | null }) {
  const storedLabel = node.decision_name || "Yeni Karar";
  if (!storedLabel.startsWith("Karar:")) return storedLabel;

  // Older roadmap entries were persisted with a 30-character title. Their
  // description still contains the complete user decision, so recover it.
  const recovered = node.description?.match(/Verdiğiniz ['‘]([\s\S]+?)['’] kararı/)?.[1];
  return recovered ? `Karar: ${recovered}` : storedLabel;
}

function getNodeDepth(node: NodeData, tree: NodeData[]) {
  let depth = 0;
  let current: NodeData | undefined = node;
  const visited = new Set<string>();

  while (current?.parent && !visited.has(current.id)) {
    visited.add(current.id);
    depth += 1;
    current = tree.find((candidate) => candidate.id === current?.parent);
  }

  return depth;
}

function getTopLevelBranchId(node: NodeData, tree: NodeData[]) {
  let current: NodeData | undefined = node;
  const visited = new Set<string>();

  while (current?.parent && !visited.has(current.id)) {
    visited.add(current.id);
    const parent = tree.find((candidate) => candidate.id === current?.parent);
    if (!parent || parent.parent === null) return current.id;
    current = parent;
  }

  return null;
}

function isDescendantOf(node: NodeData, ancestorId: string, tree: NodeData[]) {
  let current: NodeData | undefined = node;
  const visited = new Set<string>();

  while (current && !visited.has(current.id)) {
    if (current.id === ancestorId) return true;
    visited.add(current.id);
    current = current.parent ? tree.find((candidate) => candidate.id === current?.parent) : undefined;
  }

  return false;
}

function normalizeDecisionText(value: string) {
  return (value || "")
    .toLocaleLowerCase("tr-TR")
    .replace(/^öneri:\s*/i, "")
    .replace(/^karar:\s*/i, "")
    .replace(/[“”"'.,!?()\[\]{}:;]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function shortenContext(value: string, maxWords = 8) {
  const words = normalizeDecisionText(value).split(" ").filter(Boolean);
  return words.slice(0, maxWords).join(" ");
}

const SYNTHETIC_SIGNATURES = [
  "bu kararın sonucunu ölçmek için net bir başarı kriteri belirlemek",
  "en büyük riski azaltacak tek somut görevi takvime eklemek",
  "mevcut sonuçlara göre alternatif bir sonraki kilometre taşı seçmek",
  "için 7 günlük küçük bir test planı oluşturmak",
  "yolundaki en büyük riski tek hamlede azaltmak",
  "sonrasında atılacak bir sonraki somut adımı netleştirmek",
];

function isSyntheticDecisionLabel(value: string) {
  const normalized = normalizeDecisionText(value);
  if (!normalized) return true;
  if (normalized.length < 16) return true;
  if (normalized.startsWith("bu seçeneği") || normalized.startsWith("öneri")) return true;
  return SYNTHETIC_SIGNATURES.some((signature) => normalized.includes(signature));
}

function getStableSuggestionContext(node: NodeData, tree: NodeData[]) {
  let current: NodeData | undefined = node;
  const visited = new Set<string>();

  while (current && !visited.has(current.id)) {
    visited.add(current.id);
    if (!isSyntheticDecisionLabel(current.label)) {
      return shortenContext(current.label) || "bu adım";
    }
    current = current.parent ? tree.find((candidate) => candidate.id === current?.parent) : undefined;
  }

  if (node.metrics.stress >= 60) return "stresi yönetmek";
  if (node.metrics.savings <= 400) return "nakit akışını güçlendirmek";
  if (node.metrics.career <= 35) return "kariyer ivmesini artırmak";
  if (node.metrics.happiness <= 55) return "dengeyi toparlamak";
  return "hedefe ilerlemek";
}

function getPhaseCandidates(context: string, depth: number, metrics: NodeData["metrics"]) {
  if (depth <= 1) {
    return [
      `${context} için düşük riskli 14 günlük bir deneme başlatmak`,
      `${context} için maliyet ve zaman hesabını netleştirmek`,
      `${context} için dışarıdan bir uzman görüşü almak`,
    ];
  }

  if (metrics.stress >= 60) {
    return [
      "Stresi düşürmek için haftalık yükü sadeleştiren bir plan yapmak",
      "Baskıyı artıran tek darboğazı tespit edip kaldırmak",
      "Kararı sürdürülebilir kılmak için ritmi yeniden ayarlamak",
    ];
  }

  if (metrics.savings <= 400) {
    return [
      "Nakit akışını rahatlatacak kısa vadeli bir gelir adımı eklemek",
      "Bu dalın masrafını azaltacak mini bütçe revizyonu yapmak",
      "Finansal riski sınırlayan bir B planı hazırlamak",
    ];
  }

  if (depth <= 3) {
    return [
      `${context} için ölçülebilir bir başarı metriği tanımlamak`,
      `${context} için en kritik riski azaltan tek aksiyonu planlamak`,
      `${context} için bir sonraki somut kilometre taşını seçmek`,
    ];
  }

  if (depth <= 5) {
    return [
      `${context} tarafında görünür bir çıktı üretmek`,
      `${context} tarafında hızlanmak için bir darboğazı kaldırmak`,
      `${context} tarafında bir haftalık ilerleme raporu çıkarmak`,
    ];
  }

  return [
    `${context} yolunu sadeleştirip tekrarlayan adımları temizlemek`,
    `${context} için uzun vadeli sürdürülebilirlik kontrolü yapmak`,
    `${context} için alternatif bir rota ile kıyaslama denemesi yapmak`,
  ];
}

function buildNextSuggestions(node: NodeData, tree: NodeData[]) {
  const depth = getNodeDepth(node, tree);
  const decision = normalizeDecisionText(node.label);
  const context = getStableSuggestionContext(node, tree);
  const existingChildren = tree
    .filter((candidate) => candidate.parent === node.id)
    .map((candidate) => normalizeDecisionText(candidate.label));

  let candidates: string[];

  if (node.id === "node_root") {
    candidates = [
      "Yarı zamanlı freelance işlerle portfolyoyu büyütmek",
      "Mevcut işte kalıp hedef role yönelik sertifikaları tamamlamak",
      "Hedefe doğrudan geçiş için üç aylık yoğun bir plan uygulamak",
    ];
  } else if (decision.includes("iş başvuru") || decision.includes("vize")) {
    candidates = [
      "Almanca CV ve LinkedIn profilini hedef role göre tamamlamak",
      "EU Blue Card uygunluğunu maaş eşiği ve diploma denkliğiyle kontrol etmek",
      "Vize sponsorluğu sunan şirketleri ayrı bir başvuru listesinde toplamak",
    ];
  } else if (decision.includes("cv") || decision.includes("linkedin")) {
    candidates = [
      "On hedef şirket belirleyip her biri için kişiselleştirilmiş başvuru hazırlamak",
      "İki Almanya recruiter’ı ile tanışma görüşmesi planlamak",
      "CV’deki en güçlü üç projeyi İngilizce vaka çalışmasına dönüştürmek",
    ];
  } else if (decision.includes("blue card") || decision.includes("diploma") || decision.includes("denklik")) {
    candidates = [
      "Anabin üzerinden diploma denkliğini doğrulayıp gerekli belgeleri toplamak",
      "Blue Card maaş eşiğini karşılayan ilanları filtrelemek",
      "Eksik resmi belgeler için tercüme ve apostil takvimi oluşturmak",
    ];
  } else if (decision.includes("hedef şirket") || decision.includes("kişiselleştirilmiş başvuru") || decision.includes("sponsor")) {
    candidates = [
      "İlk beş başvuruyu gönderip iki hafta boyunca dönüş oranını ölçmek",
      "Hedef rol için teknik mülakat ve sistem tasarımı provası yapmak",
      "Başvuru yanıtı gelmezse CV ve rol hedefini yeniden kalibre etmek",
    ];
  } else if (decision.includes("recruiter") || decision.includes("tanışma görüşmesi") || decision.includes("network")) {
    candidates = [
      "Recruiter geri bildirimine göre CV ve maaş beklentisini güncellemek",
      "Berlin teknoloji topluluğundan iki çevrim içi etkinliğe katılmak",
      "Bir referans görüşmesi için Almanya’da çalışan bir uzmanla bağlantı kurmak",
    ];
  } else if (decision.includes("mülakat") || decision.includes("sistem tasarımı")) {
    candidates = [
      "İki deneme mülakatı yapıp eksik konu listesini çıkarmak",
      "Hedef şirket formatına uygun bir teknik proje sunumu hazırlamak",
      "Mülakat haftası için çalışma, dinlenme ve takip planı oluşturmak",
    ];
  } else if (decision.includes("anabin") || decision.includes("apostil") || decision.includes("resmi belge")) {
    candidates = [
      "Tamamlanan belgeleri tek bir dijital başvuru dosyasında toplamak",
      "Konsolosluk ve iş sözleşmesi için gereken eksik evrakları doğrulamak",
      "Belge süreci uzarsa kullanılacak alternatif vize rotasını araştırmak",
    ];
  } else if (decision.includes("maaş eşiği") || decision.includes("ilanları filtre")) {
    candidates = [
      "Maaş aralığı uygun on ilanı beceri gereksinimlerine göre sıralamak",
      "Eksik görülen en sık iki beceri için kısa bir geliştirme sprinti başlatmak",
      "Teklif pazarlığında kullanılacak piyasa maaşı verilerini toplamak",
    ];
  } else if (decision.includes("şehir") || decision.includes("berlin") || decision.includes("köln") || decision.includes("münih")) {
    candidates = [
      "Berlin, Hamburg ve Köln’ü kira ile iş ilanı sayısına göre karşılaştırmak",
      "En uygun iki şehir için aylık yaşam bütçesi çıkarmak",
      "Seçilen şehirlerdeki teknoloji toplulukları ve şirket kümelerini araştırmak",
    ];
  } else if (decision.includes("bütçe") || decision.includes("kira") || decision.includes("birikim")) {
    candidates = [
      "Altı aylık acil durum fonu için aylık tasarruf hedefi belirlemek",
      "Taşınma, depozito ve ilk ay giderlerini kalem kalem hesaplamak",
      "Bütçe açığını kapatmak için geçici uzaktan gelir planı oluşturmak",
    ];
  } else if (decision.includes("dil") || decision.includes("almanca")) {
    candidates = [
      "B1 sınavı için on iki haftalık çalışma ve deneme takvimi hazırlamak",
      "İngilizce çalışma imkânı sunan rolleri ayrı bir listede araştırmak",
      "Haftalık konuşma pratiği için bir dil partneri bulmak",
    ];
  } else if (decision.includes("uzaktan") || decision.includes("freelance")) {
    candidates = [
      "Uluslararası müşteriye uygun iki portfolyo projesini yayına almak",
      "Altı aylık uzaktan çalışma hedefi için müşteri ve gelir planı hazırlamak",
      "Uzaktan deneyimi Almanya iş başvurularına bağlayacak referanslar toplamak",
    ];
  } else if (decision.includes("master") || decision.includes("yüksek lisans") || decision.includes("üniversite")) {
    candidates = [
      "Programları ücret, burs ve mezuniyet sonrası iş imkânına göre karşılaştırmak",
      "Yüksek lisans sırasında Werkstudent olarak çalışma seçeneklerini araştırmak",
      "Dil belgesi, referans ve başvuru tarihlerini içeren takvim hazırlamak",
    ];
  } else if (node.id.includes("path_1") || decision.includes("almanya") || decision.includes("göç")) {
    candidates = [
      "Hedef şehirleri yaşam maliyeti ve iş fırsatlarına göre karşılaştırmak",
      "Dil seviyesi ile vize uygunluğunu resmi kaynaklardan doğrulamak",
      "Taşınmadan önce altı ay uluslararası uzaktan deneyim kazanmak",
    ];
  } else {
    candidates = getPhaseCandidates(context, depth, node.metrics);
  }

  const uniqueCandidates = Array.from(new Set(candidates.map((candidate) => candidate.trim())));
  const available = uniqueCandidates.filter(
    (candidate) => !existingChildren.includes(normalizeDecisionText(candidate))
  );
  const source = available.length >= 2 ? available : uniqueCandidates;
  const suggestions = source.length >= 2 ? source : [
    "Bu adım için küçük bir deneme planı başlatmak",
    "Bu adım için riski azaltan tek hamleyi belirlemek",
  ];

  return { optionA: suggestions[0], optionB: suggestions[1] };
}

export default function SimulationsPage() {
  const [tree, setTree] = useState<NodeData[]>([DEFAULT_NODE]);
  const [selectedNode, setSelectedNode] = useState<NodeData>(DEFAULT_NODE);
  const [whatIfText, setWhatIfText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlan | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [friendCode, setFriendCode] = useState("");
  const [activeGoalMessage, setActiveGoalMessage] = useState<string | null>(null);
  const [suggestionHistory, setSuggestionHistory] = useState<Record<string, string[]>>({});
  const [mapMode, setMapMode] = useState<"focus" | "all">("focus");
  const [branchCheckpoints, setBranchCheckpoints] = useState<Record<string, string>>(() => {
    if (typeof window === "undefined") return {};
    try {
      return JSON.parse(window.localStorage.getItem("alterlife_simulation_checkpoints") || "{}");
    } catch {
      return {};
    }
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const mapViewportRef = useRef<HTMLDivElement>(null);
  const viewStateLoadedRef = useRef(false);
  const branchRequestRef = useRef(false);

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
            label: getCompleteDecisionLabel(n),
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
        setBranchCheckpoints(data.branch_checkpoints || {});
        setSuggestionHistory(data.suggestion_history || {});
        setMapMode(data.map_mode === "all" ? "all" : "focus");
        
        // Backend state is authoritative; localStorage remains only as a
        // backwards-compatible fallback for older sessions.
        const lastNodeId = data.last_selected_node_id || (typeof window !== "undefined"
          ? window.localStorage.getItem("alterlife_simulation_last_node")
          : null);
        const lastNode = mapped.find((node) => node.id === lastNodeId);
        const retainedNode = mapped.find((node) => node.id === selectedNode.id);
        setSelectedNode(lastNode || retainedNode || mapped[0]);
        viewStateLoadedRef.current = true;
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

  const aiSuggestions = useMemo(
    () => buildNextSuggestions(selectedNode, tree),
    [selectedNode, tree]
  );

  useEffect(() => {
    setSuggestionHistory((previous) => {
      if (previous[selectedNode.id]) return previous;
      return {
        ...previous,
        [selectedNode.id]: [aiSuggestions.optionA, aiSuggestions.optionB],
      };
    });
  }, [aiSuggestions, selectedNode.id]);

  useEffect(() => {
    setActionPlan(null);
  }, [selectedNode.id]);

  useEffect(() => {
    const topLevelBranchId = getTopLevelBranchId(selectedNode, tree);
    if (!topLevelBranchId || selectedNode.isSuggestion) return;

    window.localStorage.setItem("alterlife_simulation_last_node", selectedNode.id);
    setBranchCheckpoints((previous) => {
      if (previous[topLevelBranchId] === selectedNode.id) return previous;
      const next = { ...previous, [topLevelBranchId]: selectedNode.id };
      window.localStorage.setItem("alterlife_simulation_checkpoints", JSON.stringify(next));
      return next;
    });
  }, [selectedNode, tree]);

  useEffect(() => {
    if (!viewStateLoadedRef.current || selectedNode.isSuggestion) return;
    const timer = window.setTimeout(() => {
      saveSimulationViewState({
        last_selected_node_id: selectedNode.id,
        branch_checkpoints: branchCheckpoints,
        suggestion_history: suggestionHistory,
        map_mode: mapMode,
      }).catch((err) => {
        setError(err.message || "Yol haritasının görünümü kaydedilemedi.");
      });
    }, 250);
    return () => window.clearTimeout(timer);
  }, [branchCheckpoints, mapMode, selectedNode.id, selectedNode.isSuggestion, suggestionHistory]);

  // Handle Add Branch (What If)
  const handleAddNewBranch = async (text: string, parentNodeId = selectedNode.id) => {
    const cleanText = text.replace(/^Öneri:\s*/i, "").trim();
    if (!cleanText || branchRequestRef.current) return;

    const normalizedInput = normalizeDecisionText(cleanText);
    const hasDuplicateChild = tree
      .filter((node) => node.parent === parentNodeId)
      .some((node) => normalizeDecisionText(node.label) === normalizedInput);
    if (hasDuplicateChild) {
      setError("Bu adım zaten mevcut. Farklı bir seçenek deneyin.");
      return;
    }

    branchRequestRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const newNode = await branchSimulation(parentNodeId, cleanText);
      const mappedNode: NodeData = {
        id: newNode.node_id,
        label: getCompleteDecisionLabel(newNode),
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
      setSuggestionHistory((previous) => ({
        ...previous,
        [parentNodeId]: (previous[parentNodeId] || []).filter(
          (suggestion) => normalizeDecisionText(suggestion) !== normalizeDecisionText(cleanText)
        ),
      }));
      setSelectedNode(mappedNode);
      setWhatIfText("");
    } catch (err: any) {
      setError(err.message || "Yeni dal oluşturulamadı.");
    } finally {
      branchRequestRef.current = false;
      setLoading(false);
    }
  };

  const visualTree = useMemo(() => {
    const activePath: NodeData[] = [];
    let current: NodeData | undefined = selectedNode;
    const visited = new Set<string>();

    while (current && !visited.has(current.id)) {
      activePath.unshift(current);
      visited.add(current.id);
      current = current.parent ? tree.find((node) => node.id === current?.parent) : undefined;
    }

    const activePathIds = new Set(activePath.map((node) => node.id));
    const visibleNodeIds = new Set(activePathIds);

    // Keep focus mode compact: show the chosen continuation plus at most one
    // sibling at previous steps. At the current step show at most two existing
    // children; fresh AI options are rendered separately as preview nodes.
    activePath.forEach((pathNode, pathIndex) => {
      const children = tree.filter((node) => node.parent === pathNode.id);
      const activeChild = activePath[pathIndex + 1];

      if (activeChild) {
        visibleNodeIds.add(activeChild.id);
        const sibling = children.find((node) => node.id !== activeChild.id);
        if (sibling) visibleNodeIds.add(sibling.id);
        return;
      }

      children.slice(-2).forEach((node) => visibleNodeIds.add(node.id));
    });

    tree
      .filter((node) => node.parent === null)
      .forEach((node) => visibleNodeIds.add(node.id));

    const visibleTree = mapMode === "all"
      ? tree
      : tree.filter((node) => visibleNodeIds.has(node.id));
    const previewNodes: NodeData[] = [];

    Object.entries(suggestionHistory).forEach(([parentId, suggestions]) => {
      if (mapMode === "focus" && !activePathIds.has(parentId)) return;
      const parent = tree.find((node) => node.id === parentId);
      if (!parent) return;

      suggestions.forEach((suggestion, index) => {
        previewNodes.push({
          id: `suggestion_${parentId}_${index}_${suggestion.slice(0, 12)}`,
          label: `Öneri: ${suggestion}`,
          parent: parentId,
          metrics: parent.metrics,
          desc: "Henüz seçilmemiş alternatif sonraki adım.",
          color: "var(--accent-amber)",
          isSuggestion: true,
          suggestionText: suggestion,
        });
      });
    });

    return [...visibleTree, ...previewNodes];
  }, [mapMode, selectedNode, suggestionHistory, tree]);

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

  const handleCreateActionPlan = async () => {
    setPlanLoading(true);
    setError(null);
    try {
      const data = await getBranchActionPlan(selectedNode.id, friendCode.trim() || undefined);
      setActionPlan(data);
    } catch (err: any) {
      setError(err.message || "Hedef planı oluşturulamadı.");
    } finally {
      setPlanLoading(false);
    }
  };

  const handleSetActiveGoal = async () => {
    try {
      await setActiveGoal({ simulation_id: `sim_${localStorage.getItem("alterlife_user_id") || "dev_user_001"}`, node_id: selectedNode.id });
      setActiveGoalMessage("Bu dal ana hedef olarak seçildi.");
      setTimeout(() => setActiveGoalMessage(null), 2500);
    } catch (err: any) {
      setError(err.message || "Aktif hedef seçilemedi.");
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

  // Coordinates Layout Calculation
  const layoutData = useMemo(() => {
    // Group every node in the full tree by its real depth. The previous layout
    // followed only the selected breadcrumb, hiding descendants of sibling
    // branches even though they were stored correctly.
    const nodeById = new Map(visualTree.map((node) => [node.id, node]));
    const depthCache = new Map<string, number>();

    const resolveDepth = (node: NodeData, visiting = new Set<string>()): number => {
      const cached = depthCache.get(node.id);
      if (cached !== undefined) return cached;
      if (!node.parent || !nodeById.has(node.parent)) {
        depthCache.set(node.id, 0);
        return 0;
      }
      if (visiting.has(node.id)) {
        depthCache.set(node.id, 0);
        return 0;
      }

      const nextVisiting = new Set(visiting);
      nextVisiting.add(node.id);
      const parent = nodeById.get(node.parent);
      const depth = parent ? resolveDepth(parent, nextVisiting) + 1 : 0;
      depthCache.set(node.id, depth);
      return depth;
    };

    const columnsByDepth = new Map<number, NodeData[]>();
    visualTree.forEach((node) => {
      const depth = resolveDepth(node);
      const column = columnsByDepth.get(depth) || [];
      column.push(node);
      columnsByDepth.set(depth, column);
    });

    const maxDepth = Math.max(0, ...columnsByDepth.keys());
    const columns: NodeData[][] = Array.from(
      { length: maxDepth + 1 },
      (_, depth) => columnsByDepth.get(depth) || []
    );

    const nodeCoords: { [id: string]: { x: number; y: number } } = {};
    const colWidth = 260;
    const colGap = 80;
    const rowHeight = 96;
    
    columns.forEach((nodes, colIdx) => {
      const colX = colIdx * (colWidth + colGap) + 20;
      nodes.forEach((node, nodeIdx) => {
        // Space nodes vertically
        const nodeY = nodeIdx * rowHeight + 24;
        nodeCoords[node.id] = { x: colX, y: nodeY };
      });
    });

    // Find connections
    const connections: {
      id: string;
      targetId: string;
      from: { x: number; y: number };
      to: { x: number; y: number };
      color: string;
      isSuggestion: boolean;
    }[] = [];
    visualTree.forEach((node) => {
      if (node.parent && nodeCoords[node.parent] && nodeCoords[node.id]) {
        connections.push({
          id: `${node.parent}-${node.id}`,
          targetId: node.id,
          from: nodeCoords[node.parent],
          to: nodeCoords[node.id],
          color: node.color,
          isSuggestion: Boolean(node.isSuggestion),
        });
      }
    });

    // Find total height and width
    let totalHeight = 350;
    columns.forEach(nodes => {
      const h = nodes.length * rowHeight + 48;
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
  }, [visualTree]);

  const activePath = useMemo(() => {
    const path: NodeData[] = [];
    let current: NodeData | undefined = selectedNode;
    const visited = new Set<string>();
    while (current && !visited.has(current.id)) {
      path.unshift(current);
      visited.add(current.id);
      current = current.parent ? tree.find((node) => node.id === current?.parent) : undefined;
    }
    return path;
  }, [selectedNode, tree]);

  const savedRoutes = useMemo(() => {
    const rootIds = new Set(tree.filter((node) => node.parent === null).map((node) => node.id));

    return tree
      .filter((node) => node.parent && rootIds.has(node.parent))
      .map((branch) => {
        const checkpointId = branchCheckpoints[branch.id];
        const checkpoint = tree.find(
          (node) => node.id === checkpointId && isDescendantOf(node, branch.id, tree)
        ) || branch;

        return {
          branch,
          checkpoint,
          depth: Math.max(1, getNodeDepth(checkpoint, tree)),
          isActive: getTopLevelBranchId(selectedNode, tree) === branch.id,
        };
      });
  }, [branchCheckpoints, selectedNode, tree]);

  const resumeRoute = (branchId: string) => {
    const checkpointId = branchCheckpoints[branchId];
    const checkpoint = tree.find(
      (node) => node.id === checkpointId && isDescendantOf(node, branchId, tree)
    );
    const branch = tree.find((node) => node.id === branchId);
    if (checkpoint || branch) {
      setMapMode("focus");
      setSelectedNode(checkpoint || branch!);
    }
  };

  const focusSelectedNode = () => {
    const viewport = mapViewportRef.current;
    const coords = layoutData.nodeCoords[selectedNode.id];
    if (!viewport || !coords) return;
    viewport.scrollTo({
      left: Math.max(0, coords.x - viewport.clientWidth / 2 + 120),
      top: Math.max(0, coords.y - viewport.clientHeight / 2 + 22),
      behavior: "smooth",
    });
  };

  useEffect(() => {
    const frame = window.setTimeout(focusSelectedNode, 80);
    return () => window.clearTimeout(frame);
  }, [selectedNode.id, mapMode, layoutData.width, layoutData.height]);

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
      <section className={`glass-card ${styles.mapPanel}`}>
        <div className={styles.mapHeader}>
          <div>
            <div className={styles.mapKicker}><span /> KARAR YOLCULUĞU</div>
            <h2>Gelecek Zihin Haritası</h2>
            <p>Bir seçeneğe tıklayın; o yolun bir sonraki hedefleri sağ tarafta açılsın.</p>
          </div>
          <div className={styles.mapControls}>
            <div className={styles.modeSwitch} aria-label="Harita görünümü">
              <button type="button" data-active={mapMode === "focus"} onClick={() => setMapMode("focus")}>Aktif yol</button>
              <button type="button" data-active={mapMode === "all"} onClick={() => setMapMode("all")}>Tüm ağaç</button>
            </div>
            <button type="button" className={styles.focusButton} onClick={focusSelectedNode}>◎ Seçili adıma git</button>
          </div>
        </div>

        <div className={styles.pathBar}>
          <span className={styles.pathLabel}>AKTİF YOL</span>
          <div className={styles.breadcrumbs}>
            {activePath.map((node, index) => (
              <div key={node.id} className={styles.breadcrumbItem}>
                {index > 0 && <span className={styles.breadcrumbArrow}>→</span>}
                <button type="button" data-current={node.id === selectedNode.id} onClick={() => setSelectedNode(node)}>
                  {index === 0 ? "Başlangıç" : node.label.replace(/^Karar:\s*/i, "")}
                </button>
              </div>
            ))}
          </div>
          <span className={styles.stepCount}>{Math.max(0, activePath.length - 1)} karar</span>
        </div>

        {savedRoutes.length > 0 && (
          <div className={styles.savedRoutes}>
            <div className={styles.savedRoutesTitle}>
              <span>KAYITLI ROTALARIM</span>
              <p>Bir yolu dene, diğerine geç; ilerlemen kaybolmaz.</p>
            </div>
            <div className={styles.routeList}>
              {savedRoutes.map(({ branch, checkpoint, depth, isActive }) => (
                <button
                  type="button"
                  key={branch.id}
                  data-active={isActive}
                  onClick={() => resumeRoute(branch.id)}
                  title={`${checkpoint.label} adımından devam et`}
                >
                  <span className={styles.routeDot} />
                  <span className={styles.routeCopy}>
                    <strong>{branch.label.replace(/^Karar:\s*/i, "")}</strong>
                    <small>{depth} karar · {checkpoint.id === branch.id ? "Başlangıçta" : "Kaldığın adımdan devam"}</small>
                  </span>
                  <span className={styles.resumeLabel}>{isActive ? "Aktif" : "Devam et →"}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className={styles.mapMetaRow}>
          <div className={styles.legend}>
            <span><i className={styles.legendSelected} /> Seçili adım</span>
            <span><i className={styles.legendPath} /> Alınmış karar</span>
            <span><i className={styles.legendSuggestion} /> Yeni seçenek</span>
            <span><i className={styles.legendCrisis} /> Stres testi</span>
          </div>
          <p>{mapMode === "focus" ? "Yalnızca aktif yol ve doğrudan alternatifler gösteriliyor." : "Kaydedilmiş bütün dallar gösteriliyor."}</p>
        </div>

        <div ref={mapViewportRef} className={styles.mapViewport}>
          <div
            ref={containerRef}
            className={styles.mapCanvas}
            style={{ width: `${layoutData.width}px`, height: `${layoutData.height}px` }}
          >
          {/* SVG Connector Lines Layer */}
          <svg className={styles.connectorLayer}>
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
              
              const isSelectedPath = activePath.some(n => n.id === conn.targetId);

              return (
                <path
                  key={conn.id}
                  d={d}
                  fill="none"
                  stroke={isSelectedPath ? conn.color : conn.isSuggestion ? "rgba(245, 158, 11, 0.32)" : "rgba(255, 255, 255, 0.1)"}
                  strokeWidth={isSelectedPath ? 3.5 : 1.5}
                  strokeDasharray={conn.isSuggestion || conn.color.includes("pink") ? "5 6" : "none"}
                  style={{
                    filter: isSelectedPath ? `drop-shadow(0 0 4px ${conn.color})` : "none",
                    transition: "all 0.3s ease"
                  }}
                />
              );
            })}
          </svg>

          {/* HTML Nodes Layer */}
          <div className={styles.nodesLayer}>
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
                      onClick={() => {
                        if (node.isSuggestion && node.suggestionText && node.parent) {
                          void handleAddNewBranch(node.suggestionText, node.parent);
                          return;
                        }
                        setSelectedNode(node);
                      }}
                      title={node.isSuggestion ? "Bu öneriyi gerçek bir dala dönüştür" : node.label}
                      className={`${styles.mapNode} ${
                        node.isSuggestion ? styles.suggestionNode :
                        node.id.includes("crisis") ? styles.crisisNode :
                        isSelected ? styles.selectedNode :
                        isActivePath ? styles.pathNode : styles.alternativeNode
                      }`}
                      style={{
                        position: "absolute",
                        left: `${coords.x}px`,
                        top: `${coords.y}px`,
                        width: "240px",
                        "--node-color": node.color,
                      } as React.CSSProperties}
                    >
                      <span className={styles.nodeStatus}>
                        {node.isSuggestion ? "YENİ SEÇENEK" : node.id.includes("crisis") ? "STRES TESTİ" : isSelected ? "ŞU AN BURADASIN" : isActivePath ? "KARAR VERİLDİ" : "ALTERNATİF"}
                      </span>
                      <strong>{node.label.replace(/^Karar:\s*/i, "")}</strong>
                      {node.isSuggestion && <span className={styles.nodeAction}>Seç ve bu yolu aç →</span>}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
          </div>
        </div>
      </section>

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
          {activeGoalMessage && (
            <p style={{ color: "var(--accent-green)", fontSize: "0.78rem", marginBottom: "12px" }}>{activeGoalMessage}</p>
          )}
          <button type="button" className="btn-ghost" style={{ width: "100%", justifyContent: "center", marginBottom: "14px" }} onClick={handleSetActiveGoal}>
            Ana Hedef Yap
          </button>

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

          <div
            style={{
              marginTop: "20px",
              padding: "16px",
              background: "rgba(0, 229, 255, 0.035)",
              border: "1px solid rgba(0, 229, 255, 0.16)",
              borderRadius: "var(--radius-md)",
            }}
          >
            <h4 style={{ fontSize: "0.88rem", color: "var(--accent-cyan)", marginBottom: "8px" }}>
              Bu Dalı Hedefe Çevir
            </h4>
            <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: "12px" }}>
              Nasıl yapılacağını, hangi kaynakları kullanacağını, şu ana kadar ne yaptığını ve arkadaşınla nerede ortak kalıp nerede ayrışacağını çıkarır.
            </p>
            <input
              type="text"
              value={friendCode}
              onChange={(e) => setFriendCode(e.target.value.toUpperCase())}
              placeholder="Arkadaş kodu varsa yaz"
              style={{
                width: "100%",
                padding: "10px 12px",
                marginBottom: "10px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid var(--glass-border)",
                borderRadius: "var(--radius-md)",
                color: "var(--text-primary)",
                fontSize: "0.82rem",
                outline: "none",
              }}
            />
            <button
              type="button"
              className="btn-primary"
              disabled={planLoading}
              style={{ width: "100%", justifyContent: "center", fontSize: "0.85rem" }}
              onClick={handleCreateActionPlan}
            >
              {planLoading ? "Plan hazırlanıyor..." : "Hedef Planını Göster"}
            </button>
          </div>

          {actionPlan && (
            <div style={{ marginTop: "18px", display: "flex", flexDirection: "column", gap: "14px" }}>
              <div
                style={{
                  padding: "16px",
                  background: "rgba(124, 58, 237, 0.05)",
                  border: "1px solid rgba(124, 58, 237, 0.18)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center", marginBottom: "8px" }}>
                  <h4 style={{ fontSize: "0.9rem", fontWeight: 700 }}>Seçilen Hedef</h4>
                  <span className="badge badge-violet">{actionPlan.realism_score}% gerçekçi</span>
                </div>
                <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.55, marginBottom: "8px" }}>
                  {actionPlan.summary}
                </p>
                <p style={{ fontSize: "0.78rem", color: "var(--accent-green)", lineHeight: 1.45 }}>
                  {actionPlan.fun_angle}
                </p>
              </div>

              <section>
                <h4 style={sectionTitleStyle}>Nasıl Yapacağız?</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {actionPlan.steps.map((step, idx) => (
                    <div key={step.title} style={miniCardStyle}>
                      <div style={{ color: "var(--accent-cyan)", fontSize: "0.72rem", fontWeight: 700, marginBottom: "5px" }}>
                        Quest {idx + 1} · {step.duration}
                      </div>
                      <strong style={{ display: "block", fontSize: "0.83rem", marginBottom: "5px" }}>{step.title}</strong>
                      <p style={{ fontSize: "0.76rem", color: "var(--text-secondary)", lineHeight: 1.45, marginBottom: "6px" }}>
                        {step.description}
                      </p>
                      <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Kanıt: {step.proof}</span>
                    </div>
                  ))}
                </div>
              </section>

              <section>
                <h4 style={sectionTitleStyle}>Kullanılacak Kaynaklar</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {actionPlan.resources.map((resource) => (
                    <a
                      key={resource.url}
                      href={resource.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ ...miniCardStyle, textDecoration: "none", display: "block" }}
                    >
                      <span style={{ color: "var(--accent-amber)", fontSize: "0.72rem", fontWeight: 700 }}>{resource.platform}</span>
                      <strong style={{ display: "block", fontSize: "0.82rem", margin: "4px 0", color: "var(--text-primary)" }}>
                        {resource.title}
                      </strong>
                      <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", lineHeight: 1.45 }}>{resource.reason}</p>
                    </a>
                  ))}
                </div>
                <p style={{ fontSize: "0.72rem", color: "var(--text-muted)", lineHeight: 1.4, marginTop: "8px" }}>
                  {actionPlan.research_note}
                </p>
              </section>

              <section>
                <h4 style={sectionTitleStyle}>Arkadaşla Ortak Yol</h4>
                <div style={miniCardStyle}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "10px", alignItems: "center", marginBottom: "8px" }}>
                    <span style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>Ortak rota kodu</span>
                    <code style={{ color: "var(--accent-cyan)", fontWeight: 800 }}>{actionPlan.shared_path.code}</code>
                  </div>
                  <p style={{ fontSize: "0.76rem", color: "var(--text-secondary)", lineHeight: 1.45, marginBottom: "8px" }}>
                    Ortak kalınacak nokta: {actionPlan.shared_path.common_until}
                  </p>
                  <ul style={compactListStyle}>
                    {actionPlan.shared_path.together.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                  <div style={{ height: "1px", background: "var(--glass-border)", margin: "10px 0" }} />
                  <ul style={compactListStyle}>
                    {actionPlan.shared_path.divergence_options.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </div>
              </section>

              <section>
                <h4 style={sectionTitleStyle}>Şu Ana Kadar Yapılanlar</h4>
                <ul style={compactListStyle}>
                  {actionPlan.done_so_far.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </section>
            </div>
          )}

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

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "0.86rem",
  fontWeight: 700,
  color: "var(--text-primary)",
  marginBottom: "9px",
};

const miniCardStyle: React.CSSProperties = {
  padding: "12px",
  background: "rgba(255, 255, 255, 0.025)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
};

const compactListStyle: React.CSSProperties = {
  margin: 0,
  paddingLeft: "18px",
  color: "var(--text-secondary)",
  fontSize: "0.75rem",
  lineHeight: 1.55,
};