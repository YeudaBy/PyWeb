import pygame
import pygame as pg

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')

navbar_surface = pygame.Surface((1280 - 16, 40))
navbar_surface.fill("antiquewhite1")

font = pygame.font.Font("../assests/fonts/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 16)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


running = True

def draw_navbar(surface):
    pygame.draw.rect(surface, (255, 255, 255), (0, 0, surface.get_width(), surface.get_height()), border_radius=5)
    text = font.render("https://google.com", True, (0, 0, 0))
    surface.blit(text, (10, 5))


input_box1 = InputBox(100, 100, 140, 32)
input_box2 = InputBox(100, 300, 140, 32)
input_boxes = [input_box1, input_box2]

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for box in input_boxes:
            box.handle_event(event)

    for box in input_boxes:
        box.update()

    screen.fill("antiquewhite2")

    screen.blit(navbar_surface, (8, 8))

    draw_navbar(navbar_surface)

    for box in input_boxes:
        box.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
