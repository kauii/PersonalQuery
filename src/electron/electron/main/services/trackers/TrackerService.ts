import { Tracker } from './Tracker';
import { TrackerConfig } from '../../../types/StudyConfig';
import { TrackerType } from '../../../enums/TrackerType.enum';
import { getLogger } from '../../../shared/Logger';

const LOG = getLogger('TrackerService');

export class TrackerService {
  private trackers: Tracker[] = [];
  private readonly config: TrackerConfig;

  constructor(trackerConfig: TrackerConfig) {
    this.config = trackerConfig;
    LOG.debug(`TrackerService.constructor: config=${JSON.stringify(this.config)}`);
  }

  public async registerTrackerCallback(
    trackerType: TrackerType,
    callback: (data: unknown) => void
  ): Promise<void> {
    if (this.isTrackerAlreadyRegistered(trackerType)) {
      throw new Error(`Tracker ${trackerType} already registered!`);
    }
    LOG.info(`Registering tracker ${trackerType}...`);

    if (
      this.config.windowActivityTracker.enabled &&
      trackerType === TrackerType.WindowsActivityTracker
    ) {
      // Used for getting URLs
      const accessibilityPermission = false;
      // Used for getting window titles
      const screenRecordingPermission = true;
      const WAT = await import('windows-activity-tracker');
      const userInputTracker = new WAT.WindowsActivityTracker(
        callback,
        this.config.windowActivityTracker.intervalInMs,
        accessibilityPermission,
        screenRecordingPermission
      );
      this.trackers.push(userInputTracker);
    } else if (
      this.config.userInputTracker.enabled &&
      trackerType === TrackerType.UserInputTracker
    ) {
      const UIT = await import('user-input-tracker');
      const userInputTracker = new UIT.UserInputTracker(
        callback,
        this.config.userInputTracker.intervalInMs
      );
      this.trackers.push(userInputTracker);
    } else {
      throw new Error(`Tracker ${trackerType} not enabled or unsupported!`);
    }
  }

  public async startAllTrackers() {
    await Promise.all(
      this.trackers.filter((t: Tracker) => !t.isRunning).map((t: Tracker) => t.start())
    );
  }

  public async stopAllTrackers() {
    await Promise.all(
      this.trackers.filter((t: Tracker) => t.isRunning).map((t: Tracker) => t.stop())
    );
  }

  public getRunningTrackerNames() {
    return this.trackers.filter((t: Tracker) => t.isRunning).map((t: Tracker) => t.name);
  }

  public isAnyTrackerRunning() {
    return this.trackers.some((t: Tracker) => t.isRunning);
  }

  private isTrackerAlreadyRegistered(trackerType: TrackerType) {
    return this.trackers.some((t: Tracker) => t.name === trackerType);
  }
}
