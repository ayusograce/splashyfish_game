from math import sin
import os
import arcade
import random

window = arcade.Window(1000, 600, "SplashyFish")

# Create a game view for the main game
class GameView(arcade.View):
    #FUNCTION TO INITIALIZE THE GAME
    def __init__ (self) -> None:
        super().__init__()

        #Variables
        self.game_over = False
        self.score = 0
        self.time_since_last_obstacle = 0
        self.colliding = False
        self.velocity_y = 0

        
        # Read the high score from the file
        self.read_high_score()

        # Load textures for the fish
        self.dead_fish = arcade.load_texture("images/fish_red_skeleton_outline.png")
        self.alive_fish = arcade.load_texture("images/fish_red_outline.png")

        # Create sprite lists for the game
        self.sprites = arcade.SpriteList()
        self.obstacles = arcade.SpriteList()
        self.end_text = arcade.SpriteList()


        # Create and position the background, ground, fish, and game over image
        self.background = arcade.Sprite("images/bg.jpg", 0.5)
        self.background.center_x = 500
        self.background.center_y = 300
        self.sprites.append(self.background)

        self.ground = arcade.Sprite("images/piso.png", 1)
        self.ground.center_x = 500
        self.ground.center_y = -20
        self.sprites.append(self.ground)

        self.fish = arcade.Sprite("images/fish_red_outline.png", 0.5)
        self.fish.center_x = 300
        self.fish.center_y = 450
        self.sprites.append(self.fish)

        self.game_over_image = arcade.Sprite("images/game_over.png", 1)
        self.game_over_image.center_x = 500
        self.game_over_image.center_y = 300
        self.end_text.append(self.game_over_image)


        #Music and sound
        self.music = arcade.load_sound("sounds/music.wav")
        self.music.play(loop=True, volume=0.4)

        self.splash_sound = arcade.load_sound("sounds/splash.mp3")
        self.impact_sound = arcade.load_sound("sounds/punch_impact.mp3")
        self.game_over_sound = arcade.load_sound("sounds/game_over.mp3")
        
    #FUNCTION TO READ THE HIGH SCORE FROM A FILE
    def read_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                content = file.read()
                if content == "":
                    self.high_score = 0
                else:
                    self.high_score = int(content)
        else:
            self.high_score = 0
            with open("highscore.txt", "w") as file:
                file.write(str(self.high_score))

    #FUNCTION TO CHECK IF THE CURRENT SCORE IS A HIGH SCORE AND UPDATE THE FILE IF IT IS
    def high_score_check(self):
        if int(self.score) > int(self.high_score):
            self.high_score = int(self.score)
            with open("highscore.txt", "w") as file:
                file.write(str(self.high_score))

    #FUNCTION TO CREATE OBSTACLES
    def create_obstacle(self):
        # Randomly determine the vertical position of the gap
        gap_y = random.randint(150, 500)
        gap = 300

        # Create the upper and lower obstacles and add them to the obstacle list
        self.obstacle_up = arcade.Sprite("images/coral2.png", 1)
        self.obstacle_up.center_x = 1000
        self.obstacle_up.center_y = gap_y + (gap / 2) + 135
        self.obstacle_up.angle = 180
        self.obstacles.append(self.obstacle_up)

        self.obstacle_down = arcade.Sprite("images/coral2.png", 1)
        self.obstacle_down.center_x = 1000
        self.obstacle_down.center_y = gap_y - (gap / 2) - 135
        self.obstacles.append(self.obstacle_down)

    #FUNCTION TO RESET THE GAME
    def reset_game(self):
        self.game_over = False
        self.colliding = False
        self.fish.center_y = 300
        self.fish.angle = 0
        self.velocity_y = 0
        self.score = 0
        self.obstacles = arcade.SpriteList()


    #FUNCTION TO DRAW THE GAME
    def on_draw(self):
        self.clear()
        self.sprites.draw()
        self.obstacles.draw()

        #High score text
        arcade.draw_text(f"High Score: {int(self.high_score)}", 50, 540, arcade.color.WHITE, 20, bold=True, font_name="Comic Sans MS")

        # Text for the score
        arcade.draw_text(int(self.score), 500, 540, arcade.color.WHITE, 50, bold=True, font_name="Comic Sans MS")  

        # If the game is over, display "GAME OVER" text
        if self.game_over:
            self.high_score_check()
            self.end_text.draw()
            # self.game_over_sound.play(volume=0.5)


    #FUNCTION TO UPDATE THE GAME
    def on_update(self, delta_time: float):
       
        # If the game is over, we don't want to update anything
        if self.game_over:
            return

        # Apply gravity to the fish
        self.velocity_y -= 0.5
        self.fish.center_y += self.velocity_y

        # When the fish goes off the screen, end the game
        if self.fish.center_y < 50 or self.fish.center_y > 580:
            self.game_over = True
            self.colliding = True

        # Rotate the fish based on its velocity
        if self.velocity_y < 0:
            self.fish.angle -= 5
            self.fish.angle = max(self.fish.angle, 30)
        else:
            self.fish.angle += 5
            self.fish.angle = min(self.fish.angle, -10)

        # Create new obstacles every 1.5 seconds
        self.time_since_last_obstacle += delta_time
        if self.time_since_last_obstacle > 1.5:
            self.create_obstacle()
            self.time_since_last_obstacle = 0

        # Remove obstacles that have gone off the screen
        for obstacle in self.obstacles:
            if obstacle.center_x < -100:
                self.obstacles.remove(obstacle)
        
        # Move obstacles to the left
        for obstacle in self.obstacles:
            obstacle.center_x -= 5

        # Game over when fish collides with an obstacle
        if arcade.check_for_collision_with_list(self.fish, self.obstacles):
            self.colliding = True
            self.game_over = True

        # Update the fish texture based on whether it's colliding or not
        if self.colliding == True:
            self.game_over_sound.play(volume=0.5)
            self.fish.texture = self.dead_fish
        else:
            self.fish.texture = self.alive_fish

        # Update the score based on how many obstacles have been passed
        for obstacle in self.obstacles:
            if obstacle.center_x < self.fish.center_x and not hasattr(obstacle, "passed"):
                self.score += 0.5
                obstacle.passed = True

    #DEFINE THE FUNCTION TO HANDLE KEY PRESSES
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self.velocity_y = 10
            self.splash_sound.play(volume=0.5)
        # If the game is over and the player presses SPACE, reset the game and show the menu
        if key == arcade.key.SPACE and self.game_over:
            self.reset_game()
            self.window.show_view(menu)

# Create a menu view for the game
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.sprites = arcade.SpriteList()
        self.time = 0

        # Create and position the background, ground, fish, title, and space bar images
        self.background = arcade.Sprite("images/bg.jpg", 0.5)
        self.background.center_x = 500
        self.background.center_y = 300
        self.sprites.append(self.background)

        self.fish = arcade.Sprite("images/fish_red_outline.png", 0.5)
        self.fish.center_x = 300
        self.fish.center_y = 450
        self.sprites.append(self.fish)

        self.title = arcade.Sprite("images/title.png", 0.6)
        self.title.center_x = 500
        self.title.center_y = 300
        self.sprites.append(self.title)

        self.space_bar = arcade.Sprite("images/space_bar.png", 0.3)
        self.space_bar.center_x = 500
        self.space_bar.center_y = 150
        self.sprites.append(self.space_bar)

        self.ground = arcade.Sprite("images/piso.png", 1)
        self.ground.center_x = 500
        self.ground.center_y = -20
        self.sprites.append(self.ground)

    #FUNCTION TO DRAW THE MENU
    def on_draw(self):
        self.clear()
        self.sprites.draw()
        arcade.draw_text("Press SPACE to start", 365, 60, arcade.color.WHITE, 20, bold=True, font_name="Comic Sans MS")

    #FUNCTION TO UPDATE THE MENU
    def on_update(self, delta_time: float):
        self.time += delta_time
        self.space_bar.center_y = 160 + sin(self.time * 3) * 10

    #FUNCTION TO HANDLE KEY PRESSES IN THE MENU
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self.window.show_view(game)


# Create an instance of the game and run it
game = GameView()
menu = MenuView()

window.show_view(menu)
arcade.run()