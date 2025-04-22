import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from synapse.module_api import ModuleApi
from synapse.events import EventBase

# Configure logger
logger = logging.getLogger(__name__)

class TextMasker:
    def __init__(self, config: Dict, api: ModuleApi):
        self.api = api
        self.config = config
        
        # Default patterns for masking
        self.phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Load abusive words from config or use default list
        self.abusive_words = config.get("abusive_words", [
            "badword1", "badword2", "badword3"  # Add your list of abusive words here
        ])
        
        # Create regex pattern for abusive words
        self.abusive_pattern = r'\b(' + '|'.join(map(re.escape, self.abusive_words)) + r')\b'
        
        # Register the event handler
        api.register_third_party_rules_callbacks(
            check_event_allowed=self.on_event
        )

    def mask_phone_number(self, text: str) -> str:
        """Mask phone numbers in the text."""
        def mask_phone(match):
            phone = match.group(0)
            # Keep first 3 and last 4 digits, mask the rest
            return phone[:3] + '*' * (len(phone) - 7) + phone[-4:]
        
        return re.sub(self.phone_pattern, mask_phone, text)

    def mask_email(self, text: str) -> str:
        """Mask email addresses in the text."""
        def mask_email(match):
            email = match.group(0)
            username, domain = email.split('@')
            # Keep first and last character of username, mask the rest
            masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
            return f"{masked_username}@{domain}"
        
        return re.sub(self.email_pattern, mask_email, text)

    def mask_abusive_words(self, text: str) -> str:
        """Mask abusive words in the text."""
        def mask_word(match):
            word = match.group(0)
            return '*' * len(word)
        
        return re.sub(self.abusive_pattern, mask_word, text, flags=re.IGNORECASE)

    def mask_text(self, text: str) -> str:
        """Apply all masking rules to the text."""
        if not text:
            return text
            
        masked_text = text
        masked_text = self.mask_phone_number(masked_text)
        masked_text = self.mask_email(masked_text)
        masked_text = self.mask_abusive_words(masked_text)
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
            if event.type == "m.room.message" and event.content.get("msgtype") == "m.text":
                original_content = event.content.get("body", "")
                masked_content = self.mask_text(original_content)
                
                # Only modify the event if masking was applied
                if masked_content != original_content:
                    # Create a new content dictionary that preserves all original fields
                    new_content = dict(event.content)
                    new_content["body"] = masked_content
                    new_content["m.notice"] = "Some content has been masked for privacy and safety."
                    
                    # Create a new event dictionary with all original fields
                    new_event = {
                        "type": event.type,
                        "room_id": event.room_id,
                        "sender": event.sender,
                        "content": new_content,
                        "origin_server_ts": event.origin_server_ts,
                        "unsigned": event.unsigned,
                        "event_id": event.event_id,
                        "prev_event_ids": event.prev_event_ids,
                        "auth_events": event.auth_events,
                        "depth": event.depth,
                        "hashes": event.hashes,
                        "signatures": event.signatures
                    }
                    
                    return True, new_event
            
            # If no masking was needed, return None to indicate no changes
            return True, None
            
        except Exception as e:
            logger.error(f"Error in text masking: {str(e)}")
            # In case of error, allow the event but don't modify it
            return True, None

def create_module(config: Dict, api: ModuleApi):
    return TextMasker(config, api) 