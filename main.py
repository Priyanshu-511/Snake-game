import pygame
import random
import math
import os
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT =500
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (147, 112, 219)
DEEP_PURPLE = (72, 61, 139)
PINK = (255, 20, 147)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
DARK_BLUE = (25, 25, 112)
LIGHT_BLUE = (173, 216, 230)
NEON_GREEN = (57, 255, 20)
ORANGE = (255, 165, 0)

# Fonts
font_large = pygame.font.SysFont("arial", 36, bold=True)
font_medium = pygame.font.SysFont("arial", 24)
font_small = pygame.font.SysFont("arial", 18)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("🐍 Beautiful Snake Game")
clock = pygame.time.Clock()

# Animation variables
time = 0

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.size = random.randint(2, 8)
        self.color = color or random.choice([CYAN, PINK, GOLD, PURPLE])
        self.life = random.randint(30, 60)
        self.max_life = self.life
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.98  # Slow down over time
        self.vy *= 0.98
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
            surface.blit(particle_surf, (self.x - self.size, self.y - self.size))

class BackgroundEffect:
    def __init__(self):
        self.waves = []
        for _ in range(20):
            self.waves.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'radius': random.randint(50, 150),
                'speed': random.uniform(0.001, 0.003),
                'color': random.choice([DEEP_PURPLE, DARK_BLUE, (50, 50, 100)])
            })
    
    def update_and_draw(self, surface, time):
        # Draw gradient background
        for y in range(0, WINDOW_HEIGHT, 4):
            ratio = y / WINDOW_HEIGHT
            wave = math.sin(time * 0.001 + ratio * 3) * 0.2
            r = int(15 + (35 - 15) * (ratio + wave))
            g = int(15 + (25 - 15) * (ratio + wave))
            b = int(40 + (80 - 40) * ratio)
            pygame.draw.rect(surface, (r, g, b), (0, y, WINDOW_WIDTH, 4))
        
        # Draw animated waves
        for wave in self.waves:
            wave['radius'] += math.sin(time * wave['speed']) * 0.5
            alpha = int(30 + 20 * math.sin(time * wave['speed'] * 2))
            
            wave_surf = pygame.Surface((wave['radius'] * 2, wave['radius'] * 2), pygame.SRCALPHA)
            color_with_alpha = (*wave['color'], alpha)
            pygame.draw.circle(wave_surf, color_with_alpha, 
                             (int(wave['radius']), int(wave['radius'])), 
                             int(wave['radius']), 2)
            surface.blit(wave_surf, (wave['x'] - wave['radius'], wave['y'] - wave['radius']))

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow_pending = 0
        
    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        self.body.insert(0, new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
    
    def grow(self, particles):
        self.grow_pending += 1
        # Create particles at the tail
        if self.body:
            tail_x, tail_y = self.body[-1]
            for _ in range(5):
                particles.append(Particle(tail_x * GRID_SIZE + GRID_SIZE//2, 
                                        tail_y * GRID_SIZE + GRID_SIZE//2, 
                                        NEON_GREEN))
    
    def check_collision(self):
        head_x, head_y = self.body[0]
        
        # Wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Self collision
        if (head_x, head_y) in self.body[1:]:
            return True
        
        return False
    
    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            if i == 0:  # Head
                # Draw glowing head
                glow_surf = pygame.Surface((GRID_SIZE + 8, GRID_SIZE + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*NEON_GREEN, 100), (0, 0, GRID_SIZE + 8, GRID_SIZE + 8), border_radius=8)
                surface.blit(glow_surf, (rect.x - 4, rect.y - 4))
                
                pygame.draw.rect(surface, NEON_GREEN, rect, border_radius=6)
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
                
                # Eyes
                eye_size = 4
                pygame.draw.circle(surface, WHITE, (rect.x + 6, rect.y + 6), eye_size)
                pygame.draw.circle(surface, WHITE, (rect.x + 14, rect.y + 6), eye_size)
                pygame.draw.circle(surface, BLACK, (rect.x + 6, rect.y + 6), eye_size - 1)
                pygame.draw.circle(surface, BLACK, (rect.x + 14, rect.y + 6), eye_size - 1)
            else:  # Body
                # Gradient effect for body segments
                intensity = max(100, 255 - i * 10)
                body_color = (0, intensity, 0)
                pygame.draw.rect(surface, body_color, rect, border_radius=4)
                pygame.draw.rect(surface, (0, 200, 0), rect, 1, border_radius=4)

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.pulse = 0
        
    def generate_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        # Pulsing effect
        self.pulse += 0.2
        pulse_size = int(3 * math.sin(self.pulse))
        
        # Glow effect
        glow_surf = pygame.Surface((GRID_SIZE + 16, GRID_SIZE + 16), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*RED, 80), (GRID_SIZE//2 + 8, GRID_SIZE//2 + 8), GRID_SIZE//2 + 8)
        surface.blit(glow_surf, (rect.x - 8, rect.y - 8))
        
        # Food
        pygame.draw.circle(surface, RED, rect.center, GRID_SIZE//2 + pulse_size)
        pygame.draw.circle(surface, ORANGE, rect.center, GRID_SIZE//2 + pulse_size - 2)
        pygame.draw.circle(surface, GOLD, rect.center, GRID_SIZE//4)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.background = BackgroundEffect()
        self.particles = []  # Manage particles as class attribute
        
        # Try to load music
        self.music_loaded = False
        music_path = "snake_finale.mp3"
        if not os.path.exists(music_path):
            music_path = os.path.join("Snake", "snake_finale.mp3")
        if not os.path.exists(music_path):
            music_path = os.path.join("..", "snake_finale.mp3")
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                self.music_loaded = True
            except:
                self.music_loaded = False
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.game_over:
            if keys[pygame.K_UP] and self.snake.direction != (0, 1):
                self.snake.direction = (0, -1)
            elif keys[pygame.K_DOWN] and self.snake.direction != (0, -1):
                self.snake.direction = (0, 1)
            elif keys[pygame.K_LEFT] and self.snake.direction != (1, 0):
                self.snake.direction = (-1, 0)
            elif keys[pygame.K_RIGHT] and self.snake.direction != (-1, 0):
                self.snake.direction = (1, 0)
    
    def update(self):
        if not self.game_over and not self.paused:
            self.snake.move()
            
            # Check food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow(self.particles)  # Pass particles to grow method
                self.score += 10
                self.food = Food()
                
                # Create explosion particles
                food_x, food_y = self.food.position
                for _ in range(15):
                    self.particles.append(Particle(food_x * GRID_SIZE + GRID_SIZE//2, 
                                                 food_y * GRID_SIZE + GRID_SIZE//2, 
                                                 random.choice([RED, ORANGE, GOLD])))
            
            # Check collisions
            if self.snake.check_collision():
                self.game_over = True
                # Create death explosion
                head_x, head_y = self.snake.body[0]
                for _ in range(30):
                    self.particles.append(Particle(head_x * GRID_SIZE + GRID_SIZE//2, 
                                                 head_y * GRID_SIZE + GRID_SIZE//2, 
                                                 random.choice([RED, WHITE, ORANGE])))
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self, surface):
        global time
        
        # Draw animated background
        self.background.update_and_draw(surface, time)
        
        # Draw grid (subtle)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(surface, (40, 40, 60), (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(surface, (40, 40, 60), (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw game objects
        if not self.game_over:
            self.food.draw(surface)
        self.snake.draw(surface)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
        
        # Draw UI
        self.draw_ui(surface)
    
    def draw_ui(self, surface):
        # Score
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, 10)
        
        # Background for score
        score_bg = pygame.Surface((score_rect.width + 20, score_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(score_bg, (0, 0, 0, 150), (0, 0, score_rect.width + 20, score_rect.height + 10), border_radius=10)
        surface.blit(score_bg, (score_rect.x - 10, score_rect.y - 5))
        surface.blit(score_text, score_rect)
        
        # Instructions
        if not self.game_over:
            instructions = [
                "Use Arrow Keys to Move",
                "SPACE - Pause/Resume",
                "ESC - Quit"
            ]
        else:
            instructions = [
                "GAME OVER!",
                f"Final Score: {self.score}",
                "R - Restart",
                "ESC - Quit"
            ]
        
        for i, instruction in enumerate(instructions):
            color = GOLD if instruction == "GAME OVER!" else WHITE
            if instruction == f"Final Score: {self.score}":
                color = CYAN
            
            text = font_small.render(instruction, True, color)
            text_rect = text.get_rect()
            text_rect.topright = (WINDOW_WIDTH - 10, 10 + i * 25)
            
            # Background
            bg = pygame.Surface((text_rect.width + 20, text_rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(bg, (0, 0, 0, 150), (0, 0, text_rect.width + 20, text_rect.height + 6), border_radius=8)
            surface.blit(bg, (text_rect.x - 10, text_rect.y - 3))
            surface.blit(text, text_rect)
        
        # Music status
        if self.music_loaded:
            music_text = font_small.render("♪ Music Playing", True, CYAN)
        else:
            music_text = font_small.render("♪ No Music", True, (100, 100, 100))
        
        music_rect = music_text.get_rect()
        music_rect.bottomleft = (10, WINDOW_HEIGHT - 10)
        
        music_bg = pygame.Surface((music_rect.width + 16, music_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(music_bg, (0, 0, 0, 120), (0, 0, music_rect.width + 16, music_rect.height + 6), border_radius=6)
        surface.blit(music_bg, (music_rect.x - 8, music_rect.y - 3))
        surface.blit(music_text, music_rect)
        
        # Pause overlay
        if self.paused and not self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            surface.blit(overlay, (0, 0))
            
            pause_text = font_large.render("PAUSED", True, GOLD)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(pause_text, pause_rect)
    
    def restart(self):
        self.__init__()

def main():
    global time
    game = Game()
    running = True
    
    while running:
        time += clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game.game_over:
                    game.paused = not game.paused
                elif event.key == pygame.K_r and game.game_over:
                    game.restart()
        
        # Handle continuous input
        game.handle_input()
        
        # Update game
        game.update()
        
        # Draw everything
        game.draw(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()