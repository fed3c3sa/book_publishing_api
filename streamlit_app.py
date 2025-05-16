import streamlit as st
import os
import sys
import yaml # For loading base config
from datetime import datetime # For unique session IDs if needed for outputs
import uuid # For unique IDs

# Ensure the main project directory is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Attempt to import the main workflow function
try:
    from main import main_workflow, load_config
except ImportError as e:
    st.error(f"Errore nell\"importare i moduli del progetto: {e}. Assicurati che la struttura del progetto sia corretta e che streamlit_app.py sia nella directory principale del progetto book_writing_agent.")
    st.stop()

def run_book_generation(app_config):
    st.info("Avvio della generazione del libro... Questo potrebbe richiedere alcuni minuti.")
    
    # Prepare a dynamic configuration for the workflow based on UI inputs
    # We load the base config and then override/add based on UI
    base_config = load_config(os.path.join(PROJECT_ROOT,"book_publishing_api", "config.yaml"))

    # Update base_config with UI inputs
    # Note: The main_workflow might need adjustments to accept these overrides directly
    # or we create a temporary config dict to pass.
    # For now, we assume main_workflow can handle a modified config dict or specific parameters.

    # For simplicity, we will pass the core idea directly to main_workflow
    # and let it use its internal config for other things, or we can construct
    # a more specific config object if main_workflow is refactored.
    
    user_idea = app_config.get("book_idea", "Un libro generato da Streamlit.")

    # Create a placeholder config for optional agents based on UI
    # This part needs careful integration with how main_workflow consumes config
    # For now, we demonstrate how to gather them. The main_workflow would need to be
    # adapted or a new entry point created that takes these flags.
    current_run_config = base_config.copy() # Start with base config
    current_run_config["user_book_idea"] = user_idea # Pass the main idea
    current_run_config["title"] = app_config.get("title")
    current_run_config["main_genre"] = app_config.get("main_genre")
    current_run_config["writing_style_guide"] = app_config.get("writing_style") # Assumes BookPlan can take this
    current_run_config["image_style_guide"] = app_config.get("image_style") # Assumes BookPlan can take this
    
    current_run_config["enable_trend_finder"] = app_config.get("enable_trend_finder", False)
    current_run_config["enable_style_imitator"] = app_config.get("enable_style_imitator", False)
    current_run_config["style_imitation_example_text"] = app_config.get("style_imitator_example_text", "")
    current_run_config["enable_translator"] = app_config.get("enable_translator", False)
    current_run_config["translation_target_language"] = app_config.get("target_language", "")

    # The main_workflow needs to be adapted to use these more granular inputs
    # or we pass a fully constructed config object. For this iteration, we will
    # primarily use the user_book_idea and let main_workflow use its default config for other aspects,
    # then progressively refine how config is passed.

    # For now, let's assume main_workflow is called with the base_config and the user_idea.
    # The more detailed UI options would require main_workflow or agent initializations to be more flexible.

    with st.spinner("Gli agenti stanno scrivendo il tuo libro..."):
        try:
            # We need to ensure main_workflow can accept a config dictionary that reflects UI choices.
            # A simple way is to modify the main_workflow to accept these specific overrides.
            # For now, we will call it with the base config and the primary user idea.
            # A more robust solution would involve refactoring main_workflow or creating a new entry point.
            
            # Let's try to pass the most critical piece of information: the book idea.
            # The main_workflow will use its default config.yaml for other settings.
            # This is a simplification for the first pass of integration.
            project_output_dir, pdf_path = main_workflow(config=current_run_config, user_book_idea=user_idea)

            if pdf_path and "Error" not in pdf_path and os.path.exists(pdf_path):
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
                        with open(book_plan_path, "r") as f_bp:
                            st.code(f_bp.read(), language="yaml")
                
                story_summary_path = os.path.join(project_output_dir, "story_summary.txt")
                if os.path.exists(story_summary_path):
                    with st.expander("Visualizza Riepilogo della Storia"):
                        with open(story_summary_path, "r") as f_ss:
                            st.text(f_ss.read())
                            
                image_log_path = os.path.join(project_output_dir, "image_log.txt")
                if os.path.exists(image_log_path):
                    with st.expander("Visualizza Log Immagini"):
                        with open(image_log_path, "r") as f_il:
                            st.text(f_il.read())

            else:
                st.error(f"Si è verificato un errore durante la generazione del PDF. Dettagli: {pdf_path}")
                st.write(f"Controlla i log nella console o nella directory di output (se creata): {project_output_dir}")

        except Exception as e:
            st.error(f"Errore critico durante il workflow di generazione del libro: {e}")
            import traceback
            st.code(traceback.format_exc())

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
    
    genres = ["Racconto per bambini", "Fantasy", "Fantascienza", "Romanzo Rosa", "Thriller", "Saggio", "Altro"]
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

    if generate_button:
        # Collect inputs into a dictionary to pass to the generation function
        app_config_data = {
            "book_idea": book_idea,
            "title": title,
            "main_genre": main_genre if main_genre != "Altro" else other_genre,
            "writing_style": writing_style,
            "image_style": image_style,
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
