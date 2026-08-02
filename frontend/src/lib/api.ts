const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

function getHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("alterlife_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    if (response.status === 401 && typeof window !== "undefined") {
      logout();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.assign("/login");
      }
    }
    throw new Error(errorData.detail || "Bir hata oluştu");
  }

  return response.json();
}

// ── Authentication ────────────────────────────────────────────────────────────

export async function loginWithGoogle(idToken: string) {
  const data = await fetchWithAuth("/api/v1/auth/google", {
    method: "POST",
    body: JSON.stringify({ id_token: idToken }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("alterlife_token", data.access_token);
    localStorage.setItem("alterlife_user_id", data.user_id);
  }
  return data;
}

export async function loginWithEmail(email: string, password: string) {
  const data = await fetchWithAuth("/api/v1/auth/email/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("alterlife_token", data.access_token);
    localStorage.setItem("alterlife_user_id", data.user_id);
  }
  return data;
}

export async function registerWithEmail(email: string, password: string, displayName: string) {
  const data = await fetchWithAuth("/api/v1/auth/email/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("alterlife_token", data.access_token);
    localStorage.setItem("alterlife_user_id", data.user_id);
  }
  return data;
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("alterlife_token");
    localStorage.removeItem("alterlife_user_id");
    localStorage.removeItem("alterlife_onboarding");
  }
}

export function isAuthenticated(): boolean {
  if (typeof window !== "undefined") {
    return !!localStorage.getItem("alterlife_token");
  }
  return false;
}

// ── User Profile & Onboarding ──────────────────────────────────────────────────

export async function submitOnboarding(payload: {
  status: string;
  age: string;
  city: string;
  field: string;
  workPrefs: string[];
  freeGoal: string;
}) {
  return fetchWithAuth("/api/v1/user/onboarding", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getProfile() {
  return fetchWithAuth("/api/v1/user/profile");
}

export async function updateProfile(payload: {
  display_name?: string;
  role?: string;
  experience_years?: number;
  daily_preferences?: {
    day_type?: "light" | "normal" | "busy";
    best_focus_time?: "morning" | "afternoon" | "evening" | "night";
    mood?: "low" | "steady" | "playful" | "high";
    available_minutes?: number;
    include_social?: boolean;
  };
}) {
  return fetchWithAuth("/api/v1/user/profile", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteAccount() {
  return fetchWithAuth("/api/v1/user/account", { method: "DELETE" });
}

export async function generateAvatar(description: string, photoBase64?: string, photoMimeType = "image/jpeg") {
  return fetchWithAuth("/api/v1/user/avatar/generate", {
    method: "POST",
    body: JSON.stringify({ description, photo_base64: photoBase64, photo_mime_type: photoMimeType }),
  });
}

// ── Simulations ───────────────────────────────────────────────────────────────

export async function generateSimulation(target: string, currentProfile?: any) {
  return fetchWithAuth("/api/v1/simulations/generate", {
    method: "POST",
    body: JSON.stringify({ target, current_profile: currentProfile }),
  });
}

export async function getSimulationTree() {
  const userId = typeof window !== "undefined" ? localStorage.getItem("alterlife_user_id") || "dev_user_001" : "dev_user_001";
  return fetchWithAuth(`/api/v1/simulations/sim_${userId}/tree`);
}

export async function saveSimulationViewState(payload: {
  last_selected_node_id: string | null;
  branch_checkpoints: Record<string, string>;
  suggestion_history: Record<string, string[]>;
  map_mode: "focus" | "all";
}) {
  const userId = typeof window !== "undefined" ? localStorage.getItem("alterlife_user_id") || "dev_user_001" : "dev_user_001";
  return fetchWithAuth(`/api/v1/simulations/sim_${userId}/view-state`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function branchSimulation(parentNodeId: string, decisionText: string) {
  const userId = typeof window !== "undefined" ? localStorage.getItem("alterlife_user_id") || "dev_user_001" : "dev_user_001";
  return fetchWithAuth(`/api/v1/simulations/sim_${userId}/branch`, {
    method: "POST",
    body: JSON.stringify({ parent_node_id: parentNodeId, decision_text: decisionText }),
  });
}

export async function runStressTest(nodeId: string) {
  const userId = typeof window !== "undefined" ? localStorage.getItem("alterlife_user_id") || "dev_user_001" : "dev_user_001";
  return fetchWithAuth(`/api/v1/simulations/sim_${userId}/stress-test?node_id=${nodeId}`, {
    method: "POST",
  });
}

export async function getBranchActionPlan(nodeId: string, friendCode?: string) {
  const userId = typeof window !== "undefined" ? localStorage.getItem("alterlife_user_id") || "dev_user_001" : "dev_user_001";
  return fetchWithAuth(`/api/v1/simulations/sim_${userId}/nodes/${nodeId}/action-plan`, {
    method: "POST",
    body: JSON.stringify({ friend_code: friendCode || undefined }),
  });
}

// ── Quests ───────────────────────────────────────────────────────────────────

export async function getDailyQuests() {
  return fetchWithAuth("/api/v1/quests/daily");
}

export async function planDailyQuests(payload: {
  day_type: "light" | "normal" | "busy";
  best_focus_time: "morning" | "afternoon" | "evening" | "night";
  mood: "low" | "steady" | "playful" | "high";
  available_minutes: number;
  include_social: boolean;
}) {
  return fetchWithAuth("/api/v1/quests/daily/plan", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function verifyQuest(questId: string) {
  return fetchWithAuth(`/api/v1/quests/${questId}/verify`, {
    method: "POST",
  });
}

// ── Skills ────────────────────────────────────────────────────────────────────

export async function getSkillTree() {
  return fetchWithAuth("/api/v1/skills/tree");
}

export async function getSkillResources(skillId: string) {
  return fetchWithAuth(`/api/v1/skills/${skillId}/resources`);
}

export async function addSkillXP(skillId: string, xpAmount: number) {
  return fetchWithAuth(`/api/v1/skills/${skillId}/xp`, {
    method: "POST",
    body: JSON.stringify({ xp_amount: xpAmount }),
  });
}

// ── Library ───────────────────────────────────────────────────────────────────

export async function getLibrary() {
  return fetchWithAuth("/api/v1/library/resources");
}

export async function saveLibraryResource(payload: {
  title: string;
  platform: string;
  url: string;
  thumbnail_url?: string;
  skill_tags?: string[];
}) {
  return fetchWithAuth("/api/v1/library/resources", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function completeLibraryResource(resourceId: string) {
  return fetchWithAuth(`/api/v1/library/resources/${resourceId}/complete`, {
    method: "PATCH",
  });
}

export async function deleteLibraryResource(resourceId: string) {
  return fetchWithAuth(`/api/v1/library/resources/${resourceId}`, {
    method: "DELETE",
  });
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export async function getAnalyticsSummary() {
  return fetchWithAuth("/api/v1/analytics/summary");
}

// ── Integration Status ────────────────────────────────────────────────────────

export async function getCalendarStatus() {
  return fetchWithAuth("/api/v1/integrations/calendar/status");
}

export async function getGithubStatus() {
  return fetchWithAuth("/api/v1/integrations/github/status");
}

export async function connectCalendar(code: string, redirectUri: string) {
  return fetchWithAuth("/api/v1/integrations/calendar/connect", {
    method: "POST",
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
  });
}

export async function connectGithub(code: string, redirectUri: string) {
  return fetchWithAuth("/api/v1/integrations/github/connect", {
    method: "POST",
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
  });
}

export async function disconnectCalendar() {
  return fetchWithAuth("/api/v1/integrations/calendar", { method: "DELETE" });
}

export async function createCalendarQuestEvent(payload: {
  quest_id: string;
  title: string;
  description?: string;
  time_slot?: string;
  duration_minutes?: number;
}) {
  return fetchWithAuth("/api/v1/integrations/calendar/quest-event", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function disconnectGithub() {
  return fetchWithAuth("/api/v1/integrations/github", { method: "DELETE" });
}

// ── Agents ────────────────────────────────────────────────────────────────────

export async function runOrchestrator() {
  return fetchWithAuth("/api/v1/agents/orchestrate", { method: "POST" });
}

export async function runFinancialAgent() {
  return fetchWithAuth("/api/v1/agents/financial/analyze", { method: "POST" });
}

export async function runCareerCoachAgent() {
  return fetchWithAuth("/api/v1/agents/career/roadmap", { method: "POST" });
}

export async function runWellbeingAgent() {
  return fetchWithAuth("/api/v1/agents/wellbeing/check", { method: "POST" });
}

export async function runMigrationAgent() {
  return fetchWithAuth("/api/v1/agents/migration/plan", { method: "POST" });
}

export async function runTrainingPipeline(scenarioIds?: string[], agentsToTest?: string[]) {
  return fetchWithAuth("/api/v1/agents/train", {
    method: "POST",
    body: JSON.stringify({
      scenario_ids: scenarioIds,
      agents_to_test: agentsToTest,
    }),
  });
}

// ── RPG Rest (Energy/Focus yenile) ───────────────────────────────────────────

export async function restUser() {
  return fetchWithAuth("/api/v1/user/rest", { method: "POST" });
}

// ── Community RAG ─────────────────────────────────────────────────────────────

export async function getCommunityPaths(limit = 20) {
  return fetchWithAuth(`/api/v1/community/paths?limit=${limit}`);
}

export async function getCommunityOverview() {
  return fetchWithAuth("/api/v1/community/overview");
}

export async function searchCommunityPaths(goal: string, topK = 4) {
  return fetchWithAuth("/api/v1/community/paths/search", {
    method: "POST",
    body: JSON.stringify({ goal, top_k: topK }),
  });
}

export async function getCommunityCohort(pathId: string) {
  return fetchWithAuth(`/api/v1/community/paths/${pathId}/cohort`);
}

export async function joinCommunityPath(pathId: string, branch?: string) {
  return fetchWithAuth(`/api/v1/community/paths/${pathId}/join`, {
    method: "POST",
    body: JSON.stringify({ branch }),
  });
}

export async function createCommunityInvite(pathId: string, branch?: string) {
  return fetchWithAuth(`/api/v1/community/paths/${pathId}/invite`, {
    method: "POST",
    body: JSON.stringify({ branch }),
  });
}

export async function resolveCommunityInvite(code: string) {
  return fetchWithAuth(`/api/v1/community/invites/${encodeURIComponent(code)}`);
}

export async function getMyCommunityPaths() {
  return fetchWithAuth("/api/v1/community/me/paths");
}

export async function shareCommunityPath(goal: string, steps: string[], outcome: string, tags: string[]) {
  return fetchWithAuth("/api/v1/community/share", {
    method: "POST",
    body: JSON.stringify({ goal, steps, outcome, tags }),
  });
}

export async function getCommunityStats() {
  return fetchWithAuth("/api/v1/community/stats");
}

// ── Custom Skills ─────────────────────────────────────────────────────────────

export async function addCustomSkill(payload: {
  name: string;
  category?: string;
  description?: string;
  prerequisites?: string[];
  canvas_x?: number;
  canvas_y?: number;
}) {
  return fetchWithAuth("/api/v1/skills/custom", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSkillPosition(skillId: string, canvasX: number, canvasY: number) {
  return fetchWithAuth(`/api/v1/skills/${skillId}/position`, {
    method: "PATCH",
    body: JSON.stringify({ canvas_x: canvasX, canvas_y: canvasY }),
  });
}

export async function deleteCustomSkill(skillId: string) {
  return fetchWithAuth(`/api/v1/skills/${skillId}/custom`, { method: "DELETE" });
}

// ── Coach Center ─────────────────────────────────────────────────────────────

export async function getActiveGoal() {
  return fetchWithAuth("/api/v1/coach/active-goal");
}

export async function setActiveGoal(payload: { simulation_id: string; node_id: string }) {
  return fetchWithAuth("/api/v1/coach/active-goal", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getRiskRadar() {
  return fetchWithAuth("/api/v1/coach/risk-radar");
}

export async function createWeeklyReview(payload: {
  wins: string[];
  blockers: string[];
  energy_score: number;
  next_week_focus?: string;
}) {
  return fetchWithAuth("/api/v1/coach/weekly-review", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function mentorChat(message: string, tone: "friendly" | "strict" | "playful" = "friendly") {
  return fetchWithAuth("/api/v1/coach/mentor/chat", {
    method: "POST",
    body: JSON.stringify({ message, tone }),
  });
}

export async function addDecisionJournal(payload: {
  decision: string;
  expectation: string;
  confidence: number;
  revisit_in_days: number;
}) {
  return fetchWithAuth("/api/v1/coach/decision-journal", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getDecisionJournal() {
  return fetchWithAuth("/api/v1/coach/decision-journal");
}

export async function getMilestoneTimeline() {
  return fetchWithAuth("/api/v1/coach/timeline");
}

export async function getRealityCheck() {
  return fetchWithAuth("/api/v1/coach/reality-check");
}

export async function exportCoachReport() {
  return fetchWithAuth("/api/v1/coach/report");
}

export async function getNotifications() {
  return fetchWithAuth("/api/v1/coach/notifications");
}

export async function markNotificationRead(notificationId: string) {
  return fetchWithAuth("/api/v1/coach/notifications/read", {
    method: "POST",
    body: JSON.stringify({ notification_id: notificationId }),
  });
}