export default interface SessionDto {
  id: string;
  question: string;
  scale: number;
  response: number | null;
  skipped: boolean;
  startedAt: Date;
  endedAt: Date;
  durationInSeconds: number;
}
