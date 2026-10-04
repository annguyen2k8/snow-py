from typing import Tuple, Union

import pygame
from pygame import Surface, Rect, Vector2
from pygame.locals import QUIT, BLEND_RGB_ADD

import argparse
import random


class SnowParticle(pygame.sprite.Sprite):
    containers: Union[Tuple[pygame.sprite.Group], pygame.sprite.Group]
    
    def __init__(
        self, screen: Surface, image: Surface, 
        wind: float, 
        speed: float, 
        border: Vector2
        ):
        
        super().__init__(self.containers)
        
        self.screen = screen
        self.image = image
        
        self.wind = wind
        
        self.speed = speed
        if speed < 0:
            self.speed = 1
        
        
        self.border = border
        
        self.pos = Vector2(
            random.uniform(
                0 - border.x,
                screen.get_width() + border.x
                ),
            -border.y
        )
    
    def update(self, dt: float) -> None:
        self.pos += (dt * self.wind, dt * self.speed)
        
        if (
            self.pos.y > self.screen.get_height() or
            (self.wind < 0 and self.pos.x < 0) or 
            (self.wind > 0 and self.pos.x > self.screen.get_width())
            ):
            
            self.kill() 
        
        if self.image:
            self.rect = self.image.get_rect().move(self.pos)
        
        
class SnowFactory(pygame.sprite.Group):
    def __init__(
        self, screen: Surface,
        max_particles: int,
        speed: int,
        wind: int,
        depth: int = 10,
        border: Rect = Rect(0, 50, 100, 400)
        ) -> None:
        super().__init__()
        
        self.screen = screen
        self.max_particles = max_particles
        self.speed = speed
        self.wind = wind
        self.depth = depth
        self.border = border
        
        self.images = []
        
        radius = 5
        for depth in range(self.depth):
            p = min(1.1 - depth / self.depth, 1.0)
            
            light_radius = radius * 1.8
            image = Surface((light_radius * 2, light_radius * 2)).convert()
            rect = image.get_rect()
            
            pygame.draw.circle(
                image, (20, 20, 20), 
                rect.center, 
                light_radius
            )
            
            pygame.draw.circle(
                image, "white", 
                rect.center, 
                radius
            ) 
            
            image.set_alpha(min(round(255 * p), 255))
            image.set_colorkey("black")
            
            self.images.append(pygame.transform.smoothscale_by(image, p))
            

    def update(self, *args, **kwargs):
        if len(self.sprites()) < self.max_particles:
            depth = random.randint(1, self.depth)    
            depth_speed = 1.5 - depth / self.speed
            
            SnowParticle(
                self.screen,
                self.images[depth - 1],
                random.uniform(-self.wind, self.wind) * depth_speed,  
                self.speed * depth_speed,
                Vector2(
                    random.randint(self.border.left, self.border.width),
                    random.randint(self.border.top, self.border.height)
                )
            )
        
        super().update(*args, **kwargs)
    
    def draw(self, surface: Surface):
        return super().draw(surface, special_flags=BLEND_RGB_ADD)
    
    
def main():
    options = argparse.ArgumentParser(
        description="2D snow particle simulation using Pygame",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    
    options.add_argument(
        "-m", "--max", 
        type=int, 
        default=100, 
        help="maximum snow particles"
        )
    
    options.add_argument(
        "-s", "--speed", 
        type=int, 
        default=50, 
        help="particle fall speed"
        )
    
    options.add_argument(
        "-w", "--wind", 
        type=int, 
        default=10, 
        help="particle wind force"
        )
    
    options.add_argument(
        "--fps", 
        type=int,
        default=60, 
        help="limit the frames per second"
        )
    
    pygame.display.set_caption("Snow:3")
    
    args = options.parse_args()
    
    pygame.init()
    random.seed()
    
    screen = pygame.display.set_mode((854, 480))
    
    snow_factory = SnowFactory(screen, args.max, args.speed, args.wind)
    SnowParticle.containers = snow_factory 
    
    
    clock = pygame.time.Clock()
    dt = 0
    while True:
        screen.fill(0)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return 0

        snow_factory.update(dt)
        
        snow_factory.draw(screen)
        
                
        pygame.display.update()
        
        dt = clock.tick(args.fps) / 1000