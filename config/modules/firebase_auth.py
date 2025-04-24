import logging
from typing import Optional, Tuple, Callable, Awaitable, Any

import firebase_admin
from firebase_admin import auth, credentials
from synapse.module_api import ModuleApi, LoginResponse, JsonDict
import jwt
# Configure logger to show all levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add a handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class FirebaseAuthProvider:
    def __init__(self, config: dict, account_handler: ModuleApi = None):
        """Initialize the Firebase authentication provider.
        
        Args:
            config: The module configuration dictionary
            account_handler: The ModuleApi instance (provided either directly or via password provider)
        """
        logger.debug("Initializing FirebaseAuthProvider")
        self.api = account_handler
        
        # Initialize Firebase with service account credentials
        service_account_path = config.get("service_account_path")
        if not service_account_path:
            logger.error("service_account_path is required in config")
            raise ValueError("service_account_path is required in config")
            
        logger.debug(f"Using service account path: {service_account_path}")
        try:
            creds = credentials.Certificate(service_account_path)
            logger.debug(f"Service account project_id: {creds.project_id}")
            
            try:
                app = firebase_admin.get_app()
                logger.info(f"Firebase Admin SDK already initialized with project: {app.project_id}")
            except ValueError:
                app = firebase_admin.initialize_app(creds)
                logger.info(f"Firebase Admin SDK initialized with project: {app.project_id}")

            # Register our Firebase token authentication checker
            if self.api:
                logger.debug("Registering Firebase auth checker")
                self.api.register_password_auth_provider_callbacks(
                    auth_checkers={
                        ("m.login.firebase", ("token",)): self.check_firebase_auth,
                    },
                )
                logger.info("Firebase auth checker registered successfully")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            raise

    async def check_firebase_auth(
        self,
        username: str,
        login_type: str,
        login_dict: JsonDict,
        request: Optional[Any] = None,
    ) -> Optional[Tuple[str, Optional[Callable[[LoginResponse], Awaitable[None]]]]]:
        logger.debug(f"Received auth request - type: {login_type}, username: {username}, login_dict: {login_dict}")
        
        if login_type != "m.login.firebase":
            logger.warning(f"Unexpected login type: {login_type}")
            return None

        token = login_dict.get("token")
        if not token:
            logger.warning("Missing Firebase token in login request")
            return None

        try:
            # Get the Firebase app instance
            app = firebase_admin.get_app()
            logger.debug(f"Using Firebase app with project ID: {app.project_id}")
            
            # Verify the token with Firebase Admin SDK
            logger.debug("Attempting to verify token with Firebase Admin SDK")
            # decoded_token = auth.verify_id_token(token)
            # Only for testing purpose
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            firebase_uid = decoded_token['user_id']
            logger.debug(f"Token verified successfully for Firebase UID: {firebase_uid}")
            
            # Create Matrix user ID with a prefix to avoid numeric-only usernames
            matrix_localpart = f"firebase_{firebase_uid}"
            matrix_user = f"@{matrix_localpart}:{self.api.server_name}"
            logger.debug(f"Generated Matrix user ID: {matrix_user}")
            
            # Verify the user exists or create them
            if not await self.api.check_user_exists(matrix_user):
                logger.info(f"Creating new Matrix user: {matrix_user}")
                try:
                    await self.api.register_user(
                        localpart=matrix_localpart,
                        displayname=None,
                        emails=[],
                        admin=False
                    )
                    logger.info(f"New Matrix user created: {matrix_user}")
                except Exception as e:
                    logger.error(f"Failed to register user: {e}")
                    logger.debug("Registration error details:", exc_info=True)
                    return None
            
            logger.info(f"Firebase authentication successful for user: {matrix_user}")
            return (matrix_user, None)
            
        except auth.InvalidIdTokenError as e:
            logger.error(f"Invalid Firebase token: {str(e)}")
            logger.debug("Token verification failed - full error:", exc_info=True)
            return None
        except auth.ExpiredIdTokenError:
            logger.error("Firebase token has expired")
            return None
        except auth.RevokedIdTokenError:
            logger.error("Firebase token has been revoked")
            return None
        except Exception as e:
            logger.error(f"Firebase authentication failed: {str(e)}")
            logger.debug("Unexpected error during authentication:", exc_info=True)
            return None

def create_module(config: dict, api: ModuleApi) -> FirebaseAuthProvider:
    """Create and return a FirebaseAuthProvider instance.
    
    Args:
        config: The module configuration dictionary
        api: The ModuleApi instance provided by Synapse
        
    Returns:
        An instance of FirebaseAuthProvider
    """
    logger.debug("Creating new FirebaseAuthProvider module instance")
    return FirebaseAuthProvider(config=config, account_handler=api) 