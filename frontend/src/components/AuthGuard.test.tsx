import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

const replace = vi.fn();
let mockPathname = "/dashboard";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
  useRouter: () => ({ replace }),
}));

async function renderGuard() {
  const AuthGuard = (await import("./AuthGuard")).default;
  return render(
    <AuthGuard>
      <div>Protected content</div>
    </AuthGuard>
  );
}

describe("AuthGuard", () => {
  beforeEach(() => {
    localStorage.clear();
    replace.mockClear();
    vi.resetModules();
  });

  afterEach(() => {
    mockPathname = "/dashboard";
  });

  it("redirects unauthenticated users away from protected routes", async () => {
    mockPathname = "/dashboard";
    await renderGuard();

    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/login?next=%2Fdashboard");
    });
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("renders children for authenticated users without redirecting", async () => {
    mockPathname = "/dashboard";
    localStorage.setItem("alterlife_token", "tok_123");

    await renderGuard();

    await waitFor(() => {
      expect(screen.getByText("Protected content")).toBeInTheDocument();
    });
    expect(replace).not.toHaveBeenCalled();
  });

  it("renders public routes even when logged out", async () => {
    mockPathname = "/login";

    await renderGuard();

    await waitFor(() => {
      expect(screen.getByText("Protected content")).toBeInTheDocument();
    });
    expect(replace).not.toHaveBeenCalled();
  });

  it("preserves the intended destination in the login redirect", async () => {
    mockPathname = "/settings/profile";

    await renderGuard();

    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/login?next=%2Fsettings%2Fprofile");
    });
  });
});
