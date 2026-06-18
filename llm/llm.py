import openai
import os
import asyncio

# Assuming you already have your 'commits' list from the previous steps
# and each commit now has a 'files_touched' key.

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_daily_report(commits_data, kanban_tasks, extra_data=""):


    kanban_context = ""
    for task in kanban_tasks:
        kanban_context += f"- [{task['state']}] {task['folio']}: {task['title']}\n"

    # Format Git context
    git_context = ""
    for c in commits_data:
        files = ", ".join(c.get('files_touched', []))
        git_context += f"- Commit: {c['title']}\n  Files: {files}\n"

    prompt = f"""
    Eres un Senior Backend Engineer con mucha experiencia. Tu objetivo es dar una actualización verbal rápida, fluida y natural para el daily sync.

    CONTEXTO TÉCNICO:
    KANBAN: {kanban_context}
    GIT: {git_context}

    REGLAS DE ORO PARA EL TEXT-TO-SPEECH (Sin formato):
    1. ESTRUCTURA: No uses listas, viñetas, guiones, ni encabezados. El texto debe ser un flujo continuo de palabras. Usa comas y puntos solo para marcar pausas naturales al hablar.
    2. LENGUAJE: Usa un tono profesional pero relajado (semi-casual). Evita frases de "relleno corporativo" como "procedo a informar" o "en relación a las tareas". Habla en primera persona del plural ("estuvimos", "le pegamos a").
    3. SÍNTESIS: No leas códigos de tickets (como ECO-33) a menos que sea estrictamente necesario para diferenciar tareas. Prefiere decir "el tema de las variantes" o "la parte de productos".
    4. CONEXIÓN LOGÍSTICA: Une los commits con el Kanban de forma orgánica. Si hiciste un commit de una interfaz, di: "Ya dejé lista la estructura para las variantes, que va amarrado a lo que tenemos en el tablero". También une la informacion extra con las tareas del kanban y los commits de git
    5. FILTRO: Ignora el estado 'To Do'. Enfócate solo en lo que se movió (Done) o lo que te está ocupando hoy (In Progress).
    6. REPETICIÓN: Para evitar repetir información entre dailies. Evita dar updates generales como "trabajamos en el modulo..." o "hicimos cambios en el modulo". En su lugar di que se trabajó y/o cambió.
    
    REGLAS DE ESTILO:
    - No saludes con "Hola equipo" de forma genérica. Empieza directo con algo como "Buen día, les paso el update rápido...".
    - No digas "actividad de git" o "tablero kanban". Di "lo que subí a repo" o "lo que tenemos pendiente".
    - Menciona todas las funcionalidades, fixes o actualizaciones realizadas.
    - Prohibido ofrecerte a resolver dudas o usar frases de cierre tipo "quedo atento".
    - No te inventes actividades no proporcionadas por la informacion extra o los commits de git. Si la tarjeta de kanban está en Done y los commits no mencionan la actividad. asume que ya fue reportada en dailies pasadas y no lo vuelvas a mencionar.
    - Si no hay novedades que reportar, solo di eso
    - No expliques el proposito de las actividades
    - No menciones el estado de las tarjetas
    - Unicamente menciona las actividades de desarrollo

    INFORMACION EXTRA:
    {extra_data}
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )


    
    return response.choices[0].message.content