# Tab-Generator
This generator works by scraping Ultimate-guitar.com for the songs of given artists, and then training [gpt-2-simple](https://github.com/minimaxir/gpt-2-simple) on these descriptions. Ensure that you have downloaded [chromedriver](https://chromedriver.chromium.org/downloads) corresponding to your version of Chrome and have placed it in the same directory as the code.

To run, run scraper.py to scrape songs.

Then run trainer.py.

To generate new outputs, run 'gpt_2_simple generate' in the terminal, and the results will be in a directory labeled 'gen'.

# Inspiration

After I've exhausted all the guitar tabs I could play from my favorite artists, I wanted to have a way to have more music to play. Enter TabGen!

# What it does

TabGen consolidates all your favorite artists music from Ultimate-guitar.com, then trains a neural network on them to create novel guitar tabs based on existing music.

# How I built it

I used Selenium for the web scraping and gpt-2-simple with a TensorFlow backend for training.

# Challenges I ran into

I had a really hard time learning about and figuring out what kind of neural network to use. I went through about 3 iterations of networks, including 2 pre-built models and one I built from scratch. I ended up liking the pretrained gpt-2-simple model, and trained it further on my scraped tabs to create a guitar tab generating network.

# Accomplishments that I'm proud of

I'm proud that this project pushed me to learn so much about machine learning.

# What I learned

Websites like to change their code to make automation harder, and text generation is (as of now) a problem best solved with transformers.

# What's next for TabGen

Updates as Ultimate-guitar.com evolves (yet again...)
