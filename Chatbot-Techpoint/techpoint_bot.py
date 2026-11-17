""" RULE-BASED CHATBOT FOR INTERNSHIP SUPPORT ASSISTANT - DATHEON """

import json
import os
import re

def load_faqs(filename="faqs.json"):
    """
    Read greetings and FAQs from Datheon's supplied JSON dataset file.
    Validates regex patterns to prevent runtime crashes.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The required JSON dataset file '{filename}' was not found in: {script_dir}")
        
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{filename}': {e}")
    except OSError as e:
        raise RuntimeError(f"An error occurred while accessing '{filename}': {e}")
        
    responses = {}
    intent_patterns = []
    
    # 1. Process greetings from JSON
    greetings = data.get("greetings", [])
    if greetings:
        responses['greeting'] = ["Hello! Welcome to the Internship Support Assistant. How can I help you today?"]
        escaped_greetings = [re.escape(g) for g in greetings]
        greeting_pattern = r'\b(' + '|'.join(escaped_greetings) + r')\b'
        intent_patterns.append(('greeting', greeting_pattern))
        
    # 2. Process FAQs from JSON with robust phrase/keyword matching
    faqs = data.get("faqs", [])
    for idx, faq in enumerate(faqs):
        question = faq.get("question", "").strip()
        answer = faq.get("answer", "").strip()
        
        if question and answer:
            intent_name = f"faq_{idx}"
            responses[intent_name] = [answer]
            
            # Extract meaningful key phrases/words (length > 3) to prevent broad single-word triggers
            clean_q = re.sub(r'[^\w\s]', '', question).lower()
            keywords = [w for w in clean_q.split() if len(w) > 3]
            
            if keywords:
                # Build a precise pattern requiring relevant keyword chunks or phrase matches
                pattern = r'\b(' + '|'.join(re.escape(w) for w in keywords) + r')\b'
                try:
                    re.compile(pattern) # Validate regex safety
                    intent_patterns.append((intent_name, pattern))
                except re.error:
                    continue
                
    # 3. Add mandatory fallback, help, and exit intents aligned with Internship Support
    responses['fallback'] = [
        "I'm sorry, I didn't quite catch that. Could you rephrase your question, or type 'help' to see what I can assist with?"
    ]
    responses['help'] = [
        "I can help you with questions regarding:\n"
        "  • Hours of operation\n"
        "  • Internship project submissions\n"
        "  • Certificate issuance & reviews\n"
        "Type 'help' anytime to see this list or 'exit' to quit."
    ]
    responses['exit'] = [
        "Thank you for using the Internship Support Assistant. Goodbye! 👋"
    ]
    
    intent_patterns.append(('help', r'\b(help|options|assist|commands)\b'))
    intent_patterns.append(('exit', r'\b(bye|exit|quit|goodbye)\b'))
    
    return responses, intent_patterns

def normalize_input(user_input):
    """Level 1: Convert input to lowercase and strip excess whitespace."""
    return user_input.lower().strip()

def identify_intents(cleaned_text, intent_patterns):
    """Level 3: Scan user message using regex for accurate multi-intent detection."""
    matched_intents = []
    for intent_name, pattern in intent_patterns:
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            if intent_name not in matched_intents:
                matched_intents.append(intent_name)
    return matched_intents

def handle_conversational_state(matched_intents, state_tracker):
    """Level 4: Manage conversational context and state transitions."""
    # Update state based on current interactions
    for intent in matched_intents:
        if "faq" in intent:
            state_tracker['last_intent'] = intent
            state_tracker['stage'] = 'resolution'
        elif intent == 'greeting':
            state_tracker['stage'] = 'greeting'
        elif intent == 'exit':
            state_tracker['stage'] = 'exit'

def chatbot_response(matched_intents, responses, state_tracker):
    """Level 3 & 4: Generate responses based on detected intents and conversational state."""
    reply_list = []
    
    if not matched_intents:
        return [responses['fallback'][0]]
        
    for intent in matched_intents:
        if intent in responses:
            reply_list.append(responses[intent][0])
            
    handle_conversational_state(matched_intents, state_tracker)
    return reply_list

def main():
    """Level 1 to 4: Main terminal conversational loop with clean presentation."""
    print("=" * 65)
    print(f"{'INTERNSHIP SUPPORT ASSISTANT':^65}")
    print("=" * 65)
    
    try:
        responses, intent_patterns = load_faqs("faqs.json")
        print("Dataset loaded successfully! Knowledge base active.")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n[Initialization Error]: {e}")
        print("Please ensure your 'faqs.json' file is saved in the project directory.")
        return
        
    print("Type your question below. Type 'help' for options or 'exit' to quit.")
    print("-" * 65)
    
    # Conversational State Tracker
    state_tracker = {
        'stage': 'started',
        'last_intent': None
    }
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSession interrupted. Goodbye!")
            break
            
        cleaned_input = normalize_input(user_input)
        
        if not cleaned_input:
            print("Bot: Please type a message or question. I'm here to help!")
            continue
            
        matched_intents = identify_intents(cleaned_input, intent_patterns)
        bot_replies = chatbot_response(matched_intents, responses, state_tracker)
        
        for reply in bot_replies:
            print(f"Bot: {reply}")
            
        if 'exit' in matched_intents:
            break

if __name__ == "__main__":
    main()