import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const push = vi.fn();
const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace }),
}));

const loginWithEmail = vi.fn();
const registerWithEmail = vi.fn();
const loginWithGoogle = vi.fn();

vi.mock("@/lib/api", () => ({
  loginWithEmail: (...args: any[]) => loginWithEmail(...args),
  registerWithEmail: (...args: any[]) => registerWithEmail(...args),
  loginWithGoogle: (...args: any[]) => loginWithGoogle(...args),
}));

async function renderLoginPage() {
  const LoginPage = (await import("./page")).default;
  return render(<LoginPage />);
}

describe("LoginPage", () => {
  beforeEach(() => {
    push.mockClear();
    replace.mockClear();
    loginWithEmail.mockReset();
    registerWithEmail.mockReset();
    loginWithGoogle.mockReset();
    vi.resetModules();
    vi.unstubAllEnvs();
  });

  it("shows a validation error instead of calling the API when password is empty", async () => {
    const user = userEvent.setup();
    await renderLoginPage();

    // The email input carries the native `required` attribute, so leaving
    // it empty would be blocked by browser constraint validation before our
    // handler ever runs. The password field has no such attribute, so
    // filling only the email is what actually exercises the app's own
    // `!email || !password` check.
    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "a@b.com");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));

    expect(await screen.findByText("Lütfen e-posta ve şifrenizi girin.")).toBeInTheDocument();
    expect(loginWithEmail).not.toHaveBeenCalled();
  });

  it("logs in an existing user and redirects to the dashboard", async () => {
    loginWithEmail.mockResolvedValue({ access_token: "tok", user_id: "usr_1", is_new_user: false });
    const user = userEvent.setup();
    await renderLoginPage();

    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "a@b.com");
    await user.type(screen.getByPlaceholderText("Şifre"), "supersecret");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));

    await waitFor(() => {
      expect(loginWithEmail).toHaveBeenCalledWith("a@b.com", "supersecret");
    });
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("routes a brand-new user to onboarding instead of the dashboard", async () => {
    loginWithEmail.mockResolvedValue({ access_token: "tok", user_id: "usr_2", is_new_user: true });
    const user = userEvent.setup();
    await renderLoginPage();

    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "new@b.com");
    await user.type(screen.getByPlaceholderText("Şifre"), "supersecret");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/onboarding");
    });
  });

  it("displays the backend's error message when login fails", async () => {
    loginWithEmail.mockRejectedValue(new Error("Geçersiz e-posta veya şifre"));
    const user = userEvent.setup();
    await renderLoginPage();

    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "a@b.com");
    await user.type(screen.getByPlaceholderText("Şifre"), "wrongpass");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));

    expect(await screen.findByText("Geçersiz e-posta veya şifre")).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });

  it("switches to registration mode and requires a display name", async () => {
    registerWithEmail.mockResolvedValue({ access_token: "tok", user_id: "usr_3", is_new_user: true });
    const user = userEvent.setup();
    await renderLoginPage();

    await user.click(screen.getByRole("button", { name: "Kayıt Ol" }));
    expect(screen.getByPlaceholderText("Adınız")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hesap Oluştur" })).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("Adınız"), "Test User");
    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "new@b.com");
    await user.type(screen.getByPlaceholderText("Şifre"), "supersecret");
    await user.click(screen.getByRole("button", { name: "Hesap Oluştur" }));

    await waitFor(() => {
      expect(registerWithEmail).toHaveBeenCalledWith("new@b.com", "supersecret", "Test User");
    });
  });

  it("clears a previous error when toggling between login and register", async () => {
    const user = userEvent.setup();
    await renderLoginPage();

    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "a@b.com");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));
    expect(await screen.findByText("Lütfen e-posta ve şifrenizi girin.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Kayıt Ol" }));
    expect(screen.queryByText("Lütfen e-posta ve şifrenizi girin.")).not.toBeInTheDocument();
  });

  it("disables the submit button while the request is in flight", async () => {
    let resolveLogin: (value: any) => void = () => {};
    loginWithEmail.mockReturnValue(
      new Promise((resolve) => {
        resolveLogin = resolve;
      })
    );
    const user = userEvent.setup();
    await renderLoginPage();

    await user.type(screen.getByPlaceholderText("E-posta adresiniz"), "a@b.com");
    await user.type(screen.getByPlaceholderText("Şifre"), "supersecret");
    await user.click(screen.getByRole("button", { name: "Giriş Yap" }));

    expect(await screen.findByRole("button", { name: "İşleniyor..." })).toBeDisabled();

    resolveLogin({ access_token: "tok", user_id: "usr_4", is_new_user: false });
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/dashboard");
    });
  });
});
