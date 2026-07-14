import type { CurrencyCode } from "@tsubo/contracts";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

interface CurrencyContextValue {
  currency: CurrencyCode;
  setCurrency: (currency: CurrencyCode) => void;
  formatPrice: (amountJpy: number | null, amountUsd: number | null) => string;
}

const CurrencyContext = createContext<CurrencyContextValue | null>(null);

const STORAGE_KEY = "tsubo-currency";

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [currency, setCurrencyState] = useState<CurrencyCode>("USD");

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "JPY" || stored === "USD") {
      setCurrencyState(stored);
    }
  }, []);

  const setCurrency = useCallback((next: CurrencyCode) => {
    setCurrencyState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const formatPrice = useCallback(
    (amountJpy: number | null, amountUsd: number | null): string => {
      if (currency === "JPY") {
        if (amountJpy == null) return "—";
        return `¥${amountJpy.toLocaleString("ja-JP")}`;
      }
      if (amountUsd == null) return "—";
      return `$${amountUsd.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    },
    [currency],
  );

  const value = useMemo(
    () => ({ currency, setCurrency, formatPrice }),
    [currency, setCurrency, formatPrice],
  );

  return (
    <CurrencyContext.Provider value={value}>{children}</CurrencyContext.Provider>
  );
}

export function useCurrency(): CurrencyContextValue {
  const ctx = useContext(CurrencyContext);
  if (!ctx) {
    throw new Error("useCurrency must be used within CurrencyProvider");
  }
  return ctx;
}
