import pygame
import random
from game_object import GameObject

class Enemy(GameObject):
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__(x, y, (50, 50), (255, 0, 0), random.choice(["up", "down", "left", "right"]), screen_width, screen_height)
        self.speed = 2
        self.directions = ["up", "down", "left", "right"]
        self.collision_time = None  # Track the time of collision with the player
        self.last_move_time = pygame.time.get_ticks()  # Track the last move time
        self.border_offset = 5  # Shrink the border by a bit to avoid corners
        self.avoid_radius = 300  # Radius within which enemies will try to avoid the player
        self.change_direction_time = pygame.time.get_ticks()  # Track the last time direction was changed

    def update(self, player, enemies, obstacles):
        original_position = self.rect.topleft

        # Calculate distance to the player
        distance_to_player = ((self.rect.x - player.rect.x) ** 2 + (self.rect.y - player.rect.y) ** 2) ** 0.5

        if distance_to_player < self.avoid_radius:
            # Move away from the player if within the avoid radius
            if self.rect.x < player.rect.x:
                self.rect.x -= self.speed
                self.direction = "left"
            elif self.rect.x > player.rect.x:
                self.rect.x += self.speed
                self.direction = "right"
            
            if self.rect.y < player.rect.y:
                self.rect.y -= self.speed
                self.direction = "up"
            elif self.rect.y > player.rect.y:
                self.rect.y += self.speed
                self.direction = "down"
        else:
            # Random movement if outside the avoid radius
            current_time = pygame.time.get_ticks()
            if current_time - self.change_direction_time > 2000:  # Change direction every 2 seconds
                new_direction = random.choice(self.directions)
                while new_direction == self.direction:
                    new_direction = random.choice(self.directions)
                self.direction = new_direction
                self.update_image()
                self.change_direction_time = current_time

            if self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "right":
                self.rect.x += self.speed
            elif self.direction == "up":
                self.rect.y -= self.speed
            elif self.direction == "down":
                self.rect.y += self.speed

        # Adjust boundaries to shrink the border by 1/4 of the sprite's size
        if self.rect.left < self.border_offset:
            self.rect.left = self.border_offset
        if self.rect.right > self.screen_width - self.border_offset:
            self.rect.right = self.screen_width - self.border_offset
        if self.rect.top < self.border_offset:
            self.rect.top = self.border_offset
        if self.rect.bottom > self.screen_height - self.border_offset:
            self.rect.bottom = self.screen_height - self.border_offset
        
        # Check for collisions with obstacles and revert to original position if necessary
        if pygame.sprite.spritecollideany(self, obstacles):
            self.rect.topleft = original_position

        # Avoid other enemies
        for enemy in enemies:
            if enemy != self:
                offset = (self.rect.left - enemy.rect.left, self.rect.top - enemy.rect.top)
                collision_point = enemy.mask.overlap(self.mask, offset)
                if collision_point:
                    self.rect.topleft = original_position

                    # Change direction to avoid getting stuck
                    new_direction = random.choice(self.directions)
                    while new_direction == self.direction:
                        new_direction = random.choice(self.directions)
                    self.direction = new_direction
                    self.update_image()

        # Check for collision with the player
        offset = (self.rect.left - player.rect.left, self.rect.top - player.rect.top)
        collision_point = player.mask.overlap(self.mask, offset)
        if collision_point:
            if not self.collision_time:
                self.collision_time = pygame.time.get_ticks()
            else:
                elapsed_time = pygame.time.get_ticks() - self.collision_time
                if elapsed_time > 500:  # Remove enemy after 1 second of collision
                    self.kill()
        else:
            self.collision_time = None

        # Ensure the enemy doesn't stay in the same place for more than half a second
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > 500:
            new_direction = random.choice(self.directions)
            while new_direction == self.direction:
                new_direction = random.choice(self.directions)
            self.direction = new_direction
            self.update_image()
            self.last_move_time = current_time
