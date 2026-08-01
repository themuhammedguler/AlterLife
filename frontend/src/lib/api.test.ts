import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// api.ts reads NEXT_PUBLIC_API_URL at module-load time, so keep the default
// (http://localhost:8001) which is what the app uses in dev/test.

function jsonResponse(body: unknown, init: { status?: number; ok?: boolean } = {}) {
  const status = init.status ?? 200;
  return {
    ok: init.ok ?? (status >= 200 && status < 300),
    status,
    json: async () => body,
  } as Response;
}

describe("lib/api", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("fetchWithAuth", () => {
    it("sends JSON content-type and no Authorization header when logged out", async () => {
      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ ok: true })
      );

      await fetchWithAuth("/api/v1/ping");

      const [, options] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(options.headers["Content-Type"]).toBe("application/json");
      expect(options.headers.Authorization).toBeUndefined();
    });

    it("attaches a Bearer token from localStorage when present", async () => {
      localStorage.setItem("alterlife_token", "tok_123");
      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ ok: true })
      );

      await fetchWithAuth("/api/v1/ping");

      const [url, options] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe("http://localhost:8001/api/v1/ping");
      expect(options.headers.Authorization).toBe("Bearer tok_123");
    });

    it("resolves with the parsed JSON body on success", async () => {
      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ hello: "world" })
      );

      await expect(fetchWithAuth("/api/v1/ping")).resolves.toEqual({ hello: "world" });
    });

    it("throws using the backend's error detail on non-2xx responses", async () => {
      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ detail: "Yetkisiz erişim" }, { status: 403, ok: false })
      );

      await expect(fetchWithAuth("/api/v1/secret")).rejects.toThrow("Yetkisiz erişim");
    });

    it("falls back to a generic error message when the body has no detail", async () => {
      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({}, { status: 500, ok: false })
      );

      await expect(fetchWithAuth("/api/v1/broken")).rejects.toThrow("Bir hata oluştu");
    });

    it("logs the user out and redirects to /login on a 401", async () => {
      localStorage.setItem("alterlife_token", "expired-token");
      localStorage.setItem("alterlife_user_id", "usr_1");

      const assign = vi.fn();
      Object.defineProperty(window, "location", {
        value: { ...window.location, pathname: "/dashboard", assign },
        writable: true,
      });

      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ detail: "expired" }, { status: 401, ok: false })
      );

      await expect(fetchWithAuth("/api/v1/user/profile")).rejects.toThrow();

      expect(localStorage.getItem("alterlife_token")).toBeNull();
      expect(localStorage.getItem("alterlife_user_id")).toBeNull();
      expect(assign).toHaveBeenCalledWith("/login");
    });

    it("does not redirect again on a 401 if already on /login", async () => {
      const assign = vi.fn();
      Object.defineProperty(window, "location", {
        value: { ...window.location, pathname: "/login", assign },
        writable: true,
      });

      const { fetchWithAuth } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ detail: "expired" }, { status: 401, ok: false })
      );

      await expect(fetchWithAuth("/api/v1/user/profile")).rejects.toThrow();
      expect(assign).not.toHaveBeenCalled();
    });
  });

  describe("session helpers", () => {
    it("isAuthenticated reflects presence of the stored token", async () => {
      const { isAuthenticated } = await import("./api");
      expect(isAuthenticated()).toBe(false);

      localStorage.setItem("alterlife_token", "tok");
      expect(isAuthenticated()).toBe(true);
    });

    it("logout clears all session-related localStorage keys", async () => {
      localStorage.setItem("alterlife_token", "tok");
      localStorage.setItem("alterlife_user_id", "usr_1");
      localStorage.setItem("alterlife_onboarding", "done");

      const { logout } = await import("./api");
      logout();

      expect(localStorage.getItem("alterlife_token")).toBeNull();
      expect(localStorage.getItem("alterlife_user_id")).toBeNull();
      expect(localStorage.getItem("alterlife_onboarding")).toBeNull();
    });
  });

  describe("auth flows persist the session", () => {
    it("loginWithEmail stores the access token and user id", async () => {
      const { loginWithEmail } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ access_token: "tok_email", user_id: "usr_email", is_new_user: false })
      );

      const data = await loginWithEmail("a@b.com", "pw");

      expect(data.access_token).toBe("tok_email");
      expect(localStorage.getItem("alterlife_token")).toBe("tok_email");
      expect(localStorage.getItem("alterlife_user_id")).toBe("usr_email");
    });

    it("registerWithEmail sends display_name and persists the session", async () => {
      const { registerWithEmail } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ access_token: "tok_reg", user_id: "usr_reg", is_new_user: true })
      );

      await registerWithEmail("a@b.com", "pw", "Test User");

      const [, options] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      const body = JSON.parse(options.body);
      expect(body).toEqual({ email: "a@b.com", password: "pw", display_name: "Test User" });
      expect(localStorage.getItem("alterlife_token")).toBe("tok_reg");
    });
  });

  describe("endpoints that depend on the stored user id", () => {
    it("getSimulationTree targets the logged-in user's simulation", async () => {
      localStorage.setItem("alterlife_user_id", "usr_42");
      const { getSimulationTree } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ simulation_id: "sim_usr_42", nodes: [] })
      );

      await getSimulationTree();

      const [url] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe("http://localhost:8001/api/v1/simulations/sim_usr_42/tree");
    });

    it("getSimulationTree falls back to dev_user_001 when logged out", async () => {
      const { getSimulationTree } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ simulation_id: "sim_dev_user_001", nodes: [] })
      );

      await getSimulationTree();

      const [url] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe("http://localhost:8001/api/v1/simulations/sim_dev_user_001/tree");
    });
  });

  describe("request shaping for write endpoints", () => {
    it("verifyQuest POSTs to the quest-specific verify endpoint", async () => {
      const { verifyQuest } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ quest_id: "qst_1", status: "completed" })
      );

      await verifyQuest("qst_1");

      const [url, options] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe("http://localhost:8001/api/v1/quests/qst_1/verify");
      expect(options.method).toBe("POST");
    });

    it("completeLibraryResource issues a PATCH request", async () => {
      const { completeLibraryResource } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
        jsonResponse({ is_completed: true })
      );

      await completeLibraryResource("res_1");

      const [url, options] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe("http://localhost:8001/api/v1/library/resources/res_1/complete");
      expect(options.method).toBe("PATCH");
    });

    it("resolveCommunityInvite URL-encodes the invite code", async () => {
      const { resolveCommunityInvite } = await import("./api");
      (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(jsonResponse({}));

      await resolveCommunityInvite("BERLIN 42/2026");

      const [url] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toBe(
        "http://localhost:8001/api/v1/community/invites/BERLIN%2042%2F2026"
      );
    });
  });
});
