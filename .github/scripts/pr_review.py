#!/usr/bin/env python3
"""
Script para revisar Pull Requests usando OpenAI GPT-4
"""
import os
import requests
from openai import OpenAI

def main():
    # Configuración desde variables de entorno
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    REPO = os.environ['GITHUB_REPOSITORY']
    PR_NUMBER = os.environ['PR_NUMBER']
    
    # Headers para GitHub API
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print(f"📋 Obteniendo información del PR #{PR_NUMBER} en {REPO}...")
    
    # Obtener información del PR
    pr_url = f'https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}'
    pr_response = requests.get(pr_url, headers=headers)
    pr_response.raise_for_status()
    pr_data = pr_response.json()
    
    print(f"✅ PR obtenido: {pr_data.get('title', 'N/A')}")
    
    # Obtener archivos cambiados
    files_url = f'https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files'
    files_response = requests.get(files_url, headers=headers)
    files_response.raise_for_status()
    files_data = files_response.json()
    
    print(f"📁 Archivos cambiados: {len(files_data)}")
    
    # Construir el contexto para OpenAI
    changes_summary = []
    total_changes = 0
    
    for file in files_data:
        if file['status'] in ['added', 'modified']:
            changes_summary.append(f"**Archivo:** `{file['filename']}`")
            changes_summary.append(f"- Cambios: +{file['additions']} -{file['deletions']}")
            total_changes += file['additions'] + file['deletions']
            
            # Incluir el diff si es razonablemente pequeño
            if file['patch'] and len(file['patch']) < 3000:
                changes_summary.append(f"```diff\n{file['patch']}\n```")
            elif file['patch']:
                # Si es muy grande, solo incluir las primeras líneas
                patch_preview = '\n'.join(file['patch'].split('\n')[:50])
                changes_summary.append(f"```diff\n{patch_preview}\n... (diff truncado, muy grande)\n```")
            
            changes_summary.append("")
    
    context = "\n".join(changes_summary)
    
    # Limitar el tamaño del contexto si es muy grande
    if total_changes > 500:
        print("⚠️  Muchos cambios detectados, resumiendo para la revisión...")
        context = context[:8000] + "\n\n... (contexto truncado debido al tamaño)"
    
    # Prompt para OpenAI
    prompt = f"""Realiza una revisión completa del código en este Pull Request.

**Título del PR:** {pr_data.get('title', 'N/A')}
**Descripción:** {pr_data.get('body', 'N/A') or 'Sin descripción'}

**Cambios en el código:**
{context}

Por favor, analiza:
1. **Calidad del código**: Estructura, legibilidad, y mejores prácticas
2. **Seguridad**: Posibles vulnerabilidades o problemas de seguridad
3. **Rendimiento**: Optimizaciones posibles
4. **Mantenibilidad**: Código limpio y fácil de mantener
5. **Testing**: Verifica si hay tests adecuados para los cambios

Proporciona comentarios constructivos y sugerencias de mejora específicas.
Si encuentras problemas críticos, márcalos claramente con ⚠️.

Sé educativo y explica el por qué de tus sugerencias.

Formatea tu respuesta en Markdown con secciones claras."""

    print("🤖 Enviando código a OpenAI GPT-4 para revisión...")
    
    # Llamar a OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Eres un experto revisor de código que proporciona feedback constructivo y educativo. Eres profesional, amigable y específico en tus sugerencias."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.3
    )
    
    review_comment = response.choices[0].message.content
    
    print("✅ Revisión generada, publicando en el PR...")
    
    # Publicar comentario en el PR
    comment_url = f'https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments'
    comment_data = {
        'body': f"## 🤖 Revisión de Código con GPT-4\n\n{review_comment}\n\n---\n*Revisión automática generada por GitHub Actions*"
    }
    
    comment_response = requests.post(comment_url, headers=headers, json=comment_data)
    
    if comment_response.status_code == 201:
        print("✅ Revisión publicada exitosamente en el PR")
    else:
        print(f"❌ Error al publicar comentario: {comment_response.status_code}")
        print(comment_response.text)
        exit(1)

if __name__ == "__main__":
    main()

