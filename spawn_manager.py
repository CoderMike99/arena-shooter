from sprites.enemy import Enemy, Chaser, Shooter, Seeker
from settings import *
import random

# Defines spawning and spawning rules for all enemies
class SpawnManager:
    def __init__(self):
        self.current_difficulty = 1
        self.timers = {"Chaser": 0,
                       "Shooter": 0,
                       "Seeker": 0
                       }
        self.intervals = {"Chaser": CHASER_INITIAL_SPAWN_INTERVAL,
                          "Shooter": SHOOTER_INITIAL_SPAWN_INTERVAL,
                          "Seeker": SEEKER_INITIAL_SPAWN_INTERVAL}
        
        self.spawnrules = {"Chaser": False,
                          "Shooter": False,
                          "Seeker": True}

    def update(self) -> list[Enemy]:
        self.current_difficulty += 0.001
        new_enemies = []

        for enemy_type in self.timers:
            self.timers[enemy_type] += 1
            if self.timers[enemy_type] >= self.intervals[enemy_type] and self.spawnrules[enemy_type]:
                self.timers[enemy_type] = 0
                match enemy_type:
                    case "Chaser":
                        new_enemies.append(Chaser())
                        self.randomize_spawn_interval("Chaser")
                    case "Shooter":
                        new_enemies.append(Shooter())
                        self.randomize_spawn_interval("Shooter")
                    case "Seeker":
                        new_enemies.append(Seeker())
                        self.randomize_spawn_interval("Seeker")

        return new_enemies

    # Spawning Rules of each enemy -> oder lieber ausgelagert auf die jeweiligen klassen
    def randomize_spawn_interval(self, enemy):
        match enemy:
            case "Chaser":
                self.intervals["Chaser"] = random.randint(CHASER_MINIMAL_SPAWN_INTERVAL, 
                                                          max(CHASER_MINIMAL_SPAWN_INTERVAL, int(CHASER_INITIAL_SPAWN_INTERVAL - self.current_difficulty)))

            case "Shooter":
                self.intervals["Shooter"] = random.randint(SHOOTER_MINIMAL_SPAWN_INTERVAL,
                                                           max(SHOOTER_MINIMAL_SPAWN_INTERVAL, int(SHOOTER_INITIAL_SPAWN_INTERVAL - self.current_difficulty * 10)))
            
            case "Seeker":
                self.intervals["Seeker"] = random.randint(SEEKER_MINIMAL_SPAWN_INTERVAL,
                                                           max(SEEKER_MINIMAL_SPAWN_INTERVAL, int(SEEKER_INITIAL_SPAWN_INTERVAL - self.current_difficulty * 10)))
            


            case default:
                pass

    def getDifficulty(self):
        return self.current_difficulty