from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # No specific header needed for this document
        pass

    def footer(self):
        # Page number
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title_str):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, title_str, 0, 1, "L")
        self.ln(2)

    def chapter_body(self, body_str, indent=0):
        self.set_font("Helvetica", "", 12)
        current_x = self.get_x()
        self.set_x(current_x + indent)
        self.multi_cell(0, 7, body_str, 0, "L") # 7 is line height
        self.set_x(current_x) # Reset x position
        self.ln(1)

    def agent_item(self, agent_name, agent_desc):
        initial_l_margin = self.l_margin
        
        # Agent Name (bold)
        self.set_left_margin(initial_l_margin + 5) # Indent for agent name
        self.set_x(initial_l_margin + 5)
        self.set_font("Helvetica", "B", 12)
        self.multi_cell(0, 7, f"{agent_name}:", 0, "L") # Using multi_cell in case agent name is long

        # Agent Description (normal, further indented)
        self.set_left_margin(initial_l_margin + 10) # Further indent for description
        self.set_x(initial_l_margin + 10)
        self.set_font("Helvetica", "", 12)
        self.multi_cell(0, 7, agent_desc, 0, "L")
        
        self.set_left_margin(initial_l_margin) # Reset left margin
        self.ln(3) # Space after each agent item

# --- Text Content (from your input) ---
title = "Book Writing Agent Project"

descrizione_text = (
    "Questo progetto implementa un sistema multi-agente per la scrittura di libri, "
    "utilizzando Python e il framework smolagents."
)

descrizione_body = (
    "Lo strumento è progettato per orchestrare diversi agenti AI, ognuno con un ruolo "
    "specifico nel processo di creazione del libro, dall'ideazione alla generazione "
    "del PDF finale. L'obiettivo è produrre libri pronti per la pubblicazione, "
    "ad esempio su piattaforme come Amazon Kindle Direct Publishing (KDP)."
)

agenti_coinvolti_intro = "Il sistema è composto dai seguenti agenti principali:"
agenti_principali = {
    "IdeatorAgent": "Responsabile dell'ideazione del libro. Definisce il concetto generale, lo stile del libro, lo stile delle immagini e orchestra il lavoro degli altri agenti.",
    "StoryWriterAgent": "Scrive il contenuto testuale del libro basandosi sul piano fornito dall'IdeatorAgent. Inserisce placeholder per le immagini che verranno create dall'ImageCreatorAgent.",
    "ImageCreatorAgent": "Utilizza modelli generativi (attualmente simulati) per creare le immagini richieste dallo StoryWriterAgent, inclusa la copertina del libro.",
    "ImpaginatorAgent": "Raccoglie il testo e le immagini prodotte dagli altri agenti e formatta il tutto in un file PDF pronto per la pubblicazione."
}

agenti_facoltativi_intro = "Il sistema può includere anche i seguenti agenti opzionali per funzionalità aggiuntive:"
agenti_facoltativi = {
    "TrendFinderAgent": "Ricerca i libri più venduti su Amazon (o altre fonti web) relativi a un determinato argomento o genere, fornendo informazioni utili per la creazione del libro.",
    "StyleImitatorAgent": "Data una porzione di testo come esempio, analizza lo stile di scrittura e permette allo StoryWriterAgent di imitarlo.",
    "TranslatorAgent": "Traduce il testo del libro in altre lingue."
}

# --- PDF Generation ---
pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Main Title
pdf.set_font("Helvetica", "B", 18)
pdf.cell(0, 10, title, 0, 1, "C")
pdf.ln(5)

# Project Description (using the main text as a subtitle here)
pdf.set_font("Helvetica", "I", 12) # Italic for subtitle
pdf.multi_cell(0, 7, descrizione_text, 0, "C")
pdf.ln(8)

# Descrizione Section
pdf.chapter_title("Descrizione")
pdf.chapter_body(descrizione_body)
pdf.ln(5)

# Agenti Coinvolti Section
pdf.chapter_title("Agenti Coinvolti")
pdf.chapter_body(agenti_coinvolti_intro)
for agent, desc in agenti_principali.items():
    pdf.agent_item(agent, desc)
pdf.ln(2) # Extra space before next section title

# Agenti Facoltativi Section
pdf.chapter_title("Agenti Facoltativi")
pdf.chapter_body(agenti_facoltativi_intro)
for agent, desc in agenti_facoltativi.items():
    pdf.agent_item(agent, desc)

# Output the PDF
file_name = "Book_Writing_Agent_Project_IT.pdf"
try:
    pdf.output(file_name, "F")
    print(f"PDF '{file_name}' generated successfully.")
except Exception as e:
    print(f"Error generating PDF: {e}")
    # Fallback for fonts if common Helvetica fails with special chars (less likely with fpdf2)
    # This part is usually for systems where font files are not easily found by fpdf2
    # or if very specific Unicode characters are needed beyond Latin-1.
    print("Attempting with a different font approach if it was a font issue...")
    # (Note: For Colab/Jupyter, font files might need to be present or installed)
    # For this specific text, Helvetica should be fine with Italian accents.