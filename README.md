# Book Writing Agent Project

Questo progetto implementa un sistema multi-agente per la scrittura di libri, utilizzando Python e il framework `smolagents`.

## Descrizione

Lo strumento è progettato per orchestrare diversi agenti AI, ognuno con un ruolo specifico nel processo di creazione del libro, dall'ideazione alla generazione del PDF finale. L'obiettivo è produrre libri pronti per la pubblicazione, ad esempio su piattaforme come Amazon Kindle Direct Publishing (KDP).

## Agenti Coinvolti

Il sistema è composto dai seguenti agenti principali:

1.  **IdeatorAgent**: Responsabile dell'ideazione del libro. Definisce il concetto generale, lo stile del libro, lo stile delle immagini e orchestra il lavoro degli altri agenti.
2.  **StoryWriterAgent**: Scrive il contenuto testuale del libro basandosi sul piano fornito dall'IdeatorAgent. Inserisce placeholder per le immagini che verranno create dall'ImageCreatorAgent.
3.  **ImageCreatorAgent**: Utilizza modelli generativi (attualmente simulati) per creare le immagini richieste dallo StoryWriterAgent, inclusa la copertina del libro.
4.  **ImpaginatorAgent**: Raccoglie il testo e le immagini prodotte dagli altri agenti e formatta il tutto in un file PDF pronto per la pubblicazione.

### Agenti Facoltativi

Il sistema può includere anche i seguenti agenti opzionali per funzionalità aggiuntive:

*   **TrendFinderAgent**: Ricerca i libri più venduti su Amazon (o altre fonti web) relativi a un determinato argomento o genere, fornendo informazioni utili per la creazione del libro.
*   **StyleImitatorAgent**: Data una porzione di testo come esempio, analizza lo stile di scrittura e permette allo StoryWriterAgent di imitarlo.
*   **TranslatorAgent**: Traduce il testo del libro in altre lingue.

## Struttura del Progetto

```
/book_writing_agent
|-- agents/                 # Moduli per i singoli agenti (Ideator, StoryWriter, etc.)
|   |-- __init__.py
|   |-- base_agent.py
|   |-- ideator_agent.py
|   |-- story_writer_agent.py
|   |-- image_creator_agent.py
|   |-- impaginator_agent.py
|   |-- trend_finder_agent.py
|   |-- style_imitator_agent.py
|   `-- translator_agent.py
|-- data_models/            # Definizioni Pydantic per le strutture dati (BookPlan, StoryContent, etc.)
|   |-- __init__.py
|   |-- book_plan.py
|   |-- story_content.py
|   |-- image_request.py
|   `-- generated_image.py
|-- prompts/                # File YAML contenenti i prompt per gli LLM usati dagli agenti
|   |-- ideator_prompts.yaml
|   |-- story_writer_prompts.yaml
|   |-- image_creator_prompts.yaml
|   |-- impaginator_prompts.yaml
|   |-- trend_finder_prompts.yaml
|   |-- style_imitator_prompts.yaml
|   `-- translator_prompts.yaml
|-- tools/                  # Strumenti ausiliari (es. generazione PDF, wrapper per API esterne)
|   |-- __init__.py
|   |-- pdf_generator_tool.py
|   |-- image_generation_tool.py
|   |-- web_search_tool.py
|   |-- text_analysis_tool.py
|   `-- translation_tool.py
|-- outputs/                # Directory per i libri generati (NON versionata)
|   `-- book_YYYYMMDD_HHMMSS_UUID/
|       |-- book_plan.yaml
|       |-- story_summary.txt
|       |-- image_log.txt
|       |-- images/
|       |   |-- chapter1_image1.png
|       |   `-- cover.png
|       `-- nome_libro.pdf
|-- config.yaml             # File di configurazione principale (modelli LLM, API keys, etc.)
|-- main.py                 # Script principale per avviare il workflow di creazione del libro
|-- requirements.txt        # (Da generare) Dipendenze Python del progetto
`-- README.md               # Questo file
```

## Come Iniziare

1.  **Clonare il repository.**
2.  **Installare le dipendenze**: Idealmente, creare un ambiente virtuale e installare le dipendenze da `requirements.txt` (da generare con `pip freeze > requirements.txt`).
    ```bash
    python -m venv venv
    source venv/bin/activate  # Su Linux/macOS
    # venv\Scripts\activate    # Su Windows
    pip install -r requirements.txt
    ```
3.  **Configurare `config.yaml`**: Aggiornare il file `config.yaml` con le proprie configurazioni, in particolare per i modelli LLM (es. API key di OpenAI, endpoint di Ollama, etc.) e le chiavi API per eventuali servizi esterni (ricerca web, traduzione, generazione immagini).
4.  **Eseguire lo script principale**:
    ```bash
    python book_writing_agent/main.py
    ```
    Questo avvierà il workflow di creazione del libro basato sull'idea di default specificata in `config.yaml` o su un input fornito.

## Eseguire l'Applicazione Streamlit

Per utilizzare l'interfaccia utente basata sul web:

1.  Assicurati di aver installato tutte le dipendenze, inclusa Streamlit (vedi sezione "Come Iniziare").
2.  Naviga nella directory principale del progetto (`book_writing_agent`).
3.  Esegui il seguente comando nel tuo terminale:
    ```bash
    streamlit run streamlit_app.py
    ```
4.  Streamlit avvierà un server di sviluppo locale e aprirà l'applicazione nel tuo browser web predefinito. Potrai interagire con la UI per generare i libri.

## Funzionalità Chiave

*   **Architettura Modulare**: Ogni agente ha responsabilità ben definite, facilitando la manutenzione e l'estensione.
*   **Configurabilità**: I prompt degli agenti, i modelli LLM e altri parametri sono configurabili tramite file YAML.
*   **Workflow Flessibile**: Gli agenti opzionali possono essere abilitati o disabilitati tramite `config.yaml`.
*   **Output Multiplo**: Il sistema genera non solo il PDF finale del libro, ma anche file intermedi come il piano del libro, i log delle immagini e i riassunti della storia.
*   **Simulazione LLM**: Attualmente, le interazioni con i modelli LLM e i tool di generazione immagini sono simulate per permettere l'esecuzione senza API key reali. Per un funzionamento completo, è necessario integrare veri modelli LLM e servizi di generazione immagini.

## Contribuire

I contributi sono benvenuti! Si prega di aprire una issue o una pull request per discutere modifiche o nuove funzionalità.

## Licenza

Questo progetto è rilasciato sotto la Licenza MIT (o altra licenza da definire).



Step 4: Generating Images...
ImageCreatorAgent: Processing placeholder 1/8: chapter1_image1
ImageCreatorAgent: Generating image for ID 'chapter1_image1' with DALL-E
Enhanced prompt: Sparky, a small dragon with bright colors, sitting happily among flowers in a garden.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter1_image1' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter1_image1_1ec9b0.png
ImageCreatorAgent: Processing placeholder 2/8: chapter1_image2
ImageCreatorAgent: Generating image for ID 'chapter1_image2' with DALL-E
Enhanced prompt: Pippo, a tiny mouse, peeking out from behind a large, colorful flower as he meets Sparky.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter1_image2' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter1_image2_d06848.png
ImageCreatorAgent: Processing placeholder 3/8: chapter2_image1
ImageCreatorAgent: Generating image for ID 'chapter2_image1' with DALL-E
Enhanced prompt: Sparky and Pippo running through a vibrant garden, flowers swaying as they play.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter2_image1' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter2_image1_93bcc4.png
ImageCreatorAgent: Processing placeholder 4/8: chapter2_image2
ImageCreatorAgent: Generating image for ID 'chapter2_image2' with DALL-E
Enhanced prompt: Sparky and Pippo discovering a small pond in the garden and splashing water playfully.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter2_image2' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter2_image2_eb21bf.png
ImageCreatorAgent: Processing placeholder 5/8: chapter3_image1
ImageCreatorAgent: Generating image for ID 'chapter3_image1' with DALL-E
Enhanced prompt: A mysterious wizard with a long hat handing colorful candy to Sparky and Pippo in the garden.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter3_image1' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter3_image1_4a94c5.png
ImageCreatorAgent: Processing placeholder 6/8: chapter4_image1
ImageCreatorAgent: Generating image for ID 'chapter4_image1' with DALL-E
Enhanced prompt: Sparky and Pippo looking at the empty candy wrappers with sad expressions, realizing their mistake.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter4_image1' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter4_image1_49100a.png
ImageCreatorAgent: Processing placeholder 7/8: chapter4_image2
ImageCreatorAgent: Generating image for ID 'chapter4_image2' with DALL-E
Enhanced prompt: Sparky and Pippo shaking hands and smiling, promising to avoid the candy from the wizard.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter4_image2' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter4_image2_52cc70.png
ImageCreatorAgent: Processing placeholder 8/8: chapter5_image1
ImageCreatorAgent: Generating image for ID 'chapter5_image1' with DALL-E
Enhanced prompt: Sparky and Pippo playing among the flowers and enjoying the sunshine, looking carefree and joyful.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1024 to 400x400
ImageCreatorAgent: Successfully generated image for 'chapter5_image1' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/chapter5_image1_16357a.png
ImageCreatorAgent: Processing cover image with concept: 'A generic book cover.'
ImageCreatorAgent: Generating image for ID 'cover' with DALL-E
Enhanced prompt: A generic book cover.. Style: Standard image style.
ImageCreatorAgent: Resized image from 1024x1792 to 571x1000
ImageCreatorAgent: Successfully generated image for 'cover' at /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/images/cover_f9f4b7.png
ImageCreatorAgent: Finished image generation. Total images: 9
Primary gen_id: None
Cover gen_id: None
Consistency strategy used: primary
Image Generation Complete. 9 images processed.

Step 5: Creating Book PDF...
ImpaginatorAgent: Successfully generated PDF: /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/sparky,_il_drago_dei_fiori_book.pdf
PDF Creation Result: /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/sparky,_il_drago_dei_fiori_book.pdf

--- Book Creation Workflow Completed ---
All outputs saved in project directory: /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11
Final PDF (if successful): /home/federico/Desktop/personal/book_publishing_api/outputs/book_20250516_121540_005d11/sparky,_il_drago_dei_fiori_book.pdf
