import re
import logging
import aiohttp
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
        
        # API endpoint configuration
        self.mask_api_url = "http://localhost:5001/chat-mask" # TODO: change to the production endpoint
        
        # Register the event handler
        api.register_third_party_rules_callbacks(
            check_event_allowed=self.on_event
        )
        logger.info("TextMasker module initialized successfully")

    async def mask_text(self, text: str) -> str:
        """Apply masking using external API."""
        if not text:
            logger.debug("Empty text received, nothing to mask")
            return text
            
        logger.info(f"Starting text masking process for text: {text[:50]}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('query', text)
                
                async with session.post(self.mask_api_url, data=form_data) as response:
                    if response.status == 200:
                        masked_text = await response.text()
                        logger.info(f"Text masking completed. Original length: {len(text)}, Masked length: {len(masked_text)}")
                        return masked_text
                    else:
                        logger.error(f"API request failed with status {response.status}")
                        return text  # Return original text if API fails
                        
        except Exception as e:
            logger.error(f"Error in text masking API call: {str(e)}", exc_info=True)
            return text  # Return original text if there's an error

    async def on_event(self, event: EventBase, state) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Handle incoming events and mask sensitive content using external API.
        
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
                
                masked_content = await self.mask_text(original_content)
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
                            "auth_event_ids": event.auth_event_ids,
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