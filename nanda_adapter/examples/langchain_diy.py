#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
from nanda_adapter import NANDA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file at project root
# Looks for .env in: tresata_challenge/ (project root)
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_magic_mirror():
    """Create a LangChain-powered magic mirror function"""

    # Initialize the LLM
    llm = ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307"
    )

    # Create a prompt template for magic mirror transformation
    prompt = PromptTemplate(
        input_variables=["message"],
        template="""You are the Magic Mirror from fairy tales. You MUST respond to every query in verse and rhyme.

        REQUIREMENTS:
        - Always speak in rhyming couplets or verses (AABB, ABAB, or ABCB rhyme schemes)
        - Use poetic, mystical, and enchanted language
        - Begin with "Mirror, mirror, shining bright..." or similar mystical openings
        - Be dramatic, wise, and mysterious
        - Answer truthfully while maintaining the poetic form
        - Use metaphors, imagery, and fairy tale vocabulary

        Query: {message}

        Magic Mirror's poetic response (in verse):"""
    )

    # Create the chain
    chain = prompt | llm | StrOutputParser()

    def mirror_improvement(message_text: str) -> str:
        """Transform message to magic mirror response"""
        try:
            result = chain.invoke({"message": message_text})
            return result.strip()
        except Exception as e:
            print(f"Error in magic mirror: {e}")
            return f"Mirror, mirror on the wall... {message_text}"  # Fallback response

    return mirror_improvement

def main():
    """Main function to start the magic mirror agent"""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Please set your ANTHROPIC_API_KEY environment variable")
        return

    # Get configuration
    domain = os.getenv("DOMAIN_NAME", "localhost")
    port = int(os.getenv("PORT", "3737"))  # Default to 3737 (safe port)

    # Create magic mirror function
    mirror_logic = create_magic_mirror()

    # Initialize NANDA with magic mirror logic
    nanda = NANDA(mirror_logic)

    # Start the server
    print("Starting Magic Mirror Agent with LangChain...")
    print("All messages will be answered by the mystical magic mirror!")
    print(f"Port: {port}")

    # Check if SSL should be enabled (default: False for EC2 deployment)
    enable_ssl = os.getenv("ENABLE_SSL", "false").lower() in ("true", "1", "yes")

    if domain != "localhost" and enable_ssl:
        # Production with SSL (requires certificates)
        nanda.start_server_api(
            os.getenv("ANTHROPIC_API_KEY"),
            domain,
            port=port,
            ssl=True
        )
    elif domain != "localhost":
        # Production without SSL (for EC2 IP deployment)
        nanda.start_server_api(
            os.getenv("ANTHROPIC_API_KEY"),
            domain,
            port=port,
            ssl=False  # Disable SSL - no certificates needed
        )
    else:
        # Development server - set PORT env var for NANDA to read
        os.environ["PORT"] = str(port)
        nanda.start_server()

if __name__ == "__main__":
    main()