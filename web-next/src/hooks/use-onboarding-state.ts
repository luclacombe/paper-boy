"use client";

import { useState, useCallback, useEffect } from "react";
import type { Device, DeliveryMethod, EmailMethod } from "@/types";

const STORAGE_KEY = "paperboy_onboarding";

export interface OnboardingState {
  step: number;
  device: Device | null;
  feeds: { name: string; url: string; category: string }[];
  deliveryMethod: DeliveryMethod;
  title: string;
  readingTime: string;
  maxArticlesPerFeed: number;
  includeImages: boolean;
  deliveryTime: string;
  timezone: string;
  googleDriveFolder: string;
  kindleEmail: string;
  emailMethod: EmailMethod;
}

const DEFAULTS: OnboardingState = {
  step: 1,
  device: null,
  feeds: [],
  deliveryMethod: "local",
  title: "The Morning Paper",
  readingTime: "15",
  maxArticlesPerFeed: 8,
  includeImages: true,
  deliveryTime: "06:00",
  timezone: "US/Eastern",
  googleDriveFolder: "Rakuten Kobo",
  kindleEmail: "",
  emailMethod: "gmail",
};

function loadFromStorage(): OnboardingState {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

function saveToStorage(state: OnboardingState) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Storage full or unavailable — continue without persistence
  }
}

export function clearOnboardingStorage() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
}

export function getOnboardingStorage(): OnboardingState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return null;
  }
}

export function useOnboardingState() {
  const [state, setState] = useState<OnboardingState>(DEFAULTS);
  const [loaded, setLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    setState(loadFromStorage());
    setLoaded(true);
  }, []);

  // Persist to localStorage on every change (after initial load)
  useEffect(() => {
    if (loaded) saveToStorage(state);
  }, [state, loaded]);

  const update = useCallback(
    (partial: Partial<OnboardingState>) =>
      setState((prev) => ({ ...prev, ...partial })),
    []
  );

  const goToStep = useCallback(
    (step: number) => setState((prev) => ({ ...prev, step })),
    []
  );

  return { state, update, goToStep, loaded };
}
