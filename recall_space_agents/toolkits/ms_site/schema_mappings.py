"""
This module defines the schema mappings for the Microsoft SharePoint
Site functionality,
including the input schemas for extracting text from files, searching
for files, and listing files and folders.

Classes:
    ExtractTextFromFileByPathSchema: Schema for extracting text from a
    file given site name and file path.
    SearchAndExtractTextSchema: Schema for searching for a file by name
    and extracting its text.
    ListFilesAndFoldersSchema: Schema for listing files and folders in a
    given path.

Variables:
    schema_mappings: A dictionary mapping method names to their
    descriptions and input schemas.
"""

from pydantic import BaseModel, Field
from textwrap import dedent

class ExtractTextFromFileByPathSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_path: str = Field(
        ...,
        description=dedent("""
            Path to the file within the site's drive.
            For example: '/Folder1/file.docx'.
            Supported file types: .docx, .pdf, .xlsx
        """)
    )

class SearchAndExtractTextSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    file_name: str = Field(
        ...,
        description=dedent("""
            Exact name of the file to search for, including extension.
            For example: 'report.pdf'
            Supported file types: .docx, .pdf, .xlsx
        """)
    )

class ListFilesAndFoldersSchema(BaseModel):
    site_display_name: str = Field(
        ...,
        description="Display name of the SharePoint site."
    )
    folder_path: str = Field(
        ...,
        description=dedent("""
            Path to the folder within the site's drive.
            For example: '/Documents/Folder1/'
            Lists all files and folders within this path.
        """)
    )

schema_mappings = {
    "aextract_text_from_file_by_path": {
        "description": dedent("""
            Extract text from a file in a SharePoint site given the site 
            display name and file path.
            Supports .docx, .pdf, and .xlsx files."""),
        "input_schema": ExtractTextFromFileByPathSchema,
    },
    "asearch_and_extract_text": {
        "description": dedent("""
            Search for a file by name within a
            SharePoint site and extract its text. Performs an exact match
            search. Supports .docx, .pdf, and .xlsx files."""),
        "input_schema": SearchAndExtractTextSchema,
    },
    "alist_files_and_folders_in_path": {
        "description": dedent("""
            List the names of files and folders within
            a given path inside a SharePoint site's drive."""),
        "input_schema": ListFilesAndFoldersSchema,
    },
}