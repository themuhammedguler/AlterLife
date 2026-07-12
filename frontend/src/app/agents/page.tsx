"use client";

import { useEffect, useState } from "react";
import { runOrchestrator } from "@/lib/api";

export default function AgentsPage() {
  const [loading, setLoading] = useState(true);
  const [orchestratorData, setOrchestratorData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAgents() {
      try {
        const data = await runOrchestrator();
        setOrchestratorData(data);
      } catch (err: any) {
        setError(err.message || "Failed to load agents.");
      } finally {
        setLoading(false);
      }
    }
    loadAgents();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900 text-gray-100">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-accent-cyan border-t-transparent"></div>
          <h2 className="text-xl font-semibold">Beyin Çalışıyor...</h2>
          <p className="text-gray-400">Agent'lar verilerini analiz ediyor</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900 text-gray-100">
        <div className="rounded-xl border border-red-500/50 bg-red-500/10 p-6 text-center">
          <h2 className="text-xl font-bold text-red-400">Bağlantı Hatası</h2>
          <p className="mt-2 text-red-300">{error}</p>
        </div>
      </div>
    );
  }

  const {
    user_archetype,
    archetype_description,
    primary_goal,
    motivational_message,
    agent_descriptions,
    unified_report,
    agent_results,
    profile_stats,
  } = orchestratorData || {};

  return (
    <div className="min-h-screen bg-gray-900 px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 border-b border-gray-800 pb-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-accent-cyan to-accent-violet bg-clip-text text-transparent">
            AI Yönlendirme Merkezi
          </h1>
          <p className="mt-2 text-gray-400">Tüm uzman agent'larınızın ortak analizi ve kararları</p>
        </header>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Panel 1: Profile & Status */}
          <div className="space-y-6">
            <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 shadow-xl backdrop-blur-sm">
              <h2 className="text-lg font-semibold text-gray-300">Profil Arketipi</h2>
              <div className="mt-4 flex items-center space-x-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent-cyan/20 text-3xl">
                  {user_archetype === "Riskçi" ? "🎲" : user_archetype === "Planlayıcı" ? "📋" : user_archetype === "Hayalci" ? "☁️" : "🛠️"}
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-accent-cyan">{user_archetype}</h3>
                  <p className="text-sm text-gray-400">Seviye {profile_stats?.level}</p>
                </div>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-gray-300">
                {archetype_description}
              </p>
              <div className="mt-4 rounded-lg bg-gray-800 p-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Motivasyon</h4>
                <p className="mt-1 text-sm font-medium italic text-accent-violet">"{motivational_message}"</p>
              </div>
            </div>

            <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 shadow-xl backdrop-blur-sm">
              <h2 className="text-lg font-semibold text-gray-300">Aktif Uzmanlar</h2>
              <div className="mt-4 space-y-3">
                {Object.keys(agent_descriptions || {}).map((key) => {
                  const agent = agent_descriptions[key];
                  return (
                    <div key={key} className="flex items-center space-x-3 rounded-lg bg-gray-800/50 p-3">
                      <span className="text-2xl">{agent.emoji}</span>
                      <div>
                        <p className="text-sm font-semibold text-gray-200">{agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Panel 2: Unified Report (Actionable) */}
          <div className="space-y-6 lg:col-span-1">
            <div className="rounded-2xl border border-accent-cyan/30 bg-accent-cyan/5 p-6 shadow-[0_0_15px_rgba(34,211,238,0.05)] backdrop-blur-sm">
              <h2 className="flex items-center text-xl font-bold text-gray-100">
                <span className="mr-2 text-2xl">⚡</span> Bugünün Odak Noktası
              </h2>
              <div className="mt-6 space-y-4">
                {unified_report?.today_focus?.map((focus: string, idx: number) => (
                  <div key={idx} className="rounded-lg border border-gray-700 bg-gray-800 p-4">
                    <p className="text-sm text-gray-200">{focus}</p>
                  </div>
                ))}
                {(!unified_report?.today_focus || unified_report.today_focus.length === 0) && (
                  <p className="text-sm text-gray-500">Bugün için acil bir görev bulunmuyor.</p>
                )}
              </div>
            </div>

            {unified_report?.warnings?.length > 0 && (
              <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-6 backdrop-blur-sm">
                <h2 className="flex items-center text-lg font-bold text-red-400">
                  <span className="mr-2">⚠️</span> Riskler ve Uyarılar
                </h2>
                <ul className="mt-4 space-y-3">
                  {unified_report.warnings.map((warn: string, idx: number) => (
                    <li key={idx} className="flex items-start text-sm text-gray-300">
                      <span className="mr-2 mt-0.5 text-red-500">•</span> {warn}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {unified_report?.opportunities?.length > 0 && (
              <div className="rounded-2xl border border-green-500/30 bg-green-500/5 p-6 backdrop-blur-sm">
                <h2 className="flex items-center text-lg font-bold text-green-400">
                  <span className="mr-2">🌱</span> Fırsatlar
                </h2>
                <ul className="mt-4 space-y-3">
                  {unified_report.opportunities.map((opp: string, idx: number) => (
                    <li key={idx} className="flex items-start text-sm text-gray-300">
                      <span className="mr-2 mt-0.5 text-green-500">•</span> {opp}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Panel 3: Detailed Agent Insights */}
          <div className="space-y-6 lg:col-span-1">
            <h2 className="text-2xl font-bold text-gray-100">Uzman Raporları</h2>

            {agent_results?.timeline && (
              <div className="rounded-xl border border-gray-800 bg-gray-800/40 p-5">
                <h3 className="flex items-center font-semibold text-gray-200">
                  <span className="mr-2 text-xl">📅</span> Zaman Çizelgesi
                </h3>
                <p className="mt-3 text-sm text-gray-300">
                  {agent_results.timeline.reality_check}
                </p>
                <div className="mt-4 flex items-center justify-between rounded bg-gray-900 p-3">
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Mevcut Hız</p>
                    <p className="text-lg font-bold text-gray-200">{agent_results.timeline.current_pace_months} Ay</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500">Optimize</p>
                    <p className="text-lg font-bold text-accent-green">{agent_results.timeline.optimized_pace_months} Ay</p>
                  </div>
                </div>
              </div>
            )}

            {agent_results?.financial && (
              <div className="rounded-xl border border-gray-800 bg-gray-800/40 p-5">
                <h3 className="flex items-center font-semibold text-gray-200">
                  <span className="mr-2 text-xl">💰</span> Finansal Durum
                </h3>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-sm text-gray-400">Gereken Birikim:</span>
                  <span className="font-bold text-gray-200">${agent_results.financial.target_savings_usd}</span>
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-sm text-gray-400">Acil Fon:</span>
                  <span className="font-bold text-gray-200">{agent_results.financial.emergency_fund_months} Ay</span>
                </div>
              </div>
            )}

            {agent_results?.skill_gap && (
              <div className="rounded-xl border border-gray-800 bg-gray-800/40 p-5">
                <h3 className="flex items-center font-semibold text-gray-200">
                  <span className="mr-2 text-xl">📚</span> Yetenek Açığı
                </h3>
                <ul className="mt-3 space-y-2">
                  {agent_results.skill_gap.critical_gaps?.slice(0, 3).map((gap: any, i: number) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">{gap.skill}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        gap.urgency === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {gap.urgency}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {agent_results?.wellbeing && (
              <div className="rounded-xl border border-gray-800 bg-gray-800/40 p-5">
                <h3 className="flex items-center font-semibold text-gray-200">
                  <span className="mr-2 text-xl">🧘</span> Sağlık & Denge
                </h3>
                <div className="mt-3">
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-gray-400">Tükenmişlik Riski</span>
                    <span className={agent_results.wellbeing.risk_level === 'Kritik' ? 'text-red-400' : 'text-gray-200'}>
                      {agent_results.wellbeing.risk_level}
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
                    <div 
                      className={`h-full ${agent_results.wellbeing.burnout_score > 70 ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${agent_results.wellbeing.burnout_score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            
            {agent_results?.migration && (
              <div className="rounded-xl border border-gray-800 bg-gray-800/40 p-5">
                <h3 className="flex items-center font-semibold text-gray-200">
                  <span className="mr-2 text-xl">✈️</span> Göç Planı
                </h3>
                <p className="mt-3 text-sm font-medium text-accent-cyan">Hedef: {agent_results.migration.target_country}</p>
                <p className="mt-1 text-sm text-gray-400">Vize: {agent_results.migration.visa_recommendation}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
