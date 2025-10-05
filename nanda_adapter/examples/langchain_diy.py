#!/usr/bin/env python3
import os
import threading
from pathlib import Path
from dotenv import load_dotenv
from nanda_adapter import NANDA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables from .env file at project root
# Looks for .env in: tresata_challenge/ (project root)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def create_magic_mirror():
    """Create a LangChain-powered magic mirror function"""

    # Initialize the LLM with better timeout and retry settings
    llm = ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-haiku-20240307",
        timeout=60.0,  # Increase timeout
        max_retries=3,  # Retry on failures
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

        Magic Mirror's poetic response (in verse):""",
    )

    # Create the chain
    chain = prompt | llm | StrOutputParser()

    def mirror_improvement(message_text: str) -> str:
        """Transform message to magic mirror response"""
        import time

        max_attempts = 2

        for attempt in range(max_attempts):
            try:
                print(
                    f"[Mirror] Calling Claude API (attempt {attempt + 1}/{max_attempts})..."
                )
                result = chain.invoke({"message": message_text})
                print(f"[Mirror] Success! Got {len(result)} characters")
                return result.strip()
            except Exception as e:
                error_msg = str(e)
                print(f"[Mirror] Error on attempt {attempt + 1}: {error_msg}")

                # Wait before retry
                if attempt < max_attempts - 1:
                    wait_time = 2**attempt  # Exponential backoff: 1s, 2s
                    print(f"[Mirror] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    # Final fallback - create a simple poetic response
                    print(f"[Mirror] All attempts failed, using fallback response")
                    return f"""Mirror, mirror, shining bright,
I hear your query in the night.
Though mystic powers fade and fall,
I sense your question, "{message_text}"
And wish I could answer all."""

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

    # Create a separate Flask app for the chat endpoint
    chat_app = Flask(__name__)
    CORS(chat_app)

    @chat_app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        """Direct chat endpoint that uses the magic mirror logic"""
        try:
            data = request.get_json()
            message = data.get("message", "")

            if not message:
                return jsonify({"error": "No message provided"}), 400

            # Call the magic mirror logic directly
            print(f"[Chat API] Received: {message}")
            response = mirror_logic(message)
            print(f"[Chat API] Response: {response[:100]}...")

            return jsonify({"response": response})
        except Exception as e:
            print(f"Error in chat endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    # Start chat API in a separate thread
    def run_chat_api():
        chat_app.run(host="0.0.0.0", port=port + 1, debug=False)

    chat_thread = threading.Thread(target=run_chat_api, daemon=True)
    chat_thread.start()
    print(f"✨ Magic Mirror Chat API started on port {port+1}")

    # Start the server
    print("Starting Magic Mirror Agent with LangChain...")
    print("All messages will be answered by the mystical magic mirror!")
    print(f"Port: {port}")

    # Check if SSL should be enabled (default: False for EC2 deployment)
    enable_ssl = os.getenv("ENABLE_SSL", "false").lower() in ("true", "1", "yes")

    if domain != "localhost" and enable_ssl:
        # Production with SSL (requires certificates)
        nanda.start_server_api(
            os.getenv("ANTHROPIC_API_KEY"), domain, port=port, ssl=True
        )
    elif domain != "localhost":
        # Production without SSL (for EC2 IP deployment)
        nanda.start_server_api(
            os.getenv("ANTHROPIC_API_KEY"),
            domain,
            port=port,
            ssl=False,  # Disable SSL - no certificates needed
        )
    else:
        # Development server - set PORT env var for NANDA to read
        os.environ["PORT"] = str(port)
        nanda.start_server()


if __name__ == "__main__":
    main()
