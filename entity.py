####################
# TICK / LIFECYCLE #
####################
# Every tick the entity moves with self.vel_x and self.vel_y on the x and y axis accordingly.
# As, just staying alive even if not moving at all, burns energy as well, every tick 0.01% of
# self.max_stamina is used. If moving, 0.003 stamina points are used per health point, so
# entities with more health are not in complete advantage, per velocity squared, so moving
# does us up energy and reaching longer distances faster does use up more energy in total,
# than moving slowly. And finally, if the stamina is above 60%, 0.8% of self.max_health are
# healed per tick, in exchange for 1.25 times the stamina points.

from math import sqrt

class Entity:
    age = 0
    generation = 0
    sex = 0         # 0 male, 1 female
    alive = False


    pos_x = 0.0
    pos_y = 0.0
    vel_x = 0.0
    vel_y = 0.0
    velocity = 0.0

    health = 100.0
    stamina = 80.0
    max_health = 100.0
    max_stamina = 100.0

    healing_rate = 0.008
    healing_cost = 1.25

    idle_cost = 0.01
    moving_cost = 0.03

    def spawn(self):
        self.alive = True
        self.health = self.max_health
        self.stamina = self.max_stamina


    def bear(self, parent0, parent1):
        if parent0.sex == parent1.sex:
            self.kill()

        if parent0.sex == 1:
            self.pos_x = parent0.pos_x
            self.pos_y = parent0.pos_y
        else:
            self.pos_x = parent1.pos_x
            self.pos_y = parent1.pos_y

        self.generation = max(parent0.generation, parent1.generation) + 1
        ratio = random.random()

        self.vel_x = 0
        self.vel_y = 0

        mu_health = parent0.max_health * ratio + parent1.max_health * (1-ratio)
        sigma_health = sqrt((parent0.max_health * ratio - mu_health) ** 2 + (parent1.max_health * (1-ratio) - mu_health) ** 2)
        self.max_health = abs(np.random.normal(mu_health, sigma_health))

        mu_stamina = parent0.max_stamina * ratio + parent1.max_stamina * (1-ratio)
        sigma_stamina = sqrt((parent0.max_stamina * ratio - mu_stamina) ** 2 + (parent1.max_stamina * (1-ratio) - mu_stamina) ** 2)
        self.max_stamina = abs(np.random.normal(mu_stamina, sigma_stamina))

        self.health = self.max_health
        self.stamina = self.max_stamina
        alive = True
        

    def kill(self):
       self.health = 0 
       self.velocity = 0
       alive = False


    def tick(self):
        age++
        self.velocity = sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # Idle stamina burning
        self.stamina -= self.idle_cost * self.max_stamina

        # Moving stamina burning
        self.stamina -= self.moving_cost * self.max_health * self.velocity * self.velocity

        # Healing
        if self.stamina > 0.6 * self.max_stamina && self.health < self.max_health:
            # check if one healing step would heal above max_health
            if self.max_health - self.health < self.healing_rate * self.max_health:
                self.stamina -= (self.max_stamina - self.stamina) * self.healing_cost
                self.health = self.max_health
            else:
                self.stamina -= self.healing_cost * self.healing_rate * self.max_health
                self.health  += self.healing_rate * self.max_health


