import { useEffect } from "react";
import { Mic, Camera, Volume2, Navigation } from "lucide-react";
import { Layout } from "@/components/Layout";
import { useVoiceAnnouncement } from "@/hooks/useVoiceAnnouncement";

const steps = [
  {
    icon: Mic,
    title: "Speak Your Request",
    description: "Tell PathFinder AI what you need help with using natural voice commands.",
  },
  {
    icon: Camera,
    title: "Point Your Camera",
    description: "Hold your device toward your surroundings. The camera captures the scene.",
  },
  {
    icon: Volume2,
    title: "Receive Audio Guidance",
    description: "Listen to clear descriptions of objects, text, and obstacles around you.",
  },
  {
    icon: Navigation,
    title: "Navigate Safely",
    description: "Get real-time alerts about obstacles and directions to help you move confidently.",
  },
];

const HowItWorks = () => {
  const { announceOnLoad } = useVoiceAnnouncement();

  useEffect(() => {
    const timer = setTimeout(() => {
      announceOnLoad(
        "How It Works page. PathFinder AI uses voice commands, camera, and audio to help you navigate."
      );
    }, 500);

    return () => clearTimeout(timer);
  }, [announceOnLoad]);

  return (
    <Layout>
      <div
        id="aria-live-region"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />

      <div className="px-6 py-10">
        <header className="mb-10 text-center">
          <h1 className="mb-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How It Works
          </h1>
          <p className="text-lg text-muted-foreground">
            Four simple steps to get started with PathFinder AI.
          </p>
        </header>

        <ol className="mx-auto max-w-lg space-y-6" aria-label="Steps to use PathFinder AI">
          {steps.map((step, index) => (
            <li
              key={step.title}
              className="flex gap-4 rounded-xl bg-card p-5 shadow-sm"
            >
              <div
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/10"
                aria-hidden="true"
              >
                <step.icon className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h2 className="mb-1 text-lg font-semibold text-foreground">
                  <span className="sr-only">Step {index + 1}: </span>
                  {step.title}
                </h2>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </Layout>
  );
};

export default HowItWorks;
