"""Nudge satellite into Mars orbit in pygame gravity simulation game."""
import os
import math
import random
import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LT_BLUE = (173, 216, 230)

class Planet(pg.sprite.Sprite):
    """Satellite object that rotates to face planet & crashes & burns."""
    
    def __init__(self, background,photo_planet,x1planet,x2planet,y1planet,y2planet,masa):
        super().__init__()
        self.background = background

        self.image_tierra = pg.image.load(photo_planet).convert()
        self.image_copy = pg.transform.scale(self.image_tierra, (30,30)) 
        self.image_crash = pg.image.load("satellite_crash_40x33.png").convert()
        self.image = self.image_tierra
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)  # sets transparent color
        self.x = random.randrange(x1planet, x2planet)
        self.y = random.randrange(y1planet, y2planet)

        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.1)

        self.dx = random.choice([-3, 3])
        self.dy = 0
        self.heading = 0
        self.periapsis = 0  # initializes dish orientation
        self.apoapsis = 0 # miles
        self.fuel = 100
        self.mass = masa
        self.distance = 0  # initializes distance between satellite & planet
        self.thrust = pg.mixer.Sound('thrust_audio.ogg')
        self.thrust.set_volume(0.07)  # valid values are 0-1

    def thruster(self, dx, dy):
        """Execute actions associated with firing thrusters."""
        self.dx += dx
        self.dy += dy
        self.fuel -= 2
        self.thrust.play()     

    def check_keys(self):
        """Check if user presses arrow keys & call thruster() method."""
        keys = pg.key.get_pressed()       
        # fire thrusters
        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.05, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.05, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.05)  
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.05)
            
    def locate(self, planet):
        """Calculate distance & heading to planet."""
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        # get direction to planet to point dish
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90  # sprite is traveling tail-first       
        self.distance = math.hypot(dist_x, dist_y)

    #def rotate(self):
       #"""Rotate satellite using degrees so dish faces planet."""
       #self.image = pg.transform.rotate(self.image_tierra, self.heading)
       #self.rect = self.image.get_rect()

    def rotate(self):
        """Rotate the tierra image with each game loop."""
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by


    def path(self):
        """Update satellite's position & draw line to trace orbital path."""
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))



    def update(self):
        """Update satellite object during game."""
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)        
        # change image to fiery red if in atmosphere
        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)

    #def calc_eccentricity(self, dist_list):
 

    def gravity(self, satellite):
        """Calculate impact of gravity on the satellite."""
        G = 1.0  # gravitational constant for game
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)     
        # normalize to a unit vector
        dist_x /= distance
        dist_y /= distance
        # apply gravity
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)

    def orbital_mechanics(self, tick_count, fps, eccentricity_calc_interval, dist_list):

        self.dist_list.append(dist_list)
        """Calculate & return eccentricity from list of radii."""
        
        if tick_count % (eccentricity_calc_interval * fps) == 0:
        
            self.apoapsis = max(self.dist_list)
            self.periapsis = min(self.dist_list)
            self.eccentricity = (self.apoapsis - self.periapsis) / (self.apoapsis + self.periapsis)
            self.dist_list = []  # reset distance list for next calculation
            


class Sol(pg.sprite.Sprite):
    """Planet object that rotates & projects gravity field."""
    
    def __init__(self):
        super().__init__()
        self.image_sol = pg.image.load("sol.png").convert()
        self.image_water = pg.image.load("mars_water.png").convert() 
        self.image_copy = pg.transform.scale(self.image_sol, (100, 100)) 
        self.image_copy.set_colorkey(BLACK) 
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000 
        self.x = 400 
        self.y = 330
        
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        """Rotate the extrella image with each game loop."""
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        """Calculate impact of gravity on the satellite."""
        G = 1.0  # gravitational constant for game
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)     
        # normalize to a unit vector
        dist_x /= distance
        dist_y /= distance
        # apply gravity
        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)
        
    def update(self):
        """Call the rotate method."""
        self.rotate()

def calc_eccentricity(dist_list):
    """Calculate & return eccentricity from list of radii."""
    apoapsis = max(dist_list)
    periapsis = min(dist_list)
    eccentricity = (apoapsis - periapsis) / (apoapsis + periapsis)
    return eccentricity

def instruct_label(screen, text, color, x, y):
    """Take screen, list of strings, color, & origin & render text to screen."""
    instruct_font = pg.font.SysFont(None, 25)
    line_spacing = 22
    for index, line in enumerate(text):
        label = instruct_font.render(line, True, color, BLACK)
        screen.blit(label, (x, y + index * line_spacing))

def box_label(screen, text, dimensions):
    """Make fixed-size label from screen, text & left, top, width, height."""
    readout_font = pg.font.SysFont(None, 27)
    base = pg.Rect(dimensions)
    pg.draw.rect(screen, WHITE, base, 0)
    label = readout_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=base.center)
    screen.blit(label, label_rect)

def mapping_on(planet):
    """Show soil moisture image on Mars."""
    last_center = planet.rect.center
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)
    planet.rect = planet.image_copy.get_rect()
    planet.rect.center = last_center



def cast_shadow(screen):
    """Add optional terminator & shadow behind planet to screen."""
    shadow = pg.Surface((400, 100), flags=pg.SRCALPHA)  # tuple is w,h
    shadow.fill((0, 0, 0, 210))  # last number sets transparency
    screen.blit(shadow, (0, 270))  # tuple is top left coordinates

def main():
    """Set-up labels & instructions, create objects & run the game loop."""
    pg.init()  # initialize pygame
    
    # set-up display
    os.environ['SDL_VIDEO_WINDOW_POS'] = '700, 100'  # set game window origin
    screen = pg.display.set_mode((800, 660), pg.FULLSCREEN) 
    pg.display.set_caption("Mars Orbiter")
    background = pg.Surface(screen.get_size())

    # enable sound mixer
    pg.mixer.init()

    intro_text = [
        ' Reference: Lee Vaughan. IMPRACTICAL PYTHON PROJECTS: Playful Programming Activities to Make You Smarter.',
        ' (San Francisco: No Starch Press, 2019), Pag. 400. ISBN-10: 1-59327-890-X. ISBN-13: 978-1-59327-890-8.',
        ' Irv Kalb. OBJECT-ORIENTED PYTHON: Master OOP by Building Games and GUIs. Fourth Edition',
        ' (San Francisco: No Starch Press, 2022), Pag. 385. ISBN-13: 978-1-7185-0206-2 (print)',
        ' ISBN-13: 978-1-7185-0207-9 (ebook)',
        ' Software Development with Python by Hernando Cedeño Tamayo.',
        
        ]
 


    # instantiate planet and satellite objects
    extrella = Sol()
    extrella_sprite = pg.sprite.Group(extrella)
    
    mercurio = Planet(background,"mercurio.png",380, 385, 170, 175, 1.05)
    mercurio_sprite = pg.sprite.Group(mercurio)
    
    venus = Planet(background,"venus.png",375, 380, 118, 122, 1)
    venus_sprite = pg.sprite.Group(venus)
    
    tierra = Planet(background,"tierra.png",380, 385, 80, 85, 1.05)    
    tierra_sprite = pg.sprite.Group(tierra)

    #luna = Planet(background,"tierra.png",380, 385, 81, 86, 1.0)    
    #luna_sprite = pg.sprite.Group(luna)

    marte = Planet(background,"mars.png",385, 387, 60, 63, 1)
    marte_sprite = pg.sprite.Group(marte)

       
    
    # for circular orbit verification
    mercurio.dist_list = []  # list of distances for eccentricity calculation
    venus.dist_list = []  # list of distances for eccentricity calculation
    tierra.dist_list = []  # list of distances for eccentricity calculation
    marte.dist_list = []  # list of distances for eccentricity calculation  
    mercurio.apoapsis = 0
    mercurio.periapsis = 0
    venus.apoapsis = 0  
    venus.periapsis = 0
    tierra.apoapsis = 0
    tierra.periapsis = 0
    marte.apoapsis = 0
    marte.periapsis = 0      
    mercurio.eccentricity = 1
    venus.eccentricity = 1
    tierra.eccentricity = 1
    marte.eccentricity = 1
    
    eccentricity_calc_interval = 10  # optimized for 120 mile altitude
    
    # time-keeping
    clock = pg.time.Clock()
    fps = 30
    tick_count = 0
     # list of distances for eccentricity calculation

    # for soil moisture mapping functionality
    mapping_enabled = False
    
    running = True
    while running:
        clock.tick(fps)
        tick_count += 1

        
        # get keyboard input
        for event in pg.event.get():
            if event.type == pg.QUIT:  # close window
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                screen = pg.display.set_mode((800, 645))  # exit full screen
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                background.fill(BLACK)  # clear path
            elif event.type == pg.KEYUP:
                tierra.thrust.stop()  # stop sound
               
            elif mapping_enabled:
                if event.type == pg.KEYDOWN and event.key == pg.K_m:
                    mapping_on(extrella)

        # get heading & distance to planet & apply gravity               
        tierra.locate(extrella)
        venus.locate(extrella)
        mercurio.locate(extrella)
        marte.locate(extrella)
        extrella.gravity(tierra)
        extrella.gravity(venus)
        extrella.gravity(mercurio)
        extrella.gravity(marte)
        #tierra.gravity(luna)
        #extrella.gravity(luna)
        
        # calculate orbital eccentricity    
        tierra.orbital_mechanics(tick_count, fps, eccentricity_calc_interval, tierra.distance)
        venus.orbital_mechanics(tick_count, fps, eccentricity_calc_interval, venus.distance)
        mercurio.orbital_mechanics(tick_count, fps, eccentricity_calc_interval, mercurio.distance)
        marte.orbital_mechanics(tick_count, fps, eccentricity_calc_interval, marte.distance)
        # reset distance lists for next calculation
            

        # re-blit background for drawing command - prevents clearing path
        screen.blit(background, (0, 0))
        
        # Fuel/Altitude fail conditions
        if tierra.fuel <= 0:
            instruct_label(screen, ['Fuel Depleted!'], RED, 340, 195)
            tierra.fuel = 0
            tierra.dx = 2
        elif tierra.distance <= 68:
            instruct_label(screen, ['Atmospheric Entry!'], RED, 320, 195)
            tierra.dx = 0
            tierra.dy = 0

        # enable mapping functionality
        #if eccentricity_tierra < 0.05 and tierra.distance >= 69 and tierra.distance <= 120:
            #map_instruct = ['Press & hold M to map soil moisture']
            #instruct_label(screen, map_instruct, LT_BLUE, 250, 175)
            #mapping_enabled = True
        #else:
            #mapping_enabled = False

        extrella_sprite.update()
        extrella_sprite.draw(screen)
        tierra_sprite.update()
        tierra_sprite.draw(screen)
        venus_sprite.update()
        venus_sprite.draw(screen)
        mercurio_sprite.update()
        mercurio_sprite.draw(screen)
        marte_sprite.update()
        marte_sprite.draw(screen)
 # draw satellite path
        #luna_sprite.update()
        #luna_sprite.draw(screen)

        # display intro text for 15 seconds      
        if pg.time.get_ticks() <= 30000:  # time in milliseconds
            instruct_label(screen, intro_text, GREEN, 50, 550)

        # display telemetry and instructions
        box_label(screen, 'x', (100, 20, 75, 20))
        box_label(screen, 'y', (190, 20, 80, 20))
        box_label(screen, 'Altitude', (280, 20, 160, 20))
        #box_label(screen, 'Fuel', (450, 20, 160, 20))
        box_label(screen, 'Eccentricity', (450, 20, 150, 20))
        box_label(screen, 'apoapsis', (610, 20, 90, 20))
        box_label(screen, 'periapsis', (710, 20, 90, 20))
        box_label(screen, 'Tierra', (1, 100, 90, 20))
        box_label(screen, 'Venus', (1, 75, 90, 20))
        box_label(screen, 'Mercurio', (1, 50, 90, 20))
        box_label(screen, 'Marte', (1, 125, 90, 20))
        #box_label(screen, 'x', (750, 20, 75, 20))
        
        box_label(screen, '{:.1f}'.format(tierra.x), (100, 100, 75, 20))     
        box_label(screen, '{:.1f}'.format(tierra.y), (190, 100, 80, 20))
        box_label(screen, '{:.1f}'.format(tierra.distance), (280, 100, 160, 20))
        box_label(screen, '{:.1f}'.format(tierra.apoapsis), (610, 100, 90, 20))
        box_label(screen, '{:.1f}'.format(tierra.periapsis), (710, 100, 90, 20))
        #box_label(screen, '{}'.format(tierra.fuel), (450, 50, 160, 20))
        box_label(screen, '{:.8f}'.format(tierra.eccentricity), (450, 100, 150, 20))
        #box_label(screen, '{:.1f}'.format(planet.gravity(satellite=6)), (750, 50, 75, 20))

        box_label(screen, '{:.1f}'.format(venus.x), (100, 75, 75, 20))     
        box_label(screen, '{:.1f}'.format(venus.y), (190, 75, 80, 20))
        box_label(screen, '{:.1f}'.format(venus.distance), (280, 75, 160, 20))
        box_label(screen, '{:.1f}'.format(venus.apoapsis), (610, 75, 90, 20))
        box_label(screen, '{:.1f}'.format(venus.periapsis), (710, 75, 90, 20))
        #box_label(screen, '{}'.format(venus.fuel), (450, 75, 160, 20))
        box_label(screen, '{:.8f}'.format(venus.eccentricity), (450, 75, 150, 20))

        box_label(screen, '{:.1f}'.format(mercurio.x), (100, 50, 75, 20))     
        box_label(screen, '{:.1f}'.format(mercurio.y), (190, 50, 80, 20))
        box_label(screen, '{:.1f}'.format(mercurio.distance), (280, 50, 160, 20))
        box_label(screen, '{:.1f}'.format(mercurio.apoapsis), (610, 50, 90, 20))
        box_label(screen, '{:.1f}'.format(mercurio.periapsis), (710, 50, 90, 20))
        #box_label(screen, '{}'.format(mercurio.fuel), (450, 100, 160, 20))
        box_label(screen, '{:.8f}'.format(mercurio.eccentricity), (450, 50, 150, 20))

        box_label(screen, '{:.1f}'.format(marte.x), (100, 125, 75, 20))     
        box_label(screen, '{:.1f}'.format(marte.y), (190, 125, 80, 20))
        box_label(screen, '{:.1f}'.format(marte.distance), (280, 125, 160, 20))
        
        box_label(screen, '{:.1f}'.format(marte.apoapsis), (610, 125, 90, 20))
        box_label(screen, '{:.1f}'.format(marte.periapsis), (710, 125, 90, 20))
        #box_label(screen, '{}'.format(marte.fuel), (450, 125, 160, 20))
        box_label(screen, '{:.8f}'.format(marte.eccentricity), (450, 125, 150, 20))

        #instruct_label(screen, instruct_text1, WHITE, 10, 575)
        #instruct_label(screen, instruct_text2, WHITE, 570, 510)
      
        # add terminator & border
        #cast_shadow(screen)
        #pg.draw.rect(screen, WHITE, (1, 1, 798, 643), 1)

        pg.display.flip()

if __name__ == "__main__":
    main()
