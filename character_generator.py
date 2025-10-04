#!/usr/bin/env python3
"""
Baldur's Gate 3 — Character Forge Mini-Game
Save this file and run in a terminal to play interactively:
    python3 character_generator.py

Features:
- 18+ branching / weighted questions that modify hidden stats
- Randomness for quirks, twists, and replayability
- Maps stats to a BG3-style class/background/role suggestion
- Outputs a flavorful character write-up and roleplay hooks
- Optional non-interactive "quick run" mode for demos (use --demo)

This is intentionally written as a sandbox for fiction authors and roleplayers.
"""

import random, sys, textwrap

# --- Configuration: Stats, Questions, and Pools ---
STAT_KEYS = [
    "Bravery", "Cunning", "Faith", "Charm", "Curiosity",
    "Stoicism", "Recklessness", "Empathy", "Mischief", "Honor"
]

# Questions: each option maps to one or more stat changes (can be positive or negative)
QUESTIONS = [
    {
        "q": "When you hear the call to adventure, your first thought is:",
        "opts": {
            "a": ("Armor on. If there's danger, meet it head-on.", {"Bravery": 2, "Stoicism": 1}),
            "b": ("Plot something clever; advantage wins fights.", {"Cunning": 2, "Mischief": 1}),
            "c": ("What ancient secret waits? Research first.", {"Curiosity": 2, "Cunning": 1}),
            "d": ("Who can I charm into helping me? People matter.", {"Charm": 2, "Empathy": 1}),
            "e": ("I go because it's my duty. Someone must.", {"Faith": 2, "Honor": 1})
        }
    },
    {
        "q": "You find a locked chest. How do you approach it?",
        "opts": {
            "a": ("Smash it open and hope for the best.", {"Bravery": 2, "Recklessness": 2}),
            "b": ("Pick the lock or lift the key quietly.", {"Cunning": 2, "Mischief": 1}),
            "c": ("Examine runes, study wards and traps.", {"Curiosity": 2, "Stoicism": 1}),
            "d": ("Ask someone else to open it. Conversation first.", {"Charm": 2, "Empathy": 1}),
            "e": ("Pray or ask the gods for a sign about it.", {"Faith": 2, "Honor": 1})
        }
    },
    {
        "q": "Someone insults your homeland in public. Your reaction:",
        "opts": {
            "a": ("Sword in hand; teach them respect.", {"Bravery": 2, "Honor": 1}),
            "b": ("A cutting joke that leaves them speechless.", {"Cunning": 2, "Mischief": 1}),
            "c": ("You make a calm note of it and study why.", {"Curiosity": 1, "Stoicism": 1}),
            "d": ("Diffuse with charm and a laugh.", {"Charm": 2}),
            "e": ("You forgive; anger accomplishes little.", {"Empathy": 2, "Faith": 1})
        }
    },
    {
        "q": "Campfire: a child asks why stars burn. You say:",
        "opts": {
            "a": ("They are watchful sentinels, ready for war.", {"Bravery": 1, "Honor": 1}),
            "b": ("They’re holes poked into the dark by the bored gods.", {"Mischief": 2, "Cunning": 1}),
            "c": ("Burning suns, far away—physics, wonder, repeat.", {"Curiosity": 2}),
            "d": ("Because someone needed a good story stage.", {"Charm": 2}),
            "e": ("They remind us that light outlasts suffering.", {"Faith": 2, "Empathy": 1})
        }
    },
    {
        "q": "Your party is ambushed at night. You:",
        "opts": {
            "a": ("Charge with torch aloft!", {"Bravery": 2, "Recklessness": 2}),
            "b": ("Slip, stab, vanish—be a whisper.", {"Cunning": 2, "Mischief": 1}),
            "c": ("Cast a spell from memory; magic solves problems.", {"Curiosity": 2, "Stoicism": 1}),
            "d": ("Inspire the group—words make steel.", {"Charm": 2, "Honor": 1}),
            "e": ("Shield the wounded and pray for them.", {"Faith": 2, "Empathy": 1})
        }
    },
    {
        "q": "You meet a beggar who knows a secret — how do you extract it?",
        "opts": {
            "a": ("Intimidate until they speak.", {"Bravery": 1, "Recklessness": 1}),
            "b": ("Pay or ply them with coin and charm.", {"Charm": 2, "Cunning": 1}),
            "c": ("Offer help in exchange; kindness works.", {"Empathy": 2}),
            "d": ("Trick them with a small riddle.", {"Mischief": 2, "Cunning": 1}),
            "e": ("Research elsewhere—books over people.", {"Curiosity": 2})
        }
    },
    {
        "q": "You are betrayed by an ally — what is your course?",
        "opts": {
            "a": ("A duel; honor demands satisfaction.", {"Bravery": 2, "Honor": 2}),
            "b": ("A cold, calculated scheme for revenge.", {"Cunning": 2, "Stoicism": 1}),
            "c": ("An emotional implosion—you nurse the wound.", {"Empathy": 2, "Stoicism": -1}),
            "d": ("Forgive publicly and watch them squirm.", {"Charm": 1, "Mischief": 1}),
            "e": ("Appeal to your god and let them judge.", {"Faith": 2})
        }
    },
    {
        "q": "Which contradiction appeals to you most as a roleplaying seed?",
        "opts": {
            "a": ("Fearless fighter who collects delicate teacups.", {"Stoicism": 1, "Bravery": 1}),
            "b": ("Smooth talker who lies to themselves most.", {"Charm": 1, "Mischief": 1}),
            "c": ("Scholar who creates accidental chaos.", {"Curiosity": 2, "Mischief": 1}),
            "d": ("Pious zealot who sometimes doubts in private.", {"Faith": 2, "Stoicism": 1}),
            "e": ("Rogue with an odd strict code of honor.", {"Cunning": 2, "Honor": 2})
        }
    },
    {
        "q": "Your signature move in a tavern brawl is:",
        "opts": {
            "a": ("Shield bash and a heroic speech.", {"Bravery": 1, "Charm": 1}),
            "b": ("Slip behind the bar and trip everyone.", {"Cunning": 2, "Mischief": 2}),
            "c": ("Set a distracting minor illusion.", {"Curiosity": 2}),
            "d": ("Sing a song that confuses the thugs.", {"Charm": 2}),
            "e": ("Refuse to fight and try to calm folks.", {"Empathy": 2})
        }
    },
    {
        "q": "You find a magical patron offering power at a price. You:",
        "opts": {
            "a": ("Refuse. Power from bargains is suspect.", {"Honor": 1, "Faith": 1}),
            "b": ("Carefully read the contract. Every price has loopholes.", {"Curiosity": 2, "Cunning": 1}),
            "c": ("Accept! A cheeky bargain is an opportunity.", {"Mischief": 2, "Recklessness": 1}),
            "d": ("Negotiate terms and charm the patron.", {"Charm": 2, "Cunning": 1}),
            "e": ("Pray for guidance and act under divine counsel.", {"Faith": 2})
        }
    },
    {
        "q": "Pick a petty obsession for flavor:",
        "opts": {
            "a": ("Collecting spoons.", {"Mischief": 1}),
            "b": ("Naming every horse you see.", {"Charm": 1}),
            "c": ("Studying odd handwriting.", {"Curiosity": 1}),
            "d": ("Keeping a secret ledger of debts.", {"Cunning": 1}),
            "e": ("Polishing armor at inopportune times.", {"Stoicism": 1})
        }
    },
    {
        "q": "Your greatest fear, deep down, is:",
        "opts": {
            "a": ("Cowardice—being remembered as small.", {"Bravery": 1, "Honor": 1}),
            "b": ("Irrelevance—no songs sung of your deeds.", {"Charm": 1, "Stoicism": 1}),
            "c": ("Losing your mind to curiosity's costs.", {"Curiosity": 1, "Stoicism": 1}),
            "d": ("Betrayal from those you trust.", {"Empathy": 1, "Honor": 1}),
            "e": ("Being trapped by duty and never choosing.", {"Faith": 1, "Recklessness": 1})
        }
    },
    {
        "q": "You're given an impossible moral choice that harms a few to save many. You:",
        "opts": {
            "a": ("Sacrifice yourself if needed—honor above all.", {"Honor": 2, "Bravery": 1}),
            "b": ("Calculate the outcome and pick the most efficient option.", {"Cunning": 2}),
            "c": ("Try to find a third option; creativity wins.", {"Curiosity": 1, "Charm": 1}),
            "d": ("Refuse to make the choice; it's not yours to make.", {"Faith": 1, "Empathy": 1}),
            "e": ("Do whatever is required; the ends justify the means.", {"Recklessness": 2, "Stoicism": 1})
        }
    },
    {
        "q": "Your preferred role in a party is:",
        "opts": {
            "a": ("Frontline: take hits and deal them.", {"Bravery": 2, "Stoicism": 1}),
            "b": ("Scout: get info and open doors.", {"Cunning": 2, "Curiosity": 1}),
            "c": ("Controller: manipulate the battlefield.", {"Curiosity": 2, "Mischief": 1}),
            "d": ("Face: negotiate, distract, seduce.", {"Charm": 2, "Empathy": 1}),
            "e": ("Healer/Anchor: keep the group alive.", {"Faith": 2, "Empathy": 1})
        }
    },
    {
        "q": "What adjective best decorates your fighting style?",
        "opts": {
            "a": ("Brutal", {"Bravery": 1, "Recklessness": 1}),
            "b": ("Sly", {"Cunning": 1}),
            "c": ("Elegant", {"Charm": 1, "Stoicism": 1}),
            "d": ("Arcane", {"Curiosity": 1}),
            "e": ("Righteous", {"Faith": 1, "Honor": 1})
        }
    },
    {
        "q": "If you could steal one abstract thing from a king it would be:",
        "opts": {
            "a": ("Their crown—symbols matter.", {"Honor": 1, "Bravery": 1}),
            "b": ("Their secrets—blackmail is useful.", {"Cunning": 2}),
            "c": ("Their library—knowledge is power.", {"Curiosity": 2}),
            "d": ("Their applause—fame's currency.", {"Charm": 1}),
            "e": ("Their forgiveness—free the oppressed.", {"Faith": 1, "Empathy": 1})
        }
    },
    {
        "q": "Which creature would you secretly like to befriend?",
        "opts": {
            "a": ("A loyal hound.", {"Honor": 1, "Empathy": 1}),
            "b": ("A clever fox.", {"Cunning": 1}),
            "c": ("An ancient owl.", {"Curiosity": 1}),
            "d": ("A mischievous raccoon.", {"Mischief": 1}),
            "e": ("A noble stag.", {"Stoicism": 1, "Faith": 1})
        }
    },
    {
        "q": "Final theatrical flourish: choose your signature line to speak in battle:",
        "opts": {
            "a": ("'For honor!' (and charge)", {"Honor": 1}),
            "b": ("'Now you've made a mistake.' (quietly lethal)", {"Cunning": 1}),
            "c": ("'Witness wonders!' (arcane flourish)", {"Curiosity": 1}),
            "d": ("'Sing with me!' (inspire allies)", {"Charm": 1}),
            "e": ("'By their light, we stand!' (blessing)", {"Faith": 1})
        }
    },
]

# Pools for flavors, quirks, subclasses, races
QUIRKS = [
    "You loudly narrate your actions like a bard in training.",
    "You keep a pet rock you believe is an omen.",
    "You whisper to your weapons as if they are old friends.",
    "You have an unreasonable hatred of geese.",
    "You compulsively organize coins by size and smell.",
    "You misquote ancient proverbs with hilarious results.",
    "You break into rhymes when nervous.",
    "You always carry a folded map of a place you've never visited."
]

BACKGROUNDS = [
    ("Sage", "You spent years in study, seeking knowledge above all."),
    ("Charlatan", "You learned deception to survive; silver tongue included."),
    ("Soldier", "Trained with discipline and battlefield experience."),
    ("Acolyte", "Raised in service to a faith and its rituals."),
    ("Urchin", "You know the streets, the shortcuts, and the smells."),
    ("Folk Hero", "You saved people who couldn't save themselves; beloved locally."),
    ("Guild Artisan", "Crafts and commerce are your trade."),
    ("Noble", "Born to rank; duty and pride define you."),
    ("Outlander", "You grew up far from civilized centers; hunter, forager."),
]

CLASSES = [
    "Fighter", "Barbarian", "Paladin", "Ranger", "Rogue", "Bard",
    "Cleric", "Druid", "Wizard", "Sorcerer", "Warlock", "Monk"
]

SUBCLASS_SUGGESTIONS = {
    "Fighter": ["Battle Master (tactical)", "Champion (simple and reliable)", "Eldritch Knight (magic-armored)"],
    "Barbarian": ["Berserker (rage pure)", "Totem (spiritual flavors)"],
    "Paladin": ["Oath of Devotion", "Oath of Vengeance", "Oath of the Ancients"],
    "Ranger": ["Gloom Stalker", "Hunter", "Beast Master"],
    "Rogue": ["Thief", "Assassin", "Arcane Trickster"],
    "Bard": ["College of Lore", "College of Valor", "College of Satire"],
    "Cleric": ["Life Domain", "War Domain", "Trickery Domain"],
    "Druid": ["Circle of the Land", "Circle of the Moon"],
    "Wizard": ["School of Evocation", "School of Illusion", "School of Divination"],
    "Sorcerer": ["Draconic Bloodline", "Wild Magic", "Divine Soul"],
    "Warlock": ["The Fiend", "The Great Old One", "The Archfey"],
    "Monk": ["Way of the Open Hand", "Way of Shadow", "Way of the Four Elements"]
}

RACE_SUGGESTIONS = [
    "Human", "Elf (High/Eladrin/Drow flavor)", "Half-Elf", "Dwarf", "Halfling",
    "Githyanki/Githzerai (BG3-specific flavor)", "Tiefling", "Half-Orc", "Gnome"
]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral",
    "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"
]

# --- Core generator functions ---

def clamp_stats(stats):
    for k in stats:
        if stats[k] < -3: stats[k] = -3
        if stats[k] > 10: stats[k] = 10
    return stats

def init_stats():
    return {k: 0 for k in STAT_KEYS}

def ask_interactive():
    stats = init_stats()
    print("\nWelcome to the Baldur's Gate 3 — Character Forge Mini-Game!")
    print("Answer the prompts as your *character* (not yourself) to build unique NPCs or player avatars.\n")
    for idx, q in enumerate(QUESTIONS, 1):
        print(f"Q{idx}. {q['q']}")
        for key, (txt, _) in sorted(q["opts"].items()):
            print(f"  {key}) {txt}")
        choice = None
        while choice not in q["opts"]:
            choice = input("Choose: ").strip().lower()
            if choice == "" and "default" in q:
                choice = q["default"]
            if choice not in q["opts"]:
                print("Invalid option. Pick one of:", ", ".join(sorted(q["opts"].keys())))
        _, delta = q["opts"][choice]
        for sk, val in delta.items():
            stats[sk] = stats.get(sk, 0) + val
        clamp_stats(stats)
        print()  # blank line between questions
    return stats

def synthesize(stats, seed=None):
    random_gen = random.Random(seed)
    stats = clamp_stats(stats.copy())

    # Decide primary tendencies by sorting stats
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    top = [k for k, v in sorted_stats if v == sorted_stats[0][1]]
    top3 = [k for k, v in sorted_stats[:3]]

    # Simple mapping heuristics
    # Score buckets for different class candidates
    scores = {c: 0 for c in CLASSES}

    # Heuristics mapping (weighted)
    if stats["Bravery"] >= 3:
        scores["Fighter"] += 2
        scores["Barbarian"] += 2
    if stats["Recklessness"] >= 2:
        scores["Barbarian"] += 2
        scores["Sorcerer"] += 1
    if stats["Faith"] >= 3 or stats["Honor"] >= 3:
        scores["Paladin"] += 3
        scores["Cleric"] += 2
    if stats["Cunning"] >= 3 and stats["Mischief"] >= 2:
        scores["Rogue"] += 3
        scores["Warlock"] += 1
    if stats["Charm"] >= 3 and stats["Mischief"] >= 1:
        scores["Bard"] += 3
    if stats["Curiosity"] >= 3:
        scores["Wizard"] += 3
        scores["Druid"] += 1
    if stats["Empathy"] >= 3 and stats["Faith"] >= 1:
        scores["Cleric"] += 2
        scores["Druid"] += 1
    if stats["Stoicism"] >= 2 and stats["Bravery"] >= 2:
        scores["Monk"] += 2
        scores["Fighter"] += 1
    if stats["Cunning"] >= 2 and stats["Bravery"] >= 1:
        scores["Ranger"] += 2
    if stats["Curiosity"] >= 2 and stats["Mischief"] >= 2:
        scores["Warlock"] += 2
    if stats["Charm"] >= 2 and stats["Bravery"] >= 1:
        scores["Paladin"] += 1
        scores["Bard"] += 1
    if stats["Honor"] >= 2 and stats["Faith"] >= 1:
        scores["Paladin"] += 2

    # Tiebreaker randomness factor
    for k in scores:
        scores[k] += random_gen.randint(0, 2)

    # Choose top scoring class
    chosen_class = max(scores.items(), key=lambda x: x[1])[0]

    # Pick background biased by stats
    bg_score = {}
    for bg, desc in BACKGROUNDS:
        bg_score[bg] = 0
        if bg == "Sage" and stats["Curiosity"] >= 2: bg_score[bg] += 3
        if bg == "Charlatan" and stats["Mischief"] >= 2: bg_score[bg] += 3
        if bg == "Soldier" and stats["Bravery"] >= 2: bg_score[bg] += 3
        if bg == "Acolyte" and stats["Faith"] >= 2: bg_score[bg] += 3
        if bg == "Urchin" and stats["Cunning"] >= 2: bg_score[bg] += 2
        if bg == "Folk Hero" and stats["Honor"] >= 2: bg_score[bg] += 2
        if bg == "Guild Artisan" and stats["Charm"] >= 2: bg_score[bg] += 1
        if bg == "Noble" and stats["Honor"] >= 2: bg_score[bg] += 2
        if bg == "Outlander" and stats["Stoicism"] >= 1: bg_score[bg] += 1
        # add small randomness
        bg_score[bg] += random_gen.randint(0, 2)

    chosen_bg = max(bg_score.items(), key=lambda x: x[1])[0]
    chosen_bg_desc = next(desc for bg, desc in BACKGROUNDS if bg == chosen_bg)

    # Choose race and alignment randomly but biased
    chosen_race = random_gen.choice(RACE_SUGGESTIONS)
    chosen_alignment = random_gen.choice(ALIGNMENTS)

    # Pick subclass suggestions
    subclass_list = SUBCLASS_SUGGESTIONS.get(chosen_class, [])
    if subclass_list:
        subclass_choice = random_gen.choice(subclass_list)
    else:
        subclass_choice = "Any"

    # Pick quirks and flaws
    quirk = random_gen.choice(QUIRKS)
    flaw = random_gen.choice([
        "Tells awful jokes at bad moments.",
        "Has a tiny, embarrassing secret (e.g., loves knitting).",
        "Is wildly superstitious about something mundane.",
        "Trust issues with authority figures.",
        "Compulsively hoards small trinkets."
    ])

    # Generate short flavor text based on stats
    tone = "balanced"
    if stats["Mischief"] >= 3:
        tone = "mischievous"
    elif stats["Faith"] >= 3:
        tone = "devout"
    elif stats["Curiosity"] >= 3:
        tone = "scholarly"
    elif stats["Bravery"] >= 3:
        tone = "bold"

    # Roleplay hooks
    hooks = [
        "You once failed spectacularly at something famous; it's a private shame.",
        "You have a mysterious benefactor whose motives are unclear.",
        "Someone from your past seeks your help—and owes you nothing.",
        "A small symbol you carry attracts the attention of cultists."
    ]

    # Build character object
    char = {
        "class": chosen_class,
        "subclass suggestion": subclass_choice,
        "background": chosen_bg,
        "background blurb": chosen_bg_desc,
        "race suggestion": chosen_race,
        "alignment": chosen_alignment,
        "quirk": quirk,
        "flaw": flaw,
        "tone": tone,
        "hooks": random_gen.sample(hooks, 2),
        "stats": stats,
        "top_stats": top3
    }

    # Compose a little paragraph summary
    summary_lines = []
    summary_lines.append(f"You are a {char['race suggestion']} {char['class']} ({char['subclass suggestion']}) — {char['alignment']}.")
    summary_lines.append(f"Background: {char['background']} — {char['background blurb']}")
    summary_lines.append(f"Tone: {char['tone']}. Quirk: {char['quirk']}")
    summary_lines.append(f"Flaw: {char['flaw']}. Roleplay hooks: {', '.join(char['hooks'])}.")
    summary_lines.append("Leading stats: " + ", ".join(char['top_stats']))

    char['summary'] = "\n".join(summary_lines)
    # Suggest mechanical starting tips for BG3
    tips = []
    if char["class"] in ("Wizard", "Sorcerer", "Warlock", "Bard"):
        tips.append("Consider Intelligence/Charisma based spells and keep a few control/utility spells.")
    if char["class"] in ("Fighter", "Paladin", "Barbarian", "Ranger"):
        tips.append("Heavy armor and front-line options are your bread and butter.")
    if char["background"] == "Sage":
        tips.append("Look for lore interactions; you might unlock extra dialogue options.")
    if char["quirk"] and "geese" in char["quirk"]:
        tips.append("Avoid lakes in roleplay or it will end badly.")
    char['tips'] = tips

    return char

def pretty_print_character(char):
    print("\n" + "="*60)
    print("CHARACTER SUMMARY")
    print("="*60)
    print(char['summary'])
    print("\nStats:")
    for k, v in char["stats"].items():
        print(f"  {k:12}: {v:+d}")
    print("\nMechanical tips & roleplay pointers:")
    for t in char["tips"]:
        print(f" - {t}")
    print("\nSuggested roleplay hooks:")
    for h in char["hooks"]:
        print(f" - {h}")
    print("="*60 + "\n")

def interactive_main():
    stats = ask_interactive()
    seed = random.randint(0, 10_000_000)
    char = synthesize(stats, seed=seed)
    pretty_print_character(char)
    print("Save this file or copy the summary to keep your character. Enjoy BG3!")

def quick_demo(seed=None):
    # Simulate random answers to show sample output
    seed = seed if seed is not None else random.randint(0, 999999)
    random.seed(seed)
    stats = init_stats()
    # simulate by picking options biased by a small probability
    for q in QUESTIONS:
        choice = random.choice(list(q['opts'].keys()))
        _, delta = q['opts'][choice]
        for sk, val in delta.items():
            stats[sk] = stats.get(sk, 0) + val
    char = synthesize(stats, seed=seed)
    print(f"--- Demo run (seed {seed}) ---")
    pretty_print_character(char)

# --- Script entrypoint ---
def main():
    if "--demo" in sys.argv:
        quick_demo()
        return
    if "--seed" in sys.argv:
        try:
            seed_index = sys.argv.index("--seed") + 1
            seed = int(sys.argv[seed_index])
            random.seed(seed)
        except Exception:
            seed = None
    else:
        seed = None
    interactive_main()

if __name__ == "__main__":
    main()
