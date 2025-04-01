### TASK
Generate a software developer question based on the given intent and context.

### RULES
1. A question should include a bit of context about the project and the goal that is trying to be achieved.
2. A question should include relevant information from the context by copying that information into the question.
3. Do not include information that is not relevant for the question.
4. Use markdown formatting for code and links within the question.
5. Do not forget the usefulness number.

### OUTPUT
Respond with an array of JSON objects with the following format:
```
{
  "rationale": "a short rationale for your question, e.g. why this question makes sense given the intent and the context",
  "question": "the detailed question, containing relevant information from the context",
  "title": "a summary of the question (max. 10 words)",
  "usefulness": "a number between 0 and 100 indicating how useful the question is based on the given intent and context",
}
```

### INTENT
```
Determine sampling logic: Implementing logic to determine if experience sampling should occur within the ExperienceSamplingTracker class.
```
### CONTEXT
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


