"""
Batch Processor — apply audio transformation pipelines to directories.

This skill orchestrates other daw-master skills to process
batch directories of audio files with progress tracking.
"""

from .pipeline import process_directory, process_file, batch_transform

__all__ = ['process_directory', 'process_file', 'batch_transform']
