"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { getCatalogData, getBundleFeeds } from "@/actions/feed-catalog";
import { useOnboardingState } from "@/hooks/use-onboarding-state";
import { readingTimeToArticleCount } from "@/lib/reading-time";
import { StepIndicator } from "@/components/step-indicator";
import { DeviceCard } from "@/components/device-card";
import { BundleCard } from "@/components/bundle-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { DEVICES, DELIVERY_TIMES, TIMEZONES } from "@/lib/constants";
import { READING_TIME_OPTIONS } from "@/lib/reading-time";
import type {
  CatalogBundle,
  CatalogCategory,
  CatalogFeed,
  Device,
  DeliveryMethod,
} from "@/types";

const TOTAL_STEPS = 4;

export default function OnboardingPage() {
  const router = useRouter();
  const { state, update, goToStep, loaded } = useOnboardingState();

  // Catalog data loaded from server
  const [bundles, setBundles] = useState<CatalogBundle[]>([]);
  const [categories, setCategories] = useState<CatalogCategory[]>([]);
  const [bundleFeedMap, setBundleFeedMap] = useState<
    Map<string, CatalogFeed[]>
  >(new Map());
  const [selectedBundles, setSelectedBundles] = useState<Set<string>>(
    new Set()
  );

  // Step 2: custom RSS
  const [customUrl, setCustomUrl] = useState("");
  const [customUrlError, setCustomUrlError] = useState<string | null>(null);

  // Step 4: account creation
  const [authMode, setAuthMode] = useState<"google" | "email" | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  // Load catalog on mount
  useEffect(() => {
    getCatalogData().then(({ bundles: b, categories: c }) => {
      setBundles(b);
      setCategories(c);
      // Pre-load bundle feed mappings
      Promise.all(
        b.map(async (bundle) => {
          const feeds = await getBundleFeeds(bundle.name);
          return [bundle.name, feeds] as const;
        })
      ).then((entries) => {
        setBundleFeedMap(new Map(entries));
      });
    });
  }, []);

  // Two-way bundle sync: when feeds change, update which bundles are fully selected
  useEffect(() => {
    if (bundleFeedMap.size === 0) return;
    const feedUrls = new Set(state.feeds.map((f) => f.url));
    const newBundles = new Set<string>();
    for (const [name, feeds] of bundleFeedMap) {
      if (feeds.length > 0 && feeds.every((f) => feedUrls.has(f.url))) {
        newBundles.add(name);
      }
    }
    setSelectedBundles(newBundles);
  }, [state.feeds, bundleFeedMap]);

  if (!loaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-newsprint">
        <p className="font-body text-sm text-caption">Loading...</p>
      </div>
    );
  }

  // --- Helpers ---

  function toggleFeed(feed: { name: string; url: string; category: string }) {
    const exists = state.feeds.some((f) => f.url === feed.url);
    if (exists) {
      update({ feeds: state.feeds.filter((f) => f.url !== feed.url) });
    } else {
      update({ feeds: [...state.feeds, feed] });
    }
  }

  function toggleBundle(bundleName: string) {
    const feeds = bundleFeedMap.get(bundleName);
    if (!feeds) return;

    const isSelected = selectedBundles.has(bundleName);
    if (isSelected) {
      // Remove all bundle feeds
      const bundleUrls = new Set(feeds.map((f) => f.url));
      update({
        feeds: state.feeds.filter((f) => !bundleUrls.has(f.url)),
      });
    } else {
      // Add all bundle feeds that aren't already selected
      const existingUrls = new Set(state.feeds.map((f) => f.url));
      const newFeeds = feeds
        .filter((f) => !existingUrls.has(f.url))
        .map((f) => {
          // Find category for this feed
          const cat = categories.find((c) =>
            c.feeds.some((cf) => cf.url === f.url)
          );
          return { name: f.name, url: f.url, category: cat?.name ?? "" };
        });
      update({ feeds: [...state.feeds, ...newFeeds] });
    }
  }

  function addCustomFeed() {
    setCustomUrlError(null);
    const trimmed = customUrl.trim();
    if (!trimmed) return;
    if (
      !trimmed.startsWith("http://") &&
      !trimmed.startsWith("https://")
    ) {
      setCustomUrlError("URL must start with http:// or https://");
      return;
    }
    if (!trimmed.includes(".")) {
      setCustomUrlError("Please enter a valid URL");
      return;
    }
    if (state.feeds.some((f) => f.url === trimmed)) {
      setCustomUrlError("This feed is already added");
      return;
    }
    update({
      feeds: [
        ...state.feeds,
        { name: trimmed, url: trimmed, category: "Custom" },
      ],
    });
    setCustomUrl("");
  }

  function getDeliveryMethodsForDevice(
    device: Device | null
  ): { value: DeliveryMethod; label: string; description: string }[] {
    switch (device) {
      case "kobo":
        return [
          {
            value: "google_drive",
            label: "Google Drive",
            description: "Auto-sync via Kobo's Google Drive integration",
          },
          {
            value: "local",
            label: "Download",
            description: "Download EPUB and transfer manually",
          },
        ];
      case "kindle":
        return [
          {
            value: "email",
            label: "Send-to-Kindle",
            description: "Deliver via email to your Kindle",
          },
          {
            value: "local",
            label: "Download",
            description: "Download EPUB and transfer via USB",
          },
        ];
      default:
        return [
          {
            value: "local",
            label: "Download",
            description: "Download EPUB and transfer to your device",
          },
          {
            value: "email",
            label: "Email",
            description: "Send EPUB to an email address",
          },
        ];
    }
  }

  async function handleGoogleSignIn() {
    setAuthLoading(true);
    setAuthError(null);
    const supabase = createClient();
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/api/auth/callback?next=/onboarding/complete`,
      },
    });
    if (error) {
      setAuthError(error.message);
      setAuthLoading(false);
    }
    // If successful, browser redirects — no need to handle further
  }

  async function handleEmailSignUp(e: React.FormEvent) {
    e.preventDefault();
    setAuthError(null);

    if (password !== confirmPassword) {
      setAuthError("Passwords do not match");
      return;
    }
    if (password.length < 6) {
      setAuthError("Password must be at least 6 characters");
      return;
    }

    setAuthLoading(true);
    const supabase = createClient();
    const { error } = await supabase.auth.signUp({ email, password });

    if (error) {
      setAuthError(error.message);
      setAuthLoading(false);
    } else {
      router.push("/onboarding/complete");
    }
  }

  // --- Step renderers ---

  function renderStep1() {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-display text-xl font-bold text-ink">
            Choose Your Device
          </h2>
          <p className="mt-1 font-body text-sm text-caption">
            Which e-reader will you use?
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {DEVICES.map((d) => (
            <DeviceCard
              key={d.value}
              device={d.value}
              label={d.label}
              selected={state.device === d.value}
              onClick={() => {
                update({ device: d.value });
                // Set default delivery method for device
                const methods = getDeliveryMethodsForDevice(d.value);
                update({ deliveryMethod: methods[0].value });
              }}
            />
          ))}
        </div>

        {state.device && (
          <p className="text-center font-body text-xs text-caption">
            {DEVICES.find((d) => d.value === state.device)?.description}
          </p>
        )}

        <div className="flex justify-end">
          <Button
            onClick={() => goToStep(2)}
            disabled={!state.device}
            className="bg-ink font-body text-sm font-semibold uppercase tracking-wider text-newsprint hover:bg-ink/90"
          >
            Continue
          </Button>
        </div>
      </div>
    );
  }

  function renderStep2() {
    const feedUrls = new Set(state.feeds.map((f) => f.url));

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-display text-xl font-bold text-ink">
            Pick Your Sources
          </h2>
          <p className="mt-1 font-body text-sm text-caption">
            Start with a bundle or pick individual feeds.
          </p>
        </div>

        {/* Bundles */}
        <div className="space-y-3">
          <h3 className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
            Starter Bundles
          </h3>
          <div className="grid gap-3 sm:grid-cols-3">
            {bundles.map((b) => (
              <BundleCard
                key={b.name}
                name={b.name}
                description={b.description}
                selected={selectedBundles.has(b.name)}
                onClick={() => toggleBundle(b.name)}
              />
            ))}
          </div>
        </div>

        {/* Individual feeds by category */}
        <div className="space-y-4">
          <h3 className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
            Individual Sources
          </h3>
          {categories.map((cat) => (
            <details key={cat.name} className="group">
              <summary className="flex cursor-pointer items-center justify-between rounded-sm border border-rule-gray bg-white px-4 py-2.5 font-body text-sm font-semibold text-ink hover:bg-newsprint">
                <span>{cat.name}</span>
                <span className="text-xs text-caption">
                  {cat.feeds.filter((f) => feedUrls.has(f.url)).length}/
                  {cat.feeds.length}
                </span>
              </summary>
              <div className="mt-1 space-y-1 pl-1">
                {cat.feeds.map((feed) => (
                  <label
                    key={feed.id}
                    className="flex items-start gap-3 rounded-sm px-3 py-2 hover:bg-white"
                  >
                    <Checkbox
                      checked={feedUrls.has(feed.url)}
                      onCheckedChange={() =>
                        toggleFeed({
                          name: feed.name,
                          url: feed.url,
                          category: cat.name,
                        })
                      }
                      className="mt-0.5"
                    />
                    <div>
                      <span className="font-body text-sm font-semibold text-ink">
                        {feed.name}
                      </span>
                      <span className="ml-2 font-body text-xs text-caption">
                        {feed.description}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            </details>
          ))}
        </div>

        {/* Custom RSS */}
        <div className="space-y-2">
          <h3 className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
            Custom RSS Feed
          </h3>
          <div className="flex gap-2">
            <Input
              type="url"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="https://example.com/feed.xml"
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustomFeed())}
            />
            <Button
              type="button"
              onClick={addCustomFeed}
              variant="outline"
              className="shrink-0 font-body text-sm"
            >
              Add
            </Button>
          </div>
          {customUrlError && (
            <p className="font-body text-xs text-edition-red">
              {customUrlError}
            </p>
          )}
        </div>

        {/* Summary */}
        <div className="rounded-sm border border-rule-gray bg-white px-4 py-3">
          <p className="font-body text-sm text-ink">
            <span className="font-semibold">{state.feeds.length}</span>{" "}
            source{state.feeds.length !== 1 ? "s" : ""} selected
          </p>
        </div>

        <div className="flex justify-between">
          <Button
            onClick={() => goToStep(1)}
            variant="outline"
            className="font-body text-sm font-semibold uppercase tracking-wider"
          >
            Back
          </Button>
          <Button
            onClick={() => goToStep(3)}
            disabled={state.feeds.length === 0}
            className="bg-ink font-body text-sm font-semibold uppercase tracking-wider text-newsprint hover:bg-ink/90"
          >
            Continue
          </Button>
        </div>
      </div>
    );
  }

  function renderStep3() {
    const methods = getDeliveryMethodsForDevice(state.device);
    const readingMinutes = Number(state.readingTime) || 15;

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-display text-xl font-bold text-ink">
            Delivery Settings
          </h2>
          <p className="mt-1 font-body text-sm text-caption">
            How and when should your newspaper arrive?
          </p>
        </div>

        {/* Delivery method */}
        <div className="space-y-3">
          <Label className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
            Delivery Method
          </Label>
          <RadioGroup
            value={state.deliveryMethod}
            onValueChange={(v) =>
              update({ deliveryMethod: v as DeliveryMethod })
            }
            className="space-y-2"
          >
            {methods.map((m) => (
              <label
                key={m.value}
                className="flex items-start gap-3 rounded-sm border border-rule-gray bg-white px-4 py-3 hover:border-caption"
              >
                <RadioGroupItem value={m.value} className="mt-0.5" />
                <div>
                  <span className="font-body text-sm font-semibold text-ink">
                    {m.label}
                  </span>
                  <p className="font-body text-xs text-caption">
                    {m.description}
                  </p>
                </div>
              </label>
            ))}
          </RadioGroup>
        </div>

        {/* Kindle email (conditional) */}
        {state.deliveryMethod === "email" && state.device === "kindle" && (
          <div className="space-y-2">
            <Label className="font-body text-sm text-ink">
              Kindle Email Address
            </Label>
            <Input
              type="email"
              value={state.kindleEmail}
              onChange={(e) => update({ kindleEmail: e.target.value })}
              placeholder="your-kindle@kindle.com"
            />
          </div>
        )}

        {/* Schedule */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
              Delivery Time
            </Label>
            <Select
              value={state.deliveryTime}
              onValueChange={(v) => update({ deliveryTime: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DELIVERY_TIMES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
              Timezone
            </Label>
            <Select
              value={state.timezone}
              onValueChange={(v) => update({ timezone: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Newspaper settings */}
        <div className="space-y-4">
          <h3 className="font-headline text-sm font-bold uppercase tracking-wider text-caption">
            Newspaper Settings
          </h3>
          <div className="space-y-2">
            <Label className="font-body text-sm text-ink">
              Newspaper Title
            </Label>
            <Input
              value={state.title}
              onChange={(e) => update({ title: e.target.value })}
              placeholder="The Morning Paper"
            />
          </div>
          <div className="space-y-2">
            <Label className="font-body text-sm text-ink">
              Reading Time:{" "}
              <span className="font-semibold">{readingMinutes} min</span>
              <span className="ml-1 text-xs text-caption">
                (~{readingTimeToArticleCount(readingMinutes)} articles/feed)
              </span>
            </Label>
            <Slider
              value={[
                READING_TIME_OPTIONS.indexOf(readingMinutes) !== -1
                  ? READING_TIME_OPTIONS.indexOf(readingMinutes)
                  : 2,
              ]}
              onValueChange={([i]) => {
                const minutes = READING_TIME_OPTIONS[i];
                update({
                  readingTime: String(minutes),
                  maxArticlesPerFeed: readingTimeToArticleCount(minutes),
                });
              }}
              min={0}
              max={READING_TIME_OPTIONS.length - 1}
              step={1}
            />
          </div>
          <label className="flex items-center gap-3">
            <Checkbox
              checked={state.includeImages}
              onCheckedChange={(checked) =>
                update({ includeImages: checked === true })
              }
            />
            <span className="font-body text-sm text-ink">
              Include images in articles
            </span>
          </label>
        </div>

        <div className="flex justify-between">
          <Button
            onClick={() => goToStep(2)}
            variant="outline"
            className="font-body text-sm font-semibold uppercase tracking-wider"
          >
            Back
          </Button>
          <Button
            onClick={() => goToStep(4)}
            className="bg-ink font-body text-sm font-semibold uppercase tracking-wider text-newsprint hover:bg-ink/90"
          >
            Continue
          </Button>
        </div>
      </div>
    );
  }

  function renderStep4() {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="font-display text-xl font-bold text-ink">
            Create Your Account
          </h2>
          <p className="mt-1 font-body text-sm text-caption">
            A free account lets us save your settings and deliver your newspaper
            automatically each morning.
          </p>
        </div>

        {/* Google sign-in (primary) */}
        <Button
          onClick={handleGoogleSignIn}
          disabled={authLoading}
          className="flex w-full items-center justify-center gap-2 bg-ink font-body text-sm font-semibold text-newsprint hover:bg-ink/90"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          {authLoading ? "Redirecting..." : "Continue with Google"}
        </Button>

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-rule-gray" />
          <span className="font-body text-xs text-caption">or</span>
          <div className="h-px flex-1 bg-rule-gray" />
        </div>

        {/* Email/password form */}
        {authMode !== "email" ? (
          <button
            onClick={() => setAuthMode("email")}
            className="w-full font-body text-sm text-caption underline hover:text-ink"
          >
            Sign up with email and password
          </button>
        ) : (
          <form onSubmit={handleEmailSignUp} className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="ob-email" className="font-body text-sm text-ink">
                Email
              </Label>
              <Input
                id="ob-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                autoComplete="email"
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="ob-password"
                className="font-body text-sm text-ink"
              >
                Password
              </Label>
              <Input
                id="ob-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                required
                autoComplete="new-password"
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="ob-confirm"
                className="font-body text-sm text-ink"
              >
                Confirm Password
              </Label>
              <Input
                id="ob-confirm"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                required
                autoComplete="new-password"
              />
            </div>
            <Button
              type="submit"
              disabled={authLoading}
              className="w-full bg-ink font-body text-sm font-semibold uppercase tracking-wider text-newsprint hover:bg-ink/90"
            >
              {authLoading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
        )}

        {authError && (
          <p className="text-center font-body text-sm text-edition-red">
            {authError}
          </p>
        )}

        <div className="flex justify-start">
          <Button
            onClick={() => goToStep(3)}
            variant="outline"
            className="font-body text-sm font-semibold uppercase tracking-wider"
          >
            Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-newsprint">
      <main className="mx-auto max-w-xl px-6 py-12">
        {/* Masthead */}
        <div className="mb-8 text-center">
          <h1 className="font-display text-2xl font-black uppercase tracking-[0.15em] text-ink">
            Paper Boy
          </h1>
          <div className="mt-4">
            <StepIndicator currentStep={state.step} totalSteps={TOTAL_STEPS} />
          </div>
          <p className="mt-2 font-body text-xs text-caption">
            Step {state.step} of {TOTAL_STEPS}
          </p>
        </div>

        {/* Step content */}
        {state.step === 1 && renderStep1()}
        {state.step === 2 && renderStep2()}
        {state.step === 3 && renderStep3()}
        {state.step === 4 && renderStep4()}
      </main>
    </div>
  );
}
