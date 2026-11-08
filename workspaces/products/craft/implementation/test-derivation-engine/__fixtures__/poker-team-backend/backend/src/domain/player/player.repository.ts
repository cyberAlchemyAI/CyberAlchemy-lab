import { CreatePlayerInput, Player } from "./player.entity";

export type PlayerRepository = {
  create(player: CreatePlayerInput): Promise<Player>;
  findById(id: string): Promise<Player | null>;
  findAll(): Promise<Player[]>;
  update(id: string, data: Partial<Omit<Player, "id" | "createdAt">>): Promise<Player>;
};
