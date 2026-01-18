import { useEffect } from "react";
import { Eye, Keyboard, Volume2, ZoomIn } from "lucide-react";
import { Layout } from "@/components/Layout";
import { useVoiceAnnouncement } from "@/hooks/useVoiceAnnouncement";
const features = [{
  icon: Volume2,
  title: "Voice-First Design",
  description: "All features are accessible through voice commands. Speak naturally to interact."
}, {
  icon: Eye,
  title: "Screen Reader Support",
  description: "Full compatibility with VoiceOver, TalkBack, and other screen readers."
}, {
  icon: Keyboard,
  title: "Keyboard Navigation",
  description: "Navigate the entire app using only your keyboard with clear focus indicators."
}, {
  icon: ZoomIn,
  title: "Large Touch Targets",
  description: "All buttons and controls are sized for easy tapping with clear visual feedback."
}];
const Accessibility = () => {
  const {
    announceOnLoad
  } = useVoiceAnnouncement();
  useEffect(() => {
    const timer = setTimeout(() => {
      announceOnLoad("Accessibility features page. PathFinder AI is designed for voice-first interaction and full screen reader support.");
    }, 500);
    return () => clearTimeout(timer);
  }, [announceOnLoad]);
  return <Layout>
      <div id="aria-live-region" role="status" aria-live="polite" aria-atomic="true" className="sr-only" />

      <div className="px-6 py-10 pb-8">
        <header className="mb-10 text-center">
          <h1 className="mb-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Accessibility
          </h1>
          <p className="text-lg text-muted-foreground">
            Built from the ground up for visually impaired users.
          </p>
        </header>

        <ul className="mx-auto max-w-lg space-y-6" aria-label="Accessibility features">
          {features.map(feature => <li key={feature.title} className="flex gap-4 rounded-xl bg-card p-5 shadow-sm">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/10" aria-hidden="true">
                <feature.icon className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h2 className="mb-1 text-lg font-semibold text-foreground">
                  {feature.title}
                </h2>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </li>)}
        </ul>

        <section className="mx-auto mt-10 max-w-lg rounded-xl p-6 bg-primary">
          <h2 className="mb-2 text-lg font-semibold text-primary-foreground">
            Need Assistance?
          </h2>
          <p className="text-primary-foreground/90">
            Say "Help" at any time for voice guidance, or use keyboard shortcuts to navigate quickly.
          </p>
        </section>
      </div>
    </Layout>;
};
export default Accessibility;