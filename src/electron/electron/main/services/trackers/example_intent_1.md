The domain is software development. I want you to output a prompt that I can feed an LLM.
This example shows the input and the expected output. What is missing is the prompt to tell the LLM what to do.

### TASK
Output a prompt that can be given to a generative AI / LLM. DO NOT OUTPUT THE CONTEXT OR THE EXPECTED RESULT, THESE ARE ONLY EXAMPLES.

### INPUT
```
computer context:
  architecture: x64
  operating system: macOS 23.5.0
ide context:
  TODOs:
    - 'src/electron/electron/main/services/trackers/ExperienceSamplingTracker.ts: // TODO: Implement logic to determine if we should sample'
  all git diffs:
    - |
      diff --git a/src/electron/electron/main/services/trackers/ExperienceSamplingTracker.ts b/src/electron/electron/main/services/trackers/ExperienceSamplingTracker.ts
      index f73adbf..c3aea12 100644
      --- a/src/electron/electron/main/services/trackers/ExperienceSamplingTracker.ts
      +++ b/src/electron/electron/main/services/trackers/ExperienceSamplingTracker.ts
      @@ -110,6 +110,12 @@ export class ExperienceSamplingTracker implements Tracker {
           await this.startExperienceSamplingJob();
         }

      +  private shouldSample(): boolean {
      +    // TODO: Implement logic to determine if we should sample
      +    // For now, we always sample
      +    return true;
      +  }
      +
         private getRandomNextInvocationDate(): Date {
           const subtractOrAdd: 1 | -1 = Math.random() < 0.5 ? -1 : 1;
           const randomization =
    - ''
  current branch: main
  last commit message: Update README.md
  open files:
    - /Users/alex/code/PersonalAnalytics/benchmark.md (markdown)
  project name: PersonalAnalytics
```

### EXPECTED RESULT
```
{
    "goal": "Implement experience sampling logic",
    "summary": "Develop logic to determine when a sample should be taken for experience sampling",
    "confidence": 95.00,
    "rationale": "There is a TODO comment within the ExperienceSamplingTracker source file, suggesting an incomplete implementation of sampling logic."
}
```
