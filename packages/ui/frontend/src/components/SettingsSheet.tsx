import { Settings } from "lucide-react";

import type { AppStatus } from "../types";
import { Button } from "./Button";
import { OptionRow } from "./Home";
import { ModelFolder } from "./ModelsSheet";
import { Sheet } from "./Sheet";
import { Switch } from "./Switch";

interface SettingsSheetProps {
  open: boolean;
  /** Null until Python has described the installation. */
  status: AppStatus | null;
  /** A setting is being stored; its control waits. */
  saving: boolean;
  /** A model is downloading, so the folder cannot change. */
  downloading: boolean;
  onLeakCheck: (enabled: boolean) => void;
  onChangeFolder: () => void;
  onModels: () => void;
  onClose: () => void;
}

/** Preferences kept between runs, in the settings file; nothing about any document. */
export function SettingsSheet({
  open,
  status,
  saving,
  downloading,
  onLeakCheck,
  onChangeFolder,
  onModels,
  onClose,
}: SettingsSheetProps) {
  const leakCheck = status?.settings.leak_check ?? true;
  return (
    <Sheet
      open={open}
      title="Settings"
      size="wide"
      icon={<Settings size={28} />}
      onClose={onClose}
      actions={
        <Button data-default onClick={onClose}>
          Done
        </Button>
      }
    >
      <section className="settings-section" aria-label="Export">
        <h3 className="options-title">Export</h3>
        <div className="options-card">
          <OptionRow
            label="Check the copy for leaks"
            note={
              leakCheck
                ? "Before saving, the redacted copy is searched for what you redacted, and scans are read again with OCR. If something turns up, you decide whether to save."
                : "The copy is saved as redaction made it, without searching it. Exports are faster, and nothing warns you about text left in the copy."
            }
          >
            <Switch
              checked={leakCheck}
              disabled={status === null || saving}
              tone="setting"
              label="Check the redacted copy for leaks before saving it"
              onChange={onLeakCheck}
            />
          </OptionRow>
        </div>
      </section>
      <section className="settings-section" aria-label="Models">
        <h3 className="options-title">Models</h3>
        {status && (
          <ModelFolder folder={status.models_folder} downloading={downloading} onChange={onChangeFolder} />
        )}
        <Button variant="plain" onClick={onModels}>
          Manage models…
        </Button>
      </section>
    </Sheet>
  );
}
