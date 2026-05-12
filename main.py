import os
import time
import json
import typer
import sys
from datetime import datetime
from google import genai
from google.api_core import exceptions as google_exceptions
from git import Repo, exc as git_exceptions
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live

from config import API_KEY, MODEL_31B, MODEL_26B, MAX_DIFF_LENGTH, DEFAULT_IGNORES
from personas import PERSONAS
from privacy_shield import PrivacyShield
from models import AnalysisResponse
from utils import extract_json_from_text
from orchestrator import ReasoningOrchestrator

# --- Fail-Fast Validation ---
if not API_KEY or API_KEY == "[REDACTED]":
    print("[bold red]ERROR:[/bold red] GEMMA_API_KEY is missing. Please set it in your .env file.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
orchestrator = ReasoningOrchestrator(client)
console = Console()
app = typer.Typer(help="Diff-Narrator: AI-Powered Code Review Storyteller")

def get_git_diff(client=None, model_name=None, ignore_patterns=None, include_all=False):
    """Fetches the staged or unstaged diff and truncates it based on tokens if client is provided."""
    try:
        repo = Repo(os.getcwd(), search_parent_directories=True)
        
        # Prepare pathspecs for exclusion
        pathspecs = ["."]
        if ignore_patterns:
            for pattern in ignore_patterns:
                if pattern.strip():
                    pathspecs.append(f":(exclude){pattern.strip()}")
        
        # --all flag: combine staged and unstaged
        if include_all:
            diff = repo.git.diff('HEAD', '--', *pathspecs)
        else:
            diff = repo.git.diff('--cached', '--', *pathspecs)
            if not diff:
                diff = repo.git.diff('--', *pathspecs)
        
        if not diff:
            return None

        # --- Binary File Protection ---
        if "Binary files" in diff:
            lines = [line for line in diff.split("\n") if "Binary files" not in line]
            diff = "\n".join(lines)

        # --- Token-Aware Truncation (Boundary Aware) ---
        if client and model_name:
            try:
                TOKEN_LIMIT = 6000 
                token_count_resp = client.models.count_tokens(model=model_name, contents=diff)
                total_tokens = token_count_resp.total_tokens
                
                if total_tokens > TOKEN_LIMIT:
                    # Heuristic for a safe starting point
                    char_limit = TOKEN_LIMIT * 3
                    truncated_segment = diff[:char_limit]
                    
                    # Find the last file boundary to avoid chopping a file in half
                    last_boundary = truncated_segment.rfind("diff --git")
                    if last_boundary != -1 and last_boundary > (char_limit // 2):
                        diff = diff[:last_boundary] + f"\n\n...[Diff truncated at file boundary to stay within {TOKEN_LIMIT} tokens]..."
                    else:
                        # Fallback to naive truncation if no boundary is found or it's too early
                        diff = truncated_segment + f"\n\n...[Diff truncated naively at {TOKEN_LIMIT} tokens]..."
            except Exception:
                if len(diff) > MAX_DIFF_LENGTH:
                    diff = diff[:MAX_DIFF_LENGTH] + "\n\n...[Diff truncated]..."
        
        return diff
    except git_exceptions.InvalidGitRepositoryError:
        console.print("[bold red]Git Error:[/bold red] You are not in a valid git repository.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error accessing git repo:[/bold red] {e}")
        raise typer.Exit(code=1)

def print_dashboard(analysis):
    """Displays a professional dashboard with the review results."""
    console.print(Panel(Markdown(analysis.get("story", "No story generated.")), title="[bold cyan]The Narrative[/bold cyan]", border_style="cyan"))

    table = Table(title="[bold red]Risk Radar[/bold red]", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Category", style="dim", width=20)
    table.add_column("Assessment", justify="left")
    table.add_column("Level", justify="center")

    risks = analysis.get("risks", [])
    for risk in risks:
        level = risk.get("level", "Low").upper()
        color = "green" if "LOW" in level else "yellow" if "MEDIUM" in level else "red"
        table.add_row(risk.get("category", "General"), risk.get("description", "N/A"), f"[{color}]{level}[/{color}]")
    
    console.print(table)

    improvements = analysis.get("improvements", [])
    if improvements:
        imp_text = "\n".join([f"- {imp}" for imp in improvements])
        console.print(Panel(imp_text, title="[bold green]Suggested Improvements[/bold green]", border_style="green"))

@app.command()
def narrate(
    persona: str = typer.Option("senior", "--persona", "-p", help="Persona style: senior, mentor, pirate"),
    save: bool = typer.Option(False, "--save", "-s", help="Save the story to a timestamped file"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use (overrides .env)"),
    skip_shield: bool = typer.Option(False, "--skip-shield", help="Skip the Privacy Shield scan"),
    deep: bool = typer.Option(False, "--deep", "-d", help="Enable deep multi-stage reasoning pipeline"),
    ignore: str = typer.Option(None, "--ignore", "-i", help="Comma-separated glob patterns to ignore"),
    include_all: bool = typer.Option(False, "--all", "-a", help="Include both staged and unstaged changes"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the redacted diff and exit without calling AI")
):
    """Analyze the current git diff and tell its story."""
    selected_persona = PERSONAS.get(persona.lower(), PERSONAS["senior"])
    model_to_use = model or os.getenv("GEMMA_MODEL_31B", MODEL_31B)
    
    # Process ignore patterns
    ignore_list = list(DEFAULT_IGNORES)
    if ignore:
        ignore_list.extend(ignore.split(","))
    
    diff_text = get_git_diff(client, model_to_use, ignore_list, include_all)
    if not diff_text:
        console.print("[yellow]No changes found in the current repository.[/yellow]")
        return

    # --- Pre-Flight Privacy Shield ---
    shielded = False
    if not skip_shield:
        shield = PrivacyShield()
        if shield.scan(diff_text):
            summary = shield.get_summary()
            summary_text = ", ".join([f"{cat} ({count})" for cat, count in summary.items()])
            console.print(Panel(
                f"[bold red]PRIVACY ALERT![/bold red]\nSensitive information detected: [yellow]{summary_text}[/yellow]\n"
                "Auto-redacting for your safety before processing.",
                title="[bold red]Privacy Shield[/bold red]",
                border_style="red"
            ))
            diff_text = shield.redact(diff_text)
            shielded = True
    
    if dry_run:
        console.print(Panel(diff_text, title="[bold yellow]Dry Run: Redacted Diff[/bold yellow]", border_style="yellow"))
        console.print("[dim]Dry run complete. No AI calls were made.[/dim]")
        return

    console.print(Panel.fit(
        f"[bold white]Diff-Narrator[/bold white]\n[dim]Persona: {selected_persona['name']}[/dim]", 
        border_style="cyan"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            if not deep:
                progress.add_task(description=f"Gemma 4 is analyzing...", total=None)
                analysis = orchestrator.run_standard_pipeline(model_to_use, selected_persona, diff_text)
            else:
                task = progress.add_task(description="Initializing Deep Pipeline...", total=None)
                def update_progress(msg): progress.update(task, description=msg)
                analysis = orchestrator.run_deep_pipeline(model_to_use, selected_persona, diff_text, update_progress)
        except Exception as e:
            console.print(f"[orange3]Pipeline error: {e}. Falling back to 26B model...[/orange3]")
            try:
                analysis = orchestrator.run_fallback_pipeline(selected_persona, diff_text)
            except Exception as final_e:
                console.print(f"[bold red]Critical Error:[/bold red] Failed to get response from Gemma. {final_e}")
                raise typer.Exit(code=1)

    print_dashboard(analysis)

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_{timestamp}.md"
        try:
            with open(filename, "w") as f:
                f.write(f"# Diff-Narrator Story\n\n## Persona: {selected_persona['name']}\n")
                f.write(f"## Model: {model_to_use}\n")
                f.write(f"## Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(analysis.get("story", ""))
                f.write("\n\n## Risk Assessment\n\n")
                for risk in analysis.get("risks", []):
                    f.write(f"- **{risk.get('category')}**: {risk.get('description')} ({risk.get('level')})\n")
                f.write("\n\n## Improvements\n\n")
                for imp in analysis.get("improvements", []):
                    f.write(f"- {imp}\n")
            console.print(f"\n[bold green]Story saved to {filename}[/bold green]")
        except OSError as e:
            console.print(f"[bold red]Save Error:[/bold red] Could not write to {filename}: {e}")

@app.command()
def chat(
    persona: str = typer.Option("senior", "--persona", "-p", help="Persona style: senior, mentor, pirate"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use (overrides .env)"),
    skip_shield: bool = typer.Option(False, "--skip-shield", help="Skip the Privacy Shield scan"),
    ignore: str = typer.Option(None, "--ignore", "-i", help="Comma-separated glob patterns to ignore"),
    include_all: bool = typer.Option(False, "--all", "-a", help="Include both staged and unstaged changes")
):
    """Enter an interactive chat session about your current git diff."""
    selected_persona = PERSONAS.get(persona.lower(), PERSONAS["senior"])
    model_to_use = model or os.getenv("GEMMA_MODEL_31B", MODEL_31B)
    
    # Process ignore patterns
    ignore_list = list(DEFAULT_IGNORES)
    if ignore:
        ignore_list.extend(ignore.split(","))

    console.print(Panel.fit(
        f"[bold white]Diff-Chat REPL[/bold white]\n[dim]Persona: {selected_persona['name']}[/dim]\n"
        "Type 'exit' or 'quit' to end the session.", 
        border_style="magenta"
    ))
    
    diff_text = get_git_diff(client, model_to_use, ignore_list, include_all)
    if not diff_text:
        console.print("[yellow]No changes found in the current repository.[/yellow]")
        return

    if not skip_shield:
        shield = PrivacyShield()
        if shield.scan(diff_text):
            console.print("[dim yellow]Privacy Shield: Redacting sensitive data before chat initialization...[/dim yellow]")
            diff_text = shield.redact(diff_text)
    
    system_prompt = f"{selected_persona['system_prompt']}\n\nYou are currently analyzing this git diff:\n<git_diff>\n{diff_text}\n</git_diff>\n\nHelp the user with any questions they have about this code."
    
    try:
        chat_session = client.chats.create(
            model=model_to_use,
            config={"system_instruction": system_prompt}
        )
        
        console.print(f"\n[bold cyan]{selected_persona['name']}:[/bold cyan] I've analyzed your changes. What would you like to know about them?")
        
        while True:
            try:
                user_input = console.input("\n[bold green]You>[/bold green] ")
            except EOFError:
                console.print("\n[dim]Ending chat session. Goodbye![/dim]")
                break
            
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[dim]Ending chat session. Goodbye![/dim]")
                break
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description=f"{selected_persona['name']} is thinking...", total=None)
                
                max_retries = 5
                for i in range(max_retries):
                    try:
                        response = chat_session.send_message(user_input)
                        console.print(Panel(Markdown(response.text), title=f"[bold cyan]{selected_persona['name']}[/bold cyan]", border_style="cyan"))
                        break
                    except Exception as e:
                        error_str = str(e).upper()
                        if any(code in error_str for code in ["500", "503", "429", "INTERNAL", "OVERLOADED"]) and i < max_retries - 1:
                            wait_time = (2 ** i) + 3
                            time.sleep(wait_time)
                        else:
                            console.print(f"[bold red]API Error:[/bold red] {e}")
                            break
                    
    except Exception as e:
        console.print(f"[bold red]Failed to initialize chat session:[/bold red] {e}")

@app.command()
def list_personas():
    """List available personas and their descriptions."""
    table = Table(title="Available Personas", show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="dim")
    
    for key, p in PERSONAS.items():
        table.add_row(key, p["name"], p["description"])
    
    console.print(table)

if __name__ == "__main__":
    app()