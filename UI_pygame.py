import pygame
import pygame_gui
from pygame_gui.elements import UIButton as Button
from pygame_gui.elements import UIHorizontalSlider as Slider
from pygame_gui.elements import UILabel as Label
from pygame import mixer
from MidiGenerator import MidiGenerator
import pretty_midi
import numpy as np
import matplotlib.pyplot as plt

# Initialize the pygame
pygame.init()

# set the dimensions of the window and create it
window_surface = pygame.display.set_mode((800, 700))

manager = pygame_gui.UIManager((800, 700))

clock = pygame.time.Clock()

mixer.init()

midi_generator = MidiGenerator("piano-model")

# Create buttons and sliders
generate_button = Button(relative_rect=pygame.Rect((50, 20), (100, 50)), text='Generate', manager=manager)
play_button = Button(relative_rect=pygame.Rect((160, 20), (100, 50)), text='Play', manager=manager)
stop_button = Button(relative_rect=pygame.Rect((270, 20), (100, 50)), text='Stop', manager=manager)

volume_label = Label(relative_rect=pygame.Rect((50, 80), (100, 20)), text='Volume', manager=manager)
volume_slider = Slider(relative_rect=pygame.Rect((50, 110), (200, 20)), start_value=0.5, value_range=(0, 1), manager=manager)
volume_value_label = Label(relative_rect=pygame.Rect((260, 110), (50, 20)), text=str(volume_slider.get_current_value()), manager=manager)

temperature_label = Label(relative_rect=pygame.Rect((50, 150), (100, 20)), text='Temperature', manager=manager)
temperature_slider = Slider(relative_rect=pygame.Rect((50, 180), (200, 20)), start_value=1.1, value_range=(0.1, 1.5), manager=manager)
temperature_value_label = Label(relative_rect=pygame.Rect((260, 180), (50, 20)), text=str(temperature_slider.get_current_value()), manager=manager)

max_new_tokens_label = Label(relative_rect=pygame.Rect((50, 220), (150, 20)), text='Max New Tokens', manager=manager)
max_new_tokens_slider = Slider(relative_rect=pygame.Rect((50, 250), (200, 20)), start_value=550, value_range=(100, 1000), manager=manager)
max_new_tokens_value_label = Label(relative_rect=pygame.Rect((260, 250), (50, 20)), text=str(max_new_tokens_slider.get_current_value()), manager=manager)

top_k_label = Label(relative_rect=pygame.Rect((50, 290), (100, 20)), text='Top K', manager=manager)
top_k_slider = Slider(relative_rect=pygame.Rect((50, 320), (200, 20)), start_value=105, value_range=(10, 200), manager=manager)
top_k_value_label = Label(relative_rect=pygame.Rect((260, 320), (50, 20)), text=str(top_k_slider.get_current_value()), manager=manager)

status_label = Label(relative_rect=pygame.Rect((350, 220), (300, 20)), text='', manager=manager)

playing = False
piano_roll_image = None

# Main event loop
while True:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == generate_button:
                    status_label.set_text('Generating, please wait...')
                    try:
                        midi_generator.generate_midi()
                        status_label.set_text('Generation complete!')
                        # Load MIDI file into PrettyMIDI object
                        midi_data = pretty_midi.PrettyMIDI('samples/test.mid')
                        # Retrieve piano roll of the MIDI file
                        piano_roll = midi_data.get_piano_roll()
                        plt.imshow(piano_roll, aspect='auto', cmap='hot_r', origin='lower')
                        plt.savefig('samples/test.png')
                        piano_roll_image = pygame.image.load('samples/test.png')
                        piano_roll_image = pygame.transform.scale(piano_roll_image, (800, 300))  # Scaled to fit the bottom half
                    except:
                        status_label.set_text('Generation failed!, Try Again please..')

                elif event.ui_element == play_button:
                    mixer.music.load('samples/test.mid')
                    mixer.music.play()
                    playing = True
                elif event.ui_element == stop_button and playing:
                    mixer.music.stop()
                    playing = False

            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    mixer.music.set_volume(volume_slider.get_current_value())
                    volume_value_label.set_text(str(round(volume_slider.get_current_value(), 2)))
                elif event.ui_element == temperature_slider:
                    midi_generator.set_temperature(temperature_slider.get_current_value())
                    temperature_value_label.set_text(str(round(temperature_slider.get_current_value(), 2)))
                elif event.ui_element == max_new_tokens_slider:
                    midi_generator.set_max_new_tokens(int(max_new_tokens_slider.get_current_value()))
                    max_new_tokens_value_label.set_text(str(int(max_new_tokens_slider.get_current_value())))
                elif event.ui_element == top_k_slider:
                    midi_generator.set_top_k(int(top_k_slider.get_current_value()))
                    top_k_value_label.set_text(str(int(top_k_slider.get_current_value())))

        manager.process_events(event)

    manager.update(time_delta)
    
    # Fill the window_surface with a solid color
    window_surface.fill((255, 255, 255))  # This will fill the surface with white color
    
    # Draw the piano roll image
    if piano_roll_image is not None:
        window_surface.blit(piano_roll_image, (0, 350))  # Positioned at the bottom half
    
    manager.draw_ui(window_surface)

    pygame.display.update()
