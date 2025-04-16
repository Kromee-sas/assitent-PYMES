ASSISTENT-PYMES/
├── app/
│   ├── __init__.py               # Factory de la aplicación
│   ├── core/                     # Núcleo del sistema
│   │   ├── __init__.py
│   │   ├── config.py             # Configuración
│   │   ├── database.py           # ORM y DB
│   │   ├── extensions.py         # Flask-SQLAlchemy, JWT, etc.
│   │   └── exceptions.py         # Manejo de errores
│   │
│   └── modules/                 # Módulos de negocio
│       ├── auth/                 # Autenticación
│       │   ├── __init__.py
│       │   ├── models.py         # User model
│       │   ├── routes.py         # auth_routes.py
│       │   ├── services.py       # auth_logic.py
│       │   ├── schemas.py        # Validaciones
│       │   
│       │
│       └── chat/                 # Chatbot
│           ├── __init__.py
│           ├── models.py         # Message, Conversation
│           ├── routes.py         # chat_routes.py
│           ├── services.py       # chat_logic.py
│           └── nlp/              # Procesamiento NLP
│               ├── __init__.py
│               ├── query_parser.py
│               └── sql_to_df.py
│
tests/                           # Pruebas
├── unit/
│   ├── test_auth_services.py    # Prueba AuthService.registrar_usuario()
│   └── test_chat_services.py    # Prueba ChatService.enviar_mensaje()
│
└── integration/
    ├── test_auth_routes.py      # Prueba POST /auth/register
    └── test_chat_routes.py      # Prueba POST /chat/message
│
├── migrations/                   # Migraciones de DB
├── static/                       # CSS, JS, imágenes
├── templates/                    # Plantillas base
├── .env-example                  # Variables de entorno
├── .gitignore
├── config.py                     # Config principal (para Flask)
├── run.py                        # Punto de entrada
├── requirements.txt
└── README.md


# 1. Configurar entorno virtual
    
    python -m venv myenv 
    myenv\Scripts\activate 
    

# 2. Instala las dependencias:
    
    pip install -r requirements.txt
    

# 3. Crear base de datos
    
    mysql -u root -p
    CREATE DATABASE name_data_base;


# 4. Conectar base de datos 

    flask db init
    flask db migrate -m "Creación tabla usuarios"
    flask db upgrade

# 5. Ejecutar aplicacion

    python run.py

