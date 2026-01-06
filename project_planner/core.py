"""Core utilities for project planner."""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


def setup_claude_skills(package_dir: Path, work_dir: Path) -> None:
    """
    Set up Claude skills and PLANNER.md by copying .claude/ from package to working directory.

    Args:
        package_dir: Package installation directory containing .claude/
        work_dir: User's working directory where .claude/ should be copied
    """
    source_claude = package_dir / ".claude"
    dest_claude = work_dir / ".claude"
    
    # Copy .claude directory (which includes skills/ and WRITER.md) if source exists and destination doesn't
    if source_claude.exists() and not dest_claude.exists():
        try:
            shutil.copytree(source_claude, dest_claude)
            # Note: No print statements - API should be silent, progress comes via ProgressUpdate
        except Exception as e:
            pass  # Silent failure - API users can check for skills availability if needed
    # Note: No warning prints - keep API output clean


def get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get the Anthropic API key.
    
    Args:
        api_key: Optional API key to use. If not provided, reads from environment.
        
    Returns:
        The API key.
        
    Raises:
        ValueError: If API key is not found.
    """
    if api_key:
        return api_key
    
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if not env_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Either pass api_key parameter or set "
            "ANTHROPIC_API_KEY environment variable."
        )
    return env_key


def load_system_instructions(work_dir: Path) -> str:
    """
    Load system instructions from .claude/PLANNER.md in the working directory.

    Args:
        work_dir: Working directory containing .claude/PLANNER.md.

    Returns:
        System instructions string.
    """
    instructions_file = work_dir / ".claude" / "PLANNER.md"

    # Fallback to WRITER.md for backwards compatibility
    if not instructions_file.exists():
        instructions_file = work_dir / ".claude" / "WRITER.md"

    if instructions_file.exists():
        with open(instructions_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback if no instructions file exists
        return (
            "You are a project planning assistant. Help users research, plan, and "
            "document software projects with architecture designs and implementation roadmaps."
        )


def ensure_output_folder(cwd: Path, custom_dir: Optional[str] = None) -> Path:
    """
    Ensure the planning_outputs folder exists.

    Args:
        cwd: Current working directory (project root).
        custom_dir: Optional custom output directory path.

    Returns:
        Path to the output folder.
    """
    if custom_dir:
        output_folder = Path(custom_dir).resolve()
    else:
        output_folder = cwd / "planning_outputs"

    output_folder.mkdir(exist_ok=True, parents=True)
    return output_folder


def get_image_extensions() -> set:
    """Return a set of common image file extensions."""
    return {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp', '.ico'}


def get_manuscript_extensions() -> set:
    """Return a set of manuscript file extensions that should go to drafts/ folder."""
    return {'.tex'}


def get_source_extensions() -> set:
    """Return a set of source/context file extensions that should go to sources/ folder."""
    return {'.md', '.docx', '.pdf'}


def get_data_extensions() -> set:
    """Return a set of data file extensions that should go to data/ folder."""
    return {'.csv', '.json', '.txt', '.xlsx', '.xls', '.tsv', '.xml', '.yaml', '.yml', '.sql'}


def get_data_files(cwd: Path, data_files: Optional[List[str]] = None) -> List[Path]:
    """
    Get data files either from provided list or from data folder.
    
    Args:
        cwd: Current working directory (project root).
        data_files: Optional list of file paths. If not provided, reads from data/ folder.
        
    Returns:
        List of Path objects for data files.
    """
    if data_files:
        return [Path(f).resolve() for f in data_files]
    
    data_folder = cwd / "data"
    if not data_folder.exists():
        return []
    
    files = []
    for file_path in data_folder.iterdir():
        if file_path.is_file():
            files.append(file_path)
    
    return files


def extract_images_from_docx(docx_path: Path, figures_output: Path) -> List[Dict[str, Any]]:
    """
    Extract all images from a .docx file and copy them to the figures folder.
    
    A .docx file is a ZIP archive containing images in the word/media/ directory.
    This function extracts all image files and copies them to the specified output directory.
    
    Args:
        docx_path: Path to the .docx file.
        figures_output: Path to the figures output directory.
        
    Returns:
        List of dictionaries containing information about extracted images.
        Each dict has 'name', 'path', and 'source_docx' keys.
    """
    extracted_images = []
    image_extensions = get_image_extensions()
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            # List all files in the archive
            all_files = zip_ref.namelist()
            
            # Filter for files in word/media/ directory that are images
            media_files = [f for f in all_files if f.startswith('word/media/')]
            
            for media_file in media_files:
                # Get the filename from the path
                file_name = Path(media_file).name
                file_ext = Path(media_file).suffix.lower()
                
                # Only extract if it's an image file
                if file_ext in image_extensions:
                    # Extract to figures folder
                    output_path = figures_output / file_name
                    
                    # Read the file from the zip and write it to the output
                    with zip_ref.open(media_file) as source:
                        with open(output_path, 'wb') as target:
                            target.write(source.read())
                    
                    extracted_images.append({
                        'name': file_name,
                        'path': str(output_path),
                        'source_docx': docx_path.name
                    })
    
    except zipfile.BadZipFile:
        print(f"Warning: {docx_path.name} is not a valid .docx file (ZIP archive)")
    except Exception as e:
        print(f"Warning: Could not extract images from {docx_path.name}: {str(e)}")
    
    return extracted_images


def process_data_files(
    cwd: Path,
    data_files: List[Path],
    project_output_path: str,
    delete_originals: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Process data files by copying them to the project output folder.
    Spec files (.md) go to specifications/,
    images go to diagrams/,
    data files (csv, json, etc.) go to data/,
    everything else goes to sources/.

    Args:
        cwd: Current working directory (project root).
        data_files: List of file paths to process.
        project_output_path: Path to the project output directory.
        delete_originals: Whether to delete original files after copying.

    Returns:
        Dictionary with information about processed files, or None if no files.
    """
    if not data_files:
        return None

    project_output = Path(project_output_path)
    data_output = project_output / "data"
    diagrams_output = project_output / "diagrams"
    specs_output = project_output / "specifications"
    sources_output = project_output / "sources"
    
    # Ensure output directories exist
    data_output.mkdir(parents=True, exist_ok=True)
    diagrams_output.mkdir(parents=True, exist_ok=True)
    specs_output.mkdir(parents=True, exist_ok=True)
    sources_output.mkdir(parents=True, exist_ok=True)
    
    image_extensions = get_image_extensions()
    manuscript_extensions = get_manuscript_extensions()
    source_extensions = get_source_extensions()
    data_extensions = get_data_extensions()
    
    processed_info = {
        'data_files': [],
        'image_files': [],
        'spec_files': [],
        'source_files': [],
        'all_files': []
    }

    for file_path in data_files:
        file_ext = file_path.suffix.lower()
        file_name = file_path.name

        # Determine destination based on file type
        # Priority: specs (.md with spec in name) → specifications/, images → diagrams/,
        # data files → data/, everything else → sources/

        if file_ext == '.md' and ('spec' in file_name.lower() or 'requirement' in file_name.lower()):
            # Spec files go to specifications/ folder
            destination = specs_output / file_name
            file_type = 'spec'
            processed_info['spec_files'].append({
                'name': file_name,
                'path': str(destination),
                'original': str(file_path),
                'extension': file_ext
            })
        elif file_ext in image_extensions:
            destination = diagrams_output / file_name
            file_type = 'image'
            processed_info['image_files'].append({
                'name': file_name,
                'path': str(destination),
                'original': str(file_path)
            })
        elif file_ext in data_extensions:
            destination = data_output / file_name
            file_type = 'data'
            processed_info['data_files'].append({
                'name': file_name,
                'path': str(destination),
                'original': str(file_path)
            })
        else:
            # Everything else goes to sources/
            destination = sources_output / file_name
            file_type = 'source'
            processed_info['source_files'].append({
                'name': file_name,
                'path': str(destination),
                'original': str(file_path),
                'extension': file_ext
            })
        
        # Copy the file
        try:
            shutil.copy2(file_path, destination)
            processed_info['all_files'].append({
                'name': file_name,
                'type': file_type,
                'destination': str(destination)
            })
            
            # If it's a .docx file, extract images to diagrams folder
            if file_ext == '.docx':
                extracted_images = extract_images_from_docx(file_path, diagrams_output)
                if extracted_images:
                    for img_info in extracted_images:
                        processed_info['image_files'].append(img_info)
            
            # Delete the original file after successful copy if requested
            if delete_originals:
                file_path.unlink()
            
        except Exception as e:
            print(f"Warning: Could not process {file_name}: {str(e)}")
    
    return processed_info


def create_data_context_message(processed_info: Optional[Dict[str, Any]]) -> str:
    """
    Create a context message about available data files.
    
    Args:
        processed_info: Dictionary with processed file information.
        
    Returns:
        Context message string.
    """
    if not processed_info or not processed_info['all_files']:
        return ""
    
    context_parts = ["\n[DATA FILES AVAILABLE]"]

    # If spec files are present, note them
    if processed_info.get('spec_files'):
        context_parts.append("\n📋 Specification files detected (in specifications/ folder):")
        for file_info in processed_info['spec_files']:
            context_parts.append(f"  - {file_info['name']}: {file_info['path']}")
        context_parts.append("\n→ Use these as requirements input for the project plan")
    
    if processed_info.get('source_files'):
        context_parts.append("\nSource/Context files (in sources/ folder for reference):")
        for file_info in processed_info['source_files']:
            ext = file_info.get('extension', '')
            context_parts.append(f"  - {file_info['name']} ({ext}): {file_info['path']}")
        context_parts.append("\nNote: These files are available as reference/context material.")
    
    if processed_info.get('data_files'):
        context_parts.append("\nData files (in data/ folder):")
        for file_info in processed_info['data_files']:
            context_parts.append(f"  - {file_info['name']}: {file_info['path']}")
    
    if processed_info.get('image_files'):
        # Separate images by source (direct vs extracted from docx)
        direct_images = [img for img in processed_info['image_files'] if 'source_docx' not in img]
        extracted_images = [img for img in processed_info['image_files'] if 'source_docx' in img]

        context_parts.append("\nImage/diagram files (in diagrams/ folder):")

        if direct_images:
            context_parts.append("  Directly provided:")
            for file_info in direct_images:
                context_parts.append(f"    - {file_info['name']}: {file_info['path']}")

        if extracted_images:
            # Group extracted images by source docx
            from collections import defaultdict
            images_by_docx = defaultdict(list)
            for img in extracted_images:
                images_by_docx[img['source_docx']].append(img)

            context_parts.append("  Extracted from .docx files:")
            for docx_name, images in images_by_docx.items():
                img_names = ', '.join([img['name'] for img in images])
                context_parts.append(f"    - From {docx_name}: {img_names}")

        context_parts.append("\nNote: These can be referenced as existing diagrams or mockups.")
    
    context_parts.append("[END DATA FILES]\n")
    
    return "\n".join(context_parts)

