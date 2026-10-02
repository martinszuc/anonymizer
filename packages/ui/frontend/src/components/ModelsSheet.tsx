import { Download, PackageX } from "lucide-react";

import { formatBytes } from "../review";
import type { DownloadProgress, FeatureModels } from "../types";
import { Button } from "./Button";
import { Sheet } from "./Sheet";

interface ModelsSheetProps {
  open: boolean;
  /** Null while loading. */
  features: FeatureModels[] | null;
  /** Running downloads by feature; features sharing no model download side by side. */
  downloads: Record<string, DownloadProgress>;
  onDownload: (feature: string) => void;
  onClose: () => void;
}

/**
 * The models each feature needs, where they come from and their licences, with
 * a download per feature. Files come from each model's official source and are
 * checked against the catalog's checksum before they are kept.
 */
export function ModelsSheet({ open, features, downloads, onDownload, onClose }: ModelsSheetProps) {
  return (
    <Sheet
      open={open}
      title="Models"
      size="wide"
      icon={<Download size={28} />}
      onClose={onClose}
      actions={
        <Button data-default onClick={onClose}>
          Done
        </Button>
      }
    >
      <p>
        Downloaded only when you ask, from each model&apos;s official source, and checked against a
        stored checksum. After that everything runs on this computer.
      </p>
      {features === null ? (
        <p>Checking…</p>
      ) : (
        features.map((feature) => (
          <FeatureSection
            key={feature.feature}
            feature={feature}
            progress={downloads[feature.feature] ?? null}
            onDownload={() => onDownload(feature.feature)}
          />
        ))
      )}
    </Sheet>
  );
}

function FeatureSection({
  feature,
  progress,
  onDownload,
}: {
  feature: FeatureModels;
  progress: DownloadProgress | null;
  onDownload: () => void;
}) {
  const stored = feature.missing_bytes === 0;
  return (
    <section className="model-feature" aria-label={feature.title}>
      <header className="model-feature-header">
        <span className="model-feature-title">{feature.title}</span>
        <span className="model-feature-state" data-ready={stored && feature.installed}>
          {stored ? (feature.installed ? "Ready" : "Downloaded") : "Not downloaded"}
        </span>
      </header>
      <ul className="model-list">
        {feature.models.map((model) => (
          <li key={model.id} className="model-row">
            <span className="model-name">{model.name}</span>
            <span className="model-meta">
              {formatBytes(model.size)} · {model.licence} · {model.languages.join(", ")} ·{" "}
              {new URL(model.source).host}
              {model.state !== "present" && <> · {model.state === "partial" ? "incomplete" : "missing"}</>}
            </span>
          </li>
        ))}
      </ul>
      {!feature.installed && (
        <p className="model-install">
          <PackageX size={14} aria-hidden />
          <span>
            Its Python package is not installed. In a terminal: <code>{feature.install_command}</code>
          </span>
        </p>
      )}
      {progress ? (
        <div className="model-progress" role="progressbar" aria-valuemin={0} aria-valuemax={progress.total} aria-valuenow={progress.received}>
          <div className="model-progress-track">
            <div
              className="model-progress-fill"
              style={{ width: `${progress.total ? (100 * progress.received) / progress.total : 100}%` }}
            />
          </div>
          <span className="model-meta">
            {formatBytes(progress.received)} of {formatBytes(progress.total)}, then checked
          </span>
        </div>
      ) : (
        !stored && (
          <Button variant="primary" onClick={onDownload}>
            Download {formatBytes(feature.missing_bytes)}
          </Button>
        )
      )}
    </section>
  );
}
