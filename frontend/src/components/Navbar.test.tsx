import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const replace = vi.fn();
let mockPathname = "/skills";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
  useRouter: () => ({ replace, push: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: any) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

const getProfile = vi.fn();
const logout = vi.fn();

vi.mock("@/lib/api", () => ({
  getProfile: (...args: any[]) => getProfile(...args),
  logout: (...args: any[]) => logout(...args),
}));

async function renderNavbar() {
  const Navbar = (await import("./Navbar")).default;
  return render(<Navbar />);
}

describe("Navbar", () => {
  beforeEach(() => {
    replace.mockClear();
    getProfile.mockReset();
    logout.mockReset();
    vi.resetModules();
  });

  afterEach(() => {
    mockPathname = "/skills";
  });

  it("does not render on the landing, login, onboarding, or dashboard routes", async () => {
    getProfile.mockResolvedValue({ display_name: "Gezgin", level: 1, xp: 0 });

    for (const route of ["/", "/login", "/onboarding", "/dashboard", "/dashboard/today"]) {
      mockPathname = route;
      const { container, unmount } = await renderNavbar();
      expect(container).toBeEmptyDOMElement();
      unmount();
    }
  });

  it("renders on other app routes with the nav landmark", async () => {
    getProfile.mockResolvedValue({ display_name: "Gezgin", level: 1, xp: 0 });
    mockPathname = "/skills";

    await renderNavbar();

    expect(screen.getByRole("navigation", { name: "Ana navigasyon" })).toBeInTheDocument();
    expect(screen.getByText("AlterLife")).toBeInTheDocument();
  });

  it("fetches and displays the user's profile summary", async () => {
    getProfile.mockResolvedValue({ display_name: "Ada Lovelace", level: 5, xp: 1234 });
    mockPathname = "/skills";

    await renderNavbar();

    await waitFor(() => {
      expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
    });
    expect(screen.getByText("Svr 5 · 1234 XP")).toBeInTheDocument();
  });

  it("falls back to default profile display when the profile fetch fails", async () => {
    getProfile.mockRejectedValue(new Error("network error"));
    mockPathname = "/skills";

    await renderNavbar();

    await waitFor(() => {
      expect(screen.getByText("Gezgin")).toBeInTheDocument();
    });
    expect(screen.getByText("Svr 1 · 0 XP")).toBeInTheDocument();
  });

  it("highlights the link matching the current route", async () => {
    getProfile.mockResolvedValue({ display_name: "Gezgin", level: 1, xp: 0 });
    mockPathname = "/community";

    await renderNavbar();

    const activeLink = screen.getByRole("link", { name: "Topluluk" });
    expect(activeLink).toHaveStyle({ color: "var(--accent-cyan)" });

    const inactiveLink = screen.getByRole("link", { name: "Yetenekler" });
    expect(inactiveLink).toHaveStyle({ color: "var(--text-secondary)" });
  });

  it("logs the user out and redirects to /login", async () => {
    getProfile.mockResolvedValue({ display_name: "Gezgin", level: 1, xp: 0 });
    mockPathname = "/skills";
    const user = userEvent.setup();

    await renderNavbar();
    await waitFor(() => {
      expect(getProfile).toHaveBeenCalled();
    });

    await user.click(screen.getByRole("button", { name: "Oturumu kapat" }));

    expect(logout).toHaveBeenCalled();
    expect(replace).toHaveBeenCalledWith("/login");
  });
});
