"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Coins,
  Compass,
  Gauge,
  HeartPulse,
  Lightbulb,
  MapPinned,
  RefreshCw,
  Route,
  Sparkles,
  Target,
  TrendingUp,
  UsersRound,
} from "lucide-react";
import { runOrchestrator } from "@/lib/api";
import styles from "./page.module.css";

type AgentDescription = { name: string; emoji: string; description: string };
type AgentData = {
  user_archetype?: string;
  archetype_description?: string;
  primary_goal?: string;
  motivational_message?: string;
  generated_at?: string;
  urgency_score?: number;
  risk_tolerance?: string;
  agent_descriptions?: Record<string, AgentDescription>;
  unified_report?: {
    today_focus?: string[];
    warnings?: string[];
    opportunities?: string[];
  };
  agent_results?: Record<string, any>;
  profile_stats?: {
    level?: number;
    xp?: number;
    completed_quests?: number;
    skills_unlocked?: number;
    active_days?: number;
  };
};

const agentIcons: Record<string, typeof BrainCircuit> = {
  financial: Coins,
  career_coach: Compass,
  wellbeing: HeartPulse,
  migration: MapPinned,
  skill_gap: Route,
  timeline: CalendarDays,
  scenario: Sparkles,
};

const archetypeEmoji = (archetype?: string) =>
  archetype === "Riskçi" ? "🎲" : archetype === "Planlayıcı" ? "📋" : archetype === "Hayalci" ? "☁️" : "🛠️";

const cleanPrefix = (text: string) => text.replace(/^[\p{Emoji_Presentation}\p{Extended_Pictographic}\s]+/u, "");

export default function AgentsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AgentData | null>(null);
  const [error, setError] = useState("");

  const loadAgents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(await runOrchestrator());
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI ajanları yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadAgents();
  }, [loadAgents]);

  const activeAgents = useMemo(() => Object.entries(data?.agent_descriptions || {}), [data]);
  const results = data?.agent_results || {};
  const report = data?.unified_report || {};
  const stats = data?.profile_stats || {};
  const wellbeingScore = Math.min(100, Math.max(0, results.wellbeing?.burnout_score || 0));

  if (loading) {
    return (
      <div className={styles.statePage}>
        <div className={styles.loaderCore}><BrainCircuit size={42} /></div>
        <div className={styles.loaderRings} aria-hidden="true" />
        <h1>AI konseyi toplanıyor</h1>
        <p>Uzman ajanlar profilini, hedefini ve ilerlemeni birlikte değerlendiriyor.</p>
        <div className={styles.loadingSteps}>
          <span>Profil okunuyor</span><i /><span>Uzmanlar seçiliyor</span><i /><span>Rapor hazırlanıyor</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.statePage}>
        <div className={styles.errorIcon}><AlertTriangle size={34} /></div>
        <h1>AI Merkezi şu an yanıt vermiyor</h1>
        <p>{error}</p>
        <button className={styles.primaryButton} onClick={() => void loadAgents()}><RefreshCw size={17} /> Yeniden dene</button>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.ambientOne} aria-hidden="true" />
      <div className={styles.ambientTwo} aria-hidden="true" />

      <header className={styles.hero}>
        <div>
          <div className={styles.eyebrow}><BrainCircuit size={15} /> ORCHESTRATOR ONLINE <span /></div>
          <h1>AI Yönlendirme <span>Merkezi</span></h1>
          <p>{activeAgents.length} uzman ajan, hedefin için tek bir uygulanabilir yol haritasında birleşti.</p>
        </div>
        <button className={styles.refreshButton} onClick={() => void loadAgents()}>
          <RefreshCw size={17} /> Analizi yenile
        </button>
      </header>

      <section className={styles.commandGrid}>
        <article className={`${styles.panel} ${styles.identityCard}`}>
          <div className={styles.cardLabel}>DİJİTAL İKİZ PROFİLİ</div>
          <div className={styles.identityTop}>
            <div className={styles.avatar}>{archetypeEmoji(data?.user_archetype)}</div>
            <div>
              <span className={styles.muted}>Karar arketipi</span>
              <h2>{data?.user_archetype || "Pratik"}</h2>
              <div className={styles.levelPill}>SEVİYE {stats.level || 1}</div>
            </div>
          </div>
          <p className={styles.description}>{data?.archetype_description || "Hedefe odaklı, veriye dayalı karar profili."}</p>
          <div className={styles.quote}><Sparkles size={16} /><span>{data?.motivational_message || "Bir sonraki doğru adım, büyük hedefi ulaşılabilir kılar."}</span></div>
        </article>

        <article className={`${styles.panel} ${styles.goalCard}`}>
          <div className={styles.cardLabel}>ANA GÖREV</div>
          <div className={styles.goalIcon}><Target size={22} /></div>
          <h2>{data?.primary_goal || "Kariyer gelişimi"}</h2>
          <div className={styles.goalMeta}>
            <span><Gauge size={15} /> Öncelik {data?.urgency_score || 5}/10</span>
            <span><TrendingUp size={15} /> Risk: {data?.risk_tolerance || "orta"}</span>
          </div>
          <div className={styles.progressTrack}><span style={{ width: `${Math.min(100, (data?.urgency_score || 5) * 10)}%` }} /></div>
          <p>Uzman konseyinin tüm değerlendirmeleri bu hedef etrafında senkronize edildi.</p>
        </article>

        <article className={`${styles.panel} ${styles.statsCard}`}>
          <div className={styles.cardLabel}>CANLI PROFİL VERİSİ</div>
          <div className={styles.statGrid}>
            <div><strong>{stats.completed_quests || 0}</strong><span>Tamamlanan görev</span></div>
            <div><strong>{stats.skills_unlocked || 0}</strong><span>Açık yetenek</span></div>
            <div><strong>{stats.active_days || 0}</strong><span>Aktif gün</span></div>
            <div><strong>{stats.xp || 0}</strong><span>Toplam XP</span></div>
          </div>
          <div className={styles.syncLine}><CheckCircle2 size={16} /> Profil verileri ajanlarla senkronize</div>
        </article>
      </section>

      <section className={styles.workspace}>
        <div className={styles.mainColumn}>
          <article className={`${styles.panel} ${styles.focusPanel}`}>
            <div className={styles.sectionHeading}>
              <div><span className={styles.sectionIcon}><Sparkles size={19} /></span><div><span>ORTAK KARAR</span><h2>Bugünün odak noktaları</h2></div></div>
              <span className={styles.dateBadge}>{data?.generated_at || "Bugün"}</span>
            </div>
            <div className={styles.focusList}>
              {(report.today_focus?.length ? report.today_focus : ["Aktif hedefin için ilk küçük adımı bugün tamamla."]).map((focus, index) => (
                <div className={styles.focusItem} key={`${focus}-${index}`}>
                  <span className={styles.focusNumber}>{String(index + 1).padStart(2, "0")}</span>
                  <p>{cleanPrefix(focus)}</p><ArrowRight size={18} />
                </div>
              ))}
            </div>
          </article>

          <div className={styles.signalGrid}>
            <article className={`${styles.panel} ${styles.signalCard} ${styles.warningCard}`}>
              <div className={styles.signalTitle}><AlertTriangle size={18} /><h3>Risk sinyalleri</h3><span>{report.warnings?.length || 0}</span></div>
              {(report.warnings?.length ? report.warnings : ["Kritik bir risk sinyali bulunmuyor."]).map((item, index) => <p key={index}>{cleanPrefix(item)}</p>)}
            </article>
            <article className={`${styles.panel} ${styles.signalCard} ${styles.opportunityCard}`}>
              <div className={styles.signalTitle}><Lightbulb size={18} /><h3>Fırsat radarı</h3><span>{report.opportunities?.length || 0}</span></div>
              {(report.opportunities?.length ? report.opportunities : ["Yeni fırsatlar ilerleme verinle birlikte güncellenecek."]).map((item, index) => <p key={index}>{cleanPrefix(item)}</p>)}
            </article>
          </div>

          <article className={`${styles.panel} ${styles.reportsPanel}`}>
            <div className={styles.sectionHeading}>
              <div><span className={styles.sectionIcon}><UsersRound size={19} /></span><div><span>UZMAN ÇIKTILARI</span><h2>Karar istihbaratı</h2></div></div>
            </div>
            <div className={styles.reportGrid}>
              {results.timeline && <InsightCard icon={Clock3} title="Zaman çizelgesi" accent="cyan" text={results.timeline.reality_check}
                metrics={[["Mevcut hız", `${results.timeline.current_pace_months} ay`], ["Optimize", `${results.timeline.optimized_pace_months} ay`]]} />}
              {results.financial && <InsightCard icon={Coins} title="Finansal hazırlık" accent="amber"
                metrics={[["Hedef birikim", `$${results.financial.target_savings_usd}`], ["Acil fon", `${results.financial.emergency_fund_months} ay`]]} />}
              {results.skill_gap && <InsightCard icon={Route} title="Kritik yetenekler" accent="violet"
                tags={(results.skill_gap.critical_gaps || []).slice(0, 3).map((gap: any) => gap.skill)} />}
              {results.wellbeing && <InsightCard icon={HeartPulse} title="Enerji ve denge" accent="green"
                text={`Tükenmişlik riski: ${results.wellbeing.risk_level || "Düşük"}`} progress={wellbeingScore} />}
              {results.migration && <InsightCard icon={MapPinned} title="Göç planı" accent="pink"
                text={`${results.migration.target_country || "Hedef ülke"} · ${results.migration.visa_recommendation || "Vize rotası analiz edildi"}`} />}
              {results.career_coach && <InsightCard icon={Compass} title="Kariyer rotası" accent="blue"
                text={results.career_coach.quick_start_action || results.career_coach.job_market_insight || "Kariyer yol haritası hazır."} />}
            </div>
          </article>
        </div>

        <aside className={styles.agentRail}>
          <div className={styles.railHeader}><div><span>AKTİF KONSEY</span><h2>Uzman ajanlar</h2></div><span className={styles.liveBadge}><i /> {activeAgents.length} AKTİF</span></div>
          <div className={styles.agentList}>
            {activeAgents.map(([key, agent], index) => {
              const Icon = agentIcons[key] || BrainCircuit;
              return (
                <div className={styles.agentItem} key={key}>
                  <div className={styles.agentIcon}><Icon size={20} /></div>
                  <div><strong>{agent.name.replace("Agent", "")}</strong><p>{agent.description}</p></div>
                  <span className={styles.agentIndex}>{String(index + 1).padStart(2, "0")}</span>
                </div>
              );
            })}
          </div>
          <div className={styles.orchestratorCard}>
            <div className={styles.orchestratorIcon}><BrainCircuit size={27} /></div>
            <div><span>MERKEZİ BEYİN</span><strong>Orchestrator</strong><p>Tüm uzman çıktılarını tek karar raporunda sentezliyor.</p></div>
          </div>
        </aside>
      </section>
    </div>
  );
}

function InsightCard({
  icon: Icon, title, accent, text, metrics, tags, progress,
}: {
  icon: typeof BrainCircuit; title: string; accent: string; text?: string;
  metrics?: string[][]; tags?: string[]; progress?: number;
}) {
  return (
    <div className={`${styles.insightCard} ${styles[`accent_${accent}`]}`}>
      <div className={styles.insightTitle}><span><Icon size={18} /></span><h3>{title}</h3></div>
      {text && <p>{text}</p>}
      {metrics && <div className={styles.metricRow}>{metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>}
      {tags && <div className={styles.tagRow}>{tags.map((tag) => <span key={tag}>{tag}</span>)}</div>}
      {progress !== undefined && <div className={styles.riskBar}><span style={{ width: `${progress}%` }} /></div>}
    </div>
  );
}