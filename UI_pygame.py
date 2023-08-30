import pygame
import pygame_gui
from pygame_gui.elements import UIButton as Button
from pygame_gui.elements import UIHorizontalSlider as Slider
from pygame_gui.elements import UILabel as Label
from pygame import mixer
from MidiGenerator import MidiGenerator
import pretty_midi
import matplotlib.pyplot as plt

# Initialize the pygame
pygame.init()

# set the dimensions of the window and create it
window_surface = pygame.display.set_mode((800, 800))

manager = pygame_gui.UIManager((800, 800))

clock = pygame.time.Clock()

mixer.init()

midi_generator = MidiGenerator("piano-model-13M")

# Create buttons and sliders
generate_button = Button(relative_rect=pygame.Rect((50, 20), (100, 50)), text='Generate', manager=manager)
play_button = Button(relative_rect=pygame.Rect((160, 20), (100, 50)), text='Play', manager=manager)
stop_button = Button(relative_rect=pygame.Rect((270, 20), (100, 50)), text='Stop', manager=manager)

volume_label = Label(relative_rect=pygame.Rect((50, 80), (100, 20)), text='Volume', manager=manager)
volume_slider = Slider(relative_rect=pygame.Rect((50, 110), (200, 20)), start_value=0.5, value_range=(0, 1), manager=manager)
volume_value_label = Label(relative_rect=pygame.Rect((260, 110), (50, 20)), text=str(volume_slider.get_current_value()), manager=manager)

temperature_label = Label(relative_rect=pygame.Rect((50, 150), (100, 20)), text='Temperature', manager=manager)
temperature_slider = Slider(relative_rect=pygame.Rect((50, 180), (200, 20)), start_value=1.0, value_range=(0.01, 1.5), manager=manager)
temperature_value_label = Label(relative_rect=pygame.Rect((260, 180), (50, 20)), text=str(temperature_slider.get_current_value()), manager=manager)

max_new_tokens_label = Label(relative_rect=pygame.Rect((50, 220), (150, 20)), text='Max New Tokens', manager=manager)
max_new_tokens_slider = Slider(relative_rect=pygame.Rect((50, 250), (200, 20)), start_value=550, value_range=(100, 10000), manager=manager)
max_new_tokens_value_label = Label(relative_rect=pygame.Rect((260, 250), (50, 20)), text=str(max_new_tokens_slider.get_current_value()), manager=manager)

top_k_label = Label(relative_rect=pygame.Rect((50, 290), (100, 20)), text='Top K', manager=manager)
top_k_slider = Slider(relative_rect=pygame.Rect((50, 320), (200, 20)), start_value=105, value_range=(10, 500), manager=manager)
top_k_value_label = Label(relative_rect=pygame.Rect((260, 320), (50, 20)), text=str(top_k_slider.get_current_value()), manager=manager)

bmp_label = Label(relative_rect=pygame.Rect((50, 360), (100, 20)), text='BPM', manager=manager)
bmp_slider = Slider(relative_rect=pygame.Rect((50, 390), (200, 20)), start_value=120, value_range=(100, 180), manager=manager)
bmp_value_label = Label(relative_rect=pygame.Rect((260, 390), (50, 20)), text=str(bmp_slider.get_current_value()), manager=manager)

status_label = Label(relative_rect=pygame.Rect((350, 220), (300, 20)), text='', manager=manager)
response_label = Label(relative_rect=pygame.Rect((250, 250), (600, 40)), text='', manager=manager)
song_name_label = Label(relative_rect=pygame.Rect((350, 290), (300, 20)), text='', manager=manager)

# Create buttons for the two options
new_piece_button = Button(relative_rect=pygame.Rect((50, 460), (200, 50)), text='New Piece ✓', manager=manager)
continue_song_button = Button(relative_rect=pygame.Rect((260, 460), (200, 50)), text='Continue Song', manager=manager)
retry_button = Button(relative_rect=pygame.Rect((470, 460), (200, 50)), text='Retry Same Song', manager=manager)


# Create a variable to hold the selected option
selected_option = 'New Piece'  # or 'Continue Song'
last_song=""

playing = False
piano_roll_image = None

# Main event loop
while True:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            # end the program
            quit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == generate_button:
                    status_label.set_text('Generating, please wait...')
                    try:
                        response,song_name=midi_generator.generate_midi(selected_option,bpm=int(bmp_slider.get_current_value()))
                        status_label.set_text('Generation complete!')
                        response_label.set_text(response)
                        song_name_label.set_text(song_name)
                        last_song=song_name  
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
                        response_label.set_text('')

                elif event.ui_element == play_button:
                    mixer.music.load('samples/test.mid')
                    mixer.music.play()
                    playing = True
                elif event.ui_element == stop_button and playing:
                    mixer.music.stop()
                    playing = False
                        # Add these lines to update selected_option based on button click
                if event.ui_element == new_piece_button:
                    selected_option = 'New Piece'
                    new_piece_button.set_text('New Piece ✓')
                    continue_song_button.set_text('Continue Song')
                elif event.ui_element == continue_song_button:
                    selected_option = 'Continue Song'
                    continue_song_button.set_text('Continue Song ✓')
                    new_piece_button.set_text('New Piece')
                elif event.ui_element == retry_button and last_song!="":
                    # Handle what happens when Retry button is clicked
                    status_label.set_text('Retrying, please wait...')
                    try:
                        # Assume you have a method or logic to retry generation with the same song
                        response, song_name = midi_generator.generate_midi(selected_option,int(bmp_slider.get_current_value()),last_song)
                        status_label.set_text('Retry complete!')
                        response_label.set_text(response)
                        song_name_label.set_text(song_name)
                        # Load MIDI file into PrettyMIDI object
                        midi_data = pretty_midi.PrettyMIDI('samples/test.mid')
                        # Retrieve piano roll of the MIDI file
                        piano_roll = midi_data.get_piano_roll()
                        plt.imshow(piano_roll, aspect='auto', cmap='hot_r', origin='lower')
                        plt.savefig('samples/test.png')
                        piano_roll_image = pygame.image.load('samples/test.png')
                        piano_roll_image = pygame.transform.scale(piano_roll_image, (800, 300))  # Scaled to fit the bottom half  
                    except:
                        status_label.set_text('Retry failed!, Try Again please..')
                        response_label.set_text('')

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
                elif event.ui_element == bmp_slider:
                    bmp_value_label.set_text(str(int(bmp_slider.get_current_value())))

        manager.process_events(event)

    manager.update(time_delta)
    
    # Fill the window_surface with a solid color
    window_surface.fill((255, 255, 255))  # This will fill the surface with white color
    
    # Draw the piano roll image
    if piano_roll_image is not None:
        window_surface.blit(piano_roll_image, (0, 500))  # Positioned at the bottom half
    
    manager.draw_ui(window_surface)

    pygame.display.update()
