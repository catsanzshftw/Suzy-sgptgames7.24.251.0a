#!/usr/bin/env python3
"""
Pong – Jungle Vibes Edition 🎮🔊🌴
Enhanced for M1 Mac with smooth visuals and DKC-inspired sounds
Right paddle = player, left paddle = AI
60 fps, SDL2 (Pygame 2.x)
Now with Donkey Kong Country menu music!

Usage
-----
$ python3 pong_vibes_sound.py
Keys: ↑/↓ or W/S to move, SPACE to start
Game Over: Y to restart, N to quit, ESC to quit anytime
First to 5 points wins!
"""

import sys
import math
import random
import pygame
import numpy as np

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT = 1200, 675  # 16:9, larger for better experience
FPS = 60
PADDLE_W, PAD_H = 15, 100
BALL_SIZE = 16
PADDLE_SPEED = 550
AI_SPEED = 480
BALL_SPEED_INIT = 500
WIN_SCORE = 5

# Enhanced color palette
NEON_PINK = (255, 0, 128)
NEON_BLUE = (0, 191, 255)
DARK_BG = (10, 10, 15)
WHITE = (255, 255, 255)
SOFT_WHITE = (200, 200, 200)
GRID_COLOR = (30, 30, 40)
JUNGLE_GREEN = (34, 139, 34)
BANANA_YELLOW = (255, 225, 53)

# Audio settings
SAMPLE_RATE = 22050
MASTER_VOLUME = 0.05  # 5% as requested!

# --------------------------------------------------------------------------- #
# Sound Generation                                                            #
# --------------------------------------------------------------------------- #
class MusicNote:
    def __init__(self, frequency, duration, volume=0.5):
        self.frequency = frequency
        self.duration = duration
        self.volume = volume

class RetroSounds:
    def __init__(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)  # More channels for music
        self.sounds = {}
        self.music_channel = pygame.mixer.Channel(15)  # Dedicated music channel
        self.bass_channel = pygame.mixer.Channel(14)   # Bass line channel
        self.generate_all_sounds()
        self.generate_dkc_theme()
        
    def generate_tone(self, frequency, duration, wave_type='square', envelope='sharp'):
        frames = int(duration * SAMPLE_RATE)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = float(i) / SAMPLE_RATE
            
            # Generate base waveform
            if wave_type == 'square':
                arr[i] = np.sign(np.sin(2 * np.pi * frequency * t)) * 0.5
            elif wave_type == 'sine':
                arr[i] = np.sin(2 * np.pi * frequency * t)
            elif wave_type == 'triangle':
                arr[i] = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            elif wave_type == 'noise':
                arr[i] = np.random.random() * 2 - 1
                
            # Apply envelope
            if envelope == 'sharp':
                if i < frames * 0.1:
                    arr[i] *= i / (frames * 0.1)
                elif i > frames * 0.7:
                    arr[i] *= (frames - i) / (frames * 0.3)
            elif envelope == 'pluck':
                arr[i] *= np.exp(-3 * i / frames)
                
        # Add some harmonics for richness
        if wave_type != 'noise':
            arr += np.sin(2 * np.pi * frequency * 2 * np.arange(frames) / SAMPLE_RATE) * 0.1
            arr += np.sin(2 * np.pi * frequency * 0.5 * np.arange(frames) / SAMPLE_RATE) * 0.05
            
        # Normalize and convert to 16-bit
        arr = arr / np.max(np.abs(arr) + 1e-10) * 32767 * MASTER_VOLUME  # Avoid div by zero
        arr = arr.astype(np.int16)
        
        # Make stereo
        stereo = np.zeros((frames, 2), dtype=np.int16)
        stereo[:, 0] = arr
        stereo[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo)
        
    def generate_sweep(self, start_freq, end_freq, duration, wave_type='square'):
        frames = int(duration * SAMPLE_RATE)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = float(i) / SAMPLE_RATE
            # Logarithmic frequency sweep
            freq = start_freq * (end_freq / start_freq) ** (t / duration)
            
            if wave_type == 'square':
                arr[i] = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5
            else:
                arr[i] = np.sin(2 * np.pi * freq * t)
                
            # Envelope
            arr[i] *= np.exp(-2 * t / duration)
            
        # Add some noise for texture
        arr += (np.random.random(frames) - 0.5) * 0.05
        
        # Normalize and convert
        arr = arr / np.max(np.abs(arr) + 1e-10) * 32767 * MASTER_VOLUME
        arr = arr.astype(np.int16)
        
        stereo = np.zeros((frames, 2), dtype=np.int16)
        stereo[:, 0] = arr
        stereo[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo)
        
    def generate_all_sounds(self):
        # Paddle hit sounds - different pitches for variety
        self.sounds['paddle_hit_1'] = self.generate_tone(220, 0.1, 'square', 'sharp')  # A3
        self.sounds['paddle_hit_2'] = self.generate_tone(262, 0.1, 'square', 'sharp')  # C4
        self.sounds['paddle_hit_3'] = self.generate_tone(330, 0.1, 'square', 'sharp')  # E4
        
        # Wall bounce - higher pitched
        self.sounds['wall_bounce'] = self.generate_tone(440, 0.05, 'triangle', 'sharp')  # A4
        
        # Scoring sounds
        self.sounds['player_score'] = self.generate_sweep(800, 1200, 0.3, 'sine')  # Victory sweep up
        self.sounds['ai_score'] = self.generate_sweep(400, 200, 0.3, 'square')  # Defeat sweep down
        
        # Game state sounds
        self.sounds['game_start'] = self.generate_sweep(200, 600, 0.4, 'square')
        self.sounds['game_over_win'] = self.generate_sweep(400, 1000, 0.5, 'sine')
        self.sounds['game_over_lose'] = self.generate_sweep(600, 100, 0.5, 'square')
        
        # Menu beeps
        self.sounds['menu_beep'] = self.generate_tone(523, 0.05, 'sine', 'pluck')  # C5
        
    def generate_dkc_theme(self):
        """Generate DKC Title Screen Theme - Those epic orchestral hits! Incorporated elements from DK Arcade and Beethoven's 5th for variety."""
        # Note frequencies (combined from all versions)
        C2, G2, C3, D3, E3, F3, G3, A3, B3 = 65, 98, 131, 147, 165, 175, 196, 220, 247
        C4, D4, E4, F4, G4, A4, B4 = 262, 294, 330, 349, 392, 440, 494
        C5, D5, E5, Eb4 = 523, 587, 659, 311
        
        # DKC Title Screen - The dramatic orchestral hits when logo appears
        # Incorporated DK Arcade ascending pattern and Beethoven's motif for "jungle vibes"
        melody_notes = [
            # DK Arcade main phrase (ascending/descending)
            MusicNote(C4, 0.2, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(D4, 0.15, 0.7), MusicNote(E4, 0.15, 0.7),
            MusicNote(F4, 0.2, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(D4, 0.15, 0.7), MusicNote(E4, 0.15, 0.7),
            MusicNote(C4, 0.4, 0.9), MusicNote(0, 0.1, 0),
            
            # Beethoven's 5th motif (Cranky's theme)
            MusicNote(G3, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(G3, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(G3, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(Eb4, 0.6, 1.0), MusicNote(0, 0.2, 0),    # DUHHH
            
            MusicNote(F4, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(F4, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(F4, 0.15, 0.8), MusicNote(0, 0.05, 0),   # DUH
            MusicNote(D4, 0.6, 1.0), MusicNote(0, 0.2, 0),     # DUHHH
            
            # DKC orchestral hits
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.4, 1.0), MusicNote(0, 0.3, 0),     # DUH (longer)
            
            # Jungle ambience part (simplified)
            MusicNote(E3, 0.3, 0.4), MusicNote(G3, 0.3, 0.4),
            MusicNote(C4, 0.5, 0.5), MusicNote(0, 0.2, 0),
            
            # Repeat the hits
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.25, 1.0), MusicNote(0, 0.15, 0),   # DUH
            MusicNote(C3, 0.6, 1.0), MusicNote(0, 0.4, 0),     # DUHHH (final)
        ]
        
        # Bass hits for extra impact
        bass_notes = [
            MusicNote(C2, 0.2, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.7), MusicNote(C2, 0.15, 0.7),
            MusicNote(C2, 0.2, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.7), MusicNote(C2, 0.15, 0.7),
            MusicNote(C2, 0.4, 0.9), MusicNote(0, 0.1, 0),
            
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.6, 1.0), MusicNote(0, 0.2, 0),
            
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.15, 0.8), MusicNote(0, 0.05, 0),
            MusicNote(C2, 0.6, 1.0), MusicNote(0, 0.2, 0),
            
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.4, 1.0), MusicNote(0, 0.3, 0),
            
            MusicNote(C2, 0.3, 0.3), MusicNote(G2, 0.3, 0.3),
            MusicNote(C2, 0.5, 0.4), MusicNote(0, 0.2, 0),
            
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.25, 1.0), MusicNote(0, 0.15, 0),
            MusicNote(C2, 0.6, 1.0), MusicNote(0, 0.4, 0),
        ]
        
        # Generate the melody with orchestral hit sound
        melody_frames = []
        for note in melody_notes:
            if note.frequency > 0:
                frames = int(note.duration * SAMPLE_RATE)
                arr = np.zeros(frames)
                
                for i in range(frames):
                    t = float(i) / SAMPLE_RATE
                    # Orchestral hit sound - multiple harmonics
                    arr[i] = np.sin(2 * np.pi * note.frequency * t) * 0.4
                    arr[i] += np.sin(2 * np.pi * note.frequency * 2 * t) * 0.3
                    arr[i] += np.sin(2 * np.pi * note.frequency * 3 * t) * 0.2
                    arr[i] += np.sin(2 * np.pi * note.frequency * 4 * t) * 0.1
                    
                    # Sharp attack for that "hit" feeling
                    if i < frames * 0.02:
                        arr[i] *= i / (frames * 0.02)
                    elif i > frames * 0.1:
                        arr[i] *= np.exp(-3 * (i - frames * 0.1) / frames)
                        
                    # Add some noise for impact
                    if i < frames * 0.05:
                        arr[i] += (np.random.random() - 0.5) * 0.2
                        
                arr *= note.volume * MASTER_VOLUME * 1.5
                melody_frames.extend(arr)
            else:
                # Rest
                melody_frames.extend(np.zeros(int(note.duration * SAMPLE_RATE)))
                
        # Generate the bass hits
        bass_frames = []
        for note in bass_notes:
            if note.frequency > 0:
                frames = int(note.duration * SAMPLE_RATE)
                arr = np.zeros(frames)
                
                for i in range(frames):
                    t = float(i) / SAMPLE_RATE
                    # Deep bass impact
                    arr[i] = np.sin(2 * np.pi * note.frequency * t) * 0.8
                    arr[i] += np.sin(2 * np.pi * note.frequency * 0.5 * t) * 0.4
                    
                    # Very sharp attack
                    if i < frames * 0.01:
                        arr[i] *= i / (frames * 0.01)
                    elif i > frames * 0.05:
                        arr[i] *= np.exp(-5 * (i - frames * 0.05) / frames)
                        
                arr *= note.volume * MASTER_VOLUME * 1.2
                bass_frames.extend(arr)
            else:
                bass_frames.extend(np.zeros(int(note.duration * SAMPLE_RATE)))
                
        # Convert to arrays
        melody_arr = np.array(melody_frames) * 32767
        bass_arr = np.array(bass_frames) * 32767
        
        # Make stereo
        melody_stereo = np.zeros((len(melody_arr), 2), dtype=np.int16)
        melody_stereo[:, 0] = melody_arr.astype(np.int16)
        melody_stereo[:, 1] = melody_arr.astype(np.int16)
        
        bass_stereo = np.zeros((len(bass_arr), 2), dtype=np.int16)
        bass_stereo[:, 0] = bass_arr.astype(np.int16)
        bass_stereo[:, 1] = bass_arr.astype(np.int16)
        
        self.dkc_melody = pygame.sndarray.make_sound(melody_stereo)
        self.dkc_bass = pygame.sndarray.make_sound(bass_stereo)
        
    def play_menu_music(self):
        """Play the DKC theme on loop"""
        if not self.music_channel.get_busy():
            self.music_channel.play(self.dkc_melody, loops=-1)
        if not self.bass_channel.get_busy():
            self.bass_channel.play(self.dkc_bass, loops=-1)
            
    def stop_menu_music(self):
        """Stop the menu music"""
        self.music_channel.fadeout(500)  # Smooth fade
        self.bass_channel.fadeout(500)
        
    def play(self, sound_name):
        if sound_name in self.sounds:
            # Find an available channel and play
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.sounds[sound_name])
            else:
                # If no channels available, force play on channel 0
                pygame.mixer.Channel(0).play(self.sounds[sound_name])
                
    def play_paddle_hit(self):
        # Randomly choose one of the paddle hit sounds for variety
        sound = random.choice(['paddle_hit_1', 'paddle_hit_2', 'paddle_hit_3'])
        self.play(sound)

# --------------------------------------------------------------------------- #
# Visual Effects                                                              #
# --------------------------------------------------------------------------- #
class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, size=3):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = vel_x, vel_y
        self.color = color
        self.size = size
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        
    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.life -= self.decay
        self.vel_y += 200 * dt  # gravity effect
        return self.life > 0
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * self.life)
            size = int(self.size * self.life)
            if size > 0:
                # Glow effect
                for i in range(3):
                    s = pygame.Surface((size * (3-i), size * (3-i)), pygame.SRCALPHA)
                    color = (*self.color, alpha // (i+1))
                    pygame.draw.circle(s, color, (size * (3-i) // 2, size * (3-i) // 2), size * (3-i) // 2)
                    screen.blit(s, (self.x - size * (3-i) // 2, self.y - size * (3-i) // 2))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_burst(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, vel_x, vel_y, color, size))
            
    def add_trail(self, x, y, vel_x, vel_y, color):
        # Add single particle for trail effect
        self.particles.append(Particle(x, y, -vel_x * 0.1, -vel_y * 0.1, color, 4))
        
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

# --------------------------------------------------------------------------- #
# Enhanced Game Classes                                                       #
# --------------------------------------------------------------------------- #
class Paddle:
    def __init__(self, x, color):
        self.rect = pygame.Rect(x, (HEIGHT - PAD_H) // 2, PADDLE_W, PAD_H)
        self.color = color
        self.glow_offset = 0
        self.prev_y = self.rect.y
        
    def move(self, dy):
        self.prev_y = self.rect.y
        self.rect.y = max(0, min(HEIGHT - PAD_H, self.rect.y + dy))
        
    def ai_move(self, target_y, dt):
        center = self.rect.centery
        diff = target_y - center
        if abs(diff) < 5:
            return
            
        # Smoother AI movement
        move_amount = min(abs(diff), AI_SPEED * dt)
        direction = 1 if diff > 0 else -1
        self.move(direction * move_amount)
        
    def draw(self, screen):
        # Animated glow effect
        self.glow_offset = (self.glow_offset + 0.1) % (math.pi * 2)
        glow_size = 3 + math.sin(self.glow_offset) * 1
        
        # Draw glow
        for i in range(3):
            s = pygame.Surface((PADDLE_W + 20 - i*6, PAD_H + 20 - i*6), pygame.SRCALPHA)
            alpha = 40 - i*10
            color = (*self.color, alpha)
            pygame.draw.rect(s, color, (0, 0, s.get_width(), s.get_height()), border_radius=8)
            screen.blit(s, (self.rect.x - 10 + i*3, self.rect.y - 10 + i*3))
            
        # Draw paddle
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        
        # Motion blur effect
        if abs(self.rect.y - self.prev_y) > 2:
            blur_rect = self.rect.copy()
            blur_rect.y = self.prev_y
            s = pygame.Surface((PADDLE_W, PAD_H), pygame.SRCALPHA)
            s.fill((*self.color, 50))
            screen.blit(s, blur_rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect((WIDTH - BALL_SIZE) // 2, (HEIGHT - BALL_SIZE) // 2, BALL_SIZE, BALL_SIZE)
        self.vel = pygame.Vector2(BALL_SPEED_INIT, 0)
        self.vel.rotate_ip(random.uniform(-45, 45))
        self.trail_positions = []
        self.spin = 0
        
    def reset(self, direction):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-30, 30)
        self.vel = pygame.Vector2(BALL_SPEED_INIT * direction, 0)
        self.vel.rotate_ip(angle)
        self.trail_positions = []
        
    def update(self, dt, paddles, particles, sounds):
        # Store trail
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        if len(self.trail_positions) > 10:
            self.trail_positions.pop(0)
            
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt
        
        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.rect.y = max(0, min(self.rect.y, HEIGHT - BALL_SIZE))
            self.vel.y *= -1
            particles.add_burst(self.rect.centerx, self.rect.centery if self.rect.top <= 0 else HEIGHT - self.rect.centery, WHITE, 5)
            sounds.play('wall_bounce')
            
        # Paddle collision
        for pad in paddles:
            if self.rect.colliderect(pad.rect):
                # Position correction
                if self.vel.x < 0:
                    self.rect.left = pad.rect.right
                else:
                    self.rect.right = pad.rect.left
                    
                self.vel.x *= -1
                
                # Add spin based on paddle movement
                paddle_vel = (pad.rect.y - pad.prev_y) / dt if dt > 0 else 0
                self.vel.y += paddle_vel * 0.3
                
                # Speed up slightly
                current_speed = self.vel.length()
                new_speed = min(current_speed * 1.05, 800)
                if current_speed > 0:
                    self.vel.scale_to_length(new_speed)
                
                # Visual feedback
                particles.add_burst(self.rect.centerx, self.rect.centery, pad.color, 8)
                self.spin = paddle_vel * 0.5
                
                # Play paddle hit sound
                sounds.play_paddle_hit()
                
    def draw(self, screen, particles):
        # Trail effect
        for i, pos in enumerate(self.trail_positions):
            alpha = int(255 * (i / len(self.trail_positions)) * 0.3)
            size = int(BALL_SIZE * (i / len(self.trail_positions)))
            if size > 0:
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(s, (*WHITE, alpha), (size//2, size//2), size//2)
                screen.blit(s, (pos[0] - size//2, pos[1] - size//2))
                
        # Glow effect
        for i in range(3):
            s = pygame.Surface((BALL_SIZE + 12 - i*4, BALL_SIZE + 12 - i*4), pygame.SRCALPHA)
            alpha = 60 - i*20
            pygame.draw.circle(s, (*WHITE, alpha), (s.get_width()//2, s.get_height()//2), s.get_width()//2)
            screen.blit(s, (self.rect.x - 6 + i*2, self.rect.y - 6 + i*2))
            
        # Main ball
        pygame.draw.circle(screen, WHITE, self.rect.center, BALL_SIZE // 2)
        
        # Add particle trail
        if abs(self.vel.x) > 100:
            particles.add_trail(self.rect.centerx, self.rect.centery, self.vel.x, self.vel.y, WHITE)

# --------------------------------------------------------------------------- #
# Main Game                                                                   #
# --------------------------------------------------------------------------- #
def draw_background(screen):
    # Gradient background
    for y in range(HEIGHT):
        color_val = int(10 + (y / HEIGHT) * 5)
        pygame.draw.line(screen, (color_val, color_val, color_val + 5), (0, y), (WIDTH, y))
        
    # Grid effect
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong – Jungle Vibes Edition 🌴🔊")
    clock = pygame.time.Clock()
    
    # Initialize sounds
    sounds = RetroSounds()
    
    # Fonts
    font_big = pygame.font.Font(None, 120)
    font_med = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    
    # Game objects
    left_pad = Paddle(50, NEON_BLUE)
    right_pad = Paddle(WIDTH - 50 - PADDLE_W, NEON_PINK)
    ball = Ball()
    particles = ParticleSystem()
    scores = [0, 0]  # [AI, Player]
    game_state = "start"  # start, playing, game_over
    
    # Animation variables
    title_bounce = 0
    flash_alpha = 0
    menu_beep_timer = 0
    music_started = False
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        title_bounce += dt * 3
        menu_beep_timer += dt
        
        # Play menu music
        if game_state == "start" and not music_started:
            sounds.play_menu_music()
            music_started = True
        elif game_state != "start" and music_started:
            sounds.stop_menu_music()
            music_started = False
        
        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game_state == "start":
                        game_state = "playing"
                        scores = [0, 0]
                        ball.reset(1)
                        flash_alpha = 255
                        sounds.play('game_start')
                elif event.key == pygame.K_y:
                    if game_state == "game_over":
                        # Restart game
                        game_state = "playing"
                        scores = [0, 0]
                        ball.reset(1)
                        flash_alpha = 255
                        sounds.play('game_start')
                elif event.key == pygame.K_n:
                    if game_state == "game_over":
                        sounds.play('menu_beep')
                        running = False
                        
        keys = pygame.key.get_pressed()
        if game_state == "playing":
            # Player controls
            dy = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= PADDLE_SPEED * dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += PADDLE_SPEED * dt
            right_pad.move(dy)
                
            # AI movement
            left_pad.ai_move(ball.rect.centery, dt)
            
            # Update ball
            ball.update(dt, (left_pad, right_pad), particles, sounds)
            
            # Scoring
            if ball.rect.right < 0:
                scores[1] += 1  # Player scores
                particles.add_burst(WIDTH // 2, HEIGHT // 2, NEON_PINK, 20)
                ball.reset(-1)
                flash_alpha = 200
                sounds.play('player_score')
            elif ball.rect.left > WIDTH:
                scores[0] += 1  # AI scores
                particles.add_burst(WIDTH // 2, HEIGHT // 2, NEON_BLUE, 20)
                ball.reset(1)
                flash_alpha = 200
                sounds.play('ai_score')
                
            if max(scores) >= WIN_SCORE:
                game_state = "game_over"
                particles.add_burst(WIDTH // 2, HEIGHT // 2, WHITE, 50)
                if scores[1] > scores[0]:
                    sounds.play('game_over_win')
                else:
                    sounds.play('game_over_lose')
                
        # Update particles
        particles.update(dt)
        
        # Rendering
        draw_background(screen)
        
        # Flash effect
        if flash_alpha > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((255, 255, 255, min(flash_alpha, 255)))
            screen.blit(s, (0, 0))
            flash_alpha -= 500 * dt
            
        # Center line
        for y in range(0, HEIGHT, 30):
            pygame.draw.rect(screen, (80, 80, 80), (WIDTH // 2 - 2, y, 4, 20))
            
        # Draw game objects
        if game_state != "start":
            left_pad.draw(screen)
            right_pad.draw(screen)
            ball.draw(screen, particles)
            
        particles.draw(screen)
        
        # Scores
        score_offset = math.sin(title_bounce) * 5
        score1 = font_big.render(str(scores[0]), True, NEON_BLUE)
        score2 = font_big.render(str(scores[1]), True, NEON_PINK)
        screen.blit(score1, (WIDTH // 2 - 120, 50 + score_offset))
        screen.blit(score2, (WIDTH // 2 + 60, 50 + score_offset))
        
        # UI
        if game_state == "start":
            # Add some jungle particles for atmosphere
            if random.random() < 0.05:  # More frequent for vibes
                particles.add_burst(
                    random.randint(100, WIDTH - 100),
                    random.randint(100, HEIGHT - 100),
                    BANANA_YELLOW,
                    3
                )
                
            title_y = HEIGHT // 2 - 100 + math.sin(title_bounce) * 10
            title = font_big.render("PONG", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, title_y))
            
            # Title glow
            for i in range(3):
                s = pygame.Surface((title_rect.width + 40 - i*10, title_rect.height + 40 - i*10), pygame.SRCALPHA)
                s.fill((255, 255, 255, 30 - i*10))
                screen.blit(s, (title_rect.x - 20 + i*5, title_rect.y - 20 + i*5))
            screen.blit(title, title_rect)
            
            subtitle = font_med.render("JUNGLE VIBES EDITION", True, SOFT_WHITE)
            screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, title_y + 80)))
            
            # Add some DKC reference
            cranky_text = font_small.render("♪ DKC Title Screen ♪ - Cranky Kong Approved!", True, (150, 100, 50))
            screen.blit(cranky_text, cranky_text.get_rect(center=(WIDTH // 2, title_y + 120)))
            
            volume_text = font_small.render(f"Volume: {int(MASTER_VOLUME * 100)}%", True, (100, 100, 100))
            screen.blit(volume_text, volume_text.get_rect(center=(WIDTH // 2, title_y + 160)))
            
            prompt = font_small.render("Press SPACE to start", True, SOFT_WHITE)
            alpha = int(abs(math.sin(title_bounce * 0.5)) * 255)
            prompt.set_alpha(alpha)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
            
        elif game_state == "game_over":
            winner = "PLAYER" if scores[1] > scores[0] else "AI"
            color = NEON_PINK if scores[1] > scores[0] else NEON_BLUE
            
            # Game Over text
            game_over_text = font_big.render("GAME OVER!", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            screen.blit(game_over_text, game_over_rect)
            
            # Winner text
            win_text = font_med.render(f"{winner} WINS!", True, color)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Winner text glow
            for i in range(3):
                s = pygame.Surface((win_rect.width + 40 - i*10, win_rect.height + 40 - i*10), pygame.SRCALPHA)
                s.fill((*color, 30 - i*8))
                screen.blit(s, (win_rect.x - 20 + i*5, win_rect.y - 20 + i*5))
            screen.blit(win_text, win_rect)
            
            # Restart prompt
            restart_text = font_med.render("Restart?", True, SOFT_WHITE)
            screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
            
            # Y/N options with flashing effect
            flash_value = int(abs(math.sin(title_bounce * 2)) * 255)
            yes_text = font_small.render("Y = restart", True, JUNGLE_GREEN)
            no_text = font_small.render("N = quit", True, NEON_PINK)
            yes_text.set_alpha(flash_value)
            no_text.set_alpha(flash_value)
            screen.blit(yes_text, yes_text.get_rect(center=(WIDTH // 2 - 100, HEIGHT // 2 + 130)))
            screen.blit(no_text, no_text.get_rect(center=(WIDTH // 2 + 100, HEIGHT // 2 + 130)))
            
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit()
