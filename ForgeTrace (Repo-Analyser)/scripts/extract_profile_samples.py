#!/usr/bin/env python3
"""
Extract representative code samples from a repository for client profiling.

This script creates anonymized profiling datasets for benchmarking and validation.
"""

import argparse
import random
import shutil
from pathlib import Path
from typing import Dict, List, Set
import yaml
import json


def detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'JavaScript',
        '.tsx': 'TypeScript',
        '.go': 'Go',
        '.java': 'Java',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C/C++',
        '.rs': 'Rust',
        '.kt': 'Kotlin',
        '.swift': 'Swift',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.json': 'JSON',
        '.md': 'Markdown',
    }
    return ext_map.get(file_path.suffix.lower(), 'Unknown')


def collect_files(repo_path: Path, exclude_patterns: Set[str]) -> List[Path]:
    """Collect all relevant files from repository."""
    files = []
    
    for file_path in repo_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded paths
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue
        
        # Skip binary files
        if file_path.suffix.lower() in {
            '.png', '.jpg', '.jpeg', '.gif', '.svg',
            '.pdf', '.zip', '.tar', '.gz',
            '.exe', '.dll', '.so', '.dylib',
        }:
            continue
        
        files.append(file_path)
    
    return files


def stratified_sample(
    files: List[Path], 
    sample_size: int, 
    seed: int = 42
) -> Dict[str, List[Path]]:
    """
    Perform stratified sampling across programming languages.
    
    Returns dictionary mapping language -> sampled files.
    """
    random.seed(seed)
    
    # Group by language
    by_language: Dict[str, List[Path]] = {}
    for file_path in files:
        lang = detect_language(file_path)
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(file_path)
    
    # Calculate proportional sample sizes
    total_files = len(files)
    sampled: Dict[str, List[Path]] = {}
    
    for lang, lang_files in by_language.items():
        lang_proportion = len(lang_files) / total_files
        lang_sample_size = max(1, int(sample_size * lang_proportion))
        
        # Sample files
        if len(lang_files) <= lang_sample_size:
            sampled[lang] = lang_files
        else:
            sampled[lang] = random.sample(lang_files, lang_sample_size)
    
    return sampled


def create_metadata(
    profile_id: str,
    source: str,
    files: List[Path],
    sampled: Dict[str, List[Path]],
    seed: int
) -> dict:
    """Generate metadata.yaml content."""
    
    # Calculate language distribution
    lang_dist = {
        lang: len(lang_files) 
        for lang, lang_files in sampled.items()
    }
    
    # Calculate total size
    total_size = sum(
        f.stat().st_size 
        for lang_files in sampled.values() 
        for f in lang_files
    )
    
    metadata = {
        'profile_id': profile_id,
        'source': source,
        'date_created': '2025-11-16',
        'anonymized': True,
        
        'characteristics': {
            'repo_type': 'unknown',  # User should update
            'primary_languages': list(lang_dist.keys())[:3],
            'total_files': len(files),
            'total_loc': 'unknown',  # User should update
        },
        
        'sample_strategy': {
            'method': 'stratified',
            'sample_size': sum(lang_dist.values()),
            'language_distribution': lang_dist,
            'seed': seed,
        },
        
        'size_mb': round(total_size / (1024 * 1024), 2),
        
        'edge_cases': [],  # User should populate
        
        'expected_metrics': {
            'third_party_percentage': 'unknown',
            'foreground_percentage': 'unknown',
            'background_percentage': 'unknown',
        }
    }
    
    return metadata


def main():
    parser = argparse.ArgumentParser(
        description='Extract profiling samples from a repository'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to source repository'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output directory for profiling dataset'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=150,
        help='Number of files to sample (default: 150)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--profile-id',
        help='Profile identifier (default: derived from output path)'
    )
    parser.add_argument(
        '--source',
        default='Anonymous Client',
        help='Source description (e.g., "FinTech SaaS")'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Input path does not exist: {input_path}")
        return 1
    
    # Determine profile ID
    profile_id = args.profile_id or output_path.name
    
    print(f"📊 Creating profiling dataset: {profile_id}")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Sample size: {args.sample_size}")
    
    # Exclude common build/cache directories
    exclude_patterns = {
        'node_modules', '__pycache__', '.git', '.venv', 'venv',
        'dist', 'build', 'target', '.pytest_cache', 'coverage',
    }
    
    # Collect files
    print("\n🔍 Collecting files...")
    files = collect_files(input_path, exclude_patterns)
    print(f"   Found {len(files)} files")
    
    # Stratified sampling
    print("\n🎲 Performing stratified sampling...")
    sampled = stratified_sample(files, args.sample_size, args.seed)
    
    for lang, lang_files in sampled.items():
        print(f"   {lang}: {len(lang_files)} files")
    
    total_sampled = sum(len(f) for f in sampled.values())
    print(f"\n   Total sampled: {total_sampled} files")
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    samples_dir = output_path / 'samples'
    samples_dir.mkdir(exist_ok=True)
    
    # Copy sampled files
    print("\n📁 Copying files...")
    for lang, lang_files in sampled.items():
        for file_path in lang_files:
            # Preserve relative directory structure
            rel_path = file_path.relative_to(input_path)
            dest_path = samples_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
    
    print(f"   Copied {total_sampled} files to {samples_dir}")
    
    # Generate metadata
    print("\n📝 Generating metadata...")
    metadata = create_metadata(
        profile_id, args.source, files, sampled, args.seed
    )
    
    metadata_path = output_path / 'metadata.yaml'
    with open(metadata_path, 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    
    print(f"   Created {metadata_path}")
    print("\n✅ Profiling dataset created successfully!")
    print(f"\n📋 Next steps:")
    print(f"   1. Review and update {metadata_path}")
    print(f"   2. Run audit to generate ground truth:")
    print(f"      forgetrace audit {samples_dir} --out {output_path}/ground_truth")
    print(f"   3. Update training/profiling_datasets/catalog.yaml")
    
    return 0


if __name__ == '__main__':
    exit(main())
