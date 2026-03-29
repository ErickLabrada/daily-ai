import openai
import os
import asyncio

# Assuming you already have your 'commits' list from the previous steps
# and each commit now has a 'files_touched' key.

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_daily_report(commits_data, kanban_tasks):


    kanban_context = ""
    for task in kanban_tasks:
        kanban_context += f"- [{task['state']}] {task['folio']}: {task['title']}\n"

    # Format Git context
    git_context = ""
    for c in commits_data:
        files = ", ".join(c.get('files_touched', []))
        git_context += f"- Commit: {c['title']}\n  Files: {files}\n"

    prompt = f"""
    Eres un Senior Backend Engineer. Usa la siguiente informacion para escribir un reporte para el daily de tu proyecto.
    
    KANBAN BOARD TASKS:
    {kanban_context}
    
    GIT ACTIVITY:
    {git_context}
    
    Instrucciones:
    1. Conecta la actividad de git con las tareas de kanban cuando sea posible.
    2. Si hay actividad de git sin cuadrar con tareas de kanban, enlistala como 'otras mejoras tecnicas'
    3. Usa terminos tecnicos: Arquitectura hexagonal, grpc, sqlc, postgresql.
    4. Enfocate en los estados 'Done' y 'In Progress'.
    5. Escribe el reporte de manera semi-casual. Como si estuvieses hablando directamente con el personal
    6. No incluyas titulos, separadores u otro tipo de puntuacion efectiva para textos. Tu respuesta sera reproducida por un text to speech por lo que debe ser fluida y conversacional
    7. Trata de mantener la actualizacion general, no hables de implementacion o metodos en especifico a menos que sea relevante
    8. No ofrezcas responder preguntas
    9. No des una explicacion de la tarea kanban, si es necesario puedes decir el titulo o palabras clave de la funcionalidad
    10. Al final del mensaje, anuncia de manera juguetona que la respuesta fue autogenerada por un agente de IA como malicious compliance ante la insistencia de la implementacion de IA en el flujo de trabajo
        """

    response = await client.chat.completions.create(
        model="gpt-4o", # or gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content