// translations.js

const translations = {
    it: {
        // Header
        logoText: 'StoryMaker',
        tagline: 'Crea storie magiche in pochi minuti!',
        
        // Preview panel
        previewTitle: '✨ Guarda la Magia ✨',
        
        // Progress steps (new)
        yourInfo: 'Tue Info',
        bookTitle: 'Titolo',
        storyIdea: 'Storia',
        themes: 'Temi',
        details: 'Dettagli',
        characters: 'Personaggi',
        
        // Original step labels (kept for compatibility)
        step1Label: 'Storia',
        step2Label: 'Dettagli',
        step3Label: 'Personaggi',
        
        // Step 1: Your Info (new)
        letsMeet: 'Conosciamoci! 👋',
        tellUsAboutYou: 'Prima di iniziare, dicci chi sei',
        
        // Step 1: Story (original + new)
        yourName: '👤 Il Tuo Nome',
        yourNamePlaceholder: 'Inserisci il tuo nome',
        emailAddress: '📧 Indirizzo Email',
        emailPlaceholder: 'tua@email.com',
        
        // Step 2: Book Title (new)
        nameYourBook: 'Dai un nome al tuo libro 📖',
        chooseMagicalTitle: 'Scegli un titolo magico per la tua storia',
        bookTitle: '📖 Qual è il titolo del tuo libro?',
        bookTitlePlaceholder: "L'Incredibile Avventura di...",
        
        // Step 3: Story Idea (new)
        tellYourStory: 'Racconta la tua storia ✨',
        shareIdea: 'Condividi la tua idea - non serve essere perfetti!',
        storyIdea: '✨ Raccontaci la tua idea per la storia!',
        storyIdeaPlaceholder: "C'era una volta...",
        
        // Step 4: Themes (new)
        pickThemes: 'Scegli i temi 🎯',
        selectThemes: 'Quali valori vuoi trasmettere?',
        chooseThemes: '🎯 Scegli i tuoi temi:',
        
        // Themes
        friendship: '👫 Amicizia',
        adventure: '🚀 Avventura',
        courage: '💪 Coraggio',
        kindness: '💖 Gentilezza',
        family: '👨‍👩‍👧 Famiglia',
        nature: '🌳 Natura',
        
        // Step 5: Details (new + original)
        bookDetails: 'Dettagli del libro 📝',
        customizeBook: 'Personalizza il tuo libro',
        numPages: '📄 Numero di Pagine',
        pages: 'Pagine',
        ageGroup: '👶 Fascia d\'Età',
        years: 'anni',
        language: '🌍 Lingua',
        artStyle: '🎨 Stile Artistico',
        artStylePlaceholder: 'acquerello, cartone animato, digitale...',
        
        // Step 6: Characters (new + original)
        createCharacters: 'Crea i personaggi 🦸',
        bringToLife: 'Dai vita ai protagonisti della tua storia',
        createMainCharacter: 'Crea il protagonista 🦸',
        mainCharacterDesc: 'Il personaggio principale della tua storia',
        addMoreCharacters: 'Aggiungi altri personaggi 👥',
        moreCharactersDesc: 'Personaggi di supporto per arricchire la storia (opzionale)',
        moreCharacters: 'Altri',
        character: 'Personaggio',
        remove: 'Rimuovi',
        characterName: 'Nome del Personaggio',
        characterNamePlaceholder: 'Dagli un nome!',
        characterType: 'Tipo di Personaggio',
        mainCharacter: '⭐ Personaggio Principale',
        supportingCharacter: '👥 Personaggio di Supporto',
        backgroundCharacter: '🎭 Personaggio di Sfondo',
        inputMethod: 'Metodo di Input',
        describe: '📝 Descrivi',
        upload: '📷 Carica',
        description: 'Descrizione',
        descriptionPlaceholder: 'Come appare? Qual è la sua personalità?',
        clickToUpload: 'Clicca per caricare',
        uploading: 'Caricamento...',
        uploaded: 'Caricato!',
        failed: 'Fallito!',
        error: 'Errore!',
        addCharacter: '➕ Aggiungi Personaggio',
        
        // Navigation
        back: '← Indietro',
        next: 'Avanti →',
        generateBook: '✨ Genera Libro',
        
        // Alerts
        fillRequired: 'Per favore compila tutti i campi richiesti! 📝',
        validEmail: 'Per favore inserisci un indirizzo email valido! 📧',
        addAtLeastOneCharacter: 'Per favore aggiungi almeno un personaggio! 🦸',
        mainCharacterRequired: 'Per favore inserisci il nome del protagonista! 🦸',
        mainCharacterDescriptionRequired: 'Per favore descrivi il protagonista! 📝',
        acceptTerms: 'Per favore accetta i Termini di Servizio per continuare! 📜',
        
        // Preview features
        professionalQuality: 'Qualità professionale',
        uniqueIllustrations: 'Illustrazioni uniche',
        personalizedStory: 'Storia personalizzata',
        ageAppropriate: 'Adatto all\'età',
        
        // Progress modal
        creatingStory: 'Creiamo la Tua Storia!',
        magicalAI: 'La nostra IA magica sta lavorando...',
        starting: 'Inizio...',
        creatingCover: 'Creazione della copertina del libro...',
        almostReady: 'Quasi pronto!',
        
        // Success screen
        coverReady: 'La Copertina del Tuo Libro è Pronta!',
        getCompleteBook: 'Ottieni il Tuo Libro Completo!',
        professionalReview: '✅ Revisione professionale da scrittori esperti',
        highQualityIllustrations: '✅ Illustrazioni di alta qualità per tutte le pagine',
        ageAppropriate: '✅ Linguaggio e contenuti adatti all\'età',
        deliveredEmail: '✅ Consegnato via email entro 12 ore',
        pdfFormat: '✅ Formato PDF pronto per la stampa',
        payNow: '💳 Paga Ora - Ottieni il Libro Completo',
        expertReview: 'I nostri scrittori esperti rivederanno e miglioreranno la tua storia prima della consegna',
        
        // Payment success
        paymentSuccessful: 'Pagamento Riuscito!',
        thankYouOrder: 'Grazie per il tuo ordine! I nostri scrittori esperti stanno ora lavorando al tuo libro.',
        whatHappensNext: 'Cosa succede dopo:',
        paymentConfirmed: '✅ Pagamento confermato',
        expertReviewEnhancement: '🎨 Revisione ed miglioramento da esperti',
        professionalIllustration: '📚 Creazione di illustrazioni professionali',
        deliveryWithin12: '📧 Consegna entro 12 ore',
        emailConfirmation: 'Riceverai presto una conferma via email, e il tuo libro completo sarà consegnato nella tua casella di posta entro 12 ore.',
        createAnotherBook: 'Crea un Altro Libro',
        
        // Terms of Service
        termsOfService: 'Termini di Servizio',
        iAcceptTerms: 'Accetto i Termini di Servizio',
        viewTerms: 'Visualizza Termini',
        
        // Success page specific
        orderDetails: 'Dettagli dell\'Ordine',
        orderIdLabel: 'ID Ordine:',
        amountPaidLabel: 'Importo Pagato:',
        paymentMethodLabel: 'Metodo di Pagamento:',
        creditCard: 'Carta di Credito',
        contactSupport: 'Contatta il Supporto'
    },
    en: {
        // Header
        logoText: 'StoryMaker',
        tagline: 'Create magical stories in minutes!',
        
        // Preview panel
        previewTitle: '✨ See The Magic ✨',
        
        // Progress steps (new)
        yourInfo: 'Your Info',
        bookTitle: 'Title',
        storyIdea: 'Story',
        themes: 'Themes',
        details: 'Details',
        characters: 'Characters',
        
        // Original step labels (kept for compatibility)
        step1Label: 'Story',
        step2Label: 'Details',
        step3Label: 'Characters',
        
        // Step 1: Your Info (new)
        letsMeet: 'Let\'s Meet! 👋',
        tellUsAboutYou: 'Before we start, tell us who you are',
        
        // Step 1: Story (original + new)
        yourName: '👤 Your Name',
        yourNamePlaceholder: 'Enter your name',
        emailAddress: '📧 Email Address',
        emailPlaceholder: 'your@email.com',
        
        // Step 2: Book Title (new)
        nameYourBook: 'Name your book 📖',
        chooseMagicalTitle: 'Choose a magical title for your story',
        bookTitle: '📖 What\'s your book title?',
        bookTitlePlaceholder: 'The Amazing Adventure of...',
        
        // Step 3: Story Idea (new)
        tellYourStory: 'Tell your story ✨',
        shareIdea: 'Share your idea - it doesn\'t need to be perfect!',
        storyIdea: '✨ Tell us your story idea!',
        storyIdeaPlaceholder: 'Once upon a time...',
        
        // Step 4: Themes (new)
        pickThemes: 'Pick themes 🎯',
        selectThemes: 'What values do you want to convey?',
        chooseThemes: '🎯 Choose your themes:',
        
        // Themes
        friendship: '👫 Friendship',
        adventure: '🚀 Adventure',
        courage: '💪 Courage',
        kindness: '💖 Kindness',
        family: '👨‍👩‍👧 Family',
        nature: '🌳 Nature',
        
        // Step 5: Details (new + original)
        bookDetails: 'Book Details 📝',
        customizeBook: 'Customize your book',
        numPages: '📄 Number of Pages',
        pages: 'Pages',
        ageGroup: '👶 Age Group',
        years: 'years',
        language: '🌍 Language',
        artStyle: '🎨 Art Style',
        artStylePlaceholder: 'watercolor, cartoon, digital...',
        
        // Step 6: Characters (new + original)
        createCharacters: 'Create characters 🦸',
        bringToLife: 'Bring the protagonists of your story to life',
        createMainCharacter: 'Create the main character 🦸',
        mainCharacterDesc: 'The main character of your story',
        addMoreCharacters: 'Add more characters 👥',
        moreCharactersDesc: 'Supporting characters to enrich the story (optional)',
        moreCharacters: 'More',
        character: 'Character',
        remove: 'Remove',
        characterName: 'Character Name',
        characterNamePlaceholder: 'Give them a name!',
        characterType: 'Character Type',
        mainCharacter: '⭐ Main Character',
        supportingCharacter: '👥 Supporting Character',
        backgroundCharacter: '🎭 Background Character',
        inputMethod: 'Input Method',
        describe: '📝 Describe',
        upload: '📷 Upload',
        description: 'Description',
        descriptionPlaceholder: 'What do they look like? What\'s their personality?',
        clickToUpload: 'Click to upload',
        uploading: 'Uploading...',
        uploaded: 'Uploaded!',
        failed: 'Failed!',
        error: 'Error!',
        addCharacter: '➕ Add Character',
        
        // Navigation
        back: '← Back',
        next: 'Next →',
        generateBook: '✨ Generate Book',
        
        // Alerts
        fillRequired: 'Please fill in all required fields! 📝',
        validEmail: 'Please enter a valid email address! 📧',
        addAtLeastOneCharacter: 'Please add at least one character! 🦸',
        mainCharacterRequired: 'Please enter the main character\'s name! 🦸',
        mainCharacterDescriptionRequired: 'Please describe the main character! 📝',
        acceptTerms: 'Please accept the Terms of Service to continue! 📜',
        
        // Preview features
        professionalQuality: 'Professional quality',
        uniqueIllustrations: 'Unique illustrations',
        personalizedStory: 'Personalized story',
        ageAppropriate: 'Age appropriate',
        
        // Progress modal
        creatingStory: 'Creating Your Story!',
        magicalAI: 'Our magical AI is working...',
        starting: 'Starting...',
        creatingCover: 'Creating your book cover...',
        almostReady: 'Almost ready!',
        
        // Success screen
        coverReady: 'Your Book Cover is Ready!',
        getCompleteBook: 'Get Your Complete Book!',
        professionalReview: '✅ Professional review by expert writers',
        highQualityIllustrations: '✅ High-quality illustrations for all pages',
        ageAppropriate: '✅ Age-appropriate language and content',
        deliveredEmail: '✅ Delivered via email within 12 hours',
        pdfFormat: '✅ PDF format ready for printing',
        payNow: '💳 Pay Now - Get Full Book',
        expertReview: 'Our expert writers will review and enhance your story before delivery',
        
        // Payment success
        paymentSuccessful: 'Payment Successful!',
        thankYouOrder: 'Thank you for your order! Our expert writers are now working on your book.',
        whatHappensNext: 'What happens next:',
        paymentConfirmed: '✅ Payment confirmed',
        expertReviewEnhancement: '🎨 Expert review and enhancement',
        professionalIllustration: '📚 Professional illustration creation',
        deliveryWithin12: '📧 Delivery within 12 hours',
        emailConfirmation: 'You\'ll receive an email confirmation shortly, and your completed book will be delivered to your inbox within 12 hours.',
        createAnotherBook: 'Create Another Book',
        
        // Terms of Service
        termsOfService: 'Terms of Service',
        iAcceptTerms: 'I accept the Terms of Service',
        viewTerms: 'View Terms',
        
        // Success page specific
        orderDetails: 'Order Details',
        orderIdLabel: 'Order ID:',
        amountPaidLabel: 'Amount Paid:',
        paymentMethodLabel: 'Payment Method:',
        creditCard: 'Credit Card',
        contactSupport: 'Contact Support'
    }
};

// Current language (default: Italian)
let currentLanguage = 'it';

// Function to get translation
function t(key) {
    return translations[currentLanguage][key] || translations['en'][key] || key;
}

// Function to update all translations on the page
function updateTranslations() {
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else {
                element.value = translation;
            }
        } else {
            element.textContent = translation;
        }
    });
    
    // Update language dropdown to set Italian as default
    const languageSelect = document.getElementById('language');
    if (languageSelect) {
        languageSelect.value = currentLanguage === 'it' ? 'Italian' : 'English';
    }
    
    // Update page title
    if (document.title.includes('StoryMaker')) {
        document.title = currentLanguage === 'it' ? 
            'StoryMaker - Generatore di Libri per Bambini con IA' : 
            'StoryMaker - AI Children\'s Book Generator';
    } else if (document.title.includes('Pagamento')) {
        document.title = currentLanguage === 'it' ? 
            'Pagamento Completato - StoryMaker' : 
            'Payment Complete - StoryMaker';
    }
}

// Function to switch language
function switchLanguage(lang) {
    currentLanguage = lang;
    updateTranslations();
    localStorage.setItem('preferredLanguage', lang);
    
    // Update the toggle button states
    document.querySelectorAll('.lang-toggle').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });
}