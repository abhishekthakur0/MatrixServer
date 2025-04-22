import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from synapse.module_api import ModuleApi
from synapse.events import EventBase

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TextMasker:
    def __init__(self, config: Dict, api: ModuleApi):
        logger.info("Initializing TextMasker module")
        self.api = api
        self.config = config
        
        # Comprehensive pattern for various phone number formats
        self.phone_pattern = r'''
            # International format with optional country code
            (?:\+\d{1,3}[-.\s]?)?
            
            # Various formats:
            (?:
                # Standard format: (123) 456-7890
                \(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}
                |
                # International format: +1 234 567 8900
                \d{1,4}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}
                |
                # Continuous format: 1234567890
                \d{10}
                |
                # With separators: 123-456-7890 or 123.456.7890
                \d{3}[-.]\d{3}[-.]\d{4}
                |
                # With spaces: 123 456 7890
                \d{3}\s\d{3}\s\d{4}
                |
                # With mixed separators: 123_456@7890
                \d{3}[_\-@#%&\.]\d{3}[_\-@#%&\.]\d{4}
                |
                # Extension format: 123-456-7890 x1234
                \d{3}[-.\s]?\d{3}[-.\s]?\d{4}\s*(?:x|ext|extension)?\s*\d{1,5}
                |
                # Repeating number patterns: 95 95 95 95 95
                (?:\d{2,3}\s?){3,}
                |
                # Ten consecutive numbers with spaces: 1 2 3 4 5 6 7 8 9 0
                (?:\d\s){9}\d
            )
            
            # Word boundary to avoid partial matches
            \b
        '''
        self.phone_pattern = re.compile(self.phone_pattern, re.VERBOSE | re.IGNORECASE)
        
        # Comprehensive email pattern
        self.email_pattern = r'''
            # Local part (before @)
            (?:
                # Standard email characters
                [a-zA-Z0-9._%+-]+
                |
                # Quoted strings with special characters
                "[^"\\]*(?:\\.[^"\\]*)*"
            )
            @
            # Domain part
            (?:
                # Standard domain
                [a-zA-Z0-9.-]+
                |
                # IP address in brackets
                \[(?:[0-9]{1,3}\.){3}[0-9]{1,3}\]
            )
            \.
            # TLD (2+ characters)
            [a-zA-Z]{2,}
        '''
        self.email_pattern = re.compile(self.email_pattern, re.VERBOSE | re.IGNORECASE)
        
        # Load abusive words from config or use default list
        self.abusive_words = config.get("abusive_words", [
        "🖕","2 girls 1 cup","2g1c","aad","aand","abusive hashtag phrase","abusive word for Pakistan","acronym for bhosdike","acronym for bhosdike","acronym for motherfucker","acronym for motherfucker","acronym for sisterfucker","acronym for sisterfucker","acrotomophilia","alabama hot pocket","alaskan pipeline","alcoholic","alcoholic","alcoholic","alcoholic","anal","anilingus","anus","apeshit","arse","arse","arse","arsehead","arsehole","ass","ass","ass","ass hole","asshole","asshole","asshole","asshole","asshole","asshole","assmunch","auto erotic","autoerotic","b.c.","b.s.d.k","babbe","babbey","babeland","baby batter","baby juice","bahenchod","bakchod","bakchodd","bakchodi","ball gag","ball gravy","ball kicking","ball licking","ball sack","ball sucking","bangbros","bareback","barely legal","barenaked","bastard","bastard","bastard","bastard","bastard","bastard","bastard","bastard","bastardo","bastinado","bbw","bc","bdsm","beaner","beaners","beaver cleaver","beaver lips","behenchod","bestiality","bevakoof","bevda","bevdey","bevkoof","bevkuf","bewakoof","bewda","bewday","bewkoof","bewkuf","bhadua","bhaduaa","bhadva","bhadvaa","bhadwa","bhadwaa","bhenchod","bhenchodd","bhonsdike","bhosada","Bhosadchod","Bhosadchod","Bhosadchodal","Bhosadchodal","bhosda","bhosdaa","bhosdike","bhosdiki","bhosdiwala","bhosdiwale","big black","big breasts","big knockers","big tits","bimbos","birdlock","bitch","bitch","bitch","bitch","bitch","bitches","blabbering","blabbermouth","blabbermouth","black cock","blonde action","blonde on blonde action","blow job","blow your load","blowjob","blue waffle","blumpkin","bollocks","bondage","boner","boob","boobs","boobs","boobs","boobs","boobs","boobs","boobs","booty call","brotherfucker","brown showers","brunette action","bsdk","bube","bubey","bugger","bukkake","bulldyke","bullet vibe","bullshit","bung hole","bunghole","bur","burr","busty","butt","buttcheeks","butthole","buur","buurr","camel toe","camgirl","camslut","camwhore","carpet muncher","carpetmuncher","charsi","chhod","child-fucker","chocolate rosebuds","chod","chodd","chooche","choochi","choot","Christ on a bike","Christ on a cracker","chuchi","chudne","chudney","chudwa","chudwaa","chudwaane","chudwane","chut","chutad","chute","chutia","chutiya","chutiye","chuttad","circlejerk","cleveland steamer","clit","clitoris","clover clamps","clusterfuck","cock","cocks","cocksucker","coon","coons","coprolagnia","coprophilia","cornhole","crap","creampie","cum","cumming","cunnilingus","cunt","dalaal","dalal","dalle","dalley","dammit","damn","damn it","damned","darkie","date rape","daterape","daughter of a whore","deep throat","deepthroat","dendrophilia","dick","dick","dick","dick","dick","dick","dick","dick","dick","dick","dick","dick-head","dickhead","dildo","dingleberries","dingleberry","dirty pillows","dirty sanchez","dog","dog","dog","dog shit","dog shit","dog style","doggie style","doggiestyle","doggy style","doggystyle","dolcett","domination","dominatrix","dommes","donkey","donkey","donkey punch","double dong","double penetration","dp action","druggie","dry hump","dumb ass","dumb-ass","dumbass","dvda","dyke","eat my ass","ecchi","ejaculation","erotic","erotism","escort","eunuch","excreta / faeces","faeces","faeces","faeces","faggot","father-fucker","fatherfucker","fattu","fecal","felch","fellatio","feltch","female squirting","femdom","figging","fingerbang","fingering","fisting","fool","foot fetish","footjob","frotting","fuck","fuck","fuck buttons","fucked","fucked","fucked","fucked","fucker","fucker","fuckin","fucking","fucking","fucking","fucktards","fudge packer","fudgepacker","futanari","g-spot","gaand","gadha","gadhalund","gadhe","gand","gandfat","gandfut","gandiya","gandiye","gandu","gang bang","gay sex","genitals","get fuck","get fuck","giant cock","girl on","girl on top","girls gone wild","goatcx","goatse","god dammit","god damn","goddammit","goddamn","goddamned","goddamnit","godsdamn","gokkun","golden shower","goo","goo girl","goodpoop","goregasm","gote","gotey","gotte","grope","group sex","gu","guro","hag","haggu","hagne","hagney","hand job","handjob","haraamjaada","haraamjaade","haraamkhor","haraamzaade","haraamzyaada","Harami","harami","haramjada","haramkhor","haramzyada","hard core","hardcore","hell","hentai","hit / kill","hit now","holy shit","homoerotic","honkey","hooker","horseshit","hot carl","hot chick","how to kill","how to murder","huge fat","humping","husband of a whore","husband of a whore","idiot","idiot","idiot","idiot","idiot","idiot","idiot","idiot","idiot","idiot","in shit","incest","intercourse","jack off","jack-ass","jackarse","jackass","jail bait","jailbait","jelly donut","jerk","jerk off","Jesus Christ","Jesus fuck","Jesus H. Christ","Jesus Harold Christ","Jesus wept","Jesus, Mary and Joseph","jhaat","jhaatu","jhat","jhatu","jigaboo","jiggaboo","jiggerboo","jizz","juggs","kike","kinbaku","kinkster","kinky","knobbing","kutia","kutiya","Kutta","kutta","kutte","kuttey","kutti","kuttiya","lame","landi","landy","lauda","laude","laudey","launda","laundey","laundi","laundiya","laura","leather restraint","leather straight jacket","lemon party","ling","loda","lode","lolita","lora","loser","lounde","loundi","loundiya","lovemaking","lulli","lund","m.c.","maar","madarchod","madarchodd","madarchood","madarchoot","madarchut","make me come","male squirting","mamme","mammey","maro","marunga","masturbate","masturbate","masturbate","mc","menage a trois","milf","missionary position","moot","mooth","mootne","mother fucker","mother-fucker","mother's cunt","mother's cunt","motherfucker","motherfucker","motherfucker","motherfucker","mound of venus","mr hands","muff diver","muffdiving","mut","muth","mutne","nambla","Napoonsak","nawashi","negro","neonazi","nig nog","nigga","nigger","nigra","nimphomania","nipple","nipple","nipple","nipples","nipples","nsfw images","nude","nudity","nunni","nunnu","nympho","nymphomania","octopussy","omorashi","one cup two girls","one guy one jar","orgasm","orgy","paaji","paedophile","pain in the neck","paji","paki","panties","panty","pedobear","pedophile","pegging","penis","penis","penis of donkey","pesaab","pesab","peshaab","peshab","phone sex","piece of shit","pig","pig","pigfucker","pilla","pillay","pille","pilley","pimp","pimp","pimp","pimp","pimp","pimp","pimp","pimp","pimp","pimp","pisaab","pisab","piss","piss","piss","piss","piss","piss","piss","piss / pee","piss / pee","piss pig","pissed off","pissing","pisspig","pkmkb","playboy","pleasure chest","pole smoker","ponyplay","poof","poon","poontang","poop chute","poopchute","porkistan","porn","porno","pornography","prick","prince albert piercing","prostitute","prostitute","prostitute","prostitute","pthc","pubes","pubic hair","pubic hair","pubic hair","pubic hair","punany","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy","pussy fucker","pussy fucker","pussy fucker","pussy fucker","queaf","queef","quim","raand","raghead","raging boner","rand","randi","randy","rape","raping","rapist","rectum","retard","reverse cowgirl","rimjob","rimming","rosy palm","rosy palm and her 5 sisters","rusty trombone","s&m","sadism","santorum","scat","schlong","scissoring","semen","sex","sexo","sexy","shaved beaver","shaved pussy","shemale","shibari","shit","shit","shit","shit ass","shitblimp","shite","shitty","Shoot!","shota","shrimping","Shut up!!","sibling fucker","sisterfuck","sisterfucker","sisterfucker","sisterfucker","sisterfucker","sisterfucker","skeet","slanteye","slut","slut","slut","slut","slut","small sized penis","small sized penis","smut","snatch","snowballing","sodomize","sodomy","son of a bitch","son of a dog","son of a dog","son of a dog","son of a dog","son of a whore","son of a whore","son of a whore","spastic","spic","splooge","splooge moose","spooge","spread legs","spunk","strap on","strapon","strappado","strip club","stupid","style doggy","suar","suar","Suar ki aulad","suck","sucks","suicide girls","sultry women","swastika","sweet Jesus","swinger","tainted love","taste my","tatte","tatti","tatty","tea bagging","testicles","testicles","testicles","testicles","testicles","testicles","threesome","throating","ticked off","tied up","tight white","timid / fearful","tit","tits","titties","titty","to excrete","to excrete","to excrete","to piss / pee","to piss / pee","tongue in a","topless","tosser","towelhead","tranny","tribadism","tub girl","tubgirl","tushy","twat","twink","twinkie","two girls one cup","ullu","Ullu ka pattha","undressing","upskirt","urethra play","urophilia","useless","useless","vagina","venus mound","vibrator","violet wand","vorarephilia","voyeur","vulva","wank","wanker","wet dream","wetback","white power","will kill","wimp","wrapping men","wrinkled starfish","xx","xxx","yaoi","yellow showers","yiffy","your mother","zoophilia"
    ])
        logger.debug(f"Loaded {len(self.abusive_words)} abusive words from config")
        
        # Create regex pattern for abusive words
        self.abusive_pattern = r'\b(' + '|'.join(map(re.escape, self.abusive_words)) + r')\b'
        
        # Register the event handler
        api.register_third_party_rules_callbacks(
            check_event_allowed=self.on_event
        )
        logger.info("TextMasker module initialized successfully")

    def mask_phone_number(self, text: str) -> str:
        """Mask phone numbers in the text."""
        logger.debug(f"Masking phone numbers in text: {text[:50]}...")
        
        def mask_phone(match):
            phone = match.group(0)
            # Keep first 3 and last 4 digits, mask the rest
            # Handle international format
            if phone.startswith('+'):
                country_code = phone[:4]  # Keep country code
                number = phone[4:]
                return country_code + '*' * (len(number) - 4) + number[-4:]
            else:
                return phone[:3] + '*' * (len(phone) - 7) + phone[-4:]
        
        masked_text = self.phone_pattern.sub(mask_phone, text)
        logger.debug(f"Phone numbers masked: {masked_text[:50]}...")
        return masked_text

    def mask_email(self, text: str) -> str:
        """Mask email addresses in the text."""
        logger.debug(f"Masking email addresses in text: {text[:50]}...")
        
        def mask_email(match):
            email = match.group(0)
            # Split into local part and domain
            local_part, domain = email.split('@')
            
            # Handle quoted strings in local part
            if local_part.startswith('"') and local_part.endswith('"'):
                # Keep first and last character of quoted string
                masked_local = local_part[0] + '*' * (len(local_part) - 2) + local_part[-1]
            else:
                # For standard emails, keep first and last character
                if len(local_part) > 2:
                    masked_local = local_part[0] + '*' * (len(local_part) - 2) + local_part[-1]
                else:
                    masked_local = local_part[0] + '*'  # For very short local parts
            
            # Mask domain part
            domain_parts = domain.split('.')
            if len(domain_parts) > 1:
                # Keep first and last part of domain
                masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1)
                for part in domain_parts[1:-1]:
                    masked_domain += '.' + part[0] + '*' * (len(part) - 1)
                masked_domain += '.' + domain_parts[-1]  # Keep TLD as is
            else:
                masked_domain = domain[0] + '*' * (len(domain) - 1)
            
            return f"{masked_local}@{masked_domain}"
        
        masked_text = self.email_pattern.sub(mask_email, text)
        logger.debug(f"Email addresses masked: {masked_text[:50]}...")
        return masked_text

    def mask_abusive_words(self, text: str) -> str:
        """Mask abusive words in the text."""
        logger.debug(f"Masking abusive words in text: {text[:50]}...")
        def mask_word(match):
            word = match.group(0)
            return '*' * len(word)
        
        masked_text = re.sub(self.abusive_pattern, mask_word, text, flags=re.IGNORECASE)
        logger.debug(f"Abusive words masked: {masked_text[:50]}...")
        return masked_text

    def mask_text(self, text: str) -> str:
        """Apply all masking rules to the text."""
        if not text:
            logger.debug("Empty text received, nothing to mask")
            return text
            
        logger.info(f"Starting text masking process for text: {text[:50]}...")
        masked_text = text
        masked_text = self.mask_phone_number(masked_text)
        masked_text = self.mask_email(masked_text)
        masked_text = self.mask_abusive_words(masked_text)
        logger.info(f"Text masking completed. Original length: {len(text)}, Masked length: {len(masked_text)}")
        return masked_text

    async def on_event(self, event: EventBase, state) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Handle incoming events and mask sensitive content.
        
        Args:
            event: The event to check
            state: The state at the event
            
        Returns:
            A tuple of (allowed, new_content)
            - allowed: bool indicating whether the event should be allowed
            - new_content: dict containing the new event content, or None if unchanged
        """
        try:
            logger.info(f"Processing event: {event.event_id} of type {event.type}")
            
            if event.type == "m.room.message" and event.content.get("msgtype") == "m.text":
                logger.debug("Event is a text message, checking for sensitive content")
                original_content = event.content.get("body", "")
                logger.debug(f"Original content: {original_content[:50]}...")
                
                masked_content = self.mask_text(original_content)
                logger.debug(f"Masked content: {masked_content[:50]}...")
                
                # Only modify the event if masking was applied
                if masked_content != original_content:
                    logger.info("Content was modified, creating new event")
                    # Create a new content dictionary that preserves all original fields
                    new_content = dict(event.content)
                    new_content["body"] = masked_content
                    new_content["m.notice"] = "Some content has been masked for privacy and safety."
                    
                    # Create a new event dictionary with all original fields
                    try:
                        new_event = {
                            "type": event.type,
                            "room_id": event.room_id,
                            "sender": event.sender,
                            "content": new_content,
                            "origin_server_ts": event.origin_server_ts,
                            "unsigned": event.unsigned,
                            "event_id": event.event_id,
                            "prev_event_ids": event.prev_event_ids,
                            "auth_event_ids": event.auth_event_ids,  # Fixed attribute name
                            "depth": event.depth,
                            "hashes": event.hashes,
                            "signatures": event.signatures
                        }
                        
                        logger.info(f"Successfully created new event for {event.event_id}")
                        return True, new_event
                    except AttributeError as e:
                        logger.error(f"Error accessing event attribute: {str(e)}")
                        logger.error("Falling back to minimal event structure")
                        # Fallback to minimal event structure
                        return True, {
                            "type": event.type,
                            "room_id": event.room_id,
                            "sender": event.sender,
                            "content": new_content
                        }
                else:
                    logger.debug("No sensitive content found, event unchanged")
            else:
                logger.debug(f"Event type {event.type} not handled, skipping")
            
            # If no masking was needed, return None to indicate no changes
            return True, None
            
        except Exception as e:
            logger.error(f"Error in text masking for event {event.event_id}: {str(e)}", exc_info=True)
            # In case of error, allow the event but don't modify it
            return True, None

def create_module(config: Dict, api: ModuleApi):
    logger.info("Creating new TextMasker module instance")
    return TextMasker(config, api) 