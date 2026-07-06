"use client";

import { useEffect, useMemo, useState } from "react";
import type { ComponentType, CSSProperties } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowUpRight,
  BadgeCheck,
  BarChart3,
  Bell,
  Bot,
  BrainCircuit,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Clock3,
  DollarSign,
  GitBranch,
  Globe,
  GraduationCap,
  Gauge,
  Home,
  Landmark,
  Layers3,
  ListTodo,
  MapPinned,
  PlaneTakeoff,
  Rocket,
  School2,
  Settings2,
  ShieldAlert,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Trophy,
  UserRound,
  Users,
  Wallet,
  Zap,
} from "lucide-react";

import styles from "./page.module.css";

type OnboardingData = {
  field?: string;
  age?: string;
  city?: string;
  freeGoal?: string;
};

type Scenario = {
  id: string;
  title: string;
  subtitle: string;
  icon: ComponentType<{ className?: string; style?: CSSProperties }>;
  accent: string;
  glow: string;
  probability: string;
  risk: string;
  salary: string;
  timeline: string;
  description: string;
  cardClass: string;
  position: { left: string; top: string; width: string };
  path: string;
};

type Metric = {
  label: string;
  value: string;
  tone: string;
};

type SidebarItem = {
  icon: ComponentType<{ className?: string }>;
  label: string;
  href: string;
  active: boolean;
};

const goalOptions = [
  "Move to Germany",
  "Build a Startup",
  "Corporate Career",
  "Remote Work",
  "Master's Degree",
];

const futureScenarios: Scenario[] = [
  {
    id: "germany",
    title: "Move to Germany",
    subtitle: "🇩🇪 Higher salary, new ecosystem, relocation path",
    icon: Globe,
    accent: "#00e5ff",
    glow: "rgba(0, 229, 255, 0.32)",
    probability: "68%",
    risk: "Medium",
    salary: "€72k / year",
    timeline: "12-18 months",
    description: "Language readiness, visa prep, and portfolio positioning create a strong relocation lane.",
    cardClass: styles.cardBlue,
    position: { left: "6%", top: "10%", width: "21rem" },
    path: "M500 690 C 470 605 420 530 360 435 C 330 390 300 350 230 260",
  },
  {
    id: "startup",
    title: "Build a Startup",
    subtitle: "🚀 Product velocity, fundraising, and bold upside",
    icon: Rocket,
    accent: "#ec4899",
    glow: "rgba(236, 72, 153, 0.28)",
    probability: "41%",
    risk: "High",
    salary: "$180k potential",
    timeline: "9-24 months",
    description: "Best for users with high conviction, strong network effects, and willingness to iterate quickly.",
    cardClass: styles.cardPink,
    position: { left: "36%", top: "2%", width: "21rem" },
    path: "M500 690 C 495 600 500 540 510 470 C 518 410 520 360 505 250",
  },
  {
    id: "corporate",
    title: "Corporate Career",
    subtitle: "🏢 Stability, seniority, and compounding credibility",
    icon: BriefcaseBusiness,
    accent: "#7c3aed",
    glow: "rgba(124, 58, 237, 0.3)",
    probability: "81%",
    risk: "Low",
    salary: "$95k / year",
    timeline: "6-12 months",
    description: "Fastest route to stable growth, manager-level scope, and predictable financial planning.",
    cardClass: styles.cardViolet,
    position: { left: "60%", top: "10%", width: "21rem" },
    path: "M500 690 C 530 605 580 530 640 435 C 670 390 700 355 760 260",
  },
  {
    id: "remote",
    title: "Remote Work",
    subtitle: "🌍 Location freedom with global teams",
    icon: PlaneTakeoff,
    accent: "#10b981",
    glow: "rgba(16, 185, 129, 0.26)",
    probability: "74%",
    risk: "Medium",
    salary: "$88k / year",
    timeline: "3-9 months",
    description: "A flexible lane if you want time autonomy, cross-border collaboration, and lifestyle balance.",
    cardClass: styles.cardGreen,
    position: { left: "4%", top: "46%", width: "21rem" },
    path: "M500 690 C 405 645 335 610 270 545 C 200 470 145 390 120 300",
  },
  {
    id: "masters",
    title: "Master's Degree",
    subtitle: "🎓 Research depth, credentials, and network leverage",
    icon: GraduationCap,
    accent: "#f59e0b",
    glow: "rgba(245, 158, 11, 0.26)",
    probability: "63%",
    risk: "Medium",
    salary: "$70k / year",
    timeline: "18-30 months",
    description: "Strong for profile re-positioning, migration, or entering a more technical discipline.",
    cardClass: styles.cardAmber,
    position: { left: "68%", top: "44%", width: "21rem" },
    path: "M500 690 C 595 646 665 615 730 548 C 800 475 860 392 880 300",
  },
];

const focusMetrics: Metric[] = [
  { label: "Level", value: "12", tone: "cyan" },
  { label: "XP", value: "7,820", tone: "violet" },
  { label: "Energy", value: "84%", tone: "green" },
  { label: "Focus", value: "71%", tone: "amber" },
  { label: "Motivation", value: "92%", tone: "pink" },
  { label: "Consistency", value: "88%", tone: "cyan" },
];

const questItems = [
  { title: "Complete a language sprint", reward: "+120 XP", done: true },
  { title: "Review relocation checklist", reward: "+180 XP", done: false },
  { title: "Ship one portfolio artifact", reward: "+220 XP", done: false },
  { title: "Sync calendar and milestones", reward: "+90 XP", done: true },
];

const badges = ["Momentum", "Explorer", "Consistency", "Future Builder"];

const scenarioComparison = [
  {
    title: "Move to Germany",
    income: "$92k",
    growth: "High",
    quality: "Very high",
    freedom: "Medium",
    happiness: "82",
    risk: "38",
    accent: "#00e5ff",
  },
  {
    title: "Build a Startup",
    income: "$180k",
    growth: "Very high",
    quality: "Medium",
    freedom: "High",
    happiness: "77",
    risk: "74",
    accent: "#ec4899",
  },
  {
    title: "Remote Work",
    income: "$88k",
    growth: "High",
    quality: "High",
    freedom: "Very high",
    happiness: "86",
    risk: "44",
    accent: "#10b981",
  },
];

const chartPoints = [18, 23, 28, 35, 42, 51, 58, 69, 74, 81, 87];

function formatGoalLabel(goal: string) {
  return goal.replace("Build a Startup", "Build a Startup")
    .replace("Corporate Career", "Corporate Career")
    .replace("Master's Degree", "Master's Degree");
}

function Sparkline() {
  const width = 420;
  const height = 180;
  const step = width / (chartPoints.length - 1);
  const max = 100;
  const path = chartPoints
    .map((point, index) => {
      const x = index * step;
      const y = height - (point / max) * (height - 20) - 10;
      return `${index === 0 ? "M" : "L"}${x} ${y}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className={styles.sparkline} aria-hidden="true">
      <defs>
        <linearGradient id="spark-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#00e5ff" />
          <stop offset="55%" stopColor="#7c3aed" />
          <stop offset="100%" stopColor="#ec4899" />
        </linearGradient>
        <linearGradient id="spark-fill" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="rgba(0,229,255,0.28)" />
          <stop offset="100%" stopColor="rgba(124,58,237,0.02)" />
        </linearGradient>
      </defs>
      <path d={`${path} L ${width} ${height} L 0 ${height} Z`} fill="url(#spark-fill)" />
      <path d={path} fill="none" stroke="url(#spark-gradient)" strokeWidth="4" strokeLinecap="round" />
      {chartPoints.map((point, index) => {
        const x = index * step;
        const y = height - (point / max) * (height - 20) - 10;
        return <circle key={index} cx={x} cy={y} r="4.5" fill="#e2e8f0" />;
      })}
    </svg>
  );
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<OnboardingData | null>(null);
  const [selectedGoal, setSelectedGoal] = useState(goalOptions[0]);
  const sidebarItems: SidebarItem[] = [
    { icon: Home, label: "Dashboard", href: "/dashboard", active: true },
    { icon: Rocket, label: "Simulations", href: "/simulations", active: false },
    { icon: Layers3, label: "Parallel Futures", href: "/dashboard#futures", active: false },
    { icon: MapPinned, label: "Roadmap", href: "/dashboard#roadmap", active: false },
    { icon: ListTodo, label: "Daily Quests", href: "/dashboard#quests", active: false },
    { icon: Sparkles, label: "Skills", href: "/skills", active: false },
    { icon: Users, label: "Community", href: "/community", active: false },
    { icon: BarChart3, label: "Analytics", href: "/analytics", active: false },
    { icon: Settings2, label: "Settings", href: "/settings", active: false },
  ];

  useEffect(() => {
    try {
      const data = window.localStorage.getItem("alterlife_onboarding");
      if (data) {
        setProfile(JSON.parse(data));
      }
    } catch {
      setProfile(null);
    }
  }, []);

  useEffect(() => {
    if (profile?.freeGoal) {
      const matchingGoal = goalOptions.find((goal) => profile.freeGoal?.toLowerCase().includes(goal.split(" ")[0].toLowerCase()));
      if (matchingGoal) {
        setSelectedGoal(matchingGoal);
      }
    }
  }, [profile]);

  const activeScenario = useMemo(
    () => futureScenarios.find((scenario) => scenario.title === selectedGoal) ?? futureScenarios[0],
    [selectedGoal],
  );

  const username = profile?.city ? `Sedef • ${profile.city}` : "Sedef K.";
  const avatarInitials = profile?.age ? "SK" : "AL";

  return (
    <div className={styles.shell}>
      <div className={styles.orbViolet} aria-hidden="true" />
      <div className={styles.orbCyan} aria-hidden="true" />

      <aside className={styles.sidebar}>
        <div className={styles.brandBlock}>
          <div className={styles.brandMark}>
            <BrainCircuit className={styles.brandIcon} />
          </div>
          <div>
            <p className={styles.brandLabel}>AlterLife</p>
            <p className={styles.brandSubLabel}>Future Simulation OS</p>
          </div>
        </div>

        <nav className={styles.sidebarNav}>
          {sidebarItems.map(({ icon: Icon, label, href, active }) => (
            <Link key={label} href={href} className={active ? styles.sidebarLinkActive : styles.sidebarLink}>
              <Icon className={styles.sidebarLinkIcon} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.sidebarProfile}>
            <div className={styles.avatarMini}>
              {avatarInitials}
            </div>
            <div>
              <p className={styles.sidebarName}>{username}</p>
              <p className={styles.sidebarMeta}>Level 12 • 7,820 XP</p>
            </div>
          </div>
          <div className={styles.progressBlock}>
            <div className={styles.progressMetaRow}>
              <span>XP Progress</span>
              <span>7,820 / 10,000</span>
            </div>
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: "78%" }} />
            </div>
          </div>
        </div>
      </aside>

      <div className={styles.content}>
        <header className={styles.topbar}>
          <div>
            <p className={styles.topbarKicker}>Welcome back, Sedef</p>
            <h1 className={styles.topbarTitle}>You are exploring multiple versions of your future.</h1>
          </div>

          <div className={styles.goalControls}>
            <label className={styles.goalLabel} htmlFor="goal-selector">
              Current goal
            </label>
            <div className={styles.selectWrap}>
              <select
                id="goal-selector"
                value={selectedGoal}
                onChange={(event) => setSelectedGoal(event.target.value)}
                className={styles.select}
              >
                {goalOptions.map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
              <ChevronDown className={styles.selectIcon} />
            </div>

            <button className={styles.iconButton} type="button" aria-label="Notifications">
              <Bell className={styles.iconButtonIcon} />
            </button>

            <div className={styles.profileChip}>
              <div className={styles.profileChipAvatar}>
                <UserRound className={styles.profileChipAvatarIcon} />
              </div>
              <div>
                <p className={styles.profileChipName}>Sedef K.</p>
                <p className={styles.profileChipSub}>Product Strategist</p>
              </div>
            </div>
          </div>
        </header>

        <main className={styles.mainGrid}>
          <section className={styles.leftPanel}>
            <div className={styles.leftHeroCard}>
              <div className={styles.aiAvatarWrap}>
                <div className={styles.aiAvatarGlow} />
                <div className={styles.aiAvatar}>
                  <Bot className={styles.aiAvatarIcon} />
                </div>
              </div>
              <p className={styles.leftHeroEyebrow}>AI Digital Twin</p>
              <h2 className={styles.leftHeroTitle}>Lucid Twin Alpha</h2>
              <p className={styles.leftHeroText}>
                Your simulation engine is learning from preferences, milestones, and scenario probability shifts.
              </p>

              <div className={styles.heroStacks}>
                {focusMetrics.map((metric) => (
                  <div key={metric.label} className={styles.metricChip} data-tone={metric.tone}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Daily state</h3>
                <BadgeCheck className={styles.panelHeaderIcon} />
              </div>
              <div className={styles.focusBars}>
                {[
                  ["Energy", 84, "#00e5ff"],
                  ["Focus", 71, "#7c3aed"],
                  ["Motivation", 92, "#ec4899"],
                  ["Consistency", 88, "#10b981"],
                ].map(([label, value, color]) => (
                  <div key={String(label)} className={styles.barRow}>
                    <div className={styles.barMeta}>
                      <span>{label}</span>
                      <span>{value}%</span>
                    </div>
                    <div className={styles.progressBar}>
                      <div className={styles.progressFill} style={{ width: `${value}%`, background: String(color) }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Daily quote</h3>
                <Sparkles className={styles.panelHeaderIcon} />
              </div>
              <p className={styles.quoteText}>
                "The best future is not predicted. It is designed one decision at a time."
              </p>
            </div>
          </section>

          <section className={styles.centerPanel}>
            <div className={styles.stageHeader}>
              <div>
                <p className={styles.stageKicker}>Roadmap visualization</p>
                <h2 className={styles.stageTitle}>Future Branching Control Center</h2>
              </div>
              <div className={styles.stageLegend}>
                <span><Target className={styles.legendIcon} /> Current Position</span>
                <span><Activity className={styles.legendIcon} /> Live probability model</span>
              </div>
            </div>

            <div className={styles.roadmapFrame}>
              <div className={styles.roadmapAura} aria-hidden="true" />
              <svg className={styles.roadmapSvg} viewBox="0 0 1000 760" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="line-blue" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#00e5ff" />
                    <stop offset="100%" stopColor="#7c3aed" />
                  </linearGradient>
                  <linearGradient id="line-green" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="100%" stopColor="#00e5ff" />
                  </linearGradient>
                  <linearGradient id="line-pink" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#ec4899" />
                    <stop offset="100%" stopColor="#f59e0b" />
                  </linearGradient>
                  <linearGradient id="line-violet" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#7c3aed" />
                    <stop offset="100%" stopColor="#00e5ff" />
                  </linearGradient>
                  <filter id="roadmap-glow" x="-40%" y="-40%" width="180%" height="180%">
                    <feGaussianBlur stdDeviation="10" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {futureScenarios.map((scenario, index) => (
                  <g key={scenario.id} filter="url(#roadmap-glow)" opacity={0.92}>
                    <path
                      d={scenario.path}
                      fill="none"
                      stroke={`url(#line-${index % 4 === 0 ? "blue" : index % 4 === 1 ? "pink" : index % 4 === 2 ? "violet" : "green"})`}
                      strokeWidth="6"
                      strokeLinecap="round"
                    />
                  </g>
                ))}
                <path
                  d="M500 690 C 520 640 525 600 500 550"
                  fill="none"
                  stroke="rgba(255,255,255,0.12)"
                  strokeWidth="2"
                  strokeDasharray="5 10"
                />
              </svg>

              <div className={styles.currentNode}>
                <div className={styles.currentNodeInner}>
                  <div className={styles.currentNodePulse} />
                  <Target className={styles.currentNodeIcon} />
                </div>
                <div>
                  <p className={styles.currentNodeLabel}>Current Position</p>
                  <p className={styles.currentNodeMeta}>Decision point • level 12</p>
                </div>
              </div>

              {futureScenarios.map((scenario, index) => {
                const Icon = scenario.icon;
                return (
                  <article
                    key={scenario.id}
                    className={`${styles.futureCard} ${scenario.cardClass}`}
                    style={{
                      left: scenario.position.left,
                      top: scenario.position.top,
                      width: scenario.position.width,
                      boxShadow: `0 24px 80px ${scenario.glow}`,
                    }}
                  >
                    <div className={styles.futureCardTop}>
                      <div className={styles.futureCardIconWrap} style={{ borderColor: scenario.accent }}>
                        <Icon className={styles.futureCardIcon} style={{ color: scenario.accent }} />
                      </div>
                      <div>
                        <p className={styles.futureCardTitle}>{scenario.title}</p>
                        <p className={styles.futureCardSubtitle}>{scenario.subtitle}</p>
                      </div>
                    </div>

                    <div className={styles.futureIllustration} aria-hidden="true">
                      <div className={styles.futureIllustrationBlob} style={{ background: scenario.accent }} />
                      <div className={styles.futureIllustrationRing} />
                    </div>

                    <div className={styles.futureMetrics}>
                      <div>
                        <span>Success probability</span>
                        <strong>{scenario.probability}</strong>
                      </div>
                      <div>
                        <span>Risk level</span>
                        <strong>{scenario.risk}</strong>
                      </div>
                      <div>
                        <span>Estimated salary</span>
                        <strong>{scenario.salary}</strong>
                      </div>
                      <div>
                        <span>Timeline</span>
                        <strong>{scenario.timeline}</strong>
                      </div>
                    </div>

                    <p className={styles.futureDescription}>{scenario.description}</p>
                    <div className={styles.futureFooter}>
                      <span className={styles.futureTag}>AI-forecasted</span>
                      <span className={styles.futureLink}>
                        Inspect branch <ArrowUpRight className={styles.futureLinkIcon} />
                      </span>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section className={styles.rightPanel}>
            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Daily quests</h3>
                <ListTodo className={styles.panelHeaderIcon} />
              </div>
              <div className={styles.progressBlock}>
                <div className={styles.progressMetaRow}>
                  <span>Quest completion</span>
                  <span>2 / 4</span>
                </div>
                <div className={styles.progressBar}>
                  <div className={styles.progressFill} style={{ width: "50%" }} />
                </div>
              </div>

              <div className={styles.questList}>
                {questItems.map((quest) => (
                  <div key={quest.title} className={styles.questItem} data-done={quest.done}>
                    <div className={styles.questCheck}>
                      {quest.done ? <CheckCircle2 className={styles.questCheckIcon} /> : <ShieldAlert className={styles.questCheckIcon} />}
                    </div>
                    <div className={styles.questBody}>
                      <p>{quest.title}</p>
                      <span>{quest.reward}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Integrations</h3>
                <Activity className={styles.panelHeaderIcon} />
              </div>

              <div className={styles.integrationList}>
                {[
                  { name: "Google Calendar", icon: CalendarDays, state: "Synced", tone: "green" },
                  { name: "GitHub activity", icon: GitBranch, state: "Warm", tone: "violet" },
                ].map((integration) => {
                  const Icon = integration.icon;
                  return (
                    <div key={integration.name} className={styles.integrationRow}>
                      <div className={styles.integrationIconWrap}>
                        <Icon className={styles.integrationIcon} />
                      </div>
                      <div>
                        <p className={styles.integrationName}>{integration.name}</p>
                        <p className={styles.integrationState} data-tone={integration.tone}>{integration.state}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Upcoming milestones</h3>
                <Clock3 className={styles.panelHeaderIcon} />
              </div>
              <div className={styles.milestoneList}>
                {[
                  ["Portfolio refresh", "3 days"],
                  ["Language benchmark", "8 days"],
                  ["Scenario review", "12 days"],
                ].map(([title, time]) => (
                  <div key={title} className={styles.milestoneRow}>
                    <span>{title}</span>
                    <strong>{time}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.panelCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Unlocked badges</h3>
                <Trophy className={styles.panelHeaderIcon} />
              </div>
              <div className={styles.badgeCloud}>
                {badges.map((badge) => (
                  <span key={badge} className={styles.badgePill}>
                    <Star className={styles.badgePillIcon} />
                    {badge}
                  </span>
                ))}
              </div>
            </div>
          </section>
        </main>

        <section className={styles.bottomSection}>
          <div className={styles.bottomHeader}>
            <div>
              <p className={styles.stageKicker}>Scenario comparison</p>
              <h2 className={styles.stageTitle}>Compare futures across the metrics that matter most</h2>
            </div>
            <div className={styles.chartSwitches}>
              <span className={styles.chartSwitch}>Income</span>
              <span className={styles.chartSwitch}>Growth</span>
              <span className={styles.chartSwitch}>Happiness</span>
            </div>
          </div>

          <div className={styles.bottomGrid}>
            {scenarioComparison.map((scenario) => (
              <article
                key={scenario.title}
                className={styles.comparisonCard}
              >
                <div className={styles.comparisonHeader}>
                  <span className={styles.comparisonAccent} style={{ background: scenario.accent }} />
                  <div>
                    <h3>{scenario.title}</h3>
                    <p>Future lane snapshot</p>
                  </div>
                </div>

                <div className={styles.comparisonStats}>
                  <div><span>Estimated income</span><strong>{scenario.income}</strong></div>
                  <div><span>Career growth</span><strong>{scenario.growth}</strong></div>
                  <div><span>Life quality</span><strong>{scenario.quality}</strong></div>
                  <div><span>Financial freedom</span><strong>{scenario.freedom}</strong></div>
                </div>

                <div className={styles.scoreRow}>
                  <div>
                    <span>Happiness score</span>
                    <strong>{scenario.happiness}</strong>
                  </div>
                  <div>
                    <span>Risk score</span>
                    <strong>{scenario.risk}</strong>
                  </div>
                </div>

                <div className={styles.comparisonChart}>
                  <div className={styles.comparisonChartTrack}>
                    <div className={styles.comparisonChartFill} style={{ width: `${scenario.happiness}%`, background: scenario.accent }} />
                  </div>
                  <p>Projected balance trajectory</p>
                </div>
              </article>
            ))}

            <div className={styles.chartCard}>
              <div className={styles.panelHeaderRow}>
                <h3 className={styles.panelTitle}>Modern projection chart</h3>
                <Gauge className={styles.panelHeaderIcon} />
              </div>
              <div className={styles.chartContent}>
                <Sparkline />
                <div className={styles.chartMetrics}>
                  <div>
                    <span>Estimated income</span>
                    <strong>$92k</strong>
                  </div>
                  <div>
                    <span>Career growth</span>
                    <strong>+18%</strong>
                  </div>
                  <div>
                    <span>Life quality</span>
                    <strong>84</strong>
                  </div>
                  <div>
                    <span>Happiness score</span>
                    <strong>87</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.activeScenarioBar}>
            <div>
              <p className={styles.stageKicker}>Selected goal</p>
              <h3 className={styles.activeScenarioTitle}>{formatGoalLabel(activeScenario.title)}</h3>
              <p className={styles.activeScenarioText}>{activeScenario.description}</p>
            </div>
            <div className={styles.activeScenarioAction}>
              <div>
                <span>Probability</span>
                <strong>{activeScenario.probability}</strong>
              </div>
              <Link href="/simulations" className={styles.primaryLink}>
                Open simulation <ArrowUpRight className={styles.primaryLinkIcon} />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}