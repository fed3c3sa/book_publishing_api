import streamlit as st
import os
import sys
import yaml # For loading base config
from datetime import datetime # For unique session IDs if needed for outputs
import uuid # For unique IDs
import dotenv

# Load environment variables
dotenv.load_dotenv("secrets.env")

# Ensure the main project directory is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Attempt to import the main workflow function
try:
    from main import BookCreationOrchestrator
    from config.config_manager import ConfigManager
    from data_models.character import Character
    from agents.image_description_agent import ImageDescriptionAgent
    from smolagents import OpenAIServerModel
except ImportError as e:
    st.error(f"Errore nell\"importare i moduli del progetto: {e}. Assicurati che la struttura del progetto sia corretta e che streamlit_app.py sia nella directory principale del progetto book_writing_agent.")
    st.stop()

def run_book_generation(app_config):
    st.info("Avvio della generazione del libro... Questo potrebbe richiedere alcuni minuti.")
    
    try:
        # Initialize the orchestrator with the config path
        config_path = os.path.join(PROJECT_ROOT, "book_publishing_api", "config.yaml")
        orchestrator = BookCreationOrchestrator(config_path)
        
        # Get base configuration
        base_config = orchestrator.config
        
        # Update configuration with UI inputs
        user_idea = app_config.get("book_idea", "Un libro generato da Streamlit.")
        
        # Create temporary config overrides
        config_overrides = {}
        
        # Basic book info
        if app_config.get("title"):
            config_overrides["title"] = app_config["title"]
        if app_config.get("main_genre"):
            config_overrides["main_genre"] = app_config["main_genre"]
        if app_config.get("target_audience"):
            config_overrides["target_audience"] = app_config["target_audience"]
        if app_config.get("theme"):
            config_overrides["theme"] = app_config["theme"]
        if app_config.get("cover_concept"):
            config_overrides["cover_concept"] = app_config["cover_concept"]
        
        # Style guides
        if app_config.get("writing_style"):
            config_overrides["writing_style_guide"] = app_config["writing_style"]
        if app_config.get("image_style"):
            config_overrides["image_style_guide"] = app_config["image_style"]
        
        # Optional agents
        config_overrides["enable_trend_finder"] = app_config.get("enable_trend_finder", False)
        config_overrides["enable_style_imitator"] = app_config.get("enable_style_imitator", False)
        config_overrides["enable_translator"] = app_config.get("enable_translator", False)
        
        if app_config.get("style_imitator_example_text"):
            config_overrides["style_imitation_example_text"] = app_config["style_imitator_example_text"]
        if app_config.get("target_language"):
            config_overrides["translation_target_language"] = app_config["target_language"]
        
        # Apply config overrides
        for key, value in config_overrides.items():
            orchestrator.config[key] = value
        
        # Process characters from UI
        characters = []
        if app_config.get("characters"):
            for char_data in app_config["characters"]:
                try:
                    character = Character(
                        name=char_data["name"],
                        description=char_data["description"],
                        role=char_data.get("role", "main"),
                        image_source=char_data.get("image_source", "text")
                    )
                    characters.append(character)
                except Exception as e:
                    st.warning(f"Errore nel processare il personaggio {char_data.get('name', 'sconosciuto')}: {e}")
        
        with st.spinner("Gli agenti stanno scrivendo il tuo libro..."):
            # Run the book creation process
            project_output_dir, pdf_path = orchestrator.run_book_creation(user_idea, characters)

            if pdf_path and os.path.exists(pdf_path):
                st.success("Generazione del libro completata!")
                st.balloons()

                st.subheader("Il Tuo Libro è Pronto!")
                with open(pdf_path, "rb") as f_pdf:
                    st.download_button(
                        label="Scarica il Libro (PDF)",
                        data=f_pdf,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
                
                st.markdown(f"Tutti i file di output sono stati salvati in: `{project_output_dir}`")
                
                # Display other generated files if they exist
                book_plan_path = os.path.join(project_output_dir, "book_plan.yaml")
                if os.path.exists(book_plan_path):
                    with st.expander("Visualizza Piano del Libro (YAML)"):
                        with open(book_plan_path, "r", encoding="utf-8") as f_bp:
                            st.code(f_bp.read(), language="yaml")
                
                story_summary_path = os.path.join(project_output_dir, "story_summary.txt")
                if os.path.exists(story_summary_path):
                    with st.expander("Visualizza Riepilogo della Storia"):
                        with open(story_summary_path, "r", encoding="utf-8") as f_ss:
                            st.text(f_ss.read())
                            
                image_log_path = os.path.join(project_output_dir, "image_log.txt")
                if os.path.exists(image_log_path):
                    with st.expander("Visualizza Log Immagini"):
                        with open(image_log_path, "r", encoding="utf-8") as f_il:
                            st.text(f_il.read())

            else:
                st.error(f"Si è verificato un errore durante la generazione del PDF.")
                if project_output_dir:
                    st.write(f"Controlla i log nella console o nella directory di output: {project_output_dir}")

    except Exception as e:
        st.error(f"Errore critico durante il workflow di generazione del libro: {e}")
        import traceback
        st.code(traceback.format_exc())

def character_input_section():
    """Handle character input section with text or image options."""
    st.sidebar.header("Personaggi del Libro")
    
    # Initialize characters in session state if not exists
    if "characters" not in st.session_state:
        st.session_state.characters = []
    
    # Character input method selection
    input_method = st.sidebar.radio(
        "Come vuoi definire i personaggi?",
        ["Descrizione testuale", "Caricamento immagine"],
        key="character_input_method"
    )
    
    if input_method == "Descrizione testuale":
        # Use a form for text input to automatically clear after submission
        with st.sidebar.form("character_text_form", clear_on_submit=True):
            character_name = st.text_input(
                "Nome del personaggio",
                placeholder="Es. Sparky il Drago"
            )
            
            character_role = st.selectbox(
                "Ruolo del personaggio",
                ["main", "secondary", "background"],
                format_func=lambda x: {"main": "Principale", "secondary": "Secondario", "background": "Sfondo"}[x]
            )
            
            character_description = st.text_area(
                "Descrizione del personaggio",
                height=100,
                placeholder="Descrivi l'aspetto fisico, la personalità e le caratteristiche distintive del personaggio..."
            )
            
            submitted = st.form_submit_button("Aggiungi Personaggio")
            
            if submitted:
                if character_name and character_description:
                    new_character = {
                        "name": character_name,
                        "description": character_description,
                        "role": character_role,
                        "image_source": "text"
                    }
                    st.session_state.characters.append(new_character)
                    st.sidebar.success(f"Personaggio '{character_name}' aggiunto!")
                    st.rerun()
                else:
                    st.sidebar.error("Inserisci nome e descrizione del personaggio")
    
    elif input_method == "Caricamento immagine":
        # Use a form for image input
        with st.sidebar.form("character_image_form", clear_on_submit=True):
            character_name = st.text_input(
                "Nome del personaggio",
                placeholder="Es. Sparky il Drago"
            )
            
            character_role = st.selectbox(
                "Ruolo del personaggio",
                ["main", "secondary", "background"],
                format_func=lambda x: {"main": "Principale", "secondary": "Secondario", "background": "Sfondo"}[x]
            )
            
            uploaded_file = st.file_uploader(
                "Carica immagine del personaggio",
                type=["png", "jpg", "jpeg"]
            )
            
            submitted = st.form_submit_button("Analizza Immagine e Aggiungi Personaggio")
            
            if submitted:
                if character_name and uploaded_file is not None:
                    # Process image outside of form to avoid conflicts
                    try:
                        # Store image data for processing
                        image_data = uploaded_file.read()
                        
                        # Show spinner for the analysis
                        with st.spinner("Analizzando l'immagine..."):
                            # Initialize ImageDescriptionAgent for image analysis
                            try:
                                # Load API key and initialize model
                                api_key = os.getenv("OPENAI_API_KEY")
                                if not api_key:
                                    # Try to load from config
                                    config_manager = ConfigManager(os.path.join(PROJECT_ROOT, "book_publishing_api", "config.yaml"))
                                    config = config_manager.load_config()
                                    api_key = config.get("openai_api_key")
                                
                                if api_key:
                                    llm_model = OpenAIServerModel(
                                        api_key=api_key,
                                        model_id="gpt-4o"  # Use vision-capable model
                                    )
                                    image_agent = ImageDescriptionAgent(model=llm_model)
                                    
                                    # Analyze the uploaded image
                                    character_description = image_agent.analyze_character_image(
                                        image_data=image_data,
                                        character_name=character_name
                                    )
                                else:
                                    # Fallback if no API key
                                    character_description = f"Personaggio {character_name} - Descrizione generata dall'immagine caricata. (Analisi automatica non disponibile - configurare API key OpenAI)"
                                    
                            except Exception as e:
                                # Fallback description if image analysis fails
                                character_description = f"Personaggio {character_name} - Immagine caricata con successo. Descrizione dettagliata non disponibile: {str(e)}"
                        
                        # Add character after spinner is done
                        new_character = {
                            "name": character_name,
                            "description": character_description,
                            "role": character_role,
                            "image_source": "image",
                            "image_data": image_data  # Store for later processing
                        }
                        st.session_state.characters.append(new_character)
                        st.sidebar.success(f"Personaggio '{character_name}' aggiunto dall'immagine!")
                        st.rerun()
                        
                    except Exception as e:
                        st.sidebar.error(f"Errore nell'analisi dell'immagine: {e}")
                else:
                    if not character_name:
                        st.sidebar.error("Inserisci il nome del personaggio")
                    if uploaded_file is None:
                        st.sidebar.error("Carica un'immagine del personaggio")
        
        # Show preview of uploaded image outside the form
        if input_method == "Caricamento immagine":
            # This is a separate file uploader just for preview
            preview_file = st.sidebar.file_uploader(
                "Anteprima immagine (solo visualizzazione)",
                type=["png", "jpg", "jpeg"],
                key="preview_upload",
                help="Questa è solo un'anteprima. Usa il form sopra per aggiungere il personaggio."
            )
            if preview_file is not None:
                st.sidebar.image(preview_file, caption="Anteprima immagine", width=200)
    
    # Display current characters
    if st.session_state.characters:
        st.sidebar.subheader("Personaggi Aggiunti")
        for i, char in enumerate(st.session_state.characters):
            with st.sidebar.expander(f"{char['name']} ({char['role']})"):
                st.write(f"**Descrizione:** {char['description'][:100]}...")
                st.write(f"**Fonte:** {'Immagine' if char['image_source'] == 'image' else 'Testo'}")
                if st.button(f"Rimuovi {char['name']}", key=f"remove_char_{i}"):
                    st.session_state.characters.pop(i)
                    st.rerun()
    
    # Clear all characters button
    if st.session_state.characters:
        if st.sidebar.button("Rimuovi Tutti i Personaggi", key="clear_all_characters"):
            st.session_state.characters = []
            st.rerun()

def main_ui():
    st.set_page_config(layout="wide", page_title="Book Writing Agent")

    st.sidebar.title("Book Writing Agent UI")

    # --- Section: Book Idea ---
    st.sidebar.header("Idea del Libro")
    book_idea = st.sidebar.text_area(
        "Qual è l\"idea o il tema principale del tuo libro?", 
        height=100, 
        help="Descrivi brevemente il concetto centrale del libro.",
        key="book_idea",
        value="Un drago verde che non sa sputare fuoco ma scopre di avere un talento per far crescere fiori magici."
    )
    title = st.sidebar.text_input(
        "Titolo provvisorio del libro (opzionale)",
        key="title",
        value="Sparky, il Drago dei Fiori"
    )
    
    genres = ["Racconto per bambini", "Racconto per adolescenti", "Fantasy", "Fantascienza", "Romanzo Rosa", "Thriller", "Saggio", "Altro"]
    main_genre = st.sidebar.selectbox(
        "Genere principale", 
        genres,
        help="Seleziona il genere che meglio si adatta.",
        key="main_genre"
    )
    
    other_genre = ""
    if main_genre == "Altro":
        other_genre = st.sidebar.text_input(
            "Specifica \"Altro\" genere",
            key="other_genre"
        )

    # --- Section: Character Descriptions ---
    character_input_section()

    # --- Section: Writing and Image Style ---
    st.sidebar.header("Stile di Scrittura e Immagini")
    writing_style = st.sidebar.text_area(
        "Descrivi lo stile di scrittura desiderato", 
        height=100, 
        help="Es. \"Tono umoristico e leggero\", \"Linguaggio formale e accademico\", \"Narrativa evocativa e descrittiva\".",
        key="writing_style",
        value="Semplice, adatto ai bambini, con dialoghi divertenti e un messaggio positivo sull\"unicità."
    )
    image_style = st.sidebar.text_area(
        "Descrivi lo stile delle immagini desiderato", 
        height=100, 
        help="Es. \"Illustrazioni a pastello morbide\", \"Fotorealistico e dettagliato\", \"Bianco e nero minimalista\".",
        key="image_style",
        value="Illustrazioni colorate e vivaci, stile cartone animato amichevole, con personaggi espressivi."
    )

    # --- Section: Optional Agents ---
    with st.sidebar.expander("Agenti Facoltativi"):
        enable_trend_finder = st.checkbox(
            "Abilita Trend Finder", 
            help="Ricerca trend di mercato per l\"argomento specificato.",
            key="enable_trend_finder",
            value=False
        )
        enable_style_imitator = st.checkbox(
            "Abilita Style Imitator", 
            help="Imita lo stile di un testo di esempio.",
            key="enable_style_imitator",
            value=False
        )
        style_imitator_example_text = ""
        if enable_style_imitator:
            style_imitator_example_text = st.text_area(
                "Testo di esempio per Style Imitator", 
                height=150, 
                help="Incolla qui un testo di cui imitare lo stile.",
                key="style_imitator_example_text"
            )
        
        enable_translator = st.checkbox(
            "Abilita Traduttore", 
            help="Traduci il libro in un\"altra lingua dopo la generazione.",
            key="enable_translator",
            value=False
        )
        target_language = ""
        if enable_translator:
            translation_languages = ["Inglese", "Spagnolo", "Francese", "Tedesco"]
            target_language = st.selectbox(
                "Lingua di destinazione per la traduzione", 
                translation_languages,
                help="Seleziona la lingua in cui tradurre il libro.",
                key="target_language"
            )

    # --- Launch Button ---
    st.sidebar.markdown("---_---") # Visual separator
    generate_button = st.sidebar.button("Genera Libro", type="primary", key="generate_button")

    # --- Main Area ---
    st.title("Benvenuto nel Book Writing Agent!")
    st.markdown("Utilizza la barra laterale a sinistra per configurare i dettagli del tuo libro e avviare la generazione.")

    # Display character summary in main area
    if st.session_state.get("characters"):
        st.subheader("Personaggi Definiti")
        for char in st.session_state.characters:
            with st.expander(f"{char['name']} - {char['role'].title()}"):
                st.write(f"**Descrizione:** {char['description']}")
                st.write(f"**Fonte:** {'Immagine caricata' if char['image_source'] == 'image' else 'Descrizione testuale'}")

    if generate_button:
        # Collect inputs into a dictionary to pass to the generation function
        app_config_data = {
            "book_idea": book_idea,
            "title": title,
            "main_genre": main_genre if main_genre != "Altro" else other_genre,
            "writing_style": writing_style,
            "image_style": image_style,
            "characters": st.session_state.get("characters", []),
            "enable_trend_finder": enable_trend_finder,
            "enable_style_imitator": enable_style_imitator,
            "style_imitator_example_text": style_imitator_example_text if enable_style_imitator else "",
            "enable_translator": enable_translator,
            "target_language": target_language if enable_translator else ""
        }
        # Store in session state to persist across reruns if needed, or pass directly
        st.session_state.app_config_data = app_config_data
        
        run_book_generation(st.session_state.app_config_data)

if __name__ == "__main__":
    # Initialize session state for app_config_data if it doesn't exist
    if "app_config_data" not in st.session_state:
        st.session_state.app_config_data = {}
    main_ui()