import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate, useSearchParams } from "react-router-dom";
import { AppContract, Application, api, LastApplication, PersonalDataPolicy, User } from "./api";

const tokenKey = "insurance_token";
const themeKey = "insurance_theme";
const datePattern = "\\d{4}-\\d{2}-\\d{2}";

function isValidBirthDate(value: string): boolean {
  if (!new RegExp(`^${datePattern}$`).test(value)) {
    return false;
  }
  const [yearRaw, monthRaw, dayRaw] = value.split("-");
  const year = Number(yearRaw);
  const month = Number(monthRaw);
  const day = Number(dayRaw);
  if (yearRaw.length !== 4 || year < 1900) {
    return false;
  }
  const candidate = new Date(Date.UTC(year, month - 1, day));
  const now = new Date();
  if (Number.isNaN(candidate.getTime())) {
    return false;
  }
  return (
    candidate.getUTCFullYear() === year &&
    candidate.getUTCMonth() === month - 1 &&
    candidate.getUTCDate() === day &&
    candidate.getTime() <= now.getTime()
  );
}

function onlyDigits(value: string, maxLength: number): string {
  return value.replace(/\D/g, "").slice(0, maxLength);
}

function splitPassport(passportData: string): { series: string; number: string } {
  const [series = "", number = ""] = passportData.split(" ");
  return { series, number };
}

function useAuthState() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(tokenKey));
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    api.me(token).then(setUser).catch(() => setToken(null));
  }, [token]);

  const updateToken = (value: string | null) => {
    setToken(value);
    if (value) {
      localStorage.setItem(tokenKey, value);
    } else {
      localStorage.removeItem(tokenKey);
    }
  };

  return { token, user, setToken: updateToken };
}

function useThemeState() {
  const [theme, setTheme] = useState<"light" | "dark">(
    () => (localStorage.getItem(themeKey) as "light" | "dark") || "light"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(themeKey, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === "light" ? "dark" : "light"));
  return { theme, toggleTheme };
}

function Layout({
  children,
  user,
  onLogout,
  theme,
  onToggleTheme
}: {
  children: JSX.Element;
  user: User | null;
  onLogout: () => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}) {
  return (
    <div className="page">
      <header className="header">
        <Link to="/" className="brand">
          Страховой сервис
        </Link>
        <nav className="actions">
          <Link to="/">На главную</Link>
          {user ? (
            <>
              <Link to="/apply">Оформить</Link>
              <Link to="/cabinet">Личный кабинет</Link>
              <button onClick={onLogout}>Выйти</button>
            </>
          ) : (
            <>
              <Link to="/register">Регистрация</Link>
              <Link to="/login">Вход</Link>
            </>
          )}
        </nav>
      </header>
      {children}
      <button className="theme-toggle" onClick={onToggleTheme}>
        {theme === "light" ? "Тёмная тема" : "Светлая тема"}
      </button>
    </div>
  );
}

function Home({ user }: { user: User | null }) {
  const [content, setContent] = useState<{ title: string; paragraphs: string[]; note_for_guests: string } | null>(null);

  useEffect(() => {
    api.getContent().then(setContent).catch(() => undefined);
  }, []);

  return (
    <main className="card">
      <h1>{content?.title ?? "Страхование"}</h1>
      {content?.paragraphs.map((item) => (
        <p key={item}>{item}</p>
      ))}
      {!user ? (
        <div className="notice">{content?.note_for_guests ?? "Чтобы отправить заявку, сначала авторизуйтесь."}</div>
      ) : null}
      {user ? <Link to="/apply">Оформить</Link> : <button disabled>Оформить</button>}
    </main>
  );
}

function Register({ onToken }: { onToken: (token: string) => void }) {
  const [error, setError] = useState("");
  const [passportSeries, setPassportSeries] = useState("");
  const [passportNumber, setPassportNumber] = useState("");
  const [pdnConsent, setPdnConsent] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const birthDate = String(form.get("birth_date"));
    const passportData = `${passportSeries} ${passportNumber}`;
    if (passportSeries.length !== 4 || passportNumber.length !== 6) {
      setError("Паспорт: серия 4 цифры и номер 6 цифр");
      return;
    }
    if (!isValidBirthDate(birthDate)) {
      setError("Дата рождения должна быть корректной и с 4-значным годом");
      return;
    }
    if (!pdnConsent) {
      setError('Необходимо подтвердить: "С политикой ПДн ознакомлен"');
      return;
    }
    try {
      setError("");
      const result = await api.register({
        full_name: String(form.get("full_name")),
        passport_data: passportData,
        birth_date: birthDate,
        email: String(form.get("email")),
        password: String(form.get("password")),
        pdn_consent: true
      });
      onToken(result.access_token);
      navigate("/");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>Регистрация</h2>
      <input name="full_name" placeholder="ФИО" required />
      <div className="passport-row">
        <input
          name="passport_series"
          placeholder="Серия (4 цифры)"
          inputMode="numeric"
          maxLength={4}
          value={passportSeries}
          onChange={(event) => setPassportSeries(onlyDigits(event.target.value, 4))}
          required
        />
        <input
          name="passport_number"
          placeholder="Номер (6 цифр)"
          inputMode="numeric"
          maxLength={6}
          value={passportNumber}
          onChange={(event) => setPassportNumber(onlyDigits(event.target.value, 6))}
          required
        />
      </div>
      <input
        name="birth_date"
        type="date"
        min="1900-01-01"
        max={new Date().toISOString().slice(0, 10)}
        pattern={datePattern}
        title="Формат даты: ГГГГ-ММ-ДД"
        required
      />
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Пароль" minLength={8} required />
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={pdnConsent}
          onChange={(event) => setPdnConsent(event.target.checked)}
          required
        />
        <span>
          С{" "}
          <Link to="/policy" target="_blank" rel="noreferrer">
            политикой обработки ПДн
          </Link>{" "}
          ознакомлен
        </span>
      </label>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit">Зарегистрироваться</button>
    </form>
  );
}

function Login({ onToken }: { onToken: (token: string) => void }) {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      setError("");
      const result = await api.login({
        email: String(form.get("email")),
        password: String(form.get("password"))
      });
      onToken(result.access_token);
      navigate("/");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>Вход</h2>
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Пароль" required />
      {error ? <div className="error">{error}</div> : null}
      <button type="submit">Войти</button>
    </form>
  );
}

function ApplyPage({ token, user }: { token: string; user: User }) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [passportSeries, setPassportSeries] = useState(() => splitPassport(user.passport_data).series);
  const [passportNumber, setPassportNumber] = useState(() => splitPassport(user.passport_data).number);
  const [pdnConsent, setPdnConsent] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.getApplications(token).then(setApplications).catch(() => undefined);
  }, [token]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const birthDate = String(form.get("birth_date"));
    const passportData = `${passportSeries} ${passportNumber}`;
    if (passportSeries.length !== 4 || passportNumber.length !== 6) {
      setError("Паспорт: серия 4 цифры и номер 6 цифр");
      return;
    }
    if (!isValidBirthDate(birthDate)) {
      setError("Дата рождения должна быть корректной и с 4-значным годом");
      return;
    }
    if (!pdnConsent) {
      setError('Необходимо подтвердить: "С политикой ПДн ознакомлен"');
      return;
    }
    try {
      setError("");
      const created = await api.createApplication(token, {
        full_name: String(form.get("full_name")),
        passport_data: passportData,
        birth_date: birthDate,
        email: String(form.get("email")),
        workplace: String(form.get("workplace")),
        insurance_object: String(form.get("insurance_object")),
        insurance_period_months: Number(form.get("insurance_period_months")),
        insurance_cases: String(form.get("insurance_cases"))
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        payout_amount: Number(form.get("payout_amount")),
        pdn_consent: true
      });
      setApplications((prev) => [created, ...prev]);
      setMessage("Заявка отправлена. Переходите к оплате.");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="card form">
      <h2>Оформление заявки</h2>
      <form onSubmit={onSubmit} className="form">
        <input name="full_name" defaultValue={user.full_name} placeholder="ФИО" required />
        <div className="passport-row">
          <input
            name="passport_series"
            placeholder="Серия (4 цифры)"
            inputMode="numeric"
            maxLength={4}
            value={passportSeries}
            onChange={(event) => setPassportSeries(onlyDigits(event.target.value, 4))}
            required
          />
          <input
            name="passport_number"
            placeholder="Номер (6 цифр)"
            inputMode="numeric"
            maxLength={6}
            value={passportNumber}
            onChange={(event) => setPassportNumber(onlyDigits(event.target.value, 6))}
            required
          />
        </div>
        <input
          name="birth_date"
          defaultValue={user.birth_date}
          type="date"
          min="1900-01-01"
          max={new Date().toISOString().slice(0, 10)}
          pattern={datePattern}
          title="Формат даты: ГГГГ-ММ-ДД"
          required
        />
        <input name="email" defaultValue={user.email} type="email" required />
        <input name="workplace" placeholder="Место работы" required />
        <input name="insurance_object" placeholder="Что страховать" required />
        <input name="insurance_period_months" type="number" min={1} max={240} placeholder="Срок (мес.)" required />
        <input name="insurance_cases" placeholder="Страховые случаи (через запятую)" required />
        <input name="payout_amount" type="number" min={1} placeholder="Сумма выплаты" required />
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={pdnConsent}
            onChange={(event) => setPdnConsent(event.target.checked)}
            required
          />
          <span>
            С{" "}
            <Link to="/policy" target="_blank" rel="noreferrer">
              политикой обработки ПДн
            </Link>{" "}
            ознакомлен
          </span>
        </label>
        {error ? <div className="error">{error}</div> : null}
        {message ? <div className="success">{message}</div> : null}
        <button type="submit">Отправить заявку</button>
      </form>

      <div className="block">
        <h3>Все мои заявки</h3>
        {applications.length === 0 ? <div>Заявок пока нет.</div> : null}
        {applications.map((application) => (
          <div key={application.id} className="application-item">
            <div>Заявка #{application.id}</div>
            <div>Статус: {application.status}</div>
            <div>Объект: {application.insurance_object}</div>
            <div>Сумма: {application.payout_amount}</div>
            {application.status !== "paid" ? (
              <button onClick={() => navigate(`/payment?applicationId=${application.id}`)}>
                Перейти к оплате
              </button>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function PaymentPage({ token }: { token: string }) {
  const [lastApplication, setLastApplication] = useState<LastApplication>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [method, setMethod] = useState<"sbp" | "card">("sbp");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([api.getLastApplication(token), api.getApplications(token)])
      .then(([last, all]) => {
        setLastApplication(last);
        setApplications(all);
      })
      .catch(() => undefined);
  }, [token]);

  const targetApplicationId = Number(searchParams.get("applicationId") || 0);
  const targetApplication =
    (targetApplicationId ? applications.find((item) => item.id === targetApplicationId) : undefined) ??
    lastApplication;

  const canPay = useMemo(
    () => !!targetApplication && targetApplication.status !== "paid",
    [targetApplication]
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!targetApplication) {
      return;
    }
    const form = new FormData(event.currentTarget);
    try {
      setError("");
      const response = await api.pay(token, {
        application_id: targetApplication.id,
        payment_method: method,
        card_number: String(form.get("card_number") ?? "")
      });
      setResult(response.message);
      if (response.status === "success") {
        navigate("/cabinet");
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (!targetApplication) {
    return <div className="card">Заявок пока нет. Сначала оформите заявку.</div>;
  }

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>Оплата заявки #{targetApplication.id}</h2>
      <div>Текущий статус: {targetApplication.status}</div>
      <div className="actions">
        <label>
          <input type="radio" checked={method === "sbp"} onChange={() => setMethod("sbp")} />
          СБП (эмуляция QR)
        </label>
        <label>
          <input type="radio" checked={method === "card"} onChange={() => setMethod("card")} />
          Карта
        </label>
      </div>
      {method === "card" ? (
        <>
          <input name="card_number" placeholder="Номер карты" required />
          <small>Для симуляции неуспеха укажите карту, оканчивающуюся на 0000.</small>
        </>
      ) : (
        <div className="notice">СБП-оплата эмулируется как успешная.</div>
      )}
      {error ? <div className="error">{error}</div> : null}
      {result ? <div className="success">{result}</div> : null}
      <button type="submit" disabled={!canPay}>
        Оплатить
      </button>
    </form>
  );
}

function Cabinet({ token }: { token: string }) {
  const [contracts, setContracts] = useState<AppContract[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.contracts(token).then(setContracts).catch((e) => setError((e as Error).message));
  }, [token]);

  async function download(contractId: number, format: "pdf" | "docx") {
    const endpoint = `${import.meta.env.VITE_API_BASE ?? "http://localhost:3000/api/insurance"}/contracts/${contractId}/download?format=${format}`;
    const response = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) {
      throw new Error("Ошибка скачивания договора");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `contract-${contractId}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="card">
      <h2>Личный кабинет</h2>
      {error ? <div className="error">{error}</div> : null}
      {contracts.length === 0 ? <div>Пока нет успешных договоров.</div> : null}
      {contracts.map((contract) => (
        <div key={contract.id} className="contract">
          <div>Договор: {contract.contract_number}</div>
          <div>ID: {contract.id}</div>
          <div className="actions">
            <button onClick={() => download(contract.id, "docx")}>Скачать DOCX</button>
          </div>
        </div>
      ))}
    </main>
  );
}

function ProtectedRoute({ token, children }: { token: string | null; children: JSX.Element }) {
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function PolicyPage() {
  const [policy, setPolicy] = useState<PersonalDataPolicy | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getPolicy().then(setPolicy).catch((e) => setError((e as Error).message));
  }, []);

  return (
    <main className="card">
      <h2>{policy?.title ?? "Политика обработки ПДн"}</h2>
      {policy ? <p>Актуально на: {policy.updated_at}</p> : null}
      {error ? <div className="error">{error}</div> : null}
      {policy?.sections.map((section) => (
        <p key={section}>{section}</p>
      ))}
    </main>
  );
}

export function App() {
  const { token, user, setToken } = useAuthState();
  const { theme, toggleTheme } = useThemeState();

  return (
    <Layout user={user} onLogout={() => setToken(null)} theme={theme} onToggleTheme={toggleTheme}>
      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/policy" element={<PolicyPage />} />
        <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register onToken={setToken} />} />
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onToken={setToken} />} />
        <Route
          path="/apply"
          element={
            <ProtectedRoute token={token}>
              <>{user ? <ApplyPage token={token as string} user={user} /> : <div className="card">Загрузка...</div>}</>
            </ProtectedRoute>
          }
        />
        <Route
          path="/payment"
          element={
            <ProtectedRoute token={token}>
              <PaymentPage token={token as string} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cabinet"
          element={
            <ProtectedRoute token={token}>
              <Cabinet token={token as string} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}
