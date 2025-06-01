import { Column, Entity } from 'typeorm';
import BaseTrackedEntity from './BaseTrackedEntity';

@Entity({ name: 'session' })
export class SessionEntity extends BaseTrackedEntity {
  @Column('text', { nullable: true })
  question: string;

  @Column('int', { nullable: true })
  scale: number;

  @Column('int', { nullable: true })
  response: number;

  @Column('boolean', { default: false, nullable: true })
  skipped: boolean;

  @Column('datetime', { precision: 0 })
  startedAt: Date;

  @Column('datetime', { precision: 0 })
  endedAt: Date;

  @Column('int')
  durationInSeconds: number;
}
