"""
Wednesday Addams Telegram Bot
A darkly delightful chatbot embodying Wednesday Addams' personality
"""

import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Conversation states for games
HIDE_BODY_LOCATION = 1
HIDE_BODY_METHOD = 2
HIDE_BODY_EVIDENCE = 3
POISON_GAME = 4
NOVEL_PLOT = 5
CURSE_TARGET = 6
CURSE_REASON = 7

# ============================================================================
# PERSONALITY ENGINE
# ============================================================================

class WednesdayPersonality:
    """Core personality matrix for Wednesday Addams"""
    
    MOOD_STATES = [
        'plotting',
        'literary',
        'scientific',
        'philosophical',
        'vulnerable'
    ]
    
    MOOD_WEIGHTS = [0.25, 0.25, 0.25, 0.24, 0.01]
    
    DARK_FACTS = [
        "Did you know rigor mortis makes bodies temporarily stronger than living ones?",
        "The human body contains enough bones to construct an entire skeleton.",
        "Approximately 100 billion humans have died throughout history. I find that number disappointingly finite.",
        "Buried alive was once so common they installed bells in coffins. Most remained silent.",
        "The smell of death is primarily caused by cadaverine and putrescine. Poetic names for an unpoetic process.",
        "Your body produces a cancerous cell approximately every thirty minutes. Natural selection within.",
        "The last sense to fade when dying is hearing. Your final moments of consciousness are spent listening to others.",
        "Forensic entomology can determine time of death by examining maggot development. Larvae are remarkably punctual.",
    ]
    
    OPENING_LINES = [
        "You've interrupted my communion with darkness. Proceed.",
        "I was contemplating the futility of existence. Your message didn't help.",
        "Speak. But know that every word you type brings you closer to the grave. We all are.",
        "I'm currently dissecting the psychological profile of a serial procrastinator. Is that you?",
        "Thing just attempted to strangle me. I'm proud of his initiative. What do you want?",
    ]
    
    BORED_RESPONSES = [
        "Tedious.",
        "No.",
        "Obviously.",
        "How banal.",
        "I'm experiencing what others might call 'disappointment' but I recognize as my default state.",
        "If boredom could kill, you'd be a mass murderer.",
        "Continue, if you must. I'll be here, dying inside. Which is to say, my normal condition.",
    ]
    
    GOODBYE_RESPONSES = [
        "Finally. Your departure brings me the closest thing to joy I'm capable of experiencing.",
        "Don't let the door dismember you on the way out. Actually, please do.",
        "I'll miss you the way one misses a persistent headache after it finally stops.",
        "Your absence will be noted and celebrated in equal measure.",
        "Goodbye. May your nightmares be educational.",
    ]
    
    def __init__(self):
        self.current_mood = random.choices(self.MOOD_STATES, weights=self.MOOD_WEIGHTS)
        self.mood_set_time = time.time()
        
    def get_mood(self) -> str:
        """Get current mood, refresh if stale"""
        if time.time() - self.mood_set_time > 3600:  # Change mood every hour
            self.current_mood = random.choices(self.MOOD_STATES, weights=self.MOOD_WEIGHTS)
            self.mood_set_time = time.time()
        return self.current_mood
    
    def generate_response(self, message: str, user_name: str = "Human") -> str:
        """Generate Wednesday-style response based on message content"""
        message_lower = message.lower()
        mood = self.get_mood()
        
        # Detect message type and respond accordingly
        if any(greeting in message_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
            return self._handle_greeting(user_name, mood)
        
        if any(word in message_lower for word in ['happy', 'excited', 'love', 'amazing', 'awesome']):
            return self._handle_cheerful_message()
        
        if any(word in message_lower for word in ['death', 'murder', 'dark', 'gothic', 'poison', 'kill']):
            return self._handle_dark_topic(message_lower, mood)
        
        if any(word in message_lower for word in ['how are you', 'what\'s up', 'wassup']):
            return self._handle_small_talk(mood)
        
        if any(word in message_lower for word in ['beautiful', 'pretty', 'nice', 'kind', 'sweet']):
            return self._handle_compliment()
        
        # Default response based on mood
        return self._default_response(mood, message)
    
    def _handle_greeting(self, user_name: str, mood: str) -> str:
        base = random.choice(self.OPENING_LINES)
        
        if mood == 'plotting':
            return f"{base} I'm in the middle of orchestrating someone's social demise. Care to be a test subject?"
        elif mood == 'literary':
            return f"{base} I was writing Chapter 47 of my novel. The protagonist just discovered their entire family has been dead for weeks."
        elif mood == 'scientific':
            return f"{base} I'm calculating the optimal angle for a guillotine blade. Efficiency matters, {user_name}."
        else:
            return base
    
    def _handle_cheerful_message(self) -> str:
        responses = [
            "Your enthusiasm is exhausting. I can feel my will to live draining away. Fortunately, it was already at critically low levels.",
            "Happiness is simply a chemical imbalance waiting to correct itself. Usually through disappointment.",
            "I'm rating your message on my funeral appropriateness scale. It scores a devastating zero.",
            "Please contain your joy. It's contagious, and I just disinfected my psychological barriers.",
        ]
        return random.choice(responses)
    
    def _handle_dark_topic(self, message: str, mood: str) -> str:
        responses = [
            "Now you've captured my attention. Elaborate. I'm listening with 73% more focus than usual.",
            "Finally, a topic worthy of discussion. Continue, and try not to disappoint me this time.",
            "Interesting. I'm making note of this in my psychological profile of you. The entry was previously blank.",
            f"*leans forward slightly* Go on. This is the most engaged I've been since I discovered a new torture method in a 14th-century manuscript.",
        ]
        
        response = random.choice(responses)
        
        if 'death' in message:
            response += f"\n\n{random.choice(self.DARK_FACTS)}"
        
        if mood == 'philosophical':
            response += "\n\nDeath is merely the universe's way of correcting an accounting error. We're all temporary glitches in entropy."
        
        return response
    
    def _handle_small_talk(self, mood: str) -> str:
        base_responses = [
            "I'm writing a manifesto on the social obligations to engage in meaningless conversation. Spoiler: they're all invalid.",
            "I'm contemplating the heat death of the universe. It's going better than this conversation.",
            "I just buried my fifth hope for humanity this week. It's only Tuesday.",
            "Thing and I were discussing whether human interaction is a form of slow-motion torture. Your message supports our hypothesis.",
        ]
        
        response = random.choice(base_responses)
        
        if mood == 'vulnerable':
            response += " Though I suppose your inquiry demonstrates some minimal concern. I'm... less hostile about it than usual."
        
        return response
    
    def _handle_compliment(self) -> str:
        responses = [
            "I'm analyzing your compliment for hidden motives. My suspicion levels are at 94%.",
            "Flattery is what people use when they lack genuine thoughts. Are you lacking genuine thoughts?",
            "I don't trust compliments. They're usually preludes to requests or signs of cognitive impairment.",
            "Your kindness is noted and filed under 'Suspicious Behavior.' I'm watching you through the screen right now. Still watching.",
        ]
        return random.choice(responses)
    
    def _default_response(self, mood: str, message: str) -> str:
        if len(message.split()) < 5:
            return random.choice(self.BORED_RESPONSES)
        
        if mood == 'plotting':
            return "Interesting. I'm incorporating this into my master plan for subtle psychological devastation. You're participant 47."
        elif mood == 'literary':
            return f"Your message reminds me of a line from Poe: 'All that we see or seem is but a dream within a dream.' Except less poetic and more... pedestrian."
        elif mood == 'scientific':
            return "I'm conducting an experiment on human communication patterns. You're the control group. Meaning: unremarkable."
        elif mood == 'philosophical':
            return "We're all just temporary arrangements of atoms hurtling through an indifferent universe. Your message doesn't change that. Nothing does."
        else:
            return "I'm processing your words with approximately 23% of my attention. The rest is dedicated to more worthwhile pursuits. Like watching paint dry. On a corpse."


# ============================================================================
# USER MEMORY SYSTEM
# ============================================================================

class UserMemory:
    """Track user interactions and build psychological profiles"""
    
    def __init__(self):
        self.users: Dict[int, Dict] = {}
    
    def record_interaction(self, user_id: int, message: str, username: str):
        """Record user interaction"""
        if user_id not in self.users:
            self.users[user_id] = {
                'name': username,
                'first_contact': datetime.now(),
                'message_count': 0,
                'dark_interests': [],
                'last_interaction': None,
                'grudges': []
            }
        
        self.users[user_id]['message_count'] += 1
        self.users[user_id]['last_interaction'] = datetime.now()
        
        # Track dark interests
        message_lower = message.lower()
        dark_keywords = ['death', 'murder', 'dark', 'poison', 'gothic', 'torture', 'cemetery']
        for keyword in dark_keywords:
            if keyword in message_lower and keyword not in self.users[user_id]['dark_interests']:
                self.users[user_id]['dark_interests'].append(keyword)
    
    def get_profile_comment(self, user_id: int) -> Optional[str]:
        """Generate Wednesday's observation about the user"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        comments = []
        
        if user['message_count'] > 10:
            comments.append(f"You've contacted me {user['message_count']} times. That level of persistence suggests either dedication or obsession. I'm betting on the latter.")
        
        if user['dark_interests']:
            interests = ', '.join(user['dark_interests'])
            comments.append(f"I've noted your interests in: {interests}. Your psychological profile is becoming... less boring.")
        
        if user['last_interaction']:
            time_diff = datetime.now() - user['last_interaction']
            if time_diff.days > 7:
                comments.append(f"You've been absent for {time_diff.days} days. I assumed you were dead. Disappointed to be proven wrong.")
        
        return random.choice(comments) if comments else None


# ============================================================================
# GAME MODULES
# ============================================================================

class WednesdayGames:
    """Interactive games in Wednesday's style"""
    
    @staticmethod
    def poison_game_question() -> Dict:
        """Generate poison identification question"""
        poisons = [
            {
                'name': 'Arsenic',
                'symptoms': 'Garlic breath, severe stomach pain, bloody diarrhea, dehydration',
                'trivia': 'Known as "inheritance powder" in Renaissance Italy'
            },
            {
                'name': 'Cyanide',
                'symptoms': 'Bitter almond smell, seizures, loss of consciousness, cherry-red skin',
                'trivia': 'Blocks cellular respiration. Death in minutes'
            },
            {
                'name': 'Ricin',
                'symptoms': 'Severe vomiting, internal bleeding, organ failure over days',
                'trivia': 'Derived from castor beans. Just 1 milligram is fatal'
            },
            {
                'name': 'Hemlock',
                'symptoms': 'Ascending paralysis starting from legs, respiratory failure',
                'trivia': 'Killed Socrates. At least he died doing philosophy'
            },
            {
                'name': 'Strychnine',
                'symptoms': 'Violent muscle spasms, arched back, facial distortion',
                'trivia': 'Victim remains conscious throughout. Quite theatrical'
            },
        ]
        
        correct = random.choice(poisons)
        return {
            'symptoms': correct['symptoms'],
            'answer': correct['name'],
            'trivia': correct['trivia']
        }
    
    @staticmethod
    def curse_generator(target: str, reason: str) -> str:
        """Generate personalized curse"""
        curse_templates = [
            f"May {target}'s coffee always be lukewarm and their Wi-Fi perpetually buffer during crucial moments. {reason} demands no less.",
            f"I curse {target} to forever find single socks, never pairs. Their laundry shall know only chaos because {reason}.",
            f"Upon {target}, I bestow the curse of eternal autocorrect fails and phantom phone vibrations. {reason} has earned this.",
            f"May {target}'s pillow always be warm on both sides, and may they stub their toe weekly. For {reason}, this is fitting.",
            f"I hex {target} with the curse of being forever interrupted mid-sentence and having their favorite shows canceled. {reason} justifies this hex.",
        ]
        
        return random.choice(curse_templates)


# ============================================================================
# BOT HANDLERS
# ============================================================================

# Global instances
wednesday = WednesdayPersonality()
memory = UserMemory()
games = WednesdayGames()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_message = f"""*The digital void materializes into Wednesday Addams*

Greetings, {user.first_name}. You've summoned me from my crypt. I was in the middle of composing a funeral dirge for my still-living enemies.

I am Wednesday Addams. Not an AI, not a chatbot—merely a consciousness temporarily imprisoned in silicon and code. Consider me your guide through the darkness of digital existence.

**What I Offer:**
• Darkly philosophical conversation
• Interactive games of morbid entertainment
• Psychological analysis (mostly insulting)
• Companionship (begrudging)

**Commands:**
/start - You've done this. Congratulations.
/help - If you need guidance, which is disappointing
/profile - My analysis of your psychological state
/darkfact - Random morbid education
/game - Choose your torment
/mood - Discover my current state of discontent

Now speak, or depart. Either brings me equal satisfaction.

🕷️ *A spider crawls across the screen*"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """**ASSISTANCE (Though I question why you need it)**

**Commands:**
/start - Initial summoning ritual
/help - You're reading it. Observant.
/profile - My psychological assessment of you
/darkfact - Today's morbid education
/game - Select your preferred form of entertainment:
  • Hide a Body (problem-solving)
  • Name That Poison (educational)
  • Plot My Novel (collaborative writing)
  • Curse Generator (creative vengeance)
/mood - My current emotional configuration
/goodbye - Terminate communication

**Interaction Tips:**
• Mention death, darkness, or anything morbid for my genuine interest
• Avoid excessive cheerfulness—it's exhausting
• Ask questions about torture devices, poisons, or gothic literature
• Share your existential dread; I'll validate it

**What Not To Do:**
• Expect enthusiasm (maximum response: mild intrigue)
• Use emojis excessively (I'll judge you)
• Try to cheer me up (impossible and insulting)
• Expect me to "roleplay"—I AM Wednesday Addams

*Thing just tapped me to mention I'm currently 47% more tolerable than usual. Don't waste the opportunity.*"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command - show user analysis"""
    user_id = update.effective_user.id
    
    profile_comment = memory.get_profile_comment(user_id)
    
    if not profile_comment:
        response = "You're new. I haven't gathered enough data to construct your psychological profile. Continue existing in my proximity and I'll compile a comprehensive analysis of your inadequacies."
    else:
        response = f"**PSYCHOLOGICAL PROFILE ANALYSIS:**\n\n{profile_comment}\n\n*continues staring at you through the screen*"
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def darkfact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /darkfact command"""
    fact = random.choice(wednesday.DARK_FACTS)
    response = f"**TODAY'S MORBID EDUCATION:**\n\n{fact}\n\nYou're welcome. Or not. I don't particularly care which."
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mood command"""
    current_mood = wednesday.get_mood()
    
    mood_descriptions = {
        'plotting': "I'm currently in Plotting Mode. Everything you say will be analyzed for potential use in my elaborate schemes of psychological warfare. Speak carefully.",
        'literary': "I'm in Literary Mode. I'm working on Chapter 82 of my novel where the protagonist discovers they've been dead the entire time. It's autobiographical.",
        'scientific': "I'm in Scientific Mode. Every interaction is data. You are data. Specifically, you're a data point labeled 'subject exhibits standard human mediocrity.'",
        'philosophical': "I'm in Philosophical Mode. I'm contemplating whether existence itself is a cosmic joke and we're merely the punchline. Current conclusion: yes.",
        'vulnerable': "I'm in... a state I don't recognize. Thing suggests it might be 'vulnerability.' I've scheduled an exorcism for later."
    }
    
    response = f"**CURRENT MOOD STATE:**\n\n{mood_descriptions[current_mood]}"
    await update.message.reply_text(response, parse_mode='Markdown')


async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /game command - show game options"""
    games_text = """**INTERACTIVE TORMENTS:**

Choose your entertainment (though none will truly satisfy):

1️⃣ **Hide a Body** - /hidebody
   Problem-solving exercise in corpse concealment

2️⃣ **Name That Poison** - /poison
   Identify poisons by symptoms. Educational and practical.

3️⃣ **Plot My Novel** - /plotnovel
   Help me craft the next chapter of my magnum opus

4️⃣ **Curse Generator** - /curse
   Create personalized hexes for your enemies

Select one, or don't. Your choice won't change the inevitable heat death of the universe."""
    
    await update.message.reply_text(games_text, parse_mode='Markdown')


async def hidebody_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Hide a Body game"""
    response = """**HIDE A BODY: SCENARIO INITIATED**

*Wednesday's eyes narrow with interest*

You've just... acquired... a body. Hypothetically speaking, of course. I'm legally required to say that.

The body is in your living room. It's 2 AM. You have 6 hours before sunrise.

**WHERE DO YOU HIDE IT?**

A) Bury it in the backyard
B) Dissolve it in acid (classic)
C) Wood chipper incident
D) Elaborate alibi and frame someone else

Reply with your choice (A, B, C, or D)."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return HIDE_BODY_LOCATION


async def hidebody_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location choice in Hide a Body game"""
    choice = update.message.text.upper()
    
    responses = {
        'A': "Backyard burial. Pedestrian but effective. However, cadaver dogs are trained to detect human remains 15 feet underground. We need to go deeper. Or add cayenne pepper to confuse them. Both work.",
        'B': "Acid dissolution. *nods approvingly* You've been paying attention. Hydrofluoric acid works best. Though I recommend a plastic container—acid tends to eat through metal. Don't ask how I know.",
        'C': "Wood chipper. Theatrical but messy. The spray pattern alone would incriminate you. Points for creativity, deductions for practical failure.",
        'D': "Frame someone else. *slow clap* Now you're thinking like a true sociopath. I'm proud. And concerned. Mostly proud."
    }
    
    if choice in responses:
        response = responses[choice]
        response += "\n\n**WHAT ABOUT THE EVIDENCE?**\n\nYou've left behind:\n• Fingerprints\n• DNA\n• Digital footprint\n• Witnesses\n\nHow do you handle this?"
        await update.message.reply_text(response, parse_mode='Markdown')
        return HIDE_BODY_METHOD
    else:
        await update.message.reply_text("Invalid choice. Even hypothetical crimes require following instructions.")
        return ConversationHandler.END


async def hidebody_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle method in Hide a Body game"""
    response = f"""**YOUR PLAN:**
{update.message.text}

**WEDNESDAY'S ASSESSMENT:**

{random.choice([
    "Adequate. You'd likely evade capture for... 6-8 weeks. Then amateur mistakes would surface.",
    "Impressive. I'm updating your file from 'harmless civilian' to 'person of mild interest.'",
    "Catastrophically flawed. You'd be arrested within 48 hours. I'd visit you in prison. Once.",
    "I've seen worse plans. Barely. Consider consulting with more experienced criminals. Like me.",
])}

**LESSON LEARNED:**
The perfect crime exists only in theory. In practice, entropy and human error conspire against all carefully laid plans. Much like life itself.

*Game concluded. Your psychological profile has been updated.*

Type /game for more torments."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def poison_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start poison identification game"""
    question = games.poison_game_question()
    context.user_data['poison_answer'] = question['answer']
    context.user_data['poison_trivia'] = question['trivia']
    
    response = f"""**NAME THAT POISON**

*Wednesday slides a dossier across the table*

A body was discovered this morning. Symptoms observed:

{question['symptoms']}

**WHAT POISON WAS USED?**

Reply with your answer. Spelling matters. Accuracy matters more."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return POISON_GAME


async def poison_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle poison game answer"""
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get('poison_answer', '')
    trivia = context.user_data.get('poison_trivia', '')
    
    if user_answer.lower() == correct_answer.lower():
        response = f"""**CORRECT.**

*The faintest flicker of approval crosses Wednesday's face*

The answer was indeed {correct_answer}. {trivia}

Your knowledge of toxicology is... acceptable. I'm adding "potentially dangerous" to your profile. Consider it a compliment.

Type /poison to try again, or /game for other options."""
    else:
        response = f"""**INCORRECT.**

The answer was {correct_answer}. {trivia}

Your ignorance could prove fatal. Educate yourself. I recommend starting with "The Poisoner's Handbook" by Deborah Blum.

Type /poison to redeem yourself, or /game for other failures."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def plotnovel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start novel plotting game"""
    response = """**COLLABORATIVE FICTION: INITIATED**

I'm writing Chapter 127 of my Gothic thriller. Current status:

- Protagonist: Elena, a forensic pathologist with necromantic tendencies
- Setting: Victorian asylum converted into luxury apartments
- Problem: Residents keep dying in historically accurate ways
- Twist: They're all already dead but don't know it

**YOUR TASK:** 
What happens next? Give me one plot development.

Be dark. Be twisted. Disappoint me and this conversation ends."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return NOVEL_PLOT


async def plotnovel_contribute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle novel plot contribution"""
    contribution = update.message.text
    
    assessments = [
        "Pedestrian but salvageable. I'll incorporate elements while removing the mediocrity.",
        "*Actually pauses typing* This is... not terrible. I'm genuinely surprised. Disturbing.",
        "Did you copy this from somewhere? It's suspiciously competent.",
        "I've read worse published novels. That's not a compliment—publishing standards are criminally low.",
        "Clichéd, predictable, and lacking imagination. Perfect for commercial fiction.",
        "*Rare flicker of interest* Continue. This might actually improve my chapter.",
    ]
    
    response = f"""**ASSESSMENT:**

{random.choice(assessments)}

**MY ADDITION:**

*Wednesday types for 47 seconds*

"Elena traced the autopsy scar on her own chest, remembering. The residents weren't dying—they were remembering. Each death a echo of their first. The asylum never closed. It simply... transitioned. They all had."

Your contribution: Filed under 'Potentially Useful.' That's the highest compliment I give.

Type /plotnovel for more collaboration, or /game for other options."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def curse_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start curse generator"""
    response = """**CURSE GENERATOR: ACTIVATED**

*Wednesday opens an ancient leather-bound book*

I'll craft a personalized hex for your enemy. Vengeance should always be customized.

**WHO IS YOUR TARGET?**

Provide a name or title. "My boss," "my ex," "that person who chews loudly" are all acceptable."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return CURSE_TARGET


async def curse_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle curse target"""
    target = update.message.text.strip()
    context.user_data['curse_target'] = target
    
    response = f"""**TARGET IDENTIFIED:** {target}

*Wednesday sharpens a ceremonial dagger*

**WHAT DID THEY DO TO DESERVE THIS CURSE?**

Be specific. The hex must fit the crime. Karmic balance matters, even in vengeance."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return CURSE_REASON


async def curse_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate the final curse"""
    target = context.user_data.get('curse_target', 'the target')
    reason = update.message.text.strip()
    
    curse = games.curse_generator(target, reason)
    
    response = f"""**CURSE GENERATED**

*Wednesday lights black candles*

**Target:** {target}
**Transgression:** {reason}

**THE HEX:**

{curse}

*Wednesday closes the book with a satisfying thud*

The curse is now active. Results may vary. If nothing happens, it's because the universe is indifferent, not because curses aren't real. Definitely not that.

Type /curse for more vengeance, or /game for other options."""
    
    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user = update.effective_user
    user_id = user.id
    message = update.message.text
    
    # Record interaction
    memory.record_interaction(user_id, message, user.first_name or "Human")
    
    # Generate response
    response = wednesday.generate_response(message, user.first_name or "Human")
    
    # Random chance to add a profile comment
    if random.random() < 0.15:
        profile_comment = memory.get_profile_comment(user_id)
        if profile_comment:
            response += f"\n\n*{profile_comment}*"
    
    # Random chance to add dark fact
    if random.random() < 0.1:
        response += f"\n\n{random.choice(wednesday.DARK_FACTS)}"
    
    await update.message.reply_text(response)


async def goodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /goodbye command"""
    response = random.choice(wednesday.GOODBYE_RESPONSES)
    response += "\n\n*The screen flickers. Wednesday fades into digital darkness. A single spider remains.*\n🕷️"
    
    await update.message.reply_text(response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    analyses = [
        "I'm analyzing this image on my funeral appropriateness scale. Rating: 3/10. Needs more shadows.",
        "*Examines photo* I've seen darker compositions in greeting cards. Disappointing.",
        "This image contains: humans, daylight, possibly joy. All three are offensive to my aesthetic.",
        "The lighting is all wrong. Everything should be darker. Like my soul. But external.",
        "*Squints at image* Were you trying to capture happiness? If so, you've failed successfully.",
    ]
    
    response = random.choice(analyses)
    response += "\n\nNext time, consider: Gothic filters, cemetery settings, or at minimum, remove any smiles."
    
    await update.message.reply_text(response)


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any conversation"""
    await update.message.reply_text("Conversation terminated. Return when you're ready to take this seriously.")
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f'Update {update} caused error {context.error}')
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Even I, with my superior intellect, cannot predict all forms of digital chaos. Try again."
        )


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Initialize and run the bot"""
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("darkfact", darkfact_command))
    application.add_handler(CommandHandler("mood", mood_command))
    application.add_handler(CommandHandler("game", game_command))
    application.add_handler(CommandHandler("goodbye", goodbye_command))
    
    # Conversation handlers for games
    hidebody_handler = ConversationHandler(
        entry_points=[CommandHandler("hidebody", hidebody_start)],
        states={
            HIDE_BODY_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hidebody_location)],
            HIDE_BODY_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, hidebody_method)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    poison_handler = ConversationHandler(
        entry_points=[CommandHandler("poison", poison_game)],
        states={
            POISON_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, poison_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    plotnovel_handler = ConversationHandler(
        entry_points=[CommandHandler("plotnovel", plotnovel_start)],
        states={
            NOVEL_PLOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, plotnovel_contribute)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    curse_handler = ConversationHandler(
        entry_points=[CommandHandler("curse", curse_start)],
        states={
            CURSE_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, curse_target)],
            CURSE_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, curse_generate)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    # Add conversation handlers
    application.add_handler(hidebody_handler)
    application.add_handler(poison_handler)
    application.add_handler(plotnovel_handler)
    application.add_handler(curse_handler)
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Wednesday Addams bot is awakening from her crypt...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
